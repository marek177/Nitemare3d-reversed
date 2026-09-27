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

    constexpr bool internallyConsistent() const {
        return discoveredDefinitions ==
               strongOrExactMatches + weakOrManualReview;
    }

    constexpr double matchRatio() const {
        return discoveredDefinitions == 0
            ? 0.0
            : static_cast<double>(strongOrExactMatches) /
              static_cast<double>(discoveredDefinitions);
    }
};

inline constexpr FunctionCoverage kDosCoverage{
    Platform::Dos,
    "2.0",
    519,
    429,
    90
};

inline constexpr FunctionCoverage kWin16Coverage{
    Platform::Win16,
    "1.10",
    967,
    929,
    38
};

inline constexpr std::uint32_t kTotalFunctionDefinitions =
    kDosCoverage.discoveredDefinitions + kWin16Coverage.discoveredDefinitions;

inline constexpr std::uint32_t kTotalStrongOrExactMatches =
    kDosCoverage.strongOrExactMatches + kWin16Coverage.strongOrExactMatches;

inline constexpr std::uint32_t kTotalWeakOrManualReview =
    kDosCoverage.weakOrManualReview + kWin16Coverage.weakOrManualReview;

struct CoverageMeaning {
    std::string_view label;
    std::string_view meaning;
};

inline constexpr std::array<CoverageMeaning, 3> kCoverageMeaning = {{
    {"discoveredDefinitions",
     "Function definitions present in the audited decompiler/export set."},
    {"strongOrExactMatches",
     "Function identity supported by exact or strong fuzzy cross-version matching."},
    {"weakOrManualReview",
     "Definitions requiring weak-match, split/merge, thunk or manual boundary review."}
}};

inline constexpr std::string_view kImportantWarning =
    "Cross-version matching measures support for function identity, not semantic understanding.";

} // namespace n3d::re::v016
