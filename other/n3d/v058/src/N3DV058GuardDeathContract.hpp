#pragma once
// Nitemare 3D clean-room, build-scoped local numeric dispatch.
// Synthetic reference contract, NOT the author's source, not full 1:1 parity.
// Derived from strict SHA-bound original-byte audit of DOS v2.0 and Win16 1.10/alt.
#include <array>
#include <cstdint>

namespace n3d::v058 {
    enum class SoundKind : std::uint8_t { Fixed, RngModulo2, RngModulo3 };
    struct SoundRule { SoundKind kind; std::uint8_t base; };
    constexpr SoundRule fixed(unsigned v) {return {SoundKind::Fixed,static_cast<std::uint8_t>(v)};}
    constexpr SoundRule rng2(unsigned v) {return {SoundKind::RngModulo2,static_cast<std::uint8_t>(v)};}
    constexpr SoundRule rng3(unsigned v) {return {SoundKind::RngModulo3,static_cast<std::uint8_t>(v)};}
    constexpr std::array<std::int16_t,25> kScores = {
        25,75,50,100,250,150,200,100,100,0,150,150,200,-1000,1000,
        100,200,0,25,100,100,250,250,200,50
    };
    constexpr std::array<SoundRule,24> kFatalEvents = {
        fixed(35),fixed(8),fixed(7),fixed(36),fixed(4),fixed(19),fixed(14),rng3(11),
        rng3(11),fixed(0),fixed(7),fixed(7),fixed(35),fixed(0),fixed(0),fixed(70),
        fixed(70),fixed(0),fixed(74),fixed(2),fixed(2),fixed(9),fixed(70),fixed(70)
    };
    constexpr std::array<SoundRule,24> kState7Events = {
        fixed(34),rng3(56),rng3(56),fixed(59),fixed(20),fixed(21),fixed(16),rng2(54),
        rng2(54),fixed(6),fixed(63),fixed(60),fixed(0),fixed(0),fixed(18),fixed(72),
        fixed(71),fixed(0),fixed(73),fixed(13),fixed(13),fixed(56),fixed(61),fixed(61)
    };
    constexpr std::int16_t scoreFor(std::uint8_t cls) {
        return cls>=8 && cls<=0x20 ? kScores[cls-8] : 0;
    }
    constexpr std::uint32_t addSignedScore32(std::uint32_t before, std::uint8_t cls) {
        return before+static_cast<std::uint32_t>(static_cast<std::int32_t>(scoreFor(cls)));
    }
    constexpr SoundRule fatalEventFor(std::uint8_t cls) {
        return cls>=8 && cls<=0x1F ? kFatalEvents[cls-8] : fixed(0);
    }
    constexpr SoundRule state7EventFor(std::uint8_t cls) {
        return cls>=8 && cls<=0x1F ? kState7Events[cls-8] : fixed(0);
    }
    struct RngState {std::uint32_t state; std::uint32_t draws;};
    constexpr std::uint16_t nextRng(RngState &r) {
        r.state=r.state*214013U+2531011U;
        ++r.draws;
        return static_cast<std::uint16_t>((r.state>>16U)&0x7fffU);
    }
    constexpr std::uint8_t applyEvent(SoundRule rule,std::uint16_t rng15) {
        switch(rule.kind){
            case SoundKind::RngModulo2:return static_cast<std::uint8_t>(rule.base+rng15%2);
            case SoundKind::RngModulo3:return static_cast<std::uint8_t>(rule.base+rng15%3);
            default:return rule.base;
        }
    }
    struct Variant {std::uint8_t selection; std::uint32_t draws; bool resolved;};
    template<typename NextRng>
    Variant chooseVariant(std::uint8_t guardPlus12, std::uint8_t highFlag,
                          const std::array<std::uint8_t,7>&lowSlots,
                          NextRng next, std::uint32_t maxModelDraws=1024) {
        if (guardPlus12==0 && highFlag!=0)return {7,0,true};
        // Diagnostic bound and explicit unresolved case: original does NOT have this cap.
        for(std::uint32_t i=1;i<=maxModelDraws;++i) {
            const auto candidate=static_cast<std::uint8_t>(next()%7U);
            if(lowSlots[candidate]!=0)return {candidate,i,true};
        }
        return {0,maxModelDraws,false};
    }
}
