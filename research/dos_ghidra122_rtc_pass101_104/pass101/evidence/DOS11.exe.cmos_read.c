
undefined1 __cdecl16far FUN_1b9f_0042(int param_1)

{
  undefined1 uVar1;
  byte in_CF;
  byte in_PF;
  byte in_AF;
  byte in_ZF;
  byte in_SF;
  byte in_TF;
  byte in_IF;
  byte in_OF;
  byte in_NT;
  
  if (param_1 < 10) {
    FUN_1b9f_0033((uint)(in_NT & 1) * 0x4000 | (uint)(in_OF & 1) * 0x800 | (uint)(in_IF & 1) * 0x200
                  | (uint)(in_TF & 1) * 0x100 | (uint)(in_SF & 1) * 0x80 | (uint)(in_ZF & 1) * 0x40
                  | (uint)(in_AF & 1) * 0x10 | (uint)(in_PF & 1) * 4 | (uint)(in_CF & 1));
  }
  out(0x70,(char)param_1);
  uVar1 = in(0x71);
  return uVar1;
}

