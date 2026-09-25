#include "n3d_re.hpp"

namespace n3d::re {

uint16_t N3dRng::next() {
    state_ = state_ * 0x343FDu + 0x269EC3u;
    return static_cast<uint16_t>((state_ >> 16) & 0x7FFFu);
}

int16_t scoreForClass(uint8_t c) {
    switch(c) {
        case 8: case 26: return 25;
        case 9: return 75;
        case 10: case 32: return 50;
        case 11: case 15: case 16: case 23: case 27: case 28: return 100;
        case 12: case 29: case 30: return 250;
        case 13: case 18: case 19: return 150;
        case 14: case 20: case 24: case 31: return 200;
        case 17: case 25: return 0;
        case 21: return -1000;
        case 22: return 1000;
        default: return 0;
    }
}

static int asr(int v,unsigned s){ return v >> s; }

DamageResult computeDamage(const DamageInput& in) {
    DamageResult out{};
    out.rawSeed = 8 * static_cast<int>(static_cast<int16_t>(in.projectedBaseRow - in.viewportCenterY)) + (in.rngValue % 25);
    int d = out.rawSeed;
    switch(in.objectClass) {
        case 12: case 29: d=asr(d,3); break;
        case 13: d=(in.weaponSelector==1||in.weaponSelector==2)?asr(d,1):asr(d,3); break;
        case 14: case 17: case 20: d=(in.weaponSelector==2)?asr(d,1):asr(d,3); break;
        case 15: case 16: d=(in.weaponSelector==1)?0:asr(d,1); break;
        case 18: case 19: d=(in.weaponSelector==1)?0:asr(d,2); break;
        case 21: d=0; break; // unidentified helper runs first in original
        case 22: d=(in.episode==3)?3:0; break;
        case 23: d=(in.weaponSelector==1)?asr(d,8):asr(d,2); break;
        case 24:
            if(in.weaponSelector==1) d=asr(d,8);
            else if(in.weaponSelector==2) d=asr(d,4);
            else d=asr(d,3);
            break;
        case 25: d=0; break;
        case 26: d=(in.weaponSelector==1)?asr(d,1):0; break;
        case 27: case 28: d=asr(d,1); break;
        case 30: d=(in.weaponSelector==1)?0:asr(d,3); break;
        case 31: d=(in.weaponSelector==1)?0:asr(d,2); break;
        default: break;
    }
    out.transformed=d;
    if(in.difficulty==2) d/=2;
    else if(in.difficulty==0) d*=2;
    if(d>255) d=255; // lower clamp not confirmed
    out.afterDifficulty=d;
    out.storedByte=static_cast<uint8_t>(d&0xFF);
    out.confidence=Evidence::Confirmed;
    return out;
}

std::optional<uint8_t> fireDamagePerSlowUpdate(uint8_t id) {
    switch(id){ case 0x3B:return 100; case 0x3C:return 10; case 0x3D:return 2; default:return std::nullopt; }
}
std::array<int8_t,8> guardMoveX(){ return {0,8,8,0,0,-8,-8,0}; }
std::array<int8_t,8> guardMoveY(){ return {-8,0,0,8,8,0,0,-8}; }

GuardTickResult tickGuardCore(GuardState s,int16_t timer,GuardState nextState,GuardStrategy strategy,const GuardTickInput& in) {
    GuardTickResult r{s,timer};
    switch(s) {
        case GuardState::AnimateLoop: --r.timer; if(r.timer<1) r.state=nextState; break;
        case GuardState::Delay: { auto old=r.timer; --r.timer; if(old==0) r.state=GuardState::Wake; break; }
        case GuardState::Wake: r.state=GuardState::Acquire; r.unresolvedSideEffect=true; break;
        case GuardState::Acquire: r.state=in.perception7594?GuardState::Attack:GuardState::Plan; r.unresolvedSideEffect=true; break;
        case GuardState::Attack:
            if(in.perception7594) r.shouldAttackPlayer=true;
            if(!in.globalGameStateIs2) r.state=GuardState::Plan;
            r.unresolvedSideEffect=true; break;
        case GuardState::Plan: r.needsStrategyPlan=true; r.state=GuardState::Move; break;
        case GuardState::Move: --r.timer; if(r.timer==0) r.state=GuardState::Acquire; r.shouldRefreshDirectionSequence=true; break;
        case GuardState::WaitForLos:
            r.shouldRefreshDirectionSequence=true;
            if(!in.globalBlock4BE7 && in.los) r.state=(strategy==GuardStrategy::SpecialWall)?GuardState::Strategy3:GuardState::Wake;
            break;
        case GuardState::Directional0C: case GuardState::Directional0D: r.shouldRefreshDirectionSequence=true; break;
        case GuardState::CannonIdle:
            r.shouldRefreshDirectionSequence=true;
            if(in.cannonGate51A5){r.timer=0;r.state=GuardState::CannonCycle;} break;
        case GuardState::CannonCycle: {
            r.shouldRefreshDirectionSequence=true;
            if(!in.cannonGate51A5) r.state=GuardState::CannonIdle;
            else { auto old=r.timer; --r.timer; if(old==0){r.state=GuardState::CannonAttack;r.unresolvedSideEffect=true;} }
            break;
        }
        case GuardState::CannonAttack: {
            r.shouldRefreshDirectionSequence=true; auto old=r.timer; --r.timer;
            if(old==0){ if(in.perception7594) r.shouldAttackPlayer=true; r.timer=8; r.state=GuardState::CannonCycle; }
            break;
        }
        case GuardState::RecoverMove: --r.timer; if(r.timer==0){r.state=GuardState::WaitForLos;r.unresolvedSideEffect=true;} break;
        case GuardState::GlobalTimed: if(r.timer<1) r.unresolvedSideEffect=true; else --r.timer; break;
        default: r.unresolvedSideEffect=true; break;
    }
    return r;
}

int32_t inferredLevelCompletionBonus(uint16_t e,uint16_t p){
    int32_t b=0; if(e==0)b+=5000; if(p==0)b+=5000; return b;
}

GuardCategory categoryForGuard(uint8_t g){
    switch(g){
        case 5:return GuardCategory::PuzzleActor;
        case 10:return GuardCategory::BossOrScripted;
        case 11: case 12:return GuardCategory::WallEnemy;
        case 14:return GuardCategory::NPC;
        case 15:return GuardCategory::BossOrScripted;
        case 18:return GuardCategory::Hazard;
        case 26:return GuardCategory::PuzzleActor;
        default:
            if((g>=1&&g<=9)||(g>=16&&g<=24)) return GuardCategory::Combat;
            return GuardCategory::Unknown;
    }
}

} // namespace n3d::re
