#pragma once

#include "game/GameEdition.hpp"

#include <string_view>
#include <vector>

namespace n3d {

enum class MenuAction {
    NewGame,
    ConfigureGame,
    LoadGame,
    SaveGame,
    Instructions,
    Demo,
    ReturnToGame,
    Quit,
    Hardware,
    Cheats,
    Done,
    Cancel,
    Episode1,
    Episode2,
    Episode3,
    DifficultyGentle,
    DifficultyTough,
    DifficultyParty,
};

struct MenuEntry {
    std::string_view label;
    MenuAction action;
    bool enabled{true};
};

class MenuModel {
public:
    static std::vector<MenuEntry> mainMenu(bool gameActive);
    static std::vector<MenuEntry> configMenu();
    static std::vector<MenuEntry> episodeMenu(GameEdition edition);
    static std::vector<MenuEntry> difficultyMenu();
    static bool cheatsCommandVisible(GameEdition) { return true; }
};

} // namespace n3d
