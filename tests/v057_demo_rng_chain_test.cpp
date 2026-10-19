#include "re/N3DV057DemoRngChain.hpp"
#include <cassert>
using namespace n3d::re::v057;
int main() {
    static_assert(validatesChain());
    static_assert(kDos20DemoRngPrefix.size() == 18);
    static_assert(kDos20DemoRngPrefix[0].callsite == 0x56A6);
    static_assert(kDos20DemoRngPrefix[7].stateAfter == 0x72AE7869u);
    static_assert(kDos20DemoRngPrefix[15].callsite == 0x9FE3);
    static_assert(kDos20DemoRngPrefix[17].stateAfter == 0xAEA69ED3u);
    static_assert(kIndependentlyReproducedPrefixLength == 8);
    static_assert(kIndependentOriginalRuns == 2);
    static_assert(!kEntries9To18IndependentlyReproduced);
    static_assert(!kCompleteDemoRngLedgerClosed);
    assert(kDos20DemoRngPrefix[16].result == 2995);
    return 0;
}
