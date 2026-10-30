#include "re/X86OperandSizeSemantics.hpp"

using namespace n3d::re::x86;

static_assert(cbw(0x80) == 0xff80);
static_assert(cwd_pair(0x8000) == 0xffff8000u);
static_assert(cwde(0x8000) == 0xffff8000u);
static_assert(cdq_high(0x80000000u) == 0xffffffffu);
static_assert(decode_99(OperandSize::bits16) == SignExtendInstruction::CWD);
static_assert(decode_99(OperandSize::bits32) == SignExtendInstruction::CDQ);

int main() { return 0; }
