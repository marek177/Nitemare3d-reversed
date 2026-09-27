#pragma once

#include <array>
#include <cstdint>
#include <string_view>

namespace n3d::re::v014 {

enum class Evidence : std::uint8_t {
    VerifiedExe,
    VerifiedData,
    VerifiedSaveLayout,
    Behavioral,
    Inferred,
    Partial,
    Todo
};

enum class Platform : std::uint8_t {
    Dos,
    Win16
};

enum class AnalysisPass : std::uint16_t {
    FunctionBoundary       = 1u << 0,
    ControlFlowGraph       = 1u << 1,
    SsaValueFlow           = 1u << 2,
    DataFlowGraph          = 1u << 3,
    UseDefChains           = 1u << 4,
    Liveness               = 1u << 5,
    AliasAnalysis          = 1u << 6,
    CyclomaticComplexity   = 1u << 7,
    Dominators             = 1u << 8,
    NaturalLoops           = 1u << 9,
    InterproceduralCalls   = 1u << 10,
    SideEffects            = 1u << 11,
    CrossVersionMatch      = 1u << 12,
    SemanticReconstruction = 1u << 13
};

constexpr std::uint16_t bit(AnalysisPass pass) {
    return static_cast<std::uint16_t>(pass);
}

constexpr std::uint16_t kDeepStaticMask =
    bit(AnalysisPass::FunctionBoundary) |
    bit(AnalysisPass::ControlFlowGraph) |
    bit(AnalysisPass::SsaValueFlow) |
    bit(AnalysisPass::DataFlowGraph) |
    bit(AnalysisPass::UseDefChains) |
    bit(AnalysisPass::Liveness) |
    bit(AnalysisPass::AliasAnalysis) |
    bit(AnalysisPass::CyclomaticComplexity) |
    bit(AnalysisPass::Dominators) |
    bit(AnalysisPass::NaturalLoops) |
    bit(AnalysisPass::InterproceduralCalls) |
    bit(AnalysisPass::SideEffects) |
    bit(AnalysisPass::CrossVersionMatch) |
    bit(AnalysisPass::SemanticReconstruction);

struct FunctionAnalysisRecord {
    Platform platform{};
    std::string_view version{};
    std::string_view function{};
    std::uint16_t completedPasses{};
    Evidence evidence{Evidence::Todo};
    std::string_view note{};

    constexpr bool has(AnalysisPass pass) const {
        return (completedPasses & bit(pass)) != 0;
    }

    constexpr bool deepStaticComplete() const {
        return (completedPasses & kDeepStaticMask) == kDeepStaticMask;
    }
};

inline constexpr std::array<std::string_view, 14> kPassNames = {
    "function-boundary",
    "cfg",
    "ssa-value-flow",
    "dfg",
    "use-def",
    "liveness",
    "alias-analysis",
    "cyclomatic-complexity",
    "dominators",
    "natural-loops",
    "interprocedural-call-graph",
    "side-effects",
    "cross-version-match",
    "semantic-reconstruction"
};

inline constexpr std::array<std::string_view, 7> kEvidenceNames = {
    "VERIFIED_EXE",
    "VERIFIED_DATA",
    "VERIFIED_SAVE_LAYOUT",
    "BEHAVIORAL",
    "INFERRED",
    "PARTIAL",
    "TODO"
};

} // namespace n3d::re::v014
