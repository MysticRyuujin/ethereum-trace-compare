# callTracer cross-client comparison (July 2026) — DRAFT

Comparison of `{"tracer":"callTracer"}` output across Ethereum execution clients
for `debug_traceTransaction`, `debug_traceBlockByNumber`, and `debug_traceCall`
(replaying transactions as calls), feeding the callTracer standardization effort
in [ethereum/execution-apis] (follow-up to the opcode-tracer spec, PR #762).

**Status: draft.** Live legs complete; reproducible local leg (deterministic
test chain incl. ethrex) pending.

## Methodology

- Tool: this repo's callTracer mode (`compare_traces.py --tracer calltracer` +
  `calltree_diff.py`), a recursive path-aware call-frame diff. Differences are
  split into **semantic** (values, tree shape, field presence) vs **wire-format
  quirks** (omitted-vs-null-vs-`"0x"`, hex casing/padding, error wording).
  Error strings are compared by canonical class (reverted, out-of-gas,
  write-protection, …), not exact text.
- Sources: raw client bytes over SSH direct to each node's HTTP RPC. An initial
  attempt through an eRPC proxy was discarded: eRPC caches `debug_trace*`
  responses in a cache shared across upstreams and re-serializes JSON — both
  fatal to a wire-format comparison. (Methodology note for anyone repeating
  the ethPandaOps-style setup.)
- Config matrix per tx: `{}`, `{onlyTopCall}`, `{withLog}`, `{onlyTopCall,withLog}`.
- Legs:
  - **sepolia, 5 clients** (geth 1.17.4, erigon 3.5.1, nethermind 1.39.0,
    besu 26.6.1, reth 2.3.0): 150 recent txs × 4 configs × (traceTransaction +
    traceCall replay) + block traces — 2,012 comparisons.
  - **mainnet, archive trio** (geth, erigon, reth): 200 txs, same matrix —
    5,540 comparisons.
  - ethrex v20.0.0 exposes **no `debug_trace*` methods at all** (tracing exists
    only in unreleased main); it is covered by the upcoming local leg.

## Headline findings

### 1. besu diverges structurally (7 distinct behaviors)

| behavior | evidence |
|---|---|
| `tracerConfig` entirely ignored: `onlyTopCall` still returns subcalls, `withLog` never emits `logs` | 2,192 missing-logs + 448 call-count diffs |
| **chained DELEGATECALL `from` mis-attribution**: in proxy→impl→lib delegatecall chains, besu reports the *code* address of the enclosing frame as `from`; all other clients report the *context* address | 1,594 diffs, e.g. sepolia tx `0x1d757fd9…`: `calls[0].calls[0].from` = `0x5c2493…` (besu) vs `0xd070f8…` (all others) |
| root `gasUsed` excludes intrinsic gas (execution-only); all others report receipt `gasUsed` | e.g. `0x69260` vs `0x6cfa0` |
| inner-frame `gas` values computed differently (consistently higher than the 63/64ths-forwarded value others report) | 1,012 diffs |
| `debug_traceCall` default gas when omitted: `0x1000000` vs `0x23c34600` (geth/erigon/reth/nethermind) | smoke test |
| empty `output` serialized as `"0x"` where others omit the key | 16 quirks |
| `debug_traceTransaction` on an out-of-range block returns bare `Internal error` (NullPointerException in `DebugTraceTransaction.response`, besu 26.6.1) instead of a state-unavailable error | mainnet full node, reproduced on any tx |

### 2. nethermind: frame-level tree divergences

- **Drops call frames**: a CALL following a STATICCALL to the same target
  disappears from the tree (sepolia tx `0x93251d13…`,
  `calls[2].calls[0].calls[0]`: geth/erigon/reth/besu show `[STATICCALL, CALL]`
  to `0xa18454…`; nethermind shows only the STATICCALL). 6 missing-frame + 12
  call-count diffs in 150 txs.
- Conversely inserts frames the geth-family doesn't have (6 diffs, same txs
  class — under investigation).
- `output` missing on some frames where all other clients have it (16 diffs);
  `gasUsed` mismatches on 36 frames.
- callLog objects lack the `index` field (has `address/topics/data/position`).

### 3. Log `index`/`position` semantics are incoherent across the geth family

On mainnet, geth/erigon/reth agreed on **every field of every frame across 200
txs except callLog `index` and `position`**:

- `debug_traceTransaction` + `withLog`: geth numbers `index` block-globally
  (receipt log index); erigon and reth number tx-locally from 0.
- Under `{onlyTopCall, withLog}`: reth's `position` values diverge (98 diffs)
  and `index` deviant-sets shift (geth+reth vs erigon, erigon+geth vs reth, …)
  — i.e. each client recomputes numbering differently when frames are
  suppressed or failed-frame logs are cleared.
- erigon has explicit "log index gap" renumbering machinery; geth reports the
  receipt value; reth recounts locally. Three implementations, three meanings.

**Spec consequence**: `logs[].index` cannot be standardized as currently
implemented; `position` needs an exact definition (index among the frame's
subcall boundaries) including its interaction with `onlyTopCall`.

### 4. reth: reverted frames keep their logs

With `withLog`, geth/erigon (and nethermind) clear logs from reverted frames —
those logs never reach the receipt. reth returns them (mainnet tx
`0x18ca2720…`: root frame has `error: "execution reverted"` yet carries a
log). Likely upstream in `revm-inspectors`.

### 5. `debug_traceCall` validation differs

Replaying txs as `debug_traceCall` at the parent block:

- erigon rejects calls whose fee cap is below the block base fee
  (`fee cap less than block base fee`); geth/erigon also reject on
  `insufficient funds` in some replays where reth executes them.
- besu's default gas (gas omitted) is 16.7M vs 600M elsewhere.
- ethrex doesn't implement the method; nor `debug_traceBlockByHash`.

### 6. What already agrees (the de-facto standard)

Everything else. Across 350 live txs: `type`/`from`/`to`/`value`/`gas`/
`gasUsed`/`input`/`output`/`error`/`revertReason` and tree shape are
byte-identical among geth, erigon, and reth, and field-omission rules
(omit `to` on failed CREATE, omit `value` for STATICCALL, `input` always
present, omit empty `output`/`calls`/`logs`) are shared by geth, erigon, reth,
and nethermind. Revert handling (`error: "execution reverted"` + raw revert
`output` + decoded `revertReason` when `Error(string)` decodes) is consistent
outside besu. This body of agreement is the natural baseline for the spec.

## Reproduction

```
ssh -f -N -L 18545:localhost:8545 <geth-node>   # etc.
python compare_traces.py --tracer calltracer \
  --methods tx,block,call-replay --configs default,onlyTopCall,withLog,onlyTopCallWithLog \
  --geth http://localhost:18545 --erigon http://localhost:18546 ... \
  --block <N> --max-txs 150 --max-gas 8000000 --output-dir traces-<net>
python aggregate_calltracer.py traces-<net>
```

Client versions are recorded in each run's `traces-*/run_meta.json`.

## Next

- Local leg: all 6 clients (incl. ethrex built from main) on the
  execution-apis deterministic test chain, now containing a `calltree`
  contract that exercises every frame type (nested CALL/rever/STATICCALL/
  DELEGATECALL/CALLCODE/precompile/CREATE/SELFDESTRUCT + logs) in one tx.
- Upstream issues: besu (delegatecall `from`, tracerConfig ignored, NPE),
  nethermind (dropped frames, missing output), reth/revm-inspectors
  (reverted-frame logs), cross-client (log index semantics).
- Spec PR: CallFrame/CallLog schema with the agreed baseline as MUSTs; log
  `index` left optional pending semantics definition.
