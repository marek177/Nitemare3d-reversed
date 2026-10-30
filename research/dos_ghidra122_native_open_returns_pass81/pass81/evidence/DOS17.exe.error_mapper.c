
void __cdecl16near FUN_21d1_05ca(void)

{
  char cVar1;
  uint in_AX;
  
  DAT_3754_20ea._0_1_ = (byte)in_AX;
  cVar1 = (char)(in_AX >> 8);
  if (cVar1 != '\0') goto LAB_21d1_05ee;
  if (DAT_3754_20e5 < 3) {
LAB_21d1_05e4:
    if (0x13 < (byte)DAT_3754_20ea) {
LAB_21d1_05e8:
      in_AX = 0x13;
    }
  }
  else {
    if (0x21 < (byte)DAT_3754_20ea) goto LAB_21d1_05e8;
    if ((byte)DAT_3754_20ea < 0x20) goto LAB_21d1_05e4;
    in_AX = 5;
  }
  cVar1 = *(char *)(ulong)((in_AX & 0xff) + 0x2124);
LAB_21d1_05ee:
  DAT_3754_20dc = (int)cVar1;
  return;
}

