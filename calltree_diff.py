"""
Recursive, path-aware diff for callTracer output (call frame trees).

Produces the same two-tier classification as the structlog comparison:
- differences: semantic mismatches (values, tree shape, missing frames)
- format_quirks: wire-format variations that normalize to the same meaning
  (omitted vs null vs "0x", hex padding/case, error-string wording)

Paths address frames like "calls[0].calls[2]" with "" for the root frame.
"""

import json
from collections import defaultdict

FRAME_SCALAR_FIELDS = [
    "type", "from", "to", "value", "gas", "gasUsed",
    "input", "output", "error", "revertReason",
]

HEX_QUANTITY_FIELDS = {"value", "gas", "gasUsed"}
HEX_BYTES_FIELDS = {"from", "to", "input", "output"}

LOG_FIELDS = ["address", "topics", "data", "index", "position"]

ERROR_CLASSES = [
    ("reverted", ["execution reverted", "revert"]),
    ("out-of-gas", ["out of gas", "outofgas", "gas uint64 overflow"]),
    ("invalid-opcode", ["invalid opcode", "bad instruction", "invalid instruction",
                        "opcode 0x", "badinstruction"]),
    ("stack-underflow", ["stack underflow", "stackunderflow"]),
    ("stack-overflow", ["stack overflow", "stack limit"]),
    ("write-protection", ["write protection", "static call", "staticcallviolation",
                          "state modification", "writeprotection"]),
    ("contract-collision", ["contract address collision", "collision"]),
    ("code-size", ["max code size", "code size limit", "initcode"]),
    ("insufficient-balance", ["insufficient balance", "insufficient funds"]),
    ("depth-limit", ["max call depth", "depth limit", "call depth"]),
    ("precompile-failure", ["precompile", "blob", "point evaluation"]),
]


def classify_error(msg):
    """Map a client error string to a canonical class ("other" if unknown)."""
    if not isinstance(msg, str) or not msg:
        return "empty"
    low = msg.lower()
    for cls, needles in ERROR_CLASSES:
        if any(n in low for n in needles):
            return cls
    return "other"


def normalize_hex_quantity(val):
    """Normalize a hex quantity to an int; returns (ok, normalized, style)."""
    if val is None:
        return True, None, "null"
    if isinstance(val, int):
        return True, val, "json_number"
    if isinstance(val, str):
        s = val[2:] if val.startswith("0x") else val
        try:
            n = int(s, 16) if s else 0
        except ValueError:
            return False, val, "unparseable"
        if not val.startswith("0x"):
            style = "no_prefix"
        elif s != s.lower():
            style = "uppercase"
        elif len(s) > 1 and s.startswith("0"):
            style = "zero_padded"
        else:
            style = "canonical"
        return True, n, style
    return False, val, type(val).__name__


def normalize_hex_bytes(val):
    """Normalize hex byte strings; returns (ok, normalized, style)."""
    if val is None:
        return True, None, "null"
    if isinstance(val, str):
        s = val[2:] if val.startswith("0x") else val
        style = "canonical" if val.startswith("0x") else "no_prefix"
        if s != s.lower():
            style = "uppercase"
        return True, s.lower(), style
    return False, val, type(val).__name__


def frame_signature(frame):
    """Stable signature used to re-align frames when counts differ."""
    if not isinstance(frame, dict):
        return ("<non-dict>",)
    inp = frame.get("input") or ""
    return (frame.get("type"), (frame.get("to") or "").lower(), inp[:10].lower())


def align_frames(lists_by_node):
    """
    Align frame lists across clients.

    Positional when all lengths agree; otherwise aligns by frame_signature
    against the longest list.

    Returns (slots, alignment_note) where slots is a list of
    {node: frame_or_None} and alignment_note is None or a dict.
    """
    lengths = {n: len(v) for n, v in lists_by_node.items()}
    if len(set(lengths.values())) == 1:
        count = next(iter(lengths.values()))
        return (
            [{n: v[i] for n, v in lists_by_node.items()} for i in range(count)],
            None,
        )

    ref_node = max(lengths, key=lambda n: lengths[n])
    ref = lists_by_node[ref_node]
    slots = []
    cursors = {n: 0 for n in lists_by_node}
    for ref_frame in ref:
        sig = frame_signature(ref_frame)
        slot = {}
        for node, frames in lists_by_node.items():
            i = cursors[node]
            # Frames never reorder across clients, so a short lookahead miss
            # means the node omitted this frame (e.g. skipped precompile).
            match = None
            for j in range(i, min(i + 3, len(frames))):
                if frame_signature(frames[j]) == sig:
                    match = j
                    break
            if match is not None:
                slot[node] = frames[match]
                cursors[node] = match + 1
            else:
                slot[node] = None
        slots.append(slot)
    note = {
        "type": "call_count_mismatch",
        "counts": lengths,
        "aligned_by": "signature",
    }
    return slots, note


def diff_scalar(path, key, values_by_node, differences, quirks):
    """Diff one scalar field across clients at a given frame path."""
    styles = {}
    normalized = {}
    presence = {}
    for node, (has_key, val) in values_by_node.items():
        if not has_key:
            presence[node] = "omitted"
            normalized[node] = None
            continue
        if val is None:
            presence[node] = "null"
            normalized[node] = None
            continue
        presence[node] = "present"
        if key in HEX_QUANTITY_FIELDS:
            ok, norm, style = normalize_hex_quantity(val)
        elif key in HEX_BYTES_FIELDS:
            ok, norm, style = normalize_hex_bytes(val)
        else:
            norm, style = val, "string"
        normalized[node] = norm
        styles[node] = style

    # Empty-equivalence rule: omitted == null == "" == empty 0x == zero value.
    def is_emptyish(node):
        if presence[node] != "present":
            return True
        return normalized[node] in (None, "", 0)

    if all(is_emptyish(n) for n in values_by_node):
        forms = {n: (presence[n] if presence[n] != "present"
                     else repr(values_by_node[n][1])) for n in values_by_node}
        if len(set(forms.values())) > 1:
            quirks["empty_encoding"][key].append({"path": path, "forms": forms})
        return

    # Omission rules are part of the callTracer format, so present-vs-missing
    # is semantic, not a quirk.
    missing = [n for n in values_by_node if presence[n] != "present"]
    if missing:
        differences.append({
            "type": "missing_field",
            "path": path,
            "key": key,
            "missing_in": missing,
            "values": {n: values_by_node[n][1] if presence[n] == "present" else presence[n]
                       for n in values_by_node},
        })
        return

    # Error wording varies per client; only class changes count as semantic.
    if key == "error":
        classes = {n: classify_error(normalized[n]) for n in normalized}
        if len(set(classes.values())) > 1:
            differences.append({
                "type": "error_class_mismatch",
                "path": path,
                "classes": classes,
                "values": {n: values_by_node[n][1] for n in values_by_node},
            })
        elif len(set(normalized.values())) > 1:
            quirks["error_wording"][next(iter(set(classes.values())))].append({
                "path": path,
                "values": {n: values_by_node[n][1] for n in values_by_node},
            })
        return

    norm_set = set()
    for v in normalized.values():
        norm_set.add(json.dumps(v, sort_keys=True) if isinstance(v, (list, dict)) else v)
    if len(norm_set) > 1:
        differences.append({
            "type": "value_mismatch",
            "path": path,
            "key": key,
            "values": {n: values_by_node[n][1] for n in values_by_node},
        })
    elif len(set(styles.values())) > 1:
        quirks["hex_format"][key].append({"path": path, "styles": dict(styles)})


def diff_logs(path, logs_by_node, differences, quirks):
    """Diff the logs array of one frame."""
    lengths = {n: len(v) for n, v in logs_by_node.items()}
    if len(set(lengths.values())) > 1:
        differences.append({
            "type": "log_count_mismatch",
            "path": path,
            "counts": lengths,
        })
        return
    count = next(iter(lengths.values()))
    for i in range(count):
        lpath = f"{path}.logs[{i}]" if path else f"logs[{i}]"
        entries = {n: v[i] for n, v in logs_by_node.items()}
        all_keys = set()
        for e in entries.values():
            if isinstance(e, dict):
                all_keys.update(e.keys())
        for key in sorted(all_keys):
            values = {}
            for node, e in entries.items():
                has = isinstance(e, dict) and key in e
                values[node] = (has, e.get(key) if has else None)
            if key == "topics":
                missing = [n for n, (has, _) in values.items() if not has]
                if missing:
                    differences.append({"type": "missing_field", "path": lpath,
                                        "key": key, "missing_in": missing})
                    continue
                norm = {n: json.dumps([t.lower() for t in v]) for n, (_, v) in values.items()}
                if len(set(norm.values())) > 1:
                    differences.append({"type": "value_mismatch", "path": lpath,
                                        "key": key,
                                        "values": {n: v for n, (_, v) in values.items()}})
            elif key in ("index", "position"):
                diff_scalar(lpath, key, values, differences, quirks)
            elif key in ("address", "data"):
                presence_missing = [n for n, (has, _) in values.items() if not has]
                if presence_missing:
                    differences.append({"type": "missing_field", "path": lpath,
                                        "key": key, "missing_in": presence_missing})
                    continue
                normalized = {}
                styles = {}
                for n, (_, v) in values.items():
                    ok, norm, style = normalize_hex_bytes(v)
                    normalized[n] = norm
                    styles[n] = style
                if len(set(normalized.values())) > 1:
                    differences.append({"type": "value_mismatch", "path": lpath,
                                        "key": key,
                                        "values": {n: v for n, (_, v) in values.items()}})
                elif len(set(styles.values())) > 1:
                    quirks["hex_format"][key].append({"path": lpath, "styles": styles})


def diff_frames(path, frames_by_node, differences, quirks):
    """Recursively diff one aligned call frame across clients."""
    live = {n: f for n, f in frames_by_node.items() if isinstance(f, dict)}
    absent = [n for n, f in frames_by_node.items() if f is None]
    if absent and live:
        sig = frame_signature(next(iter(live.values())))
        differences.append({
            "type": "missing_frame",
            "path": path,
            "missing_in": absent,
            "frame": {"type": sig[0], "to": sig[1], "selector": sig[2]},
        })
    if len(live) < 2:
        return

    all_keys = set()
    for f in live.values():
        all_keys.update(f.keys())

    unknown = all_keys - set(FRAME_SCALAR_FIELDS) - {"calls", "logs"}
    for key in sorted(unknown):
        havers = [n for n, f in live.items() if key in f]
        quirks["extra_fields"][key].append({"path": path, "clients": havers})

    for key in FRAME_SCALAR_FIELDS:
        if not any(key in f for f in live.values()):
            continue
        values = {n: (key in f, f.get(key)) for n, f in live.items()}
        diff_scalar(path, key, values, differences, quirks)

    logs_holders = {n: f["logs"] for n, f in live.items()
                    if isinstance(f.get("logs"), list)}
    non_holders = [n for n in live if n not in logs_holders]
    if logs_holders and non_holders:
        differences.append({
            "type": "missing_field",
            "path": path,
            "key": "logs",
            "missing_in": non_holders,
            "values": {n: f"{len(v)} logs" for n, v in logs_holders.items()},
        })
    elif len(logs_holders) >= 2:
        diff_logs(path, logs_holders, differences, quirks)

    calls_by_node = {n: f.get("calls") for n, f in live.items()}
    holders = {n: v for n, v in calls_by_node.items() if isinstance(v, list) and v}
    empties = {n: v for n, v in calls_by_node.items()
               if v is None or v == []}
    if holders and empties:
        explicit_empty = [n for n, v in empties.items() if v == []]
        if explicit_empty:
            quirks["empty_encoding"]["calls"].append({
                "path": path,
                "forms": {n: ("[]" if calls_by_node[n] == [] else
                              "omitted" if n in empties else f"{len(calls_by_node[n])} calls")
                          for n in live},
            })
        differences.append({
            "type": "call_count_mismatch",
            "path": path,
            "counts": {n: len(v) if isinstance(v, list) else 0
                       for n, v in calls_by_node.items()},
        })
    if len(holders) >= 2:
        slots, note = align_frames(holders)
        if note:
            note["path"] = path
            differences.append(note)
        for i, slot in enumerate(slots):
            child_path = f"{path}.calls[{i}]" if path else f"calls[{i}]"
            diff_frames(child_path, slot, differences, quirks)


def compare_call_traces(traces_by_node):
    """
    Compare callTracer outputs (one root frame per client).

    Returns the same envelope shape as the structlog compare_traces:
    {nodes_compared, errors, differences, format_quirks}.
    """
    comparison = {
        "nodes_compared": list(traces_by_node.keys()),
        "errors": {},
        "differences": [],
        "format_quirks": {},
    }
    quirks = {
        "empty_encoding": defaultdict(list),
        "hex_format": defaultdict(list),
        "error_wording": defaultdict(list),
        "extra_fields": defaultdict(list),
    }

    successful = {}
    for node, trace in traces_by_node.items():
        # A failed frame legitimately carries "error" alongside "type"; only a
        # bare {"error": ...} envelope means the RPC itself failed.
        if trace is None or (isinstance(trace, dict) and "error" in trace and "type" not in trace):
            comparison["errors"][node] = trace.get("error") if trace else "No trace data"
        else:
            successful[node] = trace

    if len(successful) < 2:
        comparison["differences"].append({
            "type": "insufficient_successful_traces",
            "successful_count": len(successful),
        })
        return comparison

    diff_frames("", successful, comparison["differences"], quirks)

    comparison["format_quirks"] = {k: dict(v) for k, v in quirks.items() if v}
    return comparison


def compare_block_traces(block_traces_by_node):
    """
    Compare debug_traceBlockByNumber callTracer outputs
    (arrays of {txHash, result|error} per client).

    Returns an envelope with per_tx mapping txHash → frame comparison.
    """
    comparison = {
        "nodes_compared": list(block_traces_by_node.keys()),
        "errors": {},
        "differences": [],
        "format_quirks": {},
        "per_tx": {},
    }

    successful = {}
    for node, res in block_traces_by_node.items():
        if isinstance(res, list):
            successful[node] = res
        else:
            err = res.get("error") if isinstance(res, dict) else "No trace data"
            comparison["errors"][node] = err

    if len(successful) < 2:
        comparison["differences"].append({
            "type": "insufficient_successful_traces",
            "successful_count": len(successful),
        })
        return comparison

    lengths = {n: len(v) for n, v in successful.items()}
    if len(set(lengths.values())) > 1:
        comparison["differences"].append({
            "type": "block_entry_count_mismatch",
            "counts": lengths,
        })

    entries_by_hash = defaultdict(dict)
    wrapper_issues = defaultdict(list)
    for node, entries in successful.items():
        for i, entry in enumerate(entries):
            if not isinstance(entry, dict) or "txHash" not in entry:
                wrapper_issues[node].append(i)
                continue
            entries_by_hash[entry["txHash"]][node] = (i, entry)
    for node, idxs in wrapper_issues.items():
        comparison["differences"].append({
            "type": "block_entry_missing_txhash",
            "client": node,
            "indices": idxs[:10],
        })

    for tx_hash, per_node in entries_by_hash.items():
        if len(per_node) < 2:
            missing = [n for n in successful if n not in per_node]
            comparison["differences"].append({
                "type": "block_entry_missing_tx",
                "txHash": tx_hash,
                "missing_in": missing,
            })
            continue
        positions = {n: i for n, (i, _) in per_node.items()}
        if len(set(positions.values())) > 1:
            comparison["differences"].append({
                "type": "block_entry_order_mismatch",
                "txHash": tx_hash,
                "positions": positions,
            })
        results = {}
        for node, (_, entry) in per_node.items():
            if "result" in entry:
                results[node] = entry["result"]
            else:
                results[node] = {"error": entry.get("error", "missing result")}
        comparison["per_tx"][tx_hash] = compare_call_traces(results)

    return comparison
