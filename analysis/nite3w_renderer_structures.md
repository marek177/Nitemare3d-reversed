# Renderer reverse-engineering structures

This header is a **research model**, not a claim that these were the original C/C++ declarations. It gives the reconstruction code stable names for structures recovered from `nite3w.exe`.

Confidence conventions:
- CONFIRMED: size/offset or behavior directly established.
- TENTATIVE: semantic field name still needs additional XREF/runtime proof.

```cpp
#pragma once
#include <cstdint>

namespace n3d::re {

constexpr int kMapWidth = 64;
constexpr int kMapHeight = 64;
constexpr int kTileWorldUnits = 64;

constexpr int kMaxVectors = 1000;
constexpr int kMaxVectorsPerOrientationList = 333;
constexpr int kFramebufferWidth = 320;
constexpr int kFramebufferHeight = 200;
constexpr int kMaxRenderObjects = 100;

#pragma pack(push, 1)

struct VectorRecord {
    std::uint8_t wallId;          // +0x00
    std::int8_t  texOffset;       // +0x01 TENTATIVE
    std::uint8_t animAux;         // +0x02 TENTATIVE
    std::uint8_t animFrame;       // +0x03 HIGH
    std::uint8_t textureSet;      // +0x04 HIGH
    std::uint8_t flags;           // +0x05 HIGH
    std::uint8_t renderClass;     // +0x06 HIGH
    std::uint8_t orientation;     // +0x07 CONFIRMED: 0..3
    std::uint32_t timer;          // +0x08 TENTATIVE semantic name
    std::int16_t x1;              // +0x0C CONFIRMED
    std::int16_t y1;              // +0x0E CONFIRMED
    std::int16_t x2;              // +0x10 CONFIRMED
    std::int16_t y2;              // +0x12 CONFIRMED
    std::int16_t screenX1;        // +0x14 HIGH
    std::int16_t projectedY1Q4;   // +0x16 HIGH
    std::int16_t screenX2;        // +0x18 HIGH
    std::int16_t projectedY2Q4;   // +0x1A HIGH
};

static_assert(sizeof(VectorRecord) == 0x1C);

// Original executable uses a 4-byte 16:16 FAR pointer here.
// Host reconstruction code should not replace this with a native pointer
// when reproducing binary layout.
struct FarPtr16 {
    std::uint16_t offset;
    std::uint16_t segment;
};

static_assert(sizeof(FarPtr16) == 4);

struct WallSpanRecord {
    FarPtr16 vector;              // +0x00
    std::int16_t xStart;          // +0x04
    std::int16_t yStartQ4;        // +0x06
    std::int16_t xEnd;            // +0x08
    std::int16_t yEndQ4;          // +0x0A
    std::int32_t dyDx;            // +0x0C HIGH, likely fixed-point
    std::int32_t yAccumulator;    // +0x10 HIGH
};

static_assert(sizeof(WallSpanRecord) == 0x14);

struct RenderObjectRecord {
    std::uint8_t activeOrFree;    // +0x00 TENTATIVE polarity/name
    std::uint8_t subtypeOrState;  // +0x01 TENTATIVE
    FarPtr16 worldObject;         // +0x02 HIGH
    std::int16_t spriteDesc;      // +0x06 HIGH
    std::int16_t screenLeft;      // +0x08 HIGH
    std::int16_t screenRight;     // +0x0A HIGH
    std::int16_t screenTop;       // +0x0C HIGH
    std::int16_t screenBottom;    // +0x0E HIGH
    std::int16_t projectedBottomQ4; // +0x10 HIGH
};

static_assert(sizeof(RenderObjectRecord) == 0x12);

#pragma pack(pop)

enum class VectorOrientation : std::uint8_t {
    HorizontalTop = 0,
    HorizontalBottom = 1,
    VerticalRight = 2,
    VerticalLeft = 3,
};

enum VectorFlag : std::uint8_t {
    VectorActive = 0x01,          // HIGH
    VectorUnknown04 = 0x04,
    VectorUnknown08 = 0x08,
    VectorUnknown10 = 0x10,
    VectorFlipTextureU = 0x20,    // HIGH
};

} // namespace n3d::re
```

## Recovered executable locations

Working addresses from the current Win16 audit:

| Item | Location |
|---|---|
| owner-column FAR-pointer buffer | `0x53FE` |
| wall silhouette/occlusion buffer | `0x58FE` |
| wall-span count | `0x5E7E` |
| wall-span array | `0x5E88` |
| render-object queue | `0x6270` |
| VECLIST counts | around `0x697A..0x6980` |
| VECLIST 0 | `0x6982` |
| VECLIST 1 | `0x6EB6` |
| VECLIST 2 | `0x73EA` |
| VECLIST 3 | `0x791E` |

These addresses are version-specific research coordinates and should not be treated as portable API constants.

## Important correction

An older renderer working hypothesis used a **52-byte** step. The deeper audit of `FUN_1010_6266` / `FUN_1010_66B0` establishes the actual wall-span stride as **0x14 / 20 bytes**. Keep old notes only as historical hypotheses, not current structure definitions.
