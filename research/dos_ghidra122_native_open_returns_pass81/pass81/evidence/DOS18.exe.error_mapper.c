
void __cdecl16near FUN_21ea_05ce(void)

{
  char cVar1;
  uint in_AX;
  
  DAT_376d_2124._0_1_ = (byte)in_AX;
  cVar1 = (char)(in_AX >> 8);
  if (cVar1 != '\0') goto LAB_21ea_05f2;
  if (DAT_376d_211f < 3) {
LAB_21ea_05e8:
    if (0x13 < (byte)DAT_376d_2124) {
LAB_21ea_05ec:
      in_AX = 0x13;
    }
  }
  else {
    if (0x21 < (byte)DAT_376d_2124) goto LAB_21ea_05ec;
    if ((byte)DAT_376d_2124 < 0x20) goto LAB_21ea_05e8;
    in_AX = 5;
  }
  cVar1 = *(char *)(ulong)((in_AX & 0xff) + 0x215e);
LAB_21ea_05f2:
  DAT_376d_2116 = (int)cVar1;
  return;
}

