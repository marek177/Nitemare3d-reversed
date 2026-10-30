
void __cdecl16far FUN_1277_0bc2(void)

{
  DAT_374a_4472 = (int)(uint)DAT_374a_4072 >> 1;
  DAT_374a_4474 =
       (int)(CONCAT12((-(uint)(0x140 < (uint)DAT_374a_4072) - ((int)(uint)DAT_374a_4072 >> 0xf) & 1)
                      != 0,0x140 - (uint)DAT_374a_4072) >> 1);
  DAT_374a_4470 = (uint)DAT_374a_4072;
  DAT_374a_4476 = DAT_374a_4474 + (uint)DAT_374a_4072 + -1;
  DAT_374a_4478 = DAT_374a_4474 >> 1;
  DAT_374a_447a = DAT_374a_4478 + DAT_374a_4472 + -1;
  DAT_374a_447c = DAT_374a_4474 + DAT_374a_4472;
  DAT_374a_447e = DAT_374a_4478 + ((int)(uint)DAT_374a_4072 >> 2);
  DAT_374a_4480 = DAT_374a_447e * 0x10;
  FUN_1c59_0008();
  FUN_1156_0030();
  return;
}

