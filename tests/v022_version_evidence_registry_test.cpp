#include "re/N3DV022VersionEvidenceRegistry.hpp"

#include <cassert>

int main() {
    using namespace n3d::re::v022;

    static_assert(hasConfirmedFingerprint(BuildId::DosV20));
    static_assert(hasConfirmedFingerprint(BuildId::DosV10));
    static_assert(hasConfirmedFingerprint(BuildId::DosV17));
    static_assert(kBuildProfiles.size() == 6);
    static_assert(!hasConfirmedFingerprint(BuildId::DosV12));
    static_assert(hasConfirmedFingerprint(BuildId::DosV19));
    static_assert(hasConfirmedFingerprint(BuildId::Win16Unknown));

    constexpr auto* dos20 = profileFor(BuildId::DosV20);
    static_assert(dos20 != nullptr);
    static_assert(dos20->unpackedExeSize == 171360u);
    static_assert(dos20->fingerprintConfidence == Confidence::Confirmed);

    static_assert(profileFor(BuildId::DosV10)->unpackedExeSize == 154448u);
    static_assert(profileFor(BuildId::DosV17)->unpackedExeSize == 170848u);
    static_assert(profileFor(BuildId::DosV17)->sha256 ==
                  "df85d457e752860dc8fc8c39c4c36ba1c62f03b0e704f1365ee618d8ed8447ff");
    static_assert(profileFor(BuildId::DosV19)->unpackedExeSize == 171296u);
    static_assert(profileFor(BuildId::Win16Unknown)->unpackedExeSize == 230400u);

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
    static_assert(mayPromoteToImplementation(FactId::Dos20PushUpdater0E50));
    static_assert(requiresRuntimeClosure(FactId::Dos20ObjectRuntime0E50));
    static_assert(mayPromoteToImplementation(FactId::Dos20IncomingDamagePreProtection));
    static_assert(mayPromoteToImplementation(FactId::Dos19IncomingDamagePostProtection));
    static_assert(mayPromoteToImplementation(FactId::Dos20HitIndicatorCountdown));
    static_assert(kEvidenceRegistry.size() == 22);
    static_assert(mayPromoteToImplementation(FactId::Dos20SlowQuantizerSingleIncrement));
    static_assert(mayPromoteToImplementation(FactId::Dos20FrameQuantizerSingleIncrement));
    static_assert(mayPromoteToImplementation(FactId::Dos20DemoFastSlowCounterArgument));
    static_assert(mayPromoteToImplementation(FactId::Dos20UnsignedLegacy500Recovery));
    static_assert(evidenceFor(FactId::Dos20UnsignedLegacy500Recovery)->build == BuildId::DosV20);
    static_assert(!mayPromoteToImplementation(FactId::Dos20ExactFastMainOrder));
    static_assert(evidenceFor(FactId::Dos20IncomingDamagePreProtection)->build == BuildId::DosV20);
    static_assert(evidenceFor(FactId::Dos19IncomingDamagePostProtection)->build == BuildId::DosV19);

    const auto* unknown = profileFor(BuildId::Unknown);
    assert(unknown == nullptr);

    return 0;
}
