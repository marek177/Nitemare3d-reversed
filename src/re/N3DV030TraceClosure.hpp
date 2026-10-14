#pragma once

#include "re/N3DV020VerificationHarness.hpp"
#include "re/N3DV022VersionEvidenceRegistry.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>

namespace n3d::re::v030 {

// This verifier compares the *supplied* captured RNG streams. No success code
// means that the original DOS/Win16 executable was actually executed.
using RngRecord = v020::RngTraceEntry;

enum class ComparisonVerdict : std::uint8_t {
    EmptyReference,
    EmptyCandidate,
    InvalidReference,
    InvalidCandidate,
    FirstDifference,
    CountDifference,
    EqualUnsealed,
    EqualAttested
};

struct TraceSeal {
    bool referenceBeginObserved;
    bool referenceEndObserved;
    bool candidateBeginObserved;
    bool candidateEndObserved;
    bool csvDigestsChecked;
    bool originalUnpackedImageShaChecked;

    constexpr bool hasDeclaredBoundaries() const noexcept {
        return referenceBeginObserved && referenceEndObserved &&
               candidateBeginObserved && candidateEndObserved;
    }
    constexpr bool fullyAttested() const noexcept {
        return hasDeclaredBoundaries() && csvDigestsChecked &&
               originalUnpackedImageShaChecked;
    }
};

struct FirstDifference {
    ComparisonVerdict verdict;
    std::size_t index;
    std::size_t referenceCount;
    std::size_t candidateCount;
    std::uint16_t referenceCaller;
    std::uint16_t candidateCaller;

    constexpr bool streamEqual() const noexcept {
        return verdict == ComparisonVerdict::EqualUnsealed ||
               verdict == ComparisonVerdict::EqualAttested;
    }

    // Attestation describes provided metadata only; not original execution.
    constexpr bool hasAttestedEnvelope() const noexcept {
        return verdict == ComparisonVerdict::EqualAttested;
    }
};

inline constexpr std::string_view kCanonicalDos20UnpackedSha =
    v022::kDosV20Profile.sha256;
inline constexpr std::uint32_t kCanonicalDos20UnpackedLength =
    v022::kDosV20Profile.unpackedExeSize;

constexpr bool equalRecord(const RngRecord& lhs,
                           const RngRecord& rhs) noexcept {
    return lhs.caller == rhs.caller &&
           lhs.stateBefore == rhs.stateBefore &&
           lhs.stateAfter == rhs.stateAfter &&
           lhs.result == rhs.result;
}

// Reject unknown direct callsites, a nonmatching seed, an illegal LCG step,
// a wrong 15-bit result, and a discontinuous stream. This is deliberately
// strict and DOS-v2.0 scoped; it cannot validate Win16 caller offsets.
constexpr std::size_t firstInvalidRngEntry(
    std::span<const RngRecord> trace,
    std::uint32_t initialSeed) noexcept {
    if (trace.empty()) return 0;
    if (trace.front().stateBefore != initialSeed) return 0;
    for (std::size_t i = 0; i < trace.size(); ++i) {
        if (i != 0 && trace[i].stateBefore != trace[i-1].stateAfter) {
            return i;
        }
        if (!v020::validateRngTraceEntry(trace[i]).valid()) {
            return i;
        }
    }
    return trace.size();
}

constexpr FirstDifference compareRngTraces(
    std::span<const RngRecord> reference,
    std::span<const RngRecord> candidate,
    std::uint32_t initialSeed,
    TraceSeal seal = {}) noexcept {

    if (reference.empty()) {
        return {ComparisonVerdict::EmptyReference, 0, reference.size(),
                candidate.size(), 0, 0};
    }
    if (candidate.empty()) {
        return {ComparisonVerdict::EmptyCandidate, 0, reference.size(),
                candidate.size(), 0, 0};
    }

    const std::size_t refInvalid =
        firstInvalidRngEntry(reference, initialSeed);
    if (refInvalid != reference.size()) {
        return {ComparisonVerdict::InvalidReference, refInvalid,
                reference.size(), candidate.size(),
                reference[refInvalid].caller,
                static_cast<std::uint16_t>(refInvalid < candidate.size() ? candidate[refInvalid].caller : 0)};
    }
    const std::size_t candInvalid =
        firstInvalidRngEntry(candidate, initialSeed);
    if (candInvalid != candidate.size()) {
        return {ComparisonVerdict::InvalidCandidate, candInvalid,
                reference.size(), candidate.size(),
                static_cast<std::uint16_t>(candInvalid < reference.size() ? reference[candInvalid].caller : 0),
                candidate[candInvalid].caller};
    }

    const std::size_t limit = std::min(reference.size(), candidate.size());
    for (std::size_t i = 0; i < limit; ++i) {
        if (!equalRecord(reference[i], candidate[i])) {
            return {ComparisonVerdict::FirstDifference, i,
                    reference.size(), candidate.size(),
                    reference[i].caller, candidate[i].caller};
        }
    }
    if (reference.size() != candidate.size()) {
        return {ComparisonVerdict::CountDifference, limit,
                reference.size(), candidate.size(),
                static_cast<std::uint16_t>(limit < reference.size() ? reference[limit].caller : 0),
                static_cast<std::uint16_t>(limit < candidate.size() ? candidate[limit].caller : 0)};
    }
    return {seal.fullyAttested()
                ? ComparisonVerdict::EqualAttested
                : ComparisonVerdict::EqualUnsealed,
            reference.size(), reference.size(), candidate.size(), 0, 0};
}

}  // namespace n3d::re::v030
