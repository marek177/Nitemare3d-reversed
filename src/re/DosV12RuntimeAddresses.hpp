#pragma once

#include <cstdint>

namespace nitemare3d::re::dos_v12 {

// DOS Nitemare-3D v1.2 runtime addresses recovered from static disassembly and
// cross-checked against runtime captures. These are DS-relative offsets.
//
// 0800:2419 and several other animation paths read dword [07ECh] and compare
// it with a per-record dword deadline at +0x08. When due, the new deadline is
// written as currentTick + sequenceDelay. 07EEh is therefore the high word of
// the same 32-bit clock value, not an independent state variable.
inline constexpr std::uint16_t kCurrentTickLowWord = 0x07EC;
inline constexpr std::uint16_t kCurrentTickHighWord = 0x07EE;
inline constexpr std::uint16_t kCurrentTickDword = kCurrentTickLowWord;

// Static anchor of the reconstructed object/animation advance routine in the
// DOS v1.2 disassembly used for this repository's RE notes.
inline constexpr std::uint16_t kAnimationAdvanceDisasmSegment = 0x0800;
inline constexpr std::uint16_t kAnimationAdvanceDisasmOffset = 0x2410;

// Fields read/written by 0800:2410 from its runtime record argument.
inline constexpr std::uint8_t kRecordRandomVariantOffset = 0x02;
inline constexpr std::uint8_t kRecordFrameOffset = 0x03;
inline constexpr std::uint8_t kRecordRuntimeClassOffset = 0x06;
inline constexpr std::uint8_t kRecordDeadlineOffset = 0x08;

// Sequence-definition fields read by 0800:2410.
inline constexpr std::uint8_t kSequenceFrameCountOffset = 0x00;
inline constexpr std::uint8_t kSequenceDelayOffset = 0x02;
inline constexpr std::uint8_t kSequenceRandomTablePtrOffset = 0x04;

// Runtime-class branches directly visible in 0800:2410.
inline constexpr std::uint8_t kStaticLikeClass = 0x07;
inline constexpr std::uint8_t kCompletionCallbackClass = 0x2D;
inline constexpr std::uint8_t kForceFrameZeroClass = 0x2F;

} // namespace nitemare3d::re::dos_v12
