#include "re/N3DV042Oct18Closures.hpp"
#include <cassert>
using namespace n3d::re::v042;
int main(){
 assert(incomingDamageGateOrder(BuildFamily::Dos10To19)==DamageGateOrder::ProtectionBeforeCalculation);
 assert(incomingDamageGateOrder(BuildFamily::Dos20)==DamageGateOrder::CalculationBeforeProtection);
 assert(incomingDamageGateOrder(BuildFamily::Win16)==DamageGateOrder::CalculationBeforeProtection);
 assert(!hasDamageFeedbackTimer(BuildFamily::Dos10To19)); assert(hasDamageFeedbackTimer(BuildFamily::Dos20));
 assert(rngMaskForIncomingClass(0x08)==7); assert(rngMaskForIncomingClass(0x09)==15); assert(rngMaskForIncomingClass(0x14)==31);
 auto s=feedbackStep(3); assert(s.timerAfter==2&&s.selector==4&&s.active); s=feedbackStep(0); assert(s.timerAfter==-1&&s.selector==3&&s.active); assert(!feedbackStep(-1).active);
 auto c=secretSaveContract(17); assert(c.locallyWrittenBytes==17&&c.diskBytes==32&&c.undefinedTailBytes==15); assert(secretLoadStateWord(0xFE)==0x00FE);
 assert(saveLoadCallerTreatsIoAsSuccess(0)); assert(saveLoadCallerTreatsIoAsSuccess(31)); assert(!saveLoadCallerTreatsIoAsSuccess(-1));
 auto d=doorLoadLayout(BuildFamily::Dos20); assert(d.recordBytes==18&&d.runtimePrefixPreserved==8&&d.saveBytesAuthoritativeAfterLoad==10);
 auto w=doorLoadLayout(BuildFamily::Win16); assert(w.recordBytes==22&&w.runtimePrefixPreserved==12&&w.saveBytesAuthoritativeAfterLoad==10);
 auto a=winMode4Ack(2); assert(a.countAfter==1&&a.forcedPresent&&a.displayAnother&&!a.endMessageMode&&a.nextIndex==1);
 auto b=winMode4Ack(1); assert(b.countAfter==0&&b.endMessageMode&&!b.forcedPresent);
 auto e=winMode4Ack(0); assert(e.countAfter==-1&&e.endMessageMode);
 static_assert(kDosDynamicWall.capacity==64&&kDosDynamicWall.stride==18);
 static_assert(kDosClass3Geometry.capacity==32&&kDosClass3Geometry.stride==14);
 static_assert(kWinDynamicWall.capacity==64&&kWinDynamicWall.stride==22);
 static_assert(kWinClass3Geometry.capacity==32&&kWinClass3Geometry.stride==22);
 static_assert(kReclassifiedWriterSites==62&&kDirectObjectPointerCallEdgesTotal==72);
 static_assert(kWin16TimingImportOrdinals[0].ordinal==604&&kWin16TimingImportOrdinals[4].ordinal==13);
 return 0;
}
