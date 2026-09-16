#include "ui/InstructionsData.hpp"

namespace n3d {

const std::vector<InstructionPage>& instructionPages() {
    // The original 22-page in-game instruction text is used locally as
    // reverse-engineering evidence but is intentionally not redistributed in
    // this public repository. Keep page slots stable so menu/navigation code
    // and tests can exercise the reconstructed 22-page flow.
    static const std::vector<InstructionPage> pages{
        {1, "Quick Help", "[Original game instruction text intentionally not redistributed.]"},
        {2, "Contents", "[Original game instruction text intentionally not redistributed.]"},
        {3, "Credits", "[Original game instruction text intentionally not redistributed.]"},
        {4, "Story — Episode 1", "[Original game instruction text intentionally not redistributed.]"},
        {5, "Story — Episode 1 continued", "[Original game instruction text intentionally not redistributed.]"},
        {6, "Story — Episode 2", "[Original game instruction text intentionally not redistributed.]"},
        {7, "Story — Episode 3", "[Original game instruction text intentionally not redistributed.]"},
        {8, "How to Play", "[Original game instruction text intentionally not redistributed.]"},
        {9, "Controls 1/4", "[Original game instruction text intentionally not redistributed.]"},
        {10, "Controls 2/4", "[Original game instruction text intentionally not redistributed.]"},
        {11, "Controls 3/4", "[Original game instruction text intentionally not redistributed.]"},
        {12, "Controls 4/4", "[Original game instruction text intentionally not redistributed.]"},
        {13, "Secret Panels", "[Original game instruction text intentionally not redistributed.]"},
        {14, "Collectibles 1/4", "[Original game instruction text intentionally not redistributed.]"},
        {15, "Collectibles 2/4", "[Original game instruction text intentionally not redistributed.]"},
        {16, "Collectibles 3/4", "[Original game instruction text intentionally not redistributed.]"},
        {17, "Collectibles 4/4", "[Original game instruction text intentionally not redistributed.]"},
        {18, "Auto Mapping 1/2", "[Original game instruction text intentionally not redistributed.]"},
        {19, "Auto Mapping 2/2", "[Original game instruction text intentionally not redistributed.]"},
        {20, "Saving and Restoring", "[Original game instruction text intentionally not redistributed.]"},
        {21, "Status Report", "[Original game instruction text intentionally not redistributed.]"},
        {22, "Conclusion", "[Original game instruction text intentionally not redistributed.]"},
    };
    return pages;
}

} // namespace n3d
