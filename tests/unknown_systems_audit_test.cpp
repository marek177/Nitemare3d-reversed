#include "re/UnknownSystemsAudit.hpp"

#include <cassert>

int main() {
    using namespace nitemare3d::re;
    static_assert(kUnknownSystemTargets.size() == 31);
    static_assert(countByEvidence(Evidence::VerifiedExe) >= 2);
    static_assert(countByEvidence(Evidence::Todo) >= 5);
    assert(kUnknownSystemTargets[2].area == AuditArea::SequenceEvents);
    assert(kUnknownSystemTargets[2].evidence == Evidence::Todo);
    assert(kUnknownSystemTargets[3].area == AuditArea::SequenceEvents);
    assert(kUnknownSystemTargets[3].evidence == Evidence::Partial);
    assert(countByEvidence(Evidence::VerifiedData) >= 1);
    assert(countByEvidence(Evidence::Partial) >= 8);
    assert(kUnknownSystemTargets[0].anchor[0] != '\0');
    // Area membership should not depend on insertion order in the audit registry.
    constexpr auto hasAreaWithEvidence = [](AuditArea area, Evidence evidence) {
        for (const auto& item : kUnknownSystemTargets)
            if (item.area == area && item.evidence == evidence)
                return true;
        return false;
    };
    static_assert(hasAreaWithEvidence(AuditArea::SaveState, Evidence::Partial));
    static_assert(hasAreaWithEvidence(AuditArea::FunctionCoverage, Evidence::Partial));
    static_assert(hasAreaWithEvidence(AuditArea::MfcRuntimeValidation, Evidence::Partial));
}
