# callTracer cross-client divergence summary

## Run metadata

- **geth**: `Geth/v1.17.4-stable-36a7dc72/linux-amd64/go1.26.4`
- **besu**: `besu/v26.6.1/linux-x86_64/openjdk-java-25`
- **reth**: `reth/v2.3.0-9384bc5/x86_64-unknown-linux-gnu`
- **nethermind**: `Nethermind/v1.39.0+14aca2c5/linux-x64/dotnet10.0.9`
- **erigon**: `erigon/3.5.1/linux-amd64/go1.25.12`
- methods: tx, block, call-replay; configs: default, onlyTopCall, withLog, onlyTopCallWithLog

## Overview

- comparisons analyzed: 2012
- fully identical: 945
- semantic behavior rows: 16
- wire-format quirk rows: 2

## Semantic divergences

| type | field | deviating clients | count | configs |
|---|---|---|---|---|
| missing_field | logs | besu | 2192 | onlyTopCallWithLog×199, withLog×1993 |
| value_mismatch | from | besu | 1594 | default×797, withLog×797 |
| value_mismatch | gas | besu | 1012 | default×506, withLog×506 |
| value_mismatch | gasUsed | besu | 498 | default×227, onlyTopCall×22, onlyTopCallWithLog×22, withLog×227 |
| call_count_mismatch | — | besu | 448 | onlyTopCall×224, onlyTopCallWithLog×224 |
| value_mismatch | gasUsed | nethermind | 36 | default×18, withLog×18 |
| value_mismatch | value | besu | 34 | default×17, withLog×17 |
| missing_field | output | nethermind | 16 | default×8, withLog×8 |
| call_count_mismatch | — | nethermind | 12 | default×6, withLog×6 |
| missing_field | error | besu, erigon, geth, reth | 12 | default×6, withLog×6 |
| missing_frame | — | nethermind | 6 | default×3, withLog×3 |
| missing_frame | — | besu, erigon, geth, reth | 6 | default×3, withLog×3 |
| value_mismatch | output | nethermind | 4 | default×2, withLog×2 |
| missing_field | revertReason | besu | 4 | default×1, onlyTopCall×1, onlyTopCallWithLog×1, withLog×1 |
| missing_field | logs | besu, nethermind | 3 | withLog×3 |
| value_mismatch | output | besu, nethermind | 2 | default×1, withLog×1 |

### Examples

**missing_field / logs / besu**
```json
{
 "ctx": "11266068/0x0633bd7b686249ec401571a3dda6d3be8ac80e6cf0235ce05d8c759c4aed7be7/onlyTopCallWithLog",
 "path": "",
 "key": "logs",
 "missing_in": [
  "besu"
 ],
 "values": {
  "erigon": "1 logs",
  "geth": "1 logs",
  "reth": "1 logs",
  "nethermind": "1 logs"
 }
}
```
```json
{
 "ctx": "11266068/0x0633bd7b686249ec401571a3dda6d3be8ac80e6cf0235ce05d8c759c4aed7be7/onlyTopCallWithLog/call_replay",
 "path": "",
 "key": "logs",
 "missing_in": [
  "besu"
 ],
 "values": {
  "nethermind": "1 logs",
  "reth": "1 logs",
  "erigon": "1 logs",
  "geth": "1 logs"
 }
}
```
```json
{
 "ctx": "11266068/0x0633bd7b686249ec401571a3dda6d3be8ac80e6cf0235ce05d8c759c4aed7be7/withLog",
 "path": "",
 "key": "logs",
 "missing_in": [
  "besu"
 ],
 "values": {
  "erigon": "1 logs",
  "geth": "1 logs",
  "reth": "1 logs",
  "nethermind": "1 logs"
 }
}
```

**value_mismatch / from / besu**
```json
{
 "ctx": "11266068/0x1d757fd936f3a6cdfb3b8db62a336f17c836d0eb4f9553304c161b2e5bc19adc/default",
 "path": "calls[0].calls[0]",
 "key": "from",
 "values": {
  "erigon": "0xd070f8790a69872a360a53c52af4ee2d797bd987",
  "geth": "0xd070f8790a69872a360a53c52af4ee2d797bd987",
  "nethermind": "0xd070f8790a69872a360a53c52af4ee2d797bd987",
  "besu": "0x5c24937e3007723a8b3a2814c312bbf133f59ef3",
  "reth": "0xd070f8790a69872a360a53c52af4ee2d797bd987"
 }
}
```
```json
{
 "ctx": "11266068/0x1d757fd936f3a6cdfb3b8db62a336f17c836d0eb4f9553304c161b2e5bc19adc/default/call_replay",
 "path": "calls[0].calls[0]",
 "key": "from",
 "values": {
  "geth": "0xd070f8790a69872a360a53c52af4ee2d797bd987",
  "nethermind": "0xd070f8790a69872a360a53c52af4ee2d797bd987",
  "reth": "0xd070f8790a69872a360a53c52af4ee2d797bd987",
  "besu": "0x5c24937e3007723a8b3a2814c312bbf133f59ef3",
  "erigon": "0xd070f8790a69872a360a53c52af4ee2d797bd987"
 }
}
```
```json
{
 "ctx": "11266068/0x1d757fd936f3a6cdfb3b8db62a336f17c836d0eb4f9553304c161b2e5bc19adc/withLog",
 "path": "calls[0].calls[0]",
 "key": "from",
 "values": {
  "erigon": "0xd070f8790a69872a360a53c52af4ee2d797bd987",
  "geth": "0xd070f8790a69872a360a53c52af4ee2d797bd987",
  "nethermind": "0xd070f8790a69872a360a53c52af4ee2d797bd987",
  "besu": "0x5c24937e3007723a8b3a2814c312bbf133f59ef3",
  "reth": "0xd070f8790a69872a360a53c52af4ee2d797bd987"
 }
}
```

**value_mismatch / gas / besu**
```json
{
 "ctx": "11266068/0x1dede6ea015dcf350273168603a712514f848b84c7c394c7101a631b8769394a/default",
 "path": "calls[3].calls[2]",
 "key": "gas",
 "values": {
  "geth": "0xa307d",
  "reth": "0xa307d",
  "nethermind": "0xa307d",
  "besu": "0xa50ca",
  "erigon": "0xa307d"
 }
}
```
```json
{
 "ctx": "11266068/0x1dede6ea015dcf350273168603a712514f848b84c7c394c7101a631b8769394a/default",
 "path": "calls[3].calls[3]",
 "key": "gas",
 "values": {
  "geth": "0x9b29d",
  "reth": "0x9b29d",
  "nethermind": "0x9b29d",
  "besu": "0x9d2ea",
  "erigon": "0x9b29d"
 }
}
```
```json
{
 "ctx": "11266068/0x1dede6ea015dcf350273168603a712514f848b84c7c394c7101a631b8769394a/default",
 "path": "calls[3].calls[3].calls[0]",
 "key": "gas",
 "values": {
  "geth": "0x9753b",
  "reth": "0x9753b",
  "nethermind": "0x9753b",
  "besu": "0x99507",
  "erigon": "0x9753b"
 }
}
```

**value_mismatch / gasUsed / besu**
```json
{
 "ctx": "11266068/0x1dede6ea015dcf350273168603a712514f848b84c7c394c7101a631b8769394a/default",
 "path": "",
 "key": "gasUsed",
 "values": {
  "geth": "0x69a30",
  "reth": "0x69a30",
  "nethermind": "0x69a30",
  "besu": "0x61fb0",
  "erigon": "0x69a30"
 }
}
```
```json
{
 "ctx": "11266068/0x1dede6ea015dcf350273168603a712514f848b84c7c394c7101a631b8769394a/default",
 "path": "calls[3]",
 "key": "gasUsed",
 "values": {
  "geth": "0x3ac17",
  "reth": "0x3ac17",
  "nethermind": "0x3ac17",
  "besu": "0x35f87",
  "erigon": "0x3ac17"
 }
}
```
```json
{
 "ctx": "11266068/0x1dede6ea015dcf350273168603a712514f848b84c7c394c7101a631b8769394a/default",
 "path": "calls[3].calls[1]",
 "key": "gasUsed",
 "values": {
  "geth": "0x22f6",
  "reth": "0x22f6",
  "nethermind": "0x22f6",
  "besu": "0x1806",
  "erigon": "0x22f6"
 }
}
```

**call_count_mismatch / — / besu**
```json
{
 "ctx": "11266068/0x0633bd7b686249ec401571a3dda6d3be8ac80e6cf0235ce05d8c759c4aed7be7/onlyTopCall",
 "path": "",
 "counts": {
  "erigon": 0,
  "geth": 0,
  "reth": 0,
  "besu": 1,
  "nethermind": 0
 }
}
```
```json
{
 "ctx": "11266068/0x0633bd7b686249ec401571a3dda6d3be8ac80e6cf0235ce05d8c759c4aed7be7/onlyTopCall/call_replay",
 "path": "",
 "counts": {
  "nethermind": 0,
  "geth": 0,
  "erigon": 0,
  "besu": 1,
  "reth": 0
 }
}
```
```json
{
 "ctx": "11266068/0x0633bd7b686249ec401571a3dda6d3be8ac80e6cf0235ce05d8c759c4aed7be7/onlyTopCallWithLog",
 "path": "",
 "counts": {
  "erigon": 0,
  "geth": 0,
  "besu": 1,
  "reth": 0,
  "nethermind": 0
 }
}
```

**value_mismatch / gasUsed / nethermind**
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/default",
 "path": "calls[2]",
 "key": "gasUsed",
 "values": {
  "erigon": "0x1a791",
  "geth": "0x1a791",
  "nethermind": "0x7033e",
  "reth": "0x1a791",
  "besu": "0x1a791"
 }
}
```
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/default",
 "path": "calls[2].calls[0]",
 "key": "gasUsed",
 "values": {
  "erigon": "0x18ef4",
  "geth": "0x18ef4",
  "nethermind": "0x212ad",
  "reth": "0x18ef4",
  "besu": "0x18ef4"
 }
}
```
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/default",
 "path": "calls[2].calls[0].calls[0]",
 "key": "gasUsed",
 "values": {
  "erigon": "0x18d7f",
  "geth": "0x18d7f",
  "nethermind": "0x20794",
  "reth": "0x18d7f",
  "besu": "0x18d7f"
 }
}
```

**value_mismatch / value / besu**
```json
{
 "ctx": "11266068/0x1ed614f6e629de27e8834b9ac0c89919eacc28e0feeaa45e1e5e64c9ba935b02/default",
 "path": "calls[0]",
 "key": "value",
 "values": {
  "erigon": "0xa306e49374000",
  "geth": "0xa306e49374000",
  "nethermind": "0xa306e49374000",
  "besu": "0x0",
  "reth": "0xa306e49374000"
 }
}
```
```json
{
 "ctx": "11266068/0x1ed614f6e629de27e8834b9ac0c89919eacc28e0feeaa45e1e5e64c9ba935b02/default/call_replay",
 "path": "calls[0]",
 "key": "value",
 "values": {
  "nethermind": "0xa306e49374000",
  "geth": "0xa306e49374000",
  "erigon": "0xa306e49374000",
  "reth": "0xa306e49374000",
  "besu": "0x0"
 }
}
```
```json
{
 "ctx": "11266068/0x1ed614f6e629de27e8834b9ac0c89919eacc28e0feeaa45e1e5e64c9ba935b02/withLog",
 "path": "calls[0]",
 "key": "value",
 "values": {
  "erigon": "0xa306e49374000",
  "geth": "0xa306e49374000",
  "nethermind": "0xa306e49374000",
  "besu": "0x0",
  "reth": "0xa306e49374000"
 }
}
```

**missing_field / output / nethermind**
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/default",
 "path": "calls[2].calls[0]",
 "key": "output",
 "missing_in": [
  "nethermind"
 ],
 "values": {
  "erigon": "0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000",
  "geth": "0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000",
  "nethermind": "omitted",
  "reth": "0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000",
  "besu": "0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000"
 }
```
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/default",
 "path": "calls[2].calls[0].calls[0]",
 "key": "output",
 "missing_in": [
  "nethermind"
 ],
 "values": {
  "erigon": "0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000",
  "geth": "0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000",
  "nethermind": "omitted",
  "reth": "0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000",
  "besu": "0x000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000
```
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/default/call_replay",
 "path": "calls[2].calls[0]",
 "key": "output",
 "missing_in": [
  "nethermind"
 ],
 "values": {
  "geth": "0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000",
  "erigon": "0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000",
  "nethermind": "omitted",
  "reth": "0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000",
  "besu": "0x000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000
```

**call_count_mismatch / — / nethermind**
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/default",
 "counts": {
  "erigon": 1,
  "geth": 1,
  "nethermind": 2,
  "reth": 1,
  "besu": 1
 },
 "aligned_by": "signature",
 "path": "calls[2]"
}
```
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/default",
 "counts": {
  "erigon": 2,
  "geth": 2,
  "nethermind": 1,
  "reth": 2,
  "besu": 2
 },
 "aligned_by": "signature",
 "path": "calls[2].calls[0].calls[0]"
}
```
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/default/call_replay",
 "counts": {
  "geth": 1,
  "erigon": 1,
  "nethermind": 2,
  "reth": 1,
  "besu": 1
 },
 "aligned_by": "signature",
 "path": "calls[2]"
}
```

**missing_field / error / besu, erigon, geth, reth**
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/default",
 "path": "calls[2].calls[0]",
 "key": "error",
 "missing_in": [
  "erigon",
  "geth",
  "reth",
  "besu"
 ],
 "values": {
  "erigon": "omitted",
  "geth": "omitted",
  "nethermind": "execution reverted",
  "reth": "omitted",
  "besu": "omitted"
 }
}
```
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/default",
 "path": "calls[2].calls[0].calls[0]",
 "key": "error",
 "missing_in": [
  "erigon",
  "geth",
  "reth",
  "besu"
 ],
 "values": {
  "erigon": "omitted",
  "geth": "omitted",
  "nethermind": "execution reverted",
  "reth": "omitted",
  "besu": "omitted"
 }
}
```
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/default/call_replay",
 "path": "calls[2].calls[0]",
 "key": "error",
 "missing_in": [
  "geth",
  "erigon",
  "reth",
  "besu"
 ],
 "values": {
  "geth": "omitted",
  "erigon": "omitted",
  "nethermind": "execution reverted",
  "reth": "omitted",
  "besu": "omitted"
 }
}
```

**missing_frame / — / nethermind**
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/default",
 "path": "calls[2].calls[0].calls[0].calls[1]",
 "missing_in": [
  "nethermind"
 ],
 "frame": {
  "type": "CALL",
  "to": "0xa1845480ff0dcf275ec18e215e2efa4895a8b709",
  "selector": "0x9dd52469"
 }
}
```
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/default/call_replay",
 "path": "calls[2].calls[0].calls[0].calls[1]",
 "missing_in": [
  "nethermind"
 ],
 "frame": {
  "type": "CALL",
  "to": "0xa1845480ff0dcf275ec18e215e2efa4895a8b709",
  "selector": "0x9dd52469"
 }
}
```
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/withLog",
 "path": "calls[2].calls[0].calls[0].calls[1]",
 "missing_in": [
  "nethermind"
 ],
 "frame": {
  "type": "CALL",
  "to": "0xa1845480ff0dcf275ec18e215e2efa4895a8b709",
  "selector": "0x9dd52469"
 }
}
```

**missing_frame / — / besu, erigon, geth, reth**
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/default",
 "path": "calls[2].calls[1]",
 "missing_in": [
  "erigon",
  "geth",
  "reth",
  "besu"
 ],
 "frame": {
  "type": "CALL",
  "to": "0xa1845480ff0dcf275ec18e215e2efa4895a8b709",
  "selector": "0x9dd52469"
 }
}
```
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/default/call_replay",
 "path": "calls[2].calls[1]",
 "missing_in": [
  "geth",
  "erigon",
  "reth",
  "besu"
 ],
 "frame": {
  "type": "CALL",
  "to": "0xa1845480ff0dcf275ec18e215e2efa4895a8b709",
  "selector": "0x9dd52469"
 }
}
```
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/withLog",
 "path": "calls[2].calls[1]",
 "missing_in": [
  "erigon",
  "geth",
  "reth",
  "besu"
 ],
 "frame": {
  "type": "CALL",
  "to": "0xa1845480ff0dcf275ec18e215e2efa4895a8b709",
  "selector": "0x9dd52469"
 }
}
```

**value_mismatch / output / nethermind**
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/default",
 "path": "calls[2]",
 "key": "output",
 "values": {
  "erigon": "0x0000000000000000000000000000000000000000000000000002cad6daaa6496",
  "geth": "0x0000000000000000000000000000000000000000000000000002cad6daaa6496",
  "nethermind": "0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000",
  "reth": "0x0000000000000000000000000000000000000000000000000002cad6daaa6496",
  "besu": "0x0000000000000000000000000000000000000000000000000002cad6daaa6496"
 }
}
```
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/withLog",
 "path": "calls[2]",
 "key": "output",
 "values": {
  "erigon": "0x0000000000000000000000000000000000000000000000000002cad6daaa6496",
  "geth": "0x0000000000000000000000000000000000000000000000000002cad6daaa6496",
  "nethermind": "0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000",
  "reth": "0x0000000000000000000000000000000000000000000000000002cad6daaa6496",
  "besu": "0x0000000000000000000000000000000000000000000000000002cad6daaa6496"
 }
}
```
```json
{
 "ctx": "11266068/_block/default::0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785",
 "path": "calls[2]",
 "key": "output",
 "values": {
  "geth": "0x0000000000000000000000000000000000000000000000000002cad6daaa6496",
  "erigon": "0x0000000000000000000000000000000000000000000000000002cad6daaa6496",
  "nethermind": "0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000",
  "reth": "0x0000000000000000000000000000000000000000000000000002cad6daaa6496",
  "besu": "0x0000000000000000000000000000000000000000000000000002cad6daaa6496"
 }
}
```

**missing_field / revertReason / besu**
```json
{
 "ctx": "11266068/0xe73a61913c03ffac28e6e19c62862f46b168b17449774a99e7734e3205d7a6fa/default/call_replay",
 "path": "",
 "key": "revertReason",
 "missing_in": [
  "besu"
 ],
 "values": {
  "nethermind": "arithmetic underflow or overflow",
  "geth": "arithmetic underflow or overflow",
  "erigon": "arithmetic underflow or overflow",
  "besu": "omitted",
  "reth": "arithmetic underflow or overflow"
 }
}
```
```json
{
 "ctx": "11266068/0xe73a61913c03ffac28e6e19c62862f46b168b17449774a99e7734e3205d7a6fa/onlyTopCall/call_replay",
 "path": "",
 "key": "revertReason",
 "missing_in": [
  "besu"
 ],
 "values": {
  "geth": "arithmetic underflow or overflow",
  "nethermind": "arithmetic underflow or overflow",
  "erigon": "arithmetic underflow or overflow",
  "besu": "omitted",
  "reth": "arithmetic underflow or overflow"
 }
}
```
```json
{
 "ctx": "11266068/0xe73a61913c03ffac28e6e19c62862f46b168b17449774a99e7734e3205d7a6fa/onlyTopCallWithLog/call_replay",
 "path": "",
 "key": "revertReason",
 "missing_in": [
  "besu"
 ],
 "values": {
  "geth": "arithmetic underflow or overflow",
  "reth": "arithmetic underflow or overflow",
  "nethermind": "arithmetic underflow or overflow",
  "erigon": "arithmetic underflow or overflow",
  "besu": "omitted"
 }
}
```

**missing_field / logs / besu, nethermind**
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/withLog",
 "path": "calls[2]",
 "key": "logs",
 "missing_in": [
  "nethermind",
  "besu"
 ],
 "values": {
  "erigon": "1 logs",
  "geth": "1 logs",
  "reth": "1 logs"
 }
}
```
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/withLog/call_replay",
 "path": "calls[2]",
 "key": "logs",
 "missing_in": [
  "nethermind",
  "besu"
 ],
 "values": {
  "reth": "1 logs",
  "erigon": "1 logs",
  "geth": "1 logs"
 }
}
```
```json
{
 "ctx": "11266068/_block/withLog::0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785",
 "path": "calls[2]",
 "key": "logs",
 "missing_in": [
  "nethermind",
  "besu"
 ],
 "values": {
  "erigon": "1 logs",
  "geth": "1 logs",
  "reth": "1 logs"
 }
}
```

**value_mismatch / output / besu, nethermind**
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/default/call_replay",
 "path": "calls[2]",
 "key": "output",
 "values": {
  "geth": "0x0000000000000000000000000000000000000000000000000002d9638dab84de",
  "erigon": "0x0000000000000000000000000000000000000000000000000002d9638dab84de",
  "nethermind": "0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000",
  "reth": "0x0000000000000000000000000000000000000000000000000002d9638dab84de",
  "besu": "0x0000000000000000000000000000000000000000000000000001eb221e829380"
 }
}
```
```json
{
 "ctx": "11266068/0x93251d139bb72e7dec0a0da9ffe30e16786be09a89209bd53f3b2454fd917785/withLog/call_replay",
 "path": "calls[2]",
 "key": "output",
 "values": {
  "reth": "0x0000000000000000000000000000000000000000000000000002d9638dab84de",
  "erigon": "0x0000000000000000000000000000000000000000000000000002d9638dab84de",
  "nethermind": "0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000",
  "geth": "0x0000000000000000000000000000000000000000000000000002d9638dab84de",
  "besu": "0x0000000000000000000000000000000000000000000000000001eb221e829380"
 }
}
```

## Wire-format quirks

| kind | field | count | client forms |
|---|---|---|---|
| empty_encoding | output | 16 | geth:omitted (16); erigon:omitted (16); nethermind:omitted (16); reth:omitted (16); besu:'0x' (16) |
| error_wording | out-of-gas | 8 |  |

## RPC errors during collection

- **erigon**:
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0xb4d102641fd2091b9162`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0x5eEAf02E1317Fd511ef2`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0x73f97CfbF2e4823681BC`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0x6f2B0686c7B5a831faE9`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0xe87B33128c93cBCa0398`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0x9FBAB94921d3832bBB2F`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0x020fcfa773401B090A86`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0x5157592A233A7a8dc95b`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0xA360Cb036822c059eB9f`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0xE99A0B30E1B9d08398e7`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0xc4aCE2d74D6847034c60`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0x9999fFFE0Fe59aad3B7b`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0x0169098F7Ef457D386C7`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0x83b8002C6576825aD147`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0x8cA045450dec3Cea547a`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0x07e64b127c70bC7D3663`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0xfFf1EC5995C5E5C3fED9`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0x6C8C026d0F966dEFC937`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0xbE7e0c128Eb16aAefE05`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0x6e7dfc666514bdd1FC29`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0x5493Cf24C78251Ea171e`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0xe6cB61Bda0681f1642aE`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0x14a730F64980003Df6F8`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0xfd9265Bb88101Dc214df`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: fee cap less than block base fee: address 0x0df7E3dA0337BefC8E60`
- **geth**:
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0xb4d102641fd2`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0x5eEAf02E1317`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0x73f97CfbF2e4`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0x6f2B0686c7B5`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0xe87B33128c93`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0x9FBAB94921d3`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0x020fcfa77340`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0x5157592A233A`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0xA360Cb036822`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0xE99A0B30E1B9`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0xc4aCE2d74D68`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0x9999fFFE0Fe5`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0x0169098F7Ef4`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0x83b8002C6576`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0x8cA045450dec`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0x07e64b127c70`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0xfFf1EC5995C5`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0x6C8C026d0F96`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0xbE7e0c128Eb1`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0x6e7dfc666514`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0x5493Cf24C782`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0xe6cB61Bda068`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0x14a730F64980`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0xfd9265Bb8810`
  - ×4: `RPC error: {'code': -32000, 'message': 'tracing failed: max fee per gas less than block base fee: address 0x0df7E3dA0337`
- **nethermind**:
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0xb4d102641fd2091b9162740b6d01`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0x5eEAf02E1317Fd511ef27355e882`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0x73f97CfbF2e4823681BC120062F6`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0x6f2B0686c7B5a831faE9073e3C40`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0xe87B33128c93cBCa0398FE4e5B57`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0x9FBAB94921d3832bBB2Fd3b93a06`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0x020fcfa773401B090A8611329Cf6`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0x5157592A233A7a8dc95b7Eb91685`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0xA360Cb036822c059eB9f03C2d4f4`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0xE99A0B30E1B9d08398e7533D49cb`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0xc4aCE2d74D6847034c6059055477`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0x9999fFFE0Fe59aad3B7b206841fa`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0x0169098F7Ef457D386C78218d67c`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0x83b8002C6576825aD147c0DD21c7`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0x8cA045450dec3Cea547a8a00b7Ab`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0x07e64b127c70bC7D366367cb719b`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0xfFf1EC5995C5E5C3fED9D34eDcb4`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0x6C8C026d0F966dEFC937b9D536FE`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0xbE7e0c128Eb16aAefE05d63a97F6`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0x6e7dfc666514bdd1FC2903Cd2e19`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0x5493Cf24C78251Ea171e57F5E4a9`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0xe6cB61Bda0681f1642aE345eDCf6`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0x14a730F64980003Df6F82f70c608`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0xfd9265Bb88101Dc214df471B6251`
  - ×4: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee: address 0x0df7E3dA0337BefC8E604e532498`
- **reth**:
  - ×88: `RPC error: {'code': -32000, 'message': 'max fee per gas less than block base fee'}`
