#include "re/N3DV014Analysis.hpp"

#include <cassert>

int main() {
    using namespace n3d::re::v014;

    static_assert(kPassNames.size() == 14);
    static_assert(kEvidenceNames.size() == 7);
    static_assert(bit(AnalysisPass::ControlFlowGraph) != 0);
    static_assert((kDeepStaticMask & bit(AnalysisPass::InterproceduralCalls)) != 0);

    constexpr FunctionAnalysisRecord partial{
        Platform::Win16,
        "1.8",
        "example_function",
        static_cast<std::uint16_t>(
            bit(AnalysisPass::FunctionBoundary) |
            bit(AnalysisPass::ControlFlowGraph) |
            bit(AnalysisPass::DataFlowGraph)),
        Evidence::Partial,
        "Example record: semantics not yet complete."
    };

    static_assert(partial.has(AnalysisPass::FunctionBoundary));
    static_assert(partial.has(AnalysisPass::ControlFlowGraph));
    static_assert(!partial.has(AnalysisPass::AliasAnalysis));
    static_assert(!partial.deepStaticComplete());

    constexpr FunctionAnalysisRecord complete{
        Platform::Dos,
        "2.0",
        "example_complete_function",
        kDeepStaticMask,
        Evidence::VerifiedExe,
        "Schema regression fixture."
    };

    static_assert(complete.deepStaticComplete());
    assert(complete.evidence == Evidence::VerifiedExe);
    return 0;
}
