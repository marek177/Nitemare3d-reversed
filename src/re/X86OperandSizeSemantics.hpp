#pragma once
#include <cstdint>

namespace n3d::re::x86 {
// Pure 16-bit arithmetic primitives for auditing disassembler output.
// These are NOT claims about a particular Nitemare 3D call site.
constexpr std::uint16_t cbw(std::uint8_t al) noexcept {
    return static_cast<std::uint16_t>(
        static_cast<std::int16_t>(static_cast<std::int8_t>(al)));
}
constexpr std::uint16_t cwd_high(std::uint16_t ax) noexcept {
    return (ax & 0x8000u) ? 0xffffu : 0u;
}
constexpr std::uint32_t cwd_pair(std::uint16_t ax) noexcept {
    return (static_cast<std::uint32_t>(cwd_high(ax)) << 16) | ax;
}
constexpr std::uint32_t cwde(std::uint16_t ax) noexcept {
    return static_cast<std::uint32_t>(
        static_cast<std::int32_t>(static_cast<std::int16_t>(ax)));
}
constexpr std::uint32_t cdq_high(std::uint32_t eax) noexcept {
    return (eax & 0x80000000u) ? 0xffffffffu : 0u;
}
enum class OperandSize : std::uint8_t { bits16, bits32 };
enum class SignExtendInstruction : std::uint8_t { CBW, CWDE, CWD, CDQ };
constexpr SignExtendInstruction decode_98(OperandSize size) noexcept {
    return size == OperandSize::bits16 ? SignExtendInstruction::CBW : SignExtendInstruction::CWDE;
}
constexpr SignExtendInstruction decode_99(OperandSize size) noexcept {
    return size == OperandSize::bits16 ? SignExtendInstruction::CWD : SignExtendInstruction::CDQ;
}
} // namespace n3d::re::x86
