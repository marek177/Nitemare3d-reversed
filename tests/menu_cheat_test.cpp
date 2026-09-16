#include "game/CheatSystem.hpp"
#include "ui/InstructionsData.hpp"
#include "ui/MenuModel.hpp"

#include <cassert>
#include <iostream>

int main() {
    using namespace n3d;

    const auto inactive = MenuModel::mainMenu(false);
    const auto active = MenuModel::mainMenu(true);
    assert(inactive.size() == 6);
    assert(active.size() == 7);
    assert(inactive[4].label == "Demo");
    assert(active[3].label == "Save game...");
    assert(active[5].label == "Return to game");

    const auto demoEpisodes = MenuModel::episodeMenu(GameEdition::Episode1Demo);
    const auto fullEpisodes = MenuModel::episodeMenu(GameEdition::CompleteTrilogy);
    assert(demoEpisodes.size() == 1);
    assert(fullEpisodes.size() == 3);

    CheatSystem demo(GameEdition::Episode1Demo);
    assert(!demo.menuAvailable());
    assert(!demo.set(CheatMode::Omnipotent, true));
    assert(!demo.enabled(CheatMode::Omnipotent));

    CheatSystem full(GameEdition::CompleteTrilogy);
    assert(full.menuAvailable());
    assert(full.set(CheatMode::Omniscient, true));
    assert(full.set(CheatMode::Omnipotent, true));
    assert(full.set(CheatMode::Omnificent, true));
    assert(full.set(CheatMode::Omnifarious, true));

    CheatAffectedState s{};
    full.applyLevelStart(s);
    assert(s.health == 100);
    assert(s.magicEyePower == 100 && s.crystalBallPower == 100);
    assert(s.weaponMask == 0x0F);
    assert(s.keyMask == 0x0F);
    assert(s.idCardMask == 0x03);

    auto ammo = static_cast<std::uint8_t>(37);
    assert(full.consumeWeaponResource(ammo));
    assert(ammo == 37);
    full.applyPlayerDamage(s, 90);
    assert(s.health == 100);
    assert(full.enemiesIgnorePlayer());

    const auto& pages = instructionPages();
    assert(pages.size() == 22);
    assert(pages.front().page == 1 && pages.back().page == 22);

    std::cout << "menu_cheat_test: OK\n";
    return 0;
}
