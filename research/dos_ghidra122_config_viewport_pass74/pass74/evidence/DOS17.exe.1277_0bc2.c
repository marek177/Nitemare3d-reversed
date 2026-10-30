
void __cdecl16far FUN_1277_0bc2(void)

{
  DAT_3754_44b4 = (int)DAT_3754_40b4 >> 1;
  DAT_3754_44b6 =
       (int)(CONCAT12((-(uint)(0x140 < DAT_3754_40b4) - ((int)DAT_3754_40b4 >> 0xf) & 1) != 0,
                      0x140 - DAT_3754_40b4) >> 1);
  DAT_3754_44b2 = DAT_3754_40b4;
  DAT_3754_44b8 = DAT_3754_44b6 + DAT_3754_40b4 + -1;
  DAT_3754_44ba = DAT_3754_44b6 >> 1;
  DAT_3754_44bc = DAT_3754_44ba + DAT_3754_44b4 + -1;
  DAT_3754_44be = DAT_3754_44b6 + DAT_3754_44b4;
  DAT_3754_44c0 = DAT_3754_44ba + ((int)DAT_3754_40b4 >> 2);
  DAT_3754_44c2 = DAT_3754_44c0 * 0x10;
  FUN_1c63_0004();
  FUN_1156_0030();
  return;
}

