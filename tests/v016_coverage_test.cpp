#include "re/N3DV016Coverage.hpp"

#include <cassert>

int main() {
    using namespace n3d::re::v016;

    static_assert(kDosCoverage.internallyConsistent());
    static_assert(kWin16Coverage.internallyConsistent());

    static_assert(kDosCoverage.discoveredDefinitions == 519);
    static_assert(kDosCoverage.strongOrExactMatches == 429);
    static_assert(kDosCoverage.weakOrManualReview == 90);
    static_assert(kDosCoverage.manuallyReviewedWeak == 0);
    static_assert(kDosCoverage.pendingManualReview() == 90);

    static_assert(kWin16Coverage.discoveredDefinitions == 967);
    static_assert(kWin16Coverage.strongOrExactMatches == 929);
    static_assert(kWin16Coverage.weakOrManualReview == 38);
    static_assert(kWin16Coverage.manuallyReviewedWeak == 38);
    static_assert(kWin16Coverage.pendingManualReview() == 0);
    static_assert(kWin16Coverage.reviewedIdentityCount() == 967);

    static_assert(kTotalFunctionDefinitions == 1486);
    static_assert(kTotalStrongOrExactMatches == 1358);
    static_assert(kTotalWeakOrManualReview == 128);
    static_assert(kTotalManuallyReviewedWeak == 38);
    static_assert(kTotalPendingManualReview == 90);

    assert(kDosCoverage.matchRatio() > 0.82);
    assert(kWin16Coverage.matchRatio() > 0.96);
    assert(kWin16Coverage.identityReviewRatio() == 1.0);
    return 0;
}
