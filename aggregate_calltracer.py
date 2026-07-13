#!/usr/bin/env python3
"""
Aggregate callTracer _comparison.json files into a divergence report.

Walks a traces directory produced by `compare_traces.py --tracer calltracer`,
groups differences by behavior (diff type + field + deviating client set),
and emits a markdown summary with counts and examples.

Usage: python aggregate_calltracer.py ./traces-sepolia [-o summary-calltracer.md]
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path


def majority_deviants(values_or_sets):
    """Given {client: value}, return the clients holding a minority value."""
    if not isinstance(values_or_sets, dict):
        return ()
    groups = defaultdict(list)
    for client, val in values_or_sets.items():
        groups[json.dumps(val, sort_keys=True, default=str)].append(client)
    if len(groups) < 2:
        return ()
    ranked = sorted(groups.values(), key=len, reverse=True)
    deviants = []
    for g in ranked[1:]:
        deviants.extend(g)
    return tuple(sorted(deviants))


def diff_row_key(diff):
    """Group a difference into a behavior row: (type, field, deviant clients)."""
    dtype = diff["type"]
    key = diff.get("key", "")
    if dtype in ("missing_field", "missing_frame"):
        deviants = tuple(sorted(diff.get("missing_in", [])))
    elif dtype == "error_class_mismatch":
        deviants = majority_deviants(diff.get("classes", {}))
    elif dtype in ("call_count_mismatch", "log_count_mismatch",
                   "block_entry_count_mismatch"):
        deviants = majority_deviants(diff.get("counts", {}))
    else:
        deviants = majority_deviants(diff.get("values", {}))
    return (dtype, key, deviants)


def walk_comparisons(root):
    """Yield (context, comparison) for every _comparison.json under root."""
    for path in sorted(root.rglob("_comparison.json")):
        rel = path.relative_to(root)
        try:
            with open(path) as f:
                cmp_data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"skip {rel}: {e}")
            continue
        ctx = str(rel.parent)
        yield ctx, cmp_data
        for tx_hash, tx_cmp in cmp_data.get("per_tx", {}).items():
            yield f"{ctx}::{tx_hash}", tx_cmp


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("traces_dir", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=None)
    parser.add_argument("--max-examples", type=int, default=3)
    args = parser.parse_args()

    root = args.traces_dir
    out_path = args.output or root / "summary-calltracer.md"

    meta = {}
    meta_file = root / "run_meta.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text())

    rows = defaultdict(lambda: {"count": 0, "examples": [], "configs": defaultdict(int)})
    quirk_rows = defaultdict(lambda: {"count": 0, "examples": [], "clients": defaultdict(int)})
    rpc_errors = defaultdict(lambda: defaultdict(int))
    total_comparisons = 0
    identical = 0

    for ctx, cmp_data in walk_comparisons(root):
        total_comparisons += 1
        config = next((c for c in ("onlyTopCallWithLog", "onlyTopCall", "withLog", "default")
                       if f"/{c}" in f"/{ctx}/" or ctx.endswith(c)), "?")
        diffs = cmp_data.get("differences", [])
        quirks = cmp_data.get("format_quirks", {})
        if not diffs and not quirks and not cmp_data.get("errors"):
            identical += 1
        for client, err in (cmp_data.get("errors") or {}).items():
            rpc_errors[client][str(err)[:120]] += 1
        for diff in diffs:
            if diff["type"] == "insufficient_successful_traces":
                continue
            row = rows[diff_row_key(diff)]
            row["count"] += 1
            row["configs"][config] += 1
            if len(row["examples"]) < args.max_examples:
                row["examples"].append({"ctx": ctx, **{k: v for k, v in diff.items()
                                                       if k != "type"}})
        for quirk_kind, by_field in quirks.items():
            for field, items in by_field.items():
                row = quirk_rows[(quirk_kind, field)]
                row["count"] += len(items)
                for item in items:
                    forms = item.get("forms") or item.get("styles") or {}
                    for client, form in forms.items():
                        row["clients"][f"{client}:{form}"] += 1
                    if len(row["examples"]) < args.max_examples:
                        row["examples"].append({"ctx": ctx, **item})

    lines = ["# callTracer cross-client divergence summary", ""]
    if meta:
        lines += ["## Run metadata", ""]
        for c, v in meta.get("client_versions", {}).items():
            lines.append(f"- **{c}**: `{v}`")
        lines.append(f"- methods: {', '.join(meta.get('methods', []))};"
                     f" configs: {', '.join(meta.get('configs', []))}")
        lines.append("")

    lines += [f"## Overview", "",
              f"- comparisons analyzed: {total_comparisons}",
              f"- fully identical: {identical}",
              f"- semantic behavior rows: {len(rows)}",
              f"- wire-format quirk rows: {len(quirk_rows)}", ""]

    if rows:
        lines += ["## Semantic divergences", "",
                  "| type | field | deviating clients | count | configs |",
                  "|---|---|---|---|---|"]
        for (dtype, key, deviants), row in sorted(rows.items(), key=lambda x: -x[1]["count"]):
            cfgs = ", ".join(f"{c}×{n}" for c, n in sorted(row["configs"].items()))
            lines.append(f"| {dtype} | {key or '—'} | {', '.join(deviants) or '?'} "
                         f"| {row['count']} | {cfgs} |")
        lines.append("")
        lines += ["### Examples", ""]
        for (dtype, key, deviants), row in sorted(rows.items(), key=lambda x: -x[1]["count"]):
            lines.append(f"**{dtype} / {key or '—'} / {', '.join(deviants) or '?'}**")
            for ex in row["examples"]:
                lines.append(f"```json\n{json.dumps(ex, indent=1, default=str)[:800]}\n```")
            lines.append("")

    if quirk_rows:
        lines += ["## Wire-format quirks", "",
                  "| kind | field | count | client forms |",
                  "|---|---|---|---|"]
        for (kind, field), row in sorted(quirk_rows.items(), key=lambda x: -x[1]["count"]):
            top_forms = sorted(row["clients"].items(), key=lambda x: -x[1])[:6]
            forms = "; ".join(f"{k} ({n})" for k, n in top_forms)
            lines.append(f"| {kind} | {field} | {row['count']} | {forms} |")
        lines.append("")

    if rpc_errors:
        lines += ["## RPC errors during collection", ""]
        for client, errs in sorted(rpc_errors.items()):
            lines.append(f"- **{client}**:")
            for err, n in sorted(errs.items(), key=lambda x: -x[1]):
                lines.append(f"  - ×{n}: `{err}`")
        lines.append("")

    out_path.write_text("\n".join(lines))
    print(f"Wrote {out_path} ({len(rows)} semantic rows, {len(quirk_rows)} quirk rows, "
          f"{total_comparisons} comparisons)")


if __name__ == "__main__":
    main()
