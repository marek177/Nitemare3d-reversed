#include "re/N3DDos20Guard41PostDeath.hpp"
#include "re/N3DV058GuardState09.hpp"
#include <cstdlib>
#include <iostream>
namespace g=n3d::re::dos20::guard41;
static void check(bool value) { if(!value) {std::cerr<<"Post-death capture gate mismatch\n";std::exit(1);} }
int main() {
    check(g::isObservedPostDeathWriter(g::kState0To9));
    check(!g::isObservedPostDeathWriter(g::kPreDeathControl));
    // Neither correct writer, correct actor nor AL alone authenticates an event.
    for(unsigned field=0;field<8;++field) {
        auto bad=g::kState0To9;
        switch(field) {
        case 0: ++bad.cs;break;case 1: ++bad.ip;break;
        case 2: ++bad.es;break;case 3: bad.si+=26;break;
        case 4: bad.al=5;break;case 5: bad.oldState=5;break;
        case 6: bad.newState=5;break;case 7: ++bad.writeLinear;break;
        }
        check(!g::isObservedPostDeathWriter(bad));
    }
    check(n3d::re::v058::nextRngState(g::kRngBefore)==g::kRngAfter);
    check(n3d::re::v058::rng15(g::kRngAfter)==g::kRngResult);
    check((g::kWallProperty&8)==0);
    check(g::kWorldFlagWriteCpu<g::kState9WriteCpu && g::kState9WriteCpu<g::kRngLowWriteCpu && g::kRngLowWriteCpu<g::kRngHighWriteCpu);
    check(g::kState9TraceA.epilogueEntered && g::kState9TraceB.epilogueEntered);
    check(!g::kDos12Reference.epilogueEntered);
    check(!g::kContinuousFatalToState0AProven && !g::kAllDropAndCleanupPathsClosed);
    check(!g::kRawTracesReverifiedInThisIntegration);
    std::cout<<"Report-derived gate PASS; pre-death control and eight altered identities rejected\n";
}
