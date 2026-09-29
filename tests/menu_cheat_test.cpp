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
    assert(s.pentagramMask == 0x0F);
    assert(s.specialUseCharges == 99);

    auto ammo = static_cast<std::uint8_t>(37);
    assert(full.consumeWeaponResource(ammo));
    assert(ammo == 37);
    full.applyPlayerDamage(s, 90);
    assert(s.health == 100);

    // CONFIG.SAV cheat bytes are the final four bytes of the exact 20-byte block.
    static_assert(kConfigSaveSize == 20);
    static_assert(kConfigOmniscientOffset == 0x10);
    static_assert(kConfigOmnipotentOffset == 0x11);
    static_assert(kConfigOmnifariousOffset == 0x12);
    static_assert(kConfigOmnificentOffset == 0x13);

    // Omnificent does not globally freeze AI. It suppresses autonomous
    // acquisition in the passive states only.
    assert(full.omnificentEnabled());
    assert(full.suppressesAutonomousGuardAcquisition(0x07, 0x00));
    assert(full.suppressesAutonomousGuardAcquisition(0x08, 0x02));
    assert(!full.suppressesAutonomousGuardAcquisition(0x08, 0x03));
    assert(!full.suppressesAutonomousGuardAcquisition(0x02, 0x00));

    // Accepted player fire uses a separate one-shot selector wake gate.
    AcceptedFireWakeProbe wake{};
    wake.playerSelector = 7;
    wake.guardSelector = 7;
    wake.guardStrategy = 0;
    wake.guardState = 7;
    assert(acceptedFireWakesGuard(wake));
    wake.guardState = 8;
    assert(acceptedFireWakesGuard(wake));
    wake.guardState = 6;
    assert(!acceptedFireWakesGuard(wake));
    wake.guardState = 7;
    wake.guardStrategy = 3;
    assert(!acceptedFireWakesGuard(wake));
    wake.guardStrategy = 0;
    wake.guardSelector = 8;
    assert(!acceptedFireWakesGuard(wake));
    wake.guardSelector = 7;
    wake.playerSelector = 0;
    assert(!acceptedFireWakesGuard(wake));
    wake.playerSelector = 7;
    wake.selectorAlreadyWoken = true;
    assert(!acceptedFireWakesGuard(wake));
    assert(acceptedFireWakeDelay(0) == 0);
    assert(acceptedFireWakeDelay(7) == 7);
    assert(acceptedFireWakeDelay(8) == 0);

    // Firing/waking does not clear the global cheat flag; state 1 itself is
    // outside the acquisition-suppression gate and can progress to state 2.
    assert(full.omnificentEnabled());
    assert(!full.suppressesAutonomousGuardAcquisition(kGuardWakeCountdownState, 0));

    const auto& pages = instructionPages();
    assert(pages.size() == 22);
    assert(pages.front().page == 1 && pages.back().page == 22);

    std::cout << "menu_cheat_test: OK\n";
    return 0;
}
