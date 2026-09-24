#include "re/Win16MfcMemory.hpp"

#include <cassert>

int main() {
    using namespace nitemare3d::re::win16;

    static_assert(sizeof(CRuntimeClass16) == 0x10);
    static_assert(sizeof(HandleMap16) == 0x26);

    assert(kCWndObjectSize == 0x1A);
    assert(kRuntimeClasses[0].offset == kCObjectRuntimeClass);
    assert(kRuntimeClasses[1].base == kCCmdTargetRuntimeClass);
    assert(kCWndSentinels[0].pseudoHwnd == 0);
    assert(kCWndSentinels[1].pseudoHwnd == 1);
    assert(kCWndSentinels[2].pseudoHwnd == -1);
    assert(kCWndSentinels[3].pseudoHwnd == -2);

    return 0;
}
