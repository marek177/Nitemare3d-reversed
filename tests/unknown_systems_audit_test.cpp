#include "re/UnknownSystemsAudit.hpp"

#include <cassert>

int main() {
    using namespace nitemare3d::re;
    static_assert(kUnknownSystemTargets.size() == 26);
    static_assert(countByEvidence(Evidence::VerifiedExe) >= 2);
    static_assert(countByEvidence(Evidence::Todo) >= 5);
    assert(countByEvidence(Evidence::VerifiedData) >= 1);
    assert(countByEvidence(Evidence::Partial) >= 8);
    assert(kUnknownSystemTargets[0].anchor[0] != '\0');
    assert(kUnknownSystemTargets.back().area == AuditArea::SaveState);
    assert(kUnknownSystemTargets.back().evidence == Evidence::Partial);
}
