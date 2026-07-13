# callTracer cross-client comparison (July 2026) — DRAFT

Comparison of `{"tracer":"callTracer"}` output across Ethereum execution clients
for `debug_traceTransaction`, `debug_traceBlockByNumber`, and `debug_traceCall`
(replaying transactions as calls), feeding the callTracer standardization effort
in [ethereum/execution-apis] (follow-up to the opcode-tracer spec, PR #762).

**Status: draft.** Live legs and the reproducible local leg complete.

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
    only in unreleased main); it is covered by the local leg.
  - **local, all 6 clients** (same versions; ethrex v20.0.0-main): hive client
    images loaded with the execution-apis deterministic test chain, which now
    contains a `calltree` contract whose single invocation produces every
    frame type (nested CALL success/revert-with-reason, STATICCALL success/
    write-protection failure, DELEGATECALL with depth-2 log, CALLCODE,
    precompile call, CREATE + SELFDESTRUCT child, logs) — 1,060 comparisons
    over controlled scenarios (`local/docker-compose.yml`). The same fixtures
    also run in hive `rpc-compat`: geth green; erigon/nethermind/reth green on
    all callTracer content; besu fails exactly its known non-conformances.

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
| **`to` omitted on successful CREATE frames** — the created contract address, reported by all other clients, is missing | local leg, 30 diffs, `calls[7]` of every calltree tx |
| `debug_traceCall` rejects a block *hash* as the block parameter (`Invalid block param (block not found)`) | hive `calltracer-block-param-hash` |
| `debug_traceCall` replay of type-1 (access-list) transactions rejected: `Transaction type ACCESS_LIST is invalid` | local leg, 4 errors |

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

- Fee validation splits the clients: geth, erigon, and nethermind reject
  calls whose fee cap is below the block base fee (three different error
  strings for it); **reth and besu execute them** (local leg: 272 rejections
  each on geth/erigon/nethermind, zero on reth/besu). geth/erigon also
  reject on `insufficient funds` in some live replays where reth executes.
- besu's default gas (gas omitted) is 16.7M vs 600M elsewhere, and besu
  rejects block-hash block params and type-1 replays (see §1).
- ethrex doesn't implement the method; nor `debug_traceBlockByHash`.

### 5b. Error strings: one failure, four spellings

The same write-protection failure (SSTORE inside STATICCALL), from the
calltree scenario, local leg:

| client | `error` |
|---|---|
| geth, erigon | `out of gas: write protection` |
| nethermind | `write protection` |
| besu | `Illegal state change` |
| reth | `StateChangeDuringStaticCall` |

Only `execution reverted` is consistent across clients (besu included) —
supporting a spec that mandates that exact string for REVERT and leaves other
failure text free-form.

### 5c. ethrex (v20.0.0-main)

- Rejects the deterministic test chain at import: `Invalid Header, validation
  failed pre-execution: Base fee per gas is incorrect` — could not trace any
  on-chain tx in either the compose leg or hive (`Transaction not Found`).
- `debug_traceCall` and `debug_traceBlockByHash` unimplemented; releases
  through v20.0.0 have no `debug_trace*` at all.

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

Additional local-leg confirmations: DELEGATECALL frames carry the parent
context `value` (all clients, so `value` is only omitted for STATICCALL);
SELFDESTRUCT appears as a child frame with the beneficiary as `to` (all
clients); nethermind's missing callLog `index` reproduces deterministically.

## Next

- Upstream issues: besu (delegatecall `from`, CREATE `to`, tracerConfig
  ignored, gas accounting, NPE, block-hash param, type-1 traceCall),
  nethermind (dropped frames, missing output, missing log index),
  reth/revm-inspectors (reverted-frame logs, no fee validation in traceCall),
  ethrex (chain import base-fee rejection, missing methods),
  cross-client (log index semantics).
- Spec PR: CallFrame/CallLog schema with the agreed baseline as MUSTs; log
  `index` left optional pending semantics definition; exact
  `"execution reverted"` mandated, other error text free-form.
