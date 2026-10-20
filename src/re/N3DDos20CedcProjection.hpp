#pragma once
// DOS Nitemare 3D v2.0 CEDC..CFB0: original 16/32-bit integer projection.
// Computes the CEDC value BEFORE 25DC's local/NEG and 22CA's edge-U.
// Verified on 1,808 original DOS2 CPU operand/return records. The complete
// MAP->VEC->renderer chain and final framebuffer remain separately OPEN.
#include <bit>
#include <cstdint>
#include <limits>
#include <optional>

namespace n3d::re::dos20::cedc {
enum class Path : std::uint8_t {
    Selector1Horizontal, Selector1Vertical,
    Selector0Horizontal, Selector0Vertical
};
struct Input {
    std::int16_t screenX{}, screenCenterX{};
    std::uint8_t orientation{};
    std::uint16_t spanYQ4{};
    std::int32_t inverseScale{}, verticalNumerator{}, product32{};
    std::int16_t sineQ10{}, cosineQ10{};
    bool selector415cNonzero{};
};
struct Output {
    Path path{};
    std::int32_t screenOrVerticalQuotient{};
    std::int32_t combinedNumerator{};
    std::int32_t quotient32{};
    std::uint16_t returnedAX{};
};
constexpr std::int16_t asSigned16(std::uint16_t v) noexcept {
    return std::bit_cast<std::int16_t>(v);
}
constexpr std::int32_t asSigned32(std::uint32_t v) noexcept {
    return std::bit_cast<std::int32_t>(v);
}
constexpr std::int32_t wrap32(std::int64_t v) noexcept {
    return asSigned32(static_cast<std::uint32_t>(v));
}
constexpr std::int16_t subtract16(std::int16_t a,
                                  std::int16_t b) noexcept {
    return asSigned16(static_cast<std::uint16_t>(
        static_cast<std::uint16_t>(a)-static_cast<std::uint16_t>(b)));
}
// Original IDIV is signed 32-bit. Host 64-bit division also safely detects
// the INT32_MIN/-1 quotient fault without undefined behavior.
constexpr std::optional<std::int32_t> idiv(std::int64_t num,
                                           std::int64_t den) noexcept {
    if (den==0) return std::nullopt;
    const auto q=num/den; // signed quotient truncates toward zero
    if (q<std::numeric_limits<std::int32_t>::min() ||
        q>std::numeric_limits<std::int32_t>::max())return std::nullopt;
    return static_cast<std::int32_t>(q);
}
constexpr std::optional<Output> project(const Input& a) noexcept {
    if(a.orientation>3 || a.spanYQ4==0)return std::nullopt;
    const bool vertical=a.orientation>=2;
    const Path path=a.selector415cNonzero
        ? (vertical?Path::Selector1Vertical:Path::Selector1Horizontal)
        : (vertical?Path::Selector0Vertical:Path::Selector0Horizontal);
    const auto divisor=std::int32_t(a.selector415cNonzero
                                    ? a.cosineQ10:a.sineQ10);
    if(divisor==0)return std::nullopt;
    // Original 16-bit SUB AX,[DS:4550]; CWD -> sign-extended word.
    const auto screenOffset=subtract16(a.screenX,a.screenCenterX);
    const bool useScreen=path==Path::Selector1Horizontal ||
                         path==Path::Selector0Vertical;
    // Original IMUL's EAX result is the wrapped low signed 32 bits.
    const std::int32_t firstNumerator=useScreen
        ? wrap32(std::int64_t(screenOffset)*a.inverseScale)
        : a.verticalNumerator;
    const auto partial=idiv(firstNumerator,a.spanYQ4);
    if(!partial)return std::nullopt;
    std::int32_t combined{};
    if(path==Path::Selector1Horizontal)
        combined=wrap32(std::int64_t(*partial)+a.product32);
    else if(path==Path::Selector0Vertical)
        combined=wrap32(std::int64_t(a.product32)-*partial);
    else
        combined=wrap32(std::int64_t(*partial)-a.product32);
    const auto quotient=idiv(combined,divisor);
    if(!quotient)return std::nullopt;
    return Output{path,*partial,combined,*quotient,
                  static_cast<std::uint16_t>(*quotient)};
}
// The original caller adds a 16-bit local operand and may NEG SI before
// applying the independently verified DOS2 22CA edge correction.
constexpr std::uint16_t callerBefore22ca(std::uint16_t ax,
                                         std::uint16_t local16,
                                         bool negate) noexcept {
    const auto sum=static_cast<std::uint16_t>(ax+local16);
    return negate?static_cast<std::uint16_t>(0u-sum):sum;
}
} // namespace n3d::re::dos20::cedc
