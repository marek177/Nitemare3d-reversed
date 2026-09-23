#include "re/UnknownSystemsAudit.hpp"

#include <cassert>

int main() {
    using namespace nitemare3d::re;
    static_assert(kUnknownSystemTargets.size() == 29);
    static_assert(countByEvidence(Evidence::VerifiedExe) >= 2);
    static_assert(countByEvidence(Evidence::Todo) >= 5);
    assert(countByEvidence(Evidence::VerifiedData) >= 1);
    assert(countByEvidence(Evidence::Partial) >= 8);
    assert(kUnknownSystemTargets[0].anchor[0] != '\0');
    assert(kUnknownSystemTargets[kUnknownSystemTargets.size() - 3].area == AuditArea::SaveState);
    assert(kUnknownSystemTargets[kUnknownSystemTargets.size() - 3].evidence == Evidence::Partial);
    assert(kUnknownSystemTargets.back().area == AuditArea::FunctionCoverage);
    assert(kUnknownSystemTargets.back().evidence == Evidence::Partial);
}
