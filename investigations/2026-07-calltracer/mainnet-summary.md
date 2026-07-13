# callTracer cross-client divergence summary

## Run metadata

- **geth**: `Geth/v1.17.4-stable-36a7dc72/linux-amd64/go1.26.4`
- **reth**: `reth/v2.3.0-9384bc5/x86_64-unknown-linux-gnu`
- **erigon**: `erigon/3.5.1/linux-amd64/go1.25.12`
- methods: tx, block, call-replay; configs: default, onlyTopCall, withLog, onlyTopCallWithLog

## Overview

- comparisons analyzed: 5540
- fully identical: 5110
- semantic behavior rows: 7
- wire-format quirk rows: 0

## Semantic divergences

| type | field | deviating clients | count | configs |
|---|---|---|---|---|
| value_mismatch | index | geth | 2332 | onlyTopCallWithLog×326, withLog×2006 |
| value_mismatch | position | reth | 98 | onlyTopCallWithLog×98 |
| value_mismatch | index | geth, reth | 67 | onlyTopCallWithLog×56, withLog×11 |
| value_mismatch | index | erigon, geth | 42 | withLog×42 |
| value_mismatch | index | reth | 39 | withLog×39 |
| value_mismatch | index | erigon, reth | 31 | withLog×31 |
| value_mismatch | index | erigon | 15 | onlyTopCallWithLog×15 |

### Examples

**value_mismatch / index / geth**
```json
{
 "ctx": "25510400/0x03125969d12ba3f07038489d5615f323afbef4c9f765946824e87439b9a479d0/withLog",
 "path": "calls[0].logs[0]",
 "key": "index",
 "values": {
  "erigon": "0x1",
  "geth": "0x2ce",
  "reth": "0x1"
 }
}
```
```json
{
 "ctx": "25510400/0x03125969d12ba3f07038489d5615f323afbef4c9f765946824e87439b9a479d0/withLog",
 "path": "calls[0].calls[0].logs[0]",
 "key": "index",
 "values": {
  "erigon": "0x0",
  "geth": "0x2cd",
  "reth": "0x0"
 }
}
```
```json
{
 "ctx": "25510400/0x094b5f681d0da50fadd21eea4d8c6e7c8d540e85d22b859385242ae8b8440cb8/withLog",
 "path": "calls[0].logs[0]",
 "key": "index",
 "values": {
  "erigon": "0x0",
  "geth": "0x4c",
  "reth": "0x0"
 }
}
```

**value_mismatch / position / reth**
```json
{
 "ctx": "25510400/0x0cb3af1636973d15f2dcfac688fa9b145825ffd98dbfe1265395f20b7702e2e7/onlyTopCallWithLog",
 "path": "logs[0]",
 "key": "position",
 "values": {
  "erigon": "0x0",
  "geth": "0x0",
  "reth": "0x1"
 }
}
```
```json
{
 "ctx": "25510400/0x0cb3af1636973d15f2dcfac688fa9b145825ffd98dbfe1265395f20b7702e2e7/onlyTopCallWithLog/call_replay",
 "path": "logs[0]",
 "key": "position",
 "values": {
  "erigon": "0x0",
  "geth": "0x0",
  "reth": "0x1"
 }
}
```
```json
{
 "ctx": "25510400/0x3216e099c57d221d0d9e0c20614cd45c33dce433de513b57ccc3a43fa56c8de2/onlyTopCallWithLog",
 "path": "logs[1]",
 "key": "position",
 "values": {
  "erigon": "0x0",
  "geth": "0x0",
  "reth": "0x1"
 }
}
```

**value_mismatch / index / geth, reth**
```json
{
 "ctx": "25510400/0x3216e099c57d221d0d9e0c20614cd45c33dce433de513b57ccc3a43fa56c8de2/onlyTopCallWithLog",
 "path": "logs[1]",
 "key": "index",
 "values": {
  "erigon": "0x1",
  "geth": "0x39e",
  "reth": "0x2"
 }
}
```
```json
{
 "ctx": "25510400/0x3216e099c57d221d0d9e0c20614cd45c33dce433de513b57ccc3a43fa56c8de2/onlyTopCallWithLog",
 "path": "logs[2]",
 "key": "index",
 "values": {
  "erigon": "0x2",
  "geth": "0x3a3",
  "reth": "0x7"
 }
}
```
```json
{
 "ctx": "25510400/0x398192d307733592272401e58af5e70f7e5fab015ea95f6f03bcfbf1d1cda6a6/onlyTopCallWithLog",
 "path": "logs[0]",
 "key": "index",
 "values": {
  "erigon": "0x0",
  "geth": "0xc1",
  "reth": "0x4"
 }
}
```

**value_mismatch / index / erigon, geth**
```json
{
 "ctx": "25510400/_block/withLog::0xc3fbf4599ac6fc887f49450acbc2e772b9972981cd9eba6e390d4e89ee5f2752",
 "path": "logs[0]",
 "key": "index",
 "values": {
  "reth": "0x3",
  "geth": "0xd4",
  "erigon": "0x0"
 }
}
```
```json
{
 "ctx": "25510400/_block/withLog::0xc3fbf4599ac6fc887f49450acbc2e772b9972981cd9eba6e390d4e89ee5f2752",
 "path": "logs[1]",
 "key": "index",
 "values": {
  "reth": "0x7",
  "geth": "0xd5",
  "erigon": "0x1"
 }
}
```
```json
{
 "ctx": "25510400/_block/withLog::0x9ed99be8c0707efe04d3c3fa3918113607439d3add846ce609875ca30645a8ca",
 "path": "logs[2]",
 "key": "index",
 "values": {
  "reth": "0x19",
  "geth": "0xe6",
  "erigon": "0xe"
 }
}
```

**value_mismatch / index / reth**
```json
{
 "ctx": "25510400/0x9ed99be8c0707efe04d3c3fa3918113607439d3add846ce609875ca30645a8ca/withLog/call_replay",
 "path": "logs[2]",
 "key": "index",
 "values": {
  "geth": "0xe",
  "reth": "0x19",
  "erigon": "0xe"
 }
}
```
```json
{
 "ctx": "25510400/0x9ed99be8c0707efe04d3c3fa3918113607439d3add846ce609875ca30645a8ca/withLog/call_replay",
 "path": "logs[3]",
 "key": "index",
 "values": {
  "geth": "0xf",
  "reth": "0x1a",
  "erigon": "0xf"
 }
}
```
```json
{
 "ctx": "25510400/0x9ed99be8c0707efe04d3c3fa3918113607439d3add846ce609875ca30645a8ca/withLog/call_replay",
 "path": "calls[4].logs[0]",
 "key": "index",
 "values": {
  "geth": "0xb",
  "reth": "0x16",
  "erigon": "0xb"
 }
}
```

**value_mismatch / index / erigon, reth**
```json
{
 "ctx": "25510400/0x9ed99be8c0707efe04d3c3fa3918113607439d3add846ce609875ca30645a8ca/withLog",
 "path": "logs[2]",
 "key": "index",
 "values": {
  "geth": "0xe6",
  "erigon": "0xe",
  "reth": "0x19"
 }
}
```
```json
{
 "ctx": "25510400/0x9ed99be8c0707efe04d3c3fa3918113607439d3add846ce609875ca30645a8ca/withLog",
 "path": "logs[3]",
 "key": "index",
 "values": {
  "geth": "0xe7",
  "erigon": "0xf",
  "reth": "0x1a"
 }
}
```
```json
{
 "ctx": "25510400/0x9ed99be8c0707efe04d3c3fa3918113607439d3add846ce609875ca30645a8ca/withLog",
 "path": "calls[4].logs[0]",
 "key": "index",
 "values": {
  "geth": "0xe3",
  "erigon": "0xb",
  "reth": "0x16"
 }
}
```

**value_mismatch / index / erigon**
```json
{
 "ctx": "25510400/0x3216e099c57d221d0d9e0c20614cd45c33dce433de513b57ccc3a43fa56c8de2/onlyTopCallWithLog/call_replay",
 "path": "logs[1]",
 "key": "index",
 "values": {
  "erigon": "0x1",
  "geth": "0x2",
  "reth": "0x2"
 }
}
```
```json
{
 "ctx": "25510400/0x3216e099c57d221d0d9e0c20614cd45c33dce433de513b57ccc3a43fa56c8de2/onlyTopCallWithLog/call_replay",
 "path": "logs[2]",
 "key": "index",
 "values": {
  "erigon": "0x2",
  "geth": "0x7",
  "reth": "0x7"
 }
}
```
```json
{
 "ctx": "25510400/0x398192d307733592272401e58af5e70f7e5fab015ea95f6f03bcfbf1d1cda6a6/onlyTopCallWithLog/call_replay",
 "path": "logs[0]",
 "key": "index",
 "values": {
  "geth": "0x4",
  "erigon": "0x0",
  "reth": "0x4"
 }
}
```

## RPC errors during collection

- **erigon**:
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: insufficient funds for gas * price + value: address 0x5e0F1349BA`
- **geth**:
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: insufficient funds for gas * price + value: address 0x5e0F1349BA`
