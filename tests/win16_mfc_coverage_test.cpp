#include "re/Win16MfcCoverage.hpp"

#include <cassert>

int main() {
    using namespace nitemare3d::re::win16;
    static_assert(kMfcCoverage.size() == 9);
    static_assert(countCoverage(MfcCoverageState16::StaticClosed) == 5);
    static_assert(countCoverage(MfcCoverageState16::StaticStrong) == 2);
    static_assert(countCoverage(MfcCoverageState16::RuntimePending) == 2);
    assert(kMfcCoverage[0].state == MfcCoverageState16::StaticClosed);
    assert(kMfcCoverage[7].state == MfcCoverageState16::RuntimePending);
    return 0;
}
