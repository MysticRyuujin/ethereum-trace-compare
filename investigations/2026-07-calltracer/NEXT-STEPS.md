# callTracer standardization — runbook

Self-contained tracker. A cold start needs only this file, the report
(README.md beside it), and the two local branches below. Everything is
verified green as of 2026-07-14.

## What exists

| Artifact | Where | State |
|---|---|---|
| Spec + tooling + testgen + fixtures | `~/github/execution-apis` branch **`calltracer-spec`** (9 commits, `63d31f1..ee0617c`, unpushed) | verified: `make build/lint/test/fill` green, spellcheck green, two negative tests prove enforcement, hive matrix run |
| Test-chain calltree scenarios | `~/github/hive` branch **`hivechain-calltree`** (1 commit `c0192532`, unpushed; stacked on #1567's commit) | verified: chain regenerates, calltree tx traced in geth (all 8 frame types), `go test ./cmd/hivechain` green |
| Comparison tool + divergence report | this repo, pushed (`compare_traces.py --tracer calltracer`, `calltree_diff.py`, `aggregate_calltracer.py`, README.md report, per-leg summaries) | complete: sepolia 5-client, mainnet trio, local 6-client legs (~8,600 comparisons) |
| geth change (traceCall optional Block) | not written | small; description ready (§PR-C) |
| rpcwright skill | `~/github/rpcwright` `references/tracers.md` (pushed, synced to `~/.claude/skills`) | captures the recipes + gotchas from this effort |

Both branches were code-reviewed (8-angle + verification); every finding is
either fixed on the branch or recorded below as a PR open question. Nothing
is deferred without a home.

## Runbook (in order, with gates)

- [ ] **Gate 0 — land the osaka/bpo pair**: hive
      [#1567](https://github.com/ethereum/hive/pull/1567) + execution-apis
      [#846](https://github.com/ethereum/execution-apis/pull/846) (both open,
      both ours, both good as-is — reviewed; do not add Osaka feature tests,
      see Decisions).
- [ ] **1. Open hive PR-A** (after #1567 merges): `hivechain-calltree`
      rebases as a no-op (already stacked). Before pushing, clean the hive
      working tree: `git -C ~/github/hive checkout simulators/ethereum/rpc-compat/`
      and remove the staged `tests/`+`openrpc.json` there (local verification
      artifacts only).
- [ ] **2. Rebase + open execution-apis PR-B as DRAFT** (after #846 and PR-A
      merge). Rebase recipe — resolution is regeneration, never manual merge:
      1. `git rebase main calltracer-spec` keeping the 7 code commits; drop
         `6c4691c`, `12115a6`, and every `tests/` fixture hunk.
      2. Apply the queued calltree.eas edits (one recompile — see below),
         PR them to hive first if PR-A already merged, or fold into PR-A if not.
      3. Rebuild hivechain from hive master (now osaka+calltree), run the
         osaka `mkchain.sh` (`-lastfork bpo2 -length 54 -disable-txmods
         tx-largereceipt` — the flag takes a list; calltree mods unaffected).
      4. One `make fill` && `make test`; testgen finds txs via `txinfo.json`
         so the chain bump cannot shadow them.
- [ ] **3. File client issues** (parallel with PR-B discussion; table below).
- [ ] **4. geth PR-C** — only after PR-B open question 5 gets a nod; then
      bump `tools/go.mod` in execution-apis and add the omitted-Block fixture
      to PR-B.
- [ ] **5. hive rpc-compat parity PR**: port speccheck's tracer-aware branch
      selection (`tools/cmd/speccheck/tracer.go`) to the simulator's
      `schema.go` speconly path. Land before PR-B undrafts.
- [ ] **6. Undraft PR-B** when the criteria at the bottom hold.
- [ ] **7. Post-merge**: client teams implement; conformance tracked via
      hive rpc-compat.

**Queued calltree.eas bytecode edits** (batched so `calltree.bin` recompiles
exactly once, in step 2.2): §5 pin the DELEGATECALL calldata with an explicit
`mstore` (today it reads §2's residual memory — hidden ordering dependency);
§7 identity-precompile retOff/retSize `0x140/4` → `0/0` (nothing reads it);
optionally `return(0x100, 2)` for exact callme output.

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
> Predeploy addresses (`0x9dcd…27d0–d3`) are hardcoded in `calltree.eas`,
> mirrored in `genesis.go`, and guarded by a test asserting the constants
> appear in the compiled bytecode. The callees are predeployed (rather than
> reusing the deploy-* mods' instances) because deployment addresses depend
> on modifier scheduling and cannot be baked into committed bytecode.

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
> <report link>. Every MUST is annotated below with who already conforms.
>
> ### What's specified
> - **`CallFrame`** (new `src/schemas/call-tracer.yaml`): required
>   `type/from/gas/gasUsed/input`; presence/omission rules for
>   `to/value/output/error/revertReason/calls/logs` stated per field. Absent
>   fields MUST be omitted, never null. `to` present except failed CREATE;
>   `value` present (incl. zero) except STATICCALL — DELEGATECALL carries the
>   parent context value, which all clients already do; precompile calls are
>   frames; root `gas` = tx gas limit and root `gasUsed` = receipt gasUsed;
>   `error` MUST be exactly `"execution reverted"` for REVERT and is
>   free-form otherwise (the same write-protection failure currently has four
>   spellings across five clients); `revertReason` = decoded `Error(string)`
>   when decodable.
> - **`CallLog`**: `address/topics/data/position` required; `position` =
>   number of subcalls of the containing frame at emission. **`index` is
>   optional and its semantics deliberately undefined** — implementations
>   disagree (geth: block-global; erigon/reth: tx-local; nethermind: absent;
>   all shift under `onlyTopCall`). See open question 1.
> - **`CallTracerConfig`**: `onlyTopCall`, `withLog` MUST be honored, and are
>   schema-bound to `tracerConfig` via a conditional (wrong-typed values fail
>   validation); client extensions (e.g. Erigon's `includePrecompiles`) stay
>   permitted, so unknown keys are not rejected.
> - **Block entries** (`CallTracerBlockEntry`, and the opcode/named entries
>   for parity): `{txHash, result}` or `{txHash, error}` — the error
>   alternative matches geth's behavior when a single tx fails to trace and
>   only widens acceptance.
> - **`debug_traceCall`** (new method): params `GenericTransaction`,
>   `BlockNumberOrTagOrHash` (optional, default `latest` — open question 5),
>   `TraceCallConfig` (= TraceConfig + `stateOverrides`/`blockOverrides`,
>   reusing the eth_simulateV1 schemas). A reverted call is NOT a JSON-RPC
>   error.
>
> ### Tooling changes (required for the spec to be enforceable)
> - **specgen**: absolute-URI `$ref`s pass through dereferencing so the
>   recursive `CallFrame` schema (self-reference via an embedded `$id`)
>   survives into `openrpc.json`; refs that match no embedded `$id` fail the
>   build, as fragment typos always did. The `$id` URI is an identifier, not
>   a fetchable location (stated in the schema; see design note below).
> - **speccheck**: result validation selects the `anyOf` branch matching the
>   tracer the fixture requested, and errors if a known tracer has no branch.
>   Without this, the unconstrained named-tracer branch makes ALL
>   trace-result validation vacuous — including, previously, the opcode
>   branch of `debug_traceTransaction`. Verified with corrupted-fixture
>   negative tests.
>
> ### Fixtures
> 19 new callTracer/traceCall cases; the test chain gained nested-call
> scenarios (hive PR: <link PR-A>), hence the broad fixture churn.
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
> 1. **`logs[].index` semantics** — tx-local? block-global? drop? Currently
>    optional + undefined; geth is the minority among emitters.
> 2. **Reverted-frame log clearing** — spec'd MUST (receipt consistency);
>    reth returns them and "debug tracers show what executed" is coherent.
>    Input from reth/revm-inspectors wanted.
> 3. **Root gas semantics** — spec'd receipt-`gasUsed` (externally checkable,
>    4-of-5 clients); besu's execution-only value is a coherent alternative.
>    Input from besu wanted.
> 4. **Fee/balance validation in `debug_traceCall`** — geth/erigon/nethermind
>    reject fee-cap-below-base-fee calls, reth/besu execute them. Spec defers
>    to eth_call semantics.
> 5. **Block param optionality** — spec'd optional (default `latest`, #812
>    lineage); requires a small geth change (<link PR-C>).
> 6. Side-note: the reused `AccountOverride` schema requires `state`/`stateDiff`
>    so a code-only override does not validate although geth accepts it —
>    pre-existing strictness worth a separate fix.
>
> ### Design note (decided): recursive schema is not published
> Publishing a document at the `$id` URL would create a versioned release
> artifact to maintain forever. Consumers must resolve the self-reference
> in-document per JSON Schema `$id` semantics; naive HTTP-dereferencing tools
> will not resolve it.

## PR-C: go-ethereum — `eth/tracers: make debug_traceCall block parameter optional`

Not yet implemented; open after PR-B open question 5 gets a nod:

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
| besu | tracerConfig ignored; delegatecall `from`; CREATE `to`; NPE → "Internal error" on unavailable state; block-hash param; type-1 traceCall | yes — NPE + `to` are small; tracerConfig/gas is a larger `CallTracerResultConverter` refactor |
| nethermind | dropped CALL frame after STATICCALL to same target; missing `output` on some frames | yes (repro-first from report txs) |
| reth → revm-inspectors | reverted-frame logs not cleared (pending open question 2) | yes, small |
| ethrex | hive-chain import rejected ("Base fee per gas is incorrect"); null serialization; callTracer-as-default; missing `debug_traceCall`/`traceBlockByHash`; no `eth_call` state-override support | issues only (fast-moving codebase) |
| hive | port speccheck branch selection to rpc-compat `schema.go` | yes, small |

## Decisions log

- **Trace comparisons must bypass eRPC** (shared `debug_trace*` cache +
  JSON re-serialization fake agreement) — SSH direct to nodes.
- **`logs[].index` unblessed** (geth is the 1-of-3 minority; semantics shift
  under onlyTopCall) — optional + undefined pending discussion.
- **Only `"execution reverted"` is a mandated error string** (unanimous
  today); all other failure text free-form.
- **Recursion `$id` not published** (versioning burden); documented in-schema
  instead. specgen rejects refs matching no embedded `$id`.
- **Opcode + named block entries got the `{txHash, error}` alternative**
  (matches geth; acceptance-widening only).
- **`tracerConfig` schema-bound via if/then**; unknown keys stay legal
  (Erigon extensions), so typo'd key *names* are not caught — known limit.
- **No Osaka feature tests** (2026-07-14 probe of production nodes with geth
  testdata vectors): CLZ semantics + trace naming, P256VERIFY, ModExp bounds,
  EIP-7825 cap are behaviorally unanimous across all six clients. The only
  divergences are rejection *error codes* (7825: -32000/-32005/-32003;
  precompile failure: -32000/-32003/`3`) — recorded in the error-code
  standardization effort (#784 / geth #35105), not here.

## Undraft criteria for PR-B

1. Open questions 1–5 have recorded resolutions; MUST/SHOULD language updated.
2. PR-A merged; chain regeneration reproducible from upstream hivechain.
3. If Q5 = optional: PR-C merged, go.mod bumped, omitted-Block fixture added.
4. `make build && make lint && make test` green; corrupted-fixture negative
   test still fails speccheck.
5. Fresh six-client hive rpc-compat run posted to the PR thread, failures
   annotated as client-change rows matching the conformance table.

## Housekeeping

- mainnet-01 geth was ~15.5k blocks behind on 2026-07-13 (infra, unrelated).
- The local 6-client compose stack from the comparison may still be running
  (`local/docker-compose.yml`, ports 38545–38550; ethrex at block 0 — import
  rejected). `docker compose -f local/docker-compose.yml down` when done.
