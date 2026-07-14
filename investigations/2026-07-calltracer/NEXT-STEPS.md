# callTracer standardization — next steps and PR sequencing

Working tracker for landing the callTracer spec. Artifacts that exist today:

| Artifact | Where | State |
|---|---|---|
| Spec + tooling + testgen + fixtures | `execution-apis` branch `calltracer-spec` (4 commits: `63d31f1`, `6c4691c`, `6b2478b`, `9390cde`) | complete, verified locally (`make build/lint/test`, negative test, hive matrix) |
| Test-chain scenarios | `hive` branch `hivechain-calltree` (1 commit: `525a08e4`) | complete, verified (chain regenerated, traced in geth) |
| Comparison tool + divergence report | this repo (`master`, pushed) | complete (draft report, 3 legs) |
| geth change (traceCall optional Block) | not yet written | description drafted below (§PR-C) |

## Order of operations

```
0. hive #1567 + execution-apis #846      ── already open (osaka/bpo chain bump);
   land these first — see interaction note below
1. hive PR (hivechain calltree)          ── stacked on #1567; open next
2. execution-apis DRAFT PR               ── rebased onto #846 (fixtures regenerated on
                                            the osaka chain); references 1 + report
3. client-repo issues                    ── parallel with discussion (besu, nethermind,
                                            reth/revm-inspectors, ethrex)
4. geth PR (optional Block param)        ── once discussion confirms the optional-Block
   └─ then: execution-apis go.mod bump      question; unblocks the omitted-Block fixture
      + omitted-Block fixture commit
5. hive rpc-compat branch-selection PR   ── before spec merge (speconly enforcement parity)
6. resolve open questions → final MUST/SHOULD pass → regenerate fixtures →
   flip settled SpecOnly tests to exact-match → undraft → merge
7. post-merge: client teams implement; conformance tracked via hive rpc-compat
```

**Interaction with the in-flight osaka/bpo chain bump** (hive
[#1567](https://github.com/ethereum/hive/pull/1567) + execution-apis
[#846](https://github.com/ethereum/execution-apis/pull/846), both open): land
those FIRST.

- hive side: no conflict — `hivechain-calltree` is stacked directly on
  #1567's commit; the only shared file (`genesis.go`) is touched in disjoint
  regions, and #846's `-disable-txmods tx-largereceipt` doesn't affect the
  calltree mods (the flag takes an explicit list).
- execution-apis side: #846 and `calltracer-spec` both regenerate
  `tests/chain.rlp` + every fixture, so the whole fixture tree conflicts
  textually. Resolution is regeneration, not merging: after #1567 + the
  calltree hive PR + #846 land, rebase `calltracer-spec` keeping only the
  code commits (drop `6c4691c` and all fixture hunks), rebuild hivechain from
  hive master, run the osaka `mkchain.sh` (bpo2, length 54), and one
  `make fill` regenerates everything — the callTracer fixtures then exercise
  the osaka-era chain from day one. The testgen cases look transactions up
  via `txinfo.json` entries, so the chain bump can't shadow them.

**Queued for the rebase regeneration** (bytecode edits from the pre-PR code
review, batched so calltree.bin recompiles exactly once alongside the chain
regen):

- calltree.eas §5: pin the DELEGATECALL calldata with an explicit `mstore`
  (today it reads residual memory from §2 — hidden ordering dependency).
- calltree.eas §7: identity-precompile retOff/retSize `0x140/4` → `0/0`
  (nothing reads the copy).
- calltree.eas return: `return(0x100, 2)` for exact callme output instead of
  zero-padding to 32 (optional; comment already corrected).

Already applied in the amended commit (`hivechain-calltree` @ c0192532):
trimmed header/doc/commit verbosity, predeploy rationale recorded in
genesis.go, unread `Contract` field dropped from txinfo (both repos), and
mod_calltree_test.go guarding the genesis↔bytecode address coupling.

Why this order:

- **hive first** because the execution-apis branch's regenerated `tools/chain`
  was produced by the patched hivechain; the spec PR should reference a real
  hive PR (ideally merged) so chain regeneration is reproducible from public
  code, not a local checkout. The hive PR is pure test infrastructure with no
  dependency on the spec discussion, so nothing blocks it.
- **The spec PR opens as a draft** with the open questions explicitly listed —
  the point is to force the per-client discussion (as with the opcode-tracer
  PR) rather than to merge quickly. The comparison report is the evidence base
  and is linked from the description.
- **The geth PR waits for a discussion signal** on the optional-Block question
  only because it's pointless churn if reviewers prefer `required: true`; the
  code is a small, mechanical change (same shape as the block-default-to-latest
  campaign) and the description is ready (§PR-C). It gates exactly one fixture
  (omitted-Block), nothing else.
- **Fixture finalization is last** because three open questions can change
  MUST/SHOULD language and therefore fixture content; regenerating once after
  consensus avoids fixture churn during review.

## PR-A: hive — `cmd/hivechain: add calltree contract and tx mods for callTracer testing`

Branch `hivechain-calltree`. Suggested description:

> ### What
> Adds a `calltree` contract (geas) plus fixed-address predeploys of the
> existing `callme`/`callenv`/`callrevert` contracts, and two block modifiers:
>
> - `tx-calltree` — one invocation produces every callTracer frame type:
>   nested CALL (success with value / inner `Error(string)` revert),
>   STATICCALL (success / write-protection failure), DELEGATECALL emitting a
>   depth-2 log, CALLCODE, a precompile call, CREATE of a child that logs and
>   self-destructs, and a top-level LOG1.
> - `tx-callrevert` — a whole-transaction revert with a decodable revert
>   reason (`"user error"`).
>
> ### Why
> The execution-apis test chain currently contains no CALL-family opcodes,
> inner reverts, CREATE-opcode frames, or SELFDESTRUCTs, so `debug_trace*`
> fixtures cannot exercise nested call trees. This unblocks the callTracer
> standardization spec (execution-apis PR to follow; cross-client divergence
> report: <report link>).
>
> Predeploy addresses (`0x9dcd…27d0–d3`) are hardcoded in `calltree.eas` and
> mirrored in `genesis.go`. The calltree account carries a small balance so it
> can attach value to subcalls.

## PR-B: execution-apis — `Standardize callTracer output and add debug_traceCall` (DRAFT)

Branch `calltracer-spec`. Suggested description:

> ### Summary
> Specifies the output format of the `callTracer` named tracer for
> `debug_traceTransaction`, `debug_traceBlockByNumber`, `debug_traceBlockByHash`,
> and a newly-specified `debug_traceCall`, following the pattern of the opcode
> (struct) tracer standardization (#762). Other named tracers
> (`prestateTracer`, `flatCallTracer`, …) remain out of scope and keep the
> unconstrained escape-hatch branch.
>
> Evidence base: a cross-client comparison of ~8,600 trace comparisons across
> geth 1.17.4, erigon 3.5.1, nethermind 1.39.0, besu 26.6.1, reth 2.3.0, and
> ethrex v20-main, over mainnet, sepolia, and a deterministic local chain:
> <report link>. Every MUST in this spec is annotated below with who already
> conforms.
>
> ### What's specified
> - **`CallFrame`** (new `src/schemas/call-tracer.yaml`): required
>   `type/from/gas/gasUsed/input`; optional-with-omission-rules
>   `to/value/output/error/revertReason/calls/logs`. Absent fields MUST be
>   omitted, never null. `to` omitted on failed CREATE; `value` omitted for
>   STATICCALL (DELEGATECALL carries the parent context value — all clients
>   already do this); precompile calls are frames; root `gas` = tx gas limit
>   and root `gasUsed` = receipt gasUsed; `error` MUST be exactly
>   `"execution reverted"` for REVERT and is free-form otherwise (the same
>   write-protection failure currently has four spellings across five
>   clients); `revertReason` = decoded `Error(string)` when decodable.
> - **`CallLog`**: `address/topics/data/position` required; `position` =
>   number of subcalls of the containing frame at emission. **`index` is
>   optional and its semantics deliberately undefined** — current
>   implementations disagree (geth: block-global; erigon/reth: tx-local;
>   nethermind: absent; all three shift under `onlyTopCall`). See open
>   question 1.
> - **`CallTracerConfig`**: `onlyTopCall`, `withLog` MUST be honored;
>   client-specific extensions (e.g. Erigon's `includePrecompiles`) are
>   permitted.
> - **`debug_traceCall`** (new method): params `GenericTransaction`,
>   `BlockNumberOrTagOrHash` (optional, default `latest` — see open question
>   5), `TraceCallConfig` (= TraceConfig + `stateOverrides`/`blockOverrides`,
>   reusing the eth_simulateV1 schemas). A reverted call is NOT a JSON-RPC
>   error.
>
> ### Tooling changes (required for the spec to be enforceable)
> - **specgen**: absolute-URI `$ref`s now pass through dereferencing, so the
>   recursive `CallFrame` schema (self-reference via an embedded `$id`)
>   survives into `openrpc.json`. `#/components` fragment typos still fail the
>   build.
> - **speccheck**: result validation now selects the `anyOf` branch matching
>   the tracer requested by the fixture. Without this, the unconstrained
>   named-tracer branch makes ALL trace-result validation vacuous — including,
>   previously, the opcode branch of `debug_traceTransaction`. Verified with a
>   corrupted-nested-frame negative test.
>
> ### Fixtures
> 19 new callTracer/traceCall test cases; the test chain was regenerated with
> nested-call scenarios (hive PR: <link PR-A>), hence the broad fixture churn.
> Exact-match is used only for consensus-derivable output; wording- and
> `index`-sensitive cases are schema-validated (`speconly`) until the open
> questions settle.
>
> ### Current conformance (hive rpc-compat, all six clients)
> | Client | callTracer result | Changes needed |
> |---|---|---|
> | go-ethereum | green | `debug_traceCall` optional Block param (PR: <link PR-C>) |
> | erigon | green | none |
> | nethermind | green | none for conformance (two implementation bugs reported separately: dropped CALL frame after a STATICCALL to the same target; missing `output` on some frames) |
> | reth | green except reverted-frame logs | clear logs on reverted frames (revm-inspectors) — open question 2 |
> | besu | multiple failures | honor `onlyTopCall`/`withLog` + emit `logs`; context (not code) address as `from` in chained delegatecalls; report the created address as `to` on successful CREATE; root `gasUsed` = receipt value; accept block-hash Block param and type-1 transactions in `debug_traceCall`; error (not NPE) on unavailable state |
> | ethrex | not yet implementable | omit absent fields (no `null`s); default tracer must be the opcode logger, not callTracer; implement `debug_traceCall` and `debug_traceBlockByHash`; (separately: rejects the test chain at import — "Base fee per gas is incorrect") |
>
> ### Open questions for discussion
> 1. **`logs[].index` semantics** — define tx-local? block-global? or drop the
>    field? Currently optional + undefined. geth is the minority among
>    emitters (block-global vs erigon/reth tx-local).
> 2. **Reverted-frame log clearing** — spec'd as MUST (receipt consistency:
>    reverted logs never materialize); reth currently returns them, and
>    "debug tracers should show what execution did" is a coherent
>    counter-position. Input from reth/revm-inspectors wanted.
> 3. **Root gas semantics** — spec'd as receipt-`gasUsed` (externally
>    checkable; 4-of-5 clients); besu reports execution-only gas, which is a
>    coherent alternative. Input from besu wanted.
> 4. **Fee/balance validation in `debug_traceCall`** — geth/erigon/nethermind
>    reject fee-cap-below-base-fee calls, reth/besu execute them. Spec
>    currently defers to eth_call semantics.
> 5. **`debug_traceCall` Block param optionality** — spec'd optional
>    (default `latest`, consistent with #812); requires a small geth change.
> 6. Side-note: the reused `AccountOverride` schema requires `state` or
>    `stateDiff`, so a code-only override does not validate although geth
>    accepts it — pre-existing strictness worth a separate fix.
> 7. **Recursive-schema resolution (decided: not published)** — the built
>    `openrpc.json` expresses CallFrame recursion via an embedded `$id` and
>    absolute-URI self-`$ref`. The `$id` URI is an identifier, not a network
>    location (stated in the CallFrame description): publishing a document at
>    that URL would create a versioned release artifact to maintain forever.
>    Consumers must resolve the self-reference in-document per JSON Schema
>    `$id` semantics; naive HTTP-dereferencing tools will not resolve it.
>
> Resolved during pre-PR review (included in the branch): opcode and generic
> named-tracer block entries accept an `error` alternative (matches geth;
> widens acceptance only, no new client failures); `tracerConfig` is bound to
> CallTracerConfig via an if/then conditional (wrong-typed option values now
> fail validation; unknown keys remain allowed by design, since clients MAY
> accept extension options). Still deferred: a specgen guard rejecting
> absolute `$ref`s that match no embedded `$id`.

## PR-C: go-ethereum — `eth/tracers: make debug_traceCall block parameter optional`

Not yet implemented; open after open-question 5 gets a nod. Suggested description:

> `debug_traceCall` currently requires the block number/hash parameter
> (`TraceCall(args TransactionArgs, blockNrOrHash rpc.BlockNumberOrHash, …)`
> uses a value type, so omitting it yields "missing value for required
> argument 1"). The pending execution-apis callTracer spec (<link PR-B>)
> specifies the parameter as optional, defaulting to `"latest"`, consistent
> with the state-method defaults (execution-apis #814 / #812 lineage).
>
> Changes the argument to `*rpc.BlockNumberOrHash` and defaults to latest when
> nil, with a regression test through the RPC server exercising the omitted
> parameter. No behavior change when the parameter is supplied.

After merge: bump the geth pin in execution-apis `tools/go.mod`, add the
omitted-Block testgen case + fixture to PR-B.

## Client-repo issues (file during discussion; we offer patches)

| Repo | Issue(s) | Willing to PR? |
|---|---|---|
| besu | tracerConfig ignored; delegatecall `from`; CREATE `to`; NPE → "Internal error" on unavailable state; block-hash param; type-1 traceCall | yes, NPE + `to` are small; tracerConfig/gas is a larger refactor of `CallTracerResultConverter` |
| nethermind | dropped CALL frame after STATICCALL to same target; missing `output` on some frames | yes (needs repro-first minimization from report txs) |
| reth → revm-inspectors | reverted-frame logs not cleared (pending open question 2) | yes, small |
| ethrex | chain-import base-fee rejection (hive chain); null serialization; callTracer-as-default; missing debug methods | issues only (fast-moving codebase) |
| hive | port speccheck's tracer-aware branch selection to rpc-compat `schema.go` (speconly path) | yes, small (PR alongside spec merge) |

## Merge criteria for PR-B (undraft when…)

1. Open questions 1–5 each have a recorded resolution (rough consensus on the
   PR or RPC-standards call), with MUST/SHOULD language updated to match.
2. hive PR-A merged; chain regeneration reproducible from upstream hivechain.
3. If Q5 = optional: PR-C merged, go.mod bumped, omitted-Block fixture added.
4. `make build && make lint && make test` green; corrupted-fixture negative
   test still fails speccheck (enforcement is real).
5. hive rpc-compat re-run across all six clients attached to the PR thread —
   failures annotated as "client change required" rows, matching the
   conformance table.
