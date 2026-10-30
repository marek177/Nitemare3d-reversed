
void __cdecl16far FUN_1277_0bc2(void)

{
  DAT_376d_4544 = (int)DAT_376d_4144 >> 1;
  DAT_376d_4546 =
       (int)(CONCAT12((-(uint)(0x140 < DAT_376d_4144) - ((int)DAT_376d_4144 >> 0xf) & 1) != 0,
                      0x140 - DAT_376d_4144) >> 1);
  DAT_376d_4542 = DAT_376d_4144;
  DAT_376d_4548 = DAT_376d_4546 + DAT_376d_4144 + -1;
  DAT_376d_454a = DAT_376d_4546 >> 1;
  DAT_376d_454c = DAT_376d_454a + DAT_376d_4544 + -1;
  DAT_376d_454e = DAT_376d_4546 + DAT_376d_4544;
  DAT_376d_4550 = DAT_376d_454a + ((int)DAT_376d_4144 >> 2);
  DAT_376d_4552 = DAT_376d_4550 * 0x10;
  FUN_1c79_0008();
  FUN_1156_0030();
  return;
}

