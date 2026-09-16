# NITE3W.EXE function map (work in progress)

Addresses use `NE-segment:offset` notation. Names are reconstructed descriptive names unless explicitly identified by surviving symbols/strings.

| Address | Reconstructed role | Confidence | Evidence |
|---|---|---|---|
| `3:1296` | FindDoor-like lookup | medium | failure path references `Door not in map` |
| `3:133A` | FindPush-like lookup | high | failure path references `Push not in map`; scans push records |
| `3:14A8` | Initialize door table | high | hard maximum `0x40` |
| `3:16D6` | Initialize panel table | high | hard maximum `0x20` |
| `3:181C` | Initialize push table | high | runtime class `0x28`, max `0x0C` |
| `3:21B6` | StartPush | high | copies cardinal movement increments and sets 8-step counter |
| `3:2210` | UpdatePushes | high | updates fixed-point XY, map object cell, decrements counter |

Additional executable anchors include diagnostics for missing door/push records, maximum door/panel/push counts, undefined wall/object classes and empty object-class lookups. These are useful anchors for continuing door, panel, pushable and object-class dispatch reconstruction.
