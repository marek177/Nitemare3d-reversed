#pragma once
// DOS2 E1M1 ORIGINAL DS:3F50 observed key bits (V083–V086).
// Not a tick model, keyboard handler, FIRE/USE dispatcher or parity proof.
#include <array>
#include <cstdint>
namespace n3d::re::dos20_input {
enum class Key : std::uint8_t { Up, Down, Left, Right, Fire, Alt, Use };
inline constexpr std::uint16_t Up=0x0002, Down=0x0004, Left=0x0008,
    Right=0x0010, Fire=0x0080, Alt=0x0100, Use=0x0200;
inline constexpr std::uint16_t Movement=Up|Down|Left|Right;
inline constexpr std::uint16_t Actions=Fire|Alt|Use, Observed=Movement|Actions;
inline constexpr std::array<std::uint16_t,8> ActionMasks{
    0,0x0080,0x0100,0x0180,0x0200,0x0280,0x0300,0x0380
};
struct Held { bool up{}, down{}, left{}, right{}, fire{}, alt{}, use{}; };
constexpr std::uint16_t bit(Key key) noexcept {
    switch(key) {
    case Key::Up:return Up; case Key::Down:return Down;
    case Key::Left:return Left; case Key::Right:return Right;
    case Key::Fire:return Fire; case Key::Alt:return Alt;
    case Key::Use:return Use;
    }
    return 0;
}
constexpr std::uint16_t encode(Held h) noexcept {
    return (h.up?Up:0)|(h.down?Down:0)|(h.left?Left:0)|
           (h.right?Right:0)|(h.fire?Fire:0)|(h.alt?Alt:0)|(h.use?Use:0);
}
constexpr Held decode(std::uint16_t m) noexcept {
    return {bool(m&Up),bool(m&Down),bool(m&Left),bool(m&Right),
            bool(m&Fire),bool(m&Alt),bool(m&Use)};
}
// Key-bit transition only. Keep all currently unclassified bits unchanged.
constexpr std::uint16_t hold(std::uint16_t m, Key k, bool down) noexcept {
    const auto b=bit(k);
    return down?std::uint16_t(m|b):std::uint16_t(m&std::uint16_t(~b));
}
constexpr std::uint16_t actionOnly(std::uint16_t m) noexcept {return m&Actions;}
constexpr std::uint16_t unknown(std::uint16_t m) noexcept {
    return m&std::uint16_t(~Observed);
}
constexpr bool validActionMask(std::uint16_t m) noexcept {
    if(m&std::uint16_t(~Actions))return false;
    for(auto a:ActionMasks)if(m==a)return true;
    return false;
}
struct OriginalWitness { unsigned samples, aligned, stale, phases, transitions, masks; };
inline constexpr OriginalWitness V085V086{1716,1688,28,24,24,8};
// Host RAM polling was asynchronous. No per-DOS-tick latency inferred.
}
