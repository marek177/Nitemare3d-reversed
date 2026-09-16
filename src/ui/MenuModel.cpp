#include "ui/MenuModel.hpp"

namespace n3d {

std::vector<MenuEntry> MenuModel::mainMenu(bool gameActive) {
    if (gameActive) {
        return {
            {"New game", MenuAction::NewGame},
            {"Configure game...", MenuAction::ConfigureGame},
            {"Load game...", MenuAction::LoadGame},
            {"Save game...", MenuAction::SaveGame},
            {"Instructions", MenuAction::Instructions},
            {"Return to game", MenuAction::ReturnToGame},
            {"Quit", MenuAction::Quit},
        };
    }
    return {
        {"New game", MenuAction::NewGame},
        {"Configure game...", MenuAction::ConfigureGame},
        {"Load game...", MenuAction::LoadGame},
        {"Instructions", MenuAction::Instructions},
        {"Demo", MenuAction::Demo},
        {"Quit", MenuAction::Quit},
    };
}

std::vector<MenuEntry> MenuModel::configMenu() {
    return {
        {"Hardware...", MenuAction::Hardware},
        {"Cheats...", MenuAction::Cheats},
        {"Done", MenuAction::Done},
    };
}

std::vector<MenuEntry> MenuModel::episodeMenu(GameEdition edition) {
    std::vector<MenuEntry> out{{"Episode 1", MenuAction::Episode1}};
    if (hasCompleteTrilogy(edition)) {
        out.push_back({"Episode 2", MenuAction::Episode2});
        out.push_back({"Episode 3", MenuAction::Episode3});
    }
    return out;
}

std::vector<MenuEntry> MenuModel::difficultyMenu() {
    return {
        {"Be gentle!", MenuAction::DifficultyGentle},
        {"I'm tough!", MenuAction::DifficultyTough},
        {"Let's party!", MenuAction::DifficultyParty},
    };
}

} // namespace n3d
