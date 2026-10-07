#include "re/N3DV022VersionEvidenceRegistry.hpp"

#include <cassert>

int main() {
    using namespace n3d::re::v022;

    static_assert(hasConfirmedFingerprint(BuildId::DosV20));
    static_assert(!hasConfirmedFingerprint(BuildId::DosV10));
    static_assert(!hasConfirmedFingerprint(BuildId::DosV12));
    static_assert(!hasConfirmedFingerprint(BuildId::DosV19));
    static_assert(!hasConfirmedFingerprint(BuildId::Win16Unknown));

    constexpr auto* dos20 = profileFor(BuildId::DosV20);
    static_assert(dos20 != nullptr);
    static_assert(dos20->unpackedExeSize == 171360u);
    static_assert(dos20->fingerprintConfidence == Confidence::Confirmed);

    constexpr auto* player = evidenceFor(FactId::Dos20PlayerXY);
    static_assert(player != nullptr);
    static_assert(player->confidence == Confidence::Confirmed);
    static_assert(player->build == BuildId::DosV20);

    constexpr auto* guard = evidenceFor(FactId::Dos20GuardPool);
    static_assert(guard != nullptr);
    static_assert(guard->confidence == Confidence::Strong);
    static_assert(requiresRuntimeClosure(FactId::Dos20GuardPool));

    constexpr auto* scheduler = evidenceFor(FactId::Dos20ExactFastMainOrder);
    static_assert(scheduler != nullptr);
    static_assert(scheduler->confidence == Confidence::Open);
    static_assert(!mayPromoteToImplementation(
        FactId::Dos20ExactFastMainOrder));

    static_assert(mayPromoteToImplementation(FactId::Dos20RngAlgorithm));
    static_assert(mayPromoteToImplementation(FactId::Dos20SecretPanelStep));
    static_assert(requiresRuntimeClosure(FactId::Dos20ProjectileStaleCache));

    const auto* unknown = profileFor(BuildId::Unknown);
    assert(unknown == nullptr);

    return 0;
}
