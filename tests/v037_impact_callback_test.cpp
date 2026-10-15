#include "re/N3DV037ImpactCallbackEvidence.hpp"
#include <cassert>

using namespace n3d::re::v037;
int main() {
    int class4count = 0;
    for (unsigned cls = 0; cls != 256; ++cls) {
        const auto f = objectPropertyForClass(static_cast<std::uint8_t>(cls));
        if (f & 0x40) { assert(cls == 4); ++class4count; }
    }
    assert(class4count == 1);
    assert(objectPropertyForClass(4) == 0x40);
    assert(!specialCallbackResult(OriginalBuild::Dos20,0,2,10));
    assert(specialCallbackResult(OriginalBuild::Dos20,0x40,1,5).value() == 0x40);
    assert(specialCallbackResult(OriginalBuild::Dos20,0x48,3,9).value() == 0x48);
    for (auto build: { OriginalBuild::Win18, OriginalBuild::Win110 }) {
        assert(specialCallbackResult(build,0x40,1,5).value() == 0);
        assert(specialCallbackResult(build,0x40,2,9).value() == 0);
        assert(specialCallbackResult(build,0x40,2,10).value() == 1);
    }
    assert(specialCallbackResult(OriginalBuild::Dos20,0x40,2,10).value() == 1);
    assert(kLocalOriginalStaticProven);
    assert(kFirstLoadLevelCensusProvenForAuditedMapSet);
    assert(!kAllDynamicMapWritersExhausted && !kOriginalRuntimeParityVerified);
}
