#pragma once

#include <array>
#include <cstdint>
#include <string_view>

namespace n3d::re::v016 {

enum class Platform : std::uint8_t {
    Dos,
    Win16
};

enum class ReviewState : std::uint8_t {
    StrongOrExactMatch,
    WeakOrManualReview
};

struct FunctionCoverage {
    Platform platform{};
    std::string_view primaryVersion{};
    std::uint32_t discoveredDefinitions{};
    std::uint32_t strongOrExactMatches{};
    std::uint32_t weakOrManualReview{};
    std::uint32_t manuallyReviewedWeak{};

    constexpr bool internallyConsistent() const {
        return discoveredDefinitions ==
                   strongOrExactMatches + weakOrManualReview &&
               manuallyReviewedWeak <= weakOrManualReview;
    }

    constexpr std::uint32_t pendingManualReview() const {
        return weakOrManualReview - manuallyReviewedWeak;
    }

    constexpr std::uint32_t reviewedIdentityCount() const {
        return strongOrExactMatches + manuallyReviewedWeak;
    }

    constexpr double matchRatio() const {
        return discoveredDefinitions == 0
            ? 0.0
            : static_cast<double>(strongOrExactMatches) /
              static_cast<double>(discoveredDefinitions);
    }

    constexpr double identityReviewRatio() const {
        return discoveredDefinitions == 0
            ? 0.0
            : static_cast<double>(reviewedIdentityCount()) /
              static_cast<double>(discoveredDefinitions);
    }
};

inline constexpr FunctionCoverage kDosCoverage{
    Platform::Dos,
    "2.0",
    519,
    429,
    90,
    0
};

inline constexpr FunctionCoverage kWin16Coverage{
    Platform::Win16,
    "1.10",
    967,
    929,
    38,
    38
};

inline constexpr std::uint32_t kTotalFunctionDefinitions =
    kDosCoverage.discoveredDefinitions + kWin16Coverage.discoveredDefinitions;

inline constexpr std::uint32_t kTotalStrongOrExactMatches =
    kDosCoverage.strongOrExactMatches + kWin16Coverage.strongOrExactMatches;

inline constexpr std::uint32_t kTotalWeakOrManualReview =
    kDosCoverage.weakOrManualReview + kWin16Coverage.weakOrManualReview;

inline constexpr std::uint32_t kTotalManuallyReviewedWeak =
    kDosCoverage.manuallyReviewedWeak + kWin16Coverage.manuallyReviewedWeak;

inline constexpr std::uint32_t kTotalPendingManualReview =
    kDosCoverage.pendingManualReview() + kWin16Coverage.pendingManualReview();

struct CoverageMeaning {
    std::string_view label;
    std::string_view meaning;
};

inline constexpr std::array<CoverageMeaning, 5> kCoverageMeaning = {{
    {"discoveredDefinitions",
     "Function definitions present in the audited decompiler/export set."},
    {"strongOrExactMatches",
     "Function identity supported by exact or strong fuzzy cross-version matching."},
    {"weakOrManualReview",
     "Definitions that automatic matching left for weak-match, split/merge, thunk or manual review."},
    {"manuallyReviewedWeak",
     "Automatic weak/manual-review definitions whose function identity was subsequently reviewed by body/API/data/caller evidence."},
    {"identityReviewRatio",
     "Strong/exact automatic identities plus completed manual identity reviews, divided by discovered definitions."}
}};

inline constexpr std::string_view kImportantWarning =
    "Automatic cross-version matching, completed identity review, and full semantic understanding are different metrics. "
    "Win16 1.10 has 929/967 automatic strong/exact matches and 38/38 weak definitions manually identity-reviewed; "
    "that closes identity review to 967/967 without claiming every function is semantically reconstructed 1:1.";

} // namespace n3d::re::v016
