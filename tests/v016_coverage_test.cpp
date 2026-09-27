#include "re/N3DV016Coverage.hpp"

#include <cassert>

int main() {
    using namespace n3d::re::v016;

    static_assert(kDosCoverage.internallyConsistent());
    static_assert(kWin16Coverage.internallyConsistent());

    static_assert(kDosCoverage.discoveredDefinitions == 519);
    static_assert(kDosCoverage.strongOrExactMatches == 429);
    static_assert(kDosCoverage.weakOrManualReview == 90);

    static_assert(kWin16Coverage.discoveredDefinitions == 967);
    static_assert(kWin16Coverage.strongOrExactMatches == 929);
    static_assert(kWin16Coverage.weakOrManualReview == 38);

    static_assert(kTotalFunctionDefinitions == 1486);
    static_assert(kTotalStrongOrExactMatches == 1358);
    static_assert(kTotalWeakOrManualReview == 128);

    assert(kDosCoverage.matchRatio() > 0.82);
    assert(kWin16Coverage.matchRatio() > 0.96);
    return 0;
}
