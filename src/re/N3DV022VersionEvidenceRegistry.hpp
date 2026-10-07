#pragma once

#include <array>
#include <cstdint>
#include <string_view>

namespace n3d::re::v022 {

enum class Platform : std::uint8_t {
    Dos,
    Win16
};

enum class BuildId : std::uint8_t {
    DosV10,
    DosV12,
    DosV19,
    DosV20,
    Win16Unknown,
    Unknown
};

enum class Confidence : std::uint8_t {
    Confirmed,
    Strong,
    Open
};

enum class EvidenceSource : std::uint8_t {
    StaticDisassembly,
    RuntimeTrace,
    MemoryDump,
    CrossVersionMatch,
    BehavioralObservation,
    ResourceFormat,
    Unknown
};

struct BuildProfile {
    BuildId id;
    Platform platform;
    std::string_view versionLabel;
    std::uint32_t unpackedExeSize;
    std::string_view sha256;
    Confidence fingerprintConfidence;
};

inline constexpr BuildProfile kDosV20Profile{
    BuildId::DosV20,
    Platform::Dos,
    "DOS v2.0",
    171360u,
    "e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297",
    Confidence::Confirmed
};

inline constexpr BuildProfile kDosV10Profile{
    BuildId::DosV10, Platform::Dos, "DOS v1.0", 0u, "", Confidence::Open
};

inline constexpr BuildProfile kDosV12Profile{
    BuildId::DosV12, Platform::Dos, "DOS v1.2", 0u, "", Confidence::Open
};

inline constexpr BuildProfile kDosV19Profile{
    BuildId::DosV19, Platform::Dos, "DOS v1.9", 0u, "", Confidence::Open
};

inline constexpr BuildProfile kWin16UnknownProfile{
    BuildId::Win16Unknown, Platform::Win16, "Win16 analyzed build",
    0u, "", Confidence::Open
};

inline constexpr std::array<BuildProfile, 5> kBuildProfiles = {{
    kDosV10Profile,
    kDosV12Profile,
    kDosV19Profile,
    kDosV20Profile,
    kWin16UnknownProfile
}};

constexpr const BuildProfile* profileFor(BuildId id) noexcept {
    for (const auto& profile : kBuildProfiles) {
        if (profile.id == id) {
            return &profile;
        }
    }
    return nullptr;
}

constexpr bool hasConfirmedFingerprint(BuildId id) noexcept {
    const auto* profile = profileFor(id);
    return profile != nullptr &&
           profile->fingerprintConfidence == Confidence::Confirmed &&
           profile->unpackedExeSize != 0u &&
           !profile->sha256.empty();
}

enum class FactId : std::uint16_t {
    Dos20PlayerXY,
    Dos20PlayerCollisionFootprint,
    Dos20ProjectilePool,
    Dos20GuardPool,
    Dos20RngAlgorithm,
    Dos20RngDirectCallsites,
    Dos20SecretPanelRecord,
    Dos20SecretPanelStep,
    Dos20SpanPool,
    Dos20SchedulerAnchors,
    Dos20ExactFastMainOrder,
    Dos20ObjectRuntime0E50,
    Dos20ProjectileStaleCache,
    CrossVersionAddressPortability
};

struct EvidenceRecord {
    FactId fact;
    BuildId build;
    Confidence confidence;
    EvidenceSource source;
    std::string_view evidenceRef;
    std::string_view closureTest;
};

inline constexpr std::array<EvidenceRecord, 14> kEvidenceRegistry = {{
    {FactId::Dos20PlayerXY, BuildId::DosV20, Confidence::Confirmed,
     EvidenceSource::StaticDisassembly, "DS:4162/4164; stores 68B5/68B9",
     "watch X/Y commit during controlled movement"},
    {FactId::Dos20PlayerCollisionFootprint, BuildId::DosV20,
     Confidence::Confirmed, EvidenceSource::StaticDisassembly,
     "6488/6378 footprint 0x1B", "boundary collision fixture"},
    {FactId::Dos20ProjectilePool, BuildId::DosV20, Confidence::Confirmed,
     EvidenceSource::StaticDisassembly,
     "DS:41B6; 8 x 0x2A; scheduler 8230",
     "slot before/after trace"},
    {FactId::Dos20GuardPool, BuildId::DosV20, Confidence::Strong,
     EvidenceSource::StaticDisassembly,
     "DS:264E; stride 0x1A; loop 5F26",
     "runtime iteration/count trace"},
    {FactId::Dos20RngAlgorithm, BuildId::DosV20, Confidence::Confirmed,
     EvidenceSource::StaticDisassembly,
     "LCG 214013/2531011; result >>16 & 0x7fff",
     "seed/result regression"},
    {FactId::Dos20RngDirectCallsites, BuildId::DosV20, Confidence::Confirmed,
     EvidenceSource::StaticDisassembly, "20 direct calls to 0FBA:01A0",
     "runtime caller census"},
    {FactId::Dos20SecretPanelRecord, BuildId::DosV20, Confidence::Confirmed,
     EvidenceSource::StaticDisassembly,
     "base 34F6; record 0x0E; VEC0-3/MAP/state",
     "USE + per-tick record/VEC dump"},
    {FactId::Dos20SecretPanelStep, BuildId::DosV20, Confidence::Confirmed,
     EvidenceSource::StaticDisassembly, "0AEA retracts by 2 units/update",
     "per-tick endpoint trace"},
    {FactId::Dos20SpanPool, BuildId::DosV20, Confidence::Confirmed,
     EvidenceSource::StaticDisassembly,
     "count 4D64; base 4D6E; stride 0x12; max 50",
     "frame SPAN dump"},
    {FactId::Dos20SchedulerAnchors, BuildId::DosV20, Confidence::Confirmed,
     EvidenceSource::StaticDisassembly,
     "BCC2/BE74/BEB4/BEF4/C150/C0D8/C1A8",
     "one-tick scheduler trace"},
    {FactId::Dos20ExactFastMainOrder, BuildId::DosV20, Confidence::Open,
     EvidenceSource::Unknown, "static ordering hypothesis only",
     "one-tick first-divergence trace"},
    {FactId::Dos20ObjectRuntime0E50, BuildId::DosV20, Confidence::Open,
     EvidenceSource::StaticDisassembly, "0800:0E50 candidate",
     "writer/reader xrefs + runtime mutation trace"},
    {FactId::Dos20ProjectileStaleCache, BuildId::DosV20, Confidence::Strong,
     EvidenceSource::StaticDisassembly,
     "embedded OBJECT +18/+19 projected-Y cache may survive reuse",
     "slot reuse with render/no-render comparison"},
    {FactId::CrossVersionAddressPortability, BuildId::Unknown,
     Confidence::Confirmed, EvidenceSource::CrossVersionMatch,
     "4BF6/6EC8/7E5E/9806 are build-specific",
     "fingerprint each executable before address use"}
}};

constexpr const EvidenceRecord* evidenceFor(FactId fact) noexcept {
    for (const auto& record : kEvidenceRegistry) {
        if (record.fact == fact) {
            return &record;
        }
    }
    return nullptr;
}

constexpr bool mayPromoteToImplementation(FactId fact) noexcept {
    const auto* record = evidenceFor(fact);
    return record != nullptr && record->confidence == Confidence::Confirmed;
}

constexpr bool requiresRuntimeClosure(FactId fact) noexcept {
    const auto* record = evidenceFor(fact);
    return record != nullptr && record->confidence != Confidence::Confirmed;
}

}  // namespace n3d::re::v022
