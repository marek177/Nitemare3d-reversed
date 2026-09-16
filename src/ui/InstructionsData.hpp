#pragma once

#include <string_view>
#include <vector>

namespace n3d {

struct InstructionPage {
    int page{};
    std::string_view title;
    std::string_view body;
};

const std::vector<InstructionPage>& instructionPages();

} // namespace n3d
