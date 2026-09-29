#include "game/GuardSystem.hpp"

#include <cassert>
#include <cstddef>

int main() {
    using namespace nitemare3d::game;

    static_assert(sizeof(GuardRuntimeRecord) == 26);
    static_assert(kGuardCapacity == 100);
    static_assert(kGuardSaveSize == 2600);
    static_assert(offsetof(GuardRuntimeRecord, stateTimer) == 0x06);
    static_assert(offsetof(GuardRuntimeRecord, objectSlot) == 0x08);
    static_assert(offsetof(GuardRuntimeRecord, strategy) == 0x0A);
    static_assert(offsetof(GuardRuntimeRecord, state) == 0x0B);
    static_assert(offsetof(GuardRuntimeRecord, nextState) == 0x0C);
    static_assert(offsetof(GuardRuntimeRecord, strength) == 0x10);
    static_assert(offsetof(GuardRuntimeRecord, octant) == 0x11);
    static_assert(offsetof(GuardRuntimeRecord, resultOctant) == 0x12);
    static_assert(kFreshGuardStrength == 0xFF);
    static_assert(kGuardStateCount == 22);
    static_assert(static_cast<unsigned>(GuardState::PainReaction) == 0x15);
    static_assert(static_cast<unsigned>(GuardState::AlertSequence) == 0x02);
    static_assert(static_cast<unsigned>(GuardState::AttackOpportunityCheck) == 0x03);
    static_assert(static_cast<unsigned>(GuardState::AttackExecution) == 0x04);
    static_assert(static_cast<unsigned>(GuardState::MovementReplan) == 0x05);
    static_assert(static_cast<unsigned>(GuardState::TimedMovement) == 0x06);
    static_assert(static_cast<unsigned>(GuardState::StationaryAcquire) == 0x07);
    static_assert(static_cast<unsigned>(GuardState::MovingAcquire) == 0x08);

    static_assert(kGuardStrategyCount == 5);
    static_assert(isRecoveredGuardStrategy(0));
    static_assert(isRecoveredGuardStrategy(4));
    static_assert(!isRecoveredGuardStrategy(5));
    static_assert(static_cast<unsigned>(GuardStrategy::DefaultMovement) == 0);
    static_assert(static_cast<unsigned>(GuardStrategy::WoundedDoorSeek) == 1);
    static_assert(static_cast<unsigned>(GuardStrategy::RouteMarkerMovement) == 2);
    static_assert(static_cast<unsigned>(GuardStrategy::GargoyleOneShot) == 3);
    static_assert(static_cast<unsigned>(GuardStrategy::Cannon) == 4);
    static_assert(strategyUsesAlternateMoveSequence(2));
    static_assert(!strategyUsesAlternateMoveSequence(1));
    static_assert(strategySuppressesOrdinaryHitReaction(4));
    static_assert(strategyCanEnterTimedOneShotMove(3));
    static_assert(strategyForSpawnWallClass(0x43) == 1);
    static_assert(strategyForSpawnWallClass(0x42) == 2);
    static_assert(strategyForSpawnWallClass(0x46) == 2);
    static_assert(strategyForSpawnWallClass(0x41) == 0);
    static_assert(strategyOneExistsOnlyAsDormantMarkerInSuppliedMaps());

    // Original score switch anchors.
    assert(guardScoreForObjectClass(0x08) == 25);    // Bat
    assert(guardScoreForObjectClass(0x11) == 0);     // Dracula
    assert(guardScoreForObjectClass(0x15) == -1000); // Penelope
    assert(guardScoreForObjectClass(0x16) == 1000);  // Dr. Hamerstein
    assert(guardScoreForObjectClass(0x1B) == 100);   // Goldie
    assert(guardScoreForObjectClass(0x1C) == 100);   // Greenie
    assert(guardScoreForObjectClass(0x1D) == 250);   // Demon
    assert(guardScoreForObjectClass(0x20) == 50);    // GUARD25 executable-only fallback

    // The audited state 0x13 sound tick, movement attempts and blocked-step
    // timer behavior are represented separately.
    static_assert(kGuardStateLethalPlayerContact == 0x0B);
    static_assert(kGuardStateDormantUseMessage == 0x0C);
    static_assert(kGuardStateDormantSharedPose == 0x0D);
    static_assert(isRecoveredRetailDormantGuardState(0x0C));
    static_assert(isRecoveredRetailDormantGuardState(0x0D));
    static_assert(!isRecoveredRetailDormantGuardState(0x0B));
    static_assert(!isRecoveredRetailDormantGuardState(0x0E));
    static_assert(static_cast<unsigned>(GuardState::DormantUseMessage) == 0x0C);
    static_assert(static_cast<unsigned>(GuardState::DormantSharedPose) == 0x0D);
    static_assert(kGuardStateHandlerOffsets[0x0C] == kGuardStateHandlerOffsets[0x0D]);
    static_assert(kGuardStateStrategy3Movement == 0x13);
    static_assert(recoveredRetailProducedGuardStateCount() == 20);
    static_assert(guardStateHasRecoveredRetailProducer(0x00));
    static_assert(guardStateHasRecoveredRetailProducer(0x0A));
    static_assert(guardStateHasRecoveredRetailProducer(0x0B));
    static_assert(!guardStateHasRecoveredRetailProducer(0x0C));
    static_assert(!guardStateHasRecoveredRetailProducer(0x0D));
    static_assert(guardStateHasRecoveredRetailProducer(0x15));
    static_assert(isGuardTerminalState(0x0A));
    static_assert(isGuardTerminalState(0x0B));
    static_assert(!isGuardTerminalState(0x09));
    static_assert(kGuardStateReachability[0x0E] == GuardStateReachability::ClassSpecificRuntime);
    static_assert(kGuardStateReachability[0x14] == GuardStateReachability::ScriptedRuntime);
    static_assert(static_cast<unsigned>(GuardState::DeathFinalize) == 0x09);
    static_assert(static_cast<unsigned>(GuardState::DeadTerminal) == 0x0A);
    static_assert(static_cast<unsigned>(GuardState::DoorManeuver) == 0x11);
    static_assert(static_cast<unsigned>(GuardState::DeathWait) == 0x12);
    static_assert(static_cast<unsigned>(GuardState::RadioDanceScript) == 0x14);
    assert(guardState13InitialTimer(0) == 8);
    assert(guardState13InitialTimer(79) == 87);
    assert(guardState13InitialTimer(80) == 8);
    const auto wait = stepGuardState13(10, true);
    assert(wait.nextTimer == 9 && !wait.playMovementSound && !wait.attemptMovement);
    const auto sound = stepGuardState13(9, true);
    assert(sound.nextTimer == 8 && sound.playMovementSound && !sound.attemptMovement);
    const auto move = stepGuardState13(8, true);
    assert(move.nextTimer == 7 && move.attemptMovement && move.commitMovement);
    const auto blocked = stepGuardState13(8, false);
    assert(blocked.nextTimer == 7 && blocked.attemptMovement && !blocked.commitMovement);
    const auto lastAttempt = stepGuardState13(1, false);
    assert(lastAttempt.nextTimer == 0 && lastAttempt.attemptMovement && !lastAttempt.commitMovement);
    std::uint16_t timer = 8;
    int blockedMovementAttempts = 0;
    for (int i = 0; i < 8; ++i) {
        const auto step = stepGuardState13(timer, false);
        assert(step.attemptMovement && !step.commitMovement);
        timer = step.nextTimer;
        ++blockedMovementAttempts;
    }
    assert(blockedMovementAttempts == 8 && timer == 0);

    const auto finished = stepGuardState13(timer, true);
    assert(finished.clearStrategyAndEnterState2 && !finished.attemptMovement && finished.nextTimer == 0);

    // Shipped GUARD class reachability inventory.
    static_assert(guardClassPresence(0x08) == GuardClassPresence::RetailPlaced);
    static_assert(guardClassPresence(0x14) == GuardClassPresence::InternalTransformOnly);
    static_assert(guardClassPresence(0x20) == GuardClassPresence::ExecutableOnlyFallback);
    static_assert(guardClassPresence(0x21) == GuardClassPresence::RetailScripted);
    static_assert(guardClassPresence(0x22) == GuardClassPresence::NotGuard);
    static_assert(hasShippedRetailGuardPlacement(0x08));
    static_assert(!hasShippedRetailGuardPlacement(0x14));
    static_assert(!hasShippedRetailGuardPlacement(0x20));
    static_assert(hasShippedRetailGuardPlacement(0x21));
    static_assert(kGuard26DancersObjectIdEpisode1 == 0x8C);

    // Classes outside GUARD1..25 use the default score path.
    assert(guardScoreForObjectClass(0x07) == 0);
    assert(guardScoreForObjectClass(0x21) == 0); // GUARD26/Dancers default score path
}
