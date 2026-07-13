# callTracer cross-client divergence summary

## Run metadata

- **geth**: `Geth/v1.17.4-stable-36a7dc72/linux-arm64/go1.26.4`
- **besu**: `besu/v26.6.1/linux-aarch_64/openjdk-java-25`
- **reth**: `reth/v2.3.0-9384bc5/aarch64-unknown-linux-gnu`
- **nethermind**: `Nethermind/v1.39.0+14aca2c5/linux-arm64/dotnet10.0.9`
- **erigon**: `erigon/3.5.1/linux-arm64/go1.25.12`
- **ethrex**: `ethrex/v20.0.0-main-cdbb77f9ab18a0badfa4a762b903bddbbcd63bd8/aarch64-unknown-linux-gnu/rustc-v1.91.1`
- methods: tx, block, call-replay; configs: default, onlyTopCall, withLog, onlyTopCallWithLog

## Overview

- comparisons analyzed: 1060
- fully identical: 244
- semantic behavior rows: 11
- wire-format quirk rows: 1

## Semantic divergences

| type | field | deviating clients | count | configs |
|---|---|---|---|---|
| missing_field | logs | besu | 216 | onlyTopCallWithLog×93, withLog×123 |
| value_mismatch | gasUsed | besu, nethermind | 32 | default×16, withLog×16 |
| value_mismatch | gas | besu | 30 | default×15, withLog×15 |
| missing_field | to | besu | 30 | default×15, withLog×15 |
| call_count_mismatch | — | besu | 30 | onlyTopCall×15, onlyTopCallWithLog×15 |
| error_class_mismatch | — | besu, nethermind, reth | 19 | default×11, withLog×8 |
| error_class_mismatch | — | erigon, geth, nethermind | 9 | default×3, withLog×6 |
| value_mismatch | gasUsed | nethermind | 8 | default×2, onlyTopCall×2, onlyTopCallWithLog×2, withLog×2 |
| value_mismatch | gasUsed | besu | 4 | default×1, onlyTopCall×1, onlyTopCallWithLog×1, withLog×1 |
| missing_field | index | nethermind | 2 | onlyTopCallWithLog×1, withLog×1 |
| error_class_mismatch | — | besu, nethermind | 2 | default×1, withLog×1 |

### Examples

**missing_field / logs / besu**
```json
{
 "ctx": "24/0x695ad02907c9e13ab7c69963f723fa46ac13cd5e2314f61eab2cb2f07b946faa/onlyTopCallWithLog",
 "path": "",
 "key": "logs",
 "missing_in": [
  "besu"
 ],
 "values": {
  "geth": "1 logs",
  "erigon": "1 logs",
  "reth": "1 logs",
  "nethermind": "1 logs"
 }
}
```
```json
{
 "ctx": "24/0x695ad02907c9e13ab7c69963f723fa46ac13cd5e2314f61eab2cb2f07b946faa/withLog",
 "path": "",
 "key": "logs",
 "missing_in": [
  "besu"
 ],
 "values": {
  "erigon": "1 logs",
  "nethermind": "1 logs",
  "geth": "1 logs",
  "reth": "1 logs"
 }
}
```
```json
{
 "ctx": "24/_block/onlyTopCallWithLog::0x695ad02907c9e13ab7c69963f723fa46ac13cd5e2314f61eab2cb2f07b946faa",
 "path": "",
 "key": "logs",
 "missing_in": [
  "besu"
 ],
 "values": {
  "erigon": "1 logs",
  "geth": "1 logs",
  "nethermind": "1 logs",
  "reth": "1 logs"
 }
}
```

**value_mismatch / gasUsed / besu, nethermind**
```json
{
 "ctx": "27/0xa3cec99b572cbb16af9a680a23b7925523b286df43c56548f52f3b1677c99189/default",
 "path": "calls[3]",
 "key": "gasUsed",
 "values": {
  "geth": "0xea60",
  "nethermind": "0x86c",
  "reth": "0xea60",
  "erigon": "0xea60",
  "besu": "0x86c"
 }
}
```
```json
{
 "ctx": "27/0xa3cec99b572cbb16af9a680a23b7925523b286df43c56548f52f3b1677c99189/default/call_replay",
 "path": "calls[2]",
 "key": "gasUsed",
 "values": {
  "geth": "0xea60",
  "erigon": "0xea60",
  "nethermind": "0x36",
  "besu": "0x36"
 }
}
```
```json
{
 "ctx": "27/0xa3cec99b572cbb16af9a680a23b7925523b286df43c56548f52f3b1677c99189/default/call_replay",
 "path": "calls[3]",
 "key": "gasUsed",
 "values": {
  "geth": "0xea60",
  "erigon": "0xea60",
  "nethermind": "0x86c",
  "besu": "0x86c"
 }
}
```

**value_mismatch / gas / besu**
```json
{
 "ctx": "27/0xa3cec99b572cbb16af9a680a23b7925523b286df43c56548f52f3b1677c99189/default",
 "path": "calls[6]",
 "key": "gas",
 "values": {
  "geth": "0xea60",
  "nethermind": "0xea60",
  "reth": "0xea60",
  "erigon": "0xea60",
  "besu": "0x71b6d"
 }
}
```
```json
{
 "ctx": "27/0xa3cec99b572cbb16af9a680a23b7925523b286df43c56548f52f3b1677c99189/default/call_replay",
 "path": "calls[6]",
 "key": "gas",
 "values": {
  "geth": "0xea60",
  "erigon": "0xea60",
  "nethermind": "0xea60",
  "besu": "0x63532"
 }
}
```
```json
{
 "ctx": "27/0xa3cec99b572cbb16af9a680a23b7925523b286df43c56548f52f3b1677c99189/withLog",
 "path": "calls[6]",
 "key": "gas",
 "values": {
  "erigon": "0xea60",
  "reth": "0xea60",
  "nethermind": "0xea60",
  "geth": "0xea60",
  "besu": "0x71b6d"
 }
}
```

**missing_field / to / besu**
```json
{
 "ctx": "27/0xa3cec99b572cbb16af9a680a23b7925523b286df43c56548f52f3b1677c99189/default",
 "path": "calls[7]",
 "key": "to",
 "missing_in": [
  "besu"
 ],
 "values": {
  "geth": "0x2d303c5b7911d87d594bf1b31fbb9aa187888893",
  "nethermind": "0x2d303c5b7911d87d594bf1b31fbb9aa187888893",
  "reth": "0x2d303c5b7911d87d594bf1b31fbb9aa187888893",
  "erigon": "0x2d303c5b7911d87d594bf1b31fbb9aa187888893",
  "besu": "omitted"
 }
}
```
```json
{
 "ctx": "27/0xa3cec99b572cbb16af9a680a23b7925523b286df43c56548f52f3b1677c99189/default/call_replay",
 "path": "calls[7]",
 "key": "to",
 "missing_in": [
  "besu"
 ],
 "values": {
  "geth": "0x2d303c5b7911d87d594bf1b31fbb9aa187888893",
  "erigon": "0x2d303c5b7911d87d594bf1b31fbb9aa187888893",
  "nethermind": "0x2d303c5b7911d87d594bf1b31fbb9aa187888893",
  "besu": "omitted"
 }
}
```
```json
{
 "ctx": "27/0xa3cec99b572cbb16af9a680a23b7925523b286df43c56548f52f3b1677c99189/withLog",
 "path": "calls[7]",
 "key": "to",
 "missing_in": [
  "besu"
 ],
 "values": {
  "erigon": "0x2d303c5b7911d87d594bf1b31fbb9aa187888893",
  "reth": "0x2d303c5b7911d87d594bf1b31fbb9aa187888893",
  "nethermind": "0x2d303c5b7911d87d594bf1b31fbb9aa187888893",
  "geth": "0x2d303c5b7911d87d594bf1b31fbb9aa187888893",
  "besu": "omitted"
 }
}
```

**call_count_mismatch / — / besu**
```json
{
 "ctx": "27/0xa3cec99b572cbb16af9a680a23b7925523b286df43c56548f52f3b1677c99189/onlyTopCall",
 "path": "",
 "counts": {
  "geth": 0,
  "erigon": 0,
  "reth": 0,
  "nethermind": 0,
  "besu": 8
 }
}
```
```json
{
 "ctx": "27/0xa3cec99b572cbb16af9a680a23b7925523b286df43c56548f52f3b1677c99189/onlyTopCall/call_replay",
 "path": "",
 "counts": {
  "erigon": 0,
  "geth": 0,
  "nethermind": 0,
  "besu": 8
 }
}
```
```json
{
 "ctx": "27/0xa3cec99b572cbb16af9a680a23b7925523b286df43c56548f52f3b1677c99189/onlyTopCallWithLog",
 "path": "",
 "counts": {
  "geth": 0,
  "nethermind": 0,
  "erigon": 0,
  "reth": 0,
  "besu": 8
 }
}
```

**error_class_mismatch / — / besu, nethermind, reth**
```json
{
 "ctx": "27/0xa3cec99b572cbb16af9a680a23b7925523b286df43c56548f52f3b1677c99189/default",
 "path": "calls[3]",
 "classes": {
  "geth": "out-of-gas",
  "nethermind": "write-protection",
  "reth": "other",
  "erigon": "out-of-gas",
  "besu": "other"
 },
 "values": {
  "geth": "out of gas: write protection",
  "nethermind": "write protection",
  "reth": "StateChangeDuringStaticCall",
  "erigon": "out of gas: write protection",
  "besu": "Illegal state change"
 }
}
```
```json
{
 "ctx": "27/0xa3cec99b572cbb16af9a680a23b7925523b286df43c56548f52f3b1677c99189/withLog",
 "path": "calls[3]",
 "classes": {
  "erigon": "out-of-gas",
  "reth": "other",
  "nethermind": "write-protection",
  "geth": "out-of-gas",
  "besu": "other"
 },
 "values": {
  "erigon": "out of gas: write protection",
  "reth": "StateChangeDuringStaticCall",
  "nethermind": "write protection",
  "geth": "out of gas: write protection",
  "besu": "Illegal state change"
 }
}
```
```json
{
 "ctx": "27/_block/default::0xa3cec99b572cbb16af9a680a23b7925523b286df43c56548f52f3b1677c99189",
 "path": "calls[3]",
 "classes": {
  "geth": "out-of-gas",
  "reth": "other",
  "nethermind": "write-protection",
  "erigon": "out-of-gas",
  "besu": "other"
 },
 "values": {
  "geth": "out of gas: write protection",
  "reth": "StateChangeDuringStaticCall",
  "nethermind": "write protection",
  "erigon": "out of gas: write protection",
  "besu": "Illegal state change"
 }
}
```

**error_class_mismatch / — / erigon, geth, nethermind**
```json
{
 "ctx": "27/_block/withLog::0xa3cec99b572cbb16af9a680a23b7925523b286df43c56548f52f3b1677c99189",
 "path": "calls[3]",
 "classes": {
  "reth": "other",
  "erigon": "out-of-gas",
  "nethermind": "write-protection",
  "geth": "out-of-gas",
  "besu": "other"
 },
 "values": {
  "reth": "StateChangeDuringStaticCall",
  "erigon": "out of gas: write protection",
  "nethermind": "write protection",
  "geth": "out of gas: write protection",
  "besu": "Illegal state change"
 }
}
```
```json
{
 "ctx": "29/0x498dc0af7cacc5e16478aacd1885419b8457ac78092cb596ceeea91d0afe6664/withLog",
 "path": "calls[3]",
 "classes": {
  "reth": "other",
  "geth": "out-of-gas",
  "erigon": "out-of-gas",
  "nethermind": "write-protection",
  "besu": "other"
 },
 "values": {
  "reth": "StateChangeDuringStaticCall",
  "geth": "out of gas: write protection",
  "erigon": "out of gas: write protection",
  "nethermind": "write protection",
  "besu": "Illegal state change"
 }
}
```
```json
{
 "ctx": "29/_block/default::0x498dc0af7cacc5e16478aacd1885419b8457ac78092cb596ceeea91d0afe6664",
 "path": "calls[3]",
 "classes": {
  "reth": "other",
  "nethermind": "write-protection",
  "erigon": "out-of-gas",
  "geth": "out-of-gas",
  "besu": "other"
 },
 "values": {
  "reth": "StateChangeDuringStaticCall",
  "nethermind": "write protection",
  "erigon": "out of gas: write protection",
  "geth": "out of gas: write protection",
  "besu": "Illegal state change"
 }
}
```

**value_mismatch / gasUsed / nethermind**
```json
{
 "ctx": "24/0x695ad02907c9e13ab7c69963f723fa46ac13cd5e2314f61eab2cb2f07b946faa/default/call_replay",
 "path": "",
 "key": "gasUsed",
 "values": {
  "nethermind": "0xbd54",
  "geth": "0xd58c",
  "erigon": "0xd58c"
 }
}
```
```json
{
 "ctx": "24/0x695ad02907c9e13ab7c69963f723fa46ac13cd5e2314f61eab2cb2f07b946faa/onlyTopCall/call_replay",
 "path": "",
 "key": "gasUsed",
 "values": {
  "geth": "0xd58c",
  "nethermind": "0xbd54",
  "erigon": "0xd58c"
 }
}
```
```json
{
 "ctx": "24/0x695ad02907c9e13ab7c69963f723fa46ac13cd5e2314f61eab2cb2f07b946faa/onlyTopCallWithLog/call_replay",
 "path": "",
 "key": "gasUsed",
 "values": {
  "nethermind": "0xbd54",
  "geth": "0xd58c",
  "erigon": "0xd58c"
 }
}
```

**value_mismatch / gasUsed / besu**
```json
{
 "ctx": "43/0x53d4ac6a75b3d0465179287f91ba22f35564aee6dd4cf03112b0772e37bc994d/default",
 "path": "",
 "key": "gasUsed",
 "values": {
  "geth": "0xca9c",
  "reth": "0xca9c",
  "erigon": "0xca9c",
  "nethermind": "0xca9c",
  "besu": "0xbfac"
 }
}
```
```json
{
 "ctx": "43/0x53d4ac6a75b3d0465179287f91ba22f35564aee6dd4cf03112b0772e37bc994d/onlyTopCall",
 "path": "",
 "key": "gasUsed",
 "values": {
  "geth": "0xca9c",
  "erigon": "0xca9c",
  "reth": "0xca9c",
  "nethermind": "0xca9c",
  "besu": "0xbfac"
 }
}
```
```json
{
 "ctx": "43/0x53d4ac6a75b3d0465179287f91ba22f35564aee6dd4cf03112b0772e37bc994d/onlyTopCallWithLog",
 "path": "",
 "key": "gasUsed",
 "values": {
  "erigon": "0xca9c",
  "geth": "0xca9c",
  "reth": "0xca9c",
  "nethermind": "0xca9c",
  "besu": "0xbfac"
 }
}
```

**missing_field / index / nethermind**
```json
{
 "ctx": "24/0x695ad02907c9e13ab7c69963f723fa46ac13cd5e2314f61eab2cb2f07b946faa/onlyTopCallWithLog/call_replay",
 "path": "logs[0]",
 "key": "index",
 "missing_in": [
  "nethermind"
 ],
 "values": {
  "nethermind": "omitted",
  "geth": "0x0",
  "erigon": "0x0"
 }
}
```
```json
{
 "ctx": "24/0x695ad02907c9e13ab7c69963f723fa46ac13cd5e2314f61eab2cb2f07b946faa/withLog/call_replay",
 "path": "logs[0]",
 "key": "index",
 "missing_in": [
  "nethermind"
 ],
 "values": {
  "geth": "0x0",
  "erigon": "0x0",
  "nethermind": "omitted"
 }
}
```

**error_class_mismatch / — / besu, nethermind**
```json
{
 "ctx": "27/0xa3cec99b572cbb16af9a680a23b7925523b286df43c56548f52f3b1677c99189/default/call_replay",
 "path": "calls[3]",
 "classes": {
  "geth": "out-of-gas",
  "erigon": "out-of-gas",
  "nethermind": "write-protection",
  "besu": "other"
 },
 "values": {
  "geth": "out of gas: write protection",
  "erigon": "out of gas: write protection",
  "nethermind": "write protection",
  "besu": "Illegal state change"
 }
}
```
```json
{
 "ctx": "27/0xa3cec99b572cbb16af9a680a23b7925523b286df43c56548f52f3b1677c99189/withLog/call_replay",
 "path": "calls[3]",
 "classes": {
  "geth": "out-of-gas",
  "erigon": "out-of-gas",
  "nethermind": "write-protection",
  "besu": "other"
 },
 "values": {
  "geth": "out of gas: write protection",
  "erigon": "out of gas: write protection",
  "nethermind": "write protection",
  "besu": "Illegal state change"
 }
}
```

## Wire-format quirks

| kind | field | count | client forms |
|---|---|---|---|
| error_wording | invalid-opcode | 2 |  |

## RPC errors during collection

- **besu**:
  - ×4: `RPC error: {'code': -32603, 'message': 'Internal error', 'data': 'Transaction type ACCESS_LIST is invalid, accepted tran`
- **erigon**:
  - ×272: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0x7435ed30A8b4AEb0877C`
- **ethrex**:
  - ×320: `RPC error: {'code': -32603, 'message': 'Internal Error: Transaction not Found'}`
  - ×320: `RPC error: {'code': -32601, 'message': 'Method not found: debug_traceCall'}`
  - ×88: `RPC error: {'code': -32603, 'message': 'Internal Error: Block not Found'}`
- **geth**:
  - ×272: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0x7435ed30A8b4`
- **nethermind**:
  - ×272: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0x7435ed30A8b4AEb0877CEf0c6E8c`
- **reth**:
  - ×112: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee'}`
  - ×20: `RPC error: {'code': -32003, 'message': 'transaction type not supported'}`
