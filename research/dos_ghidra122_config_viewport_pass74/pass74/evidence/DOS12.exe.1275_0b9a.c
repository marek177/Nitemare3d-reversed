
void __cdecl16far FUN_1275_0b9a(void)

{
  DAT_339b_44a2 = (int)DAT_339b_40a2 >> 1;
  DAT_339b_44a4 =
       (int)(CONCAT12((-(uint)(0x140 < DAT_339b_40a2) - ((int)DAT_339b_40a2 >> 0xf) & 1) != 0,
                      0x140 - DAT_339b_40a2) >> 1);
  DAT_339b_44a0 = DAT_339b_40a2;
  DAT_339b_44a6 = DAT_339b_44a4 + DAT_339b_40a2 + -1;
  DAT_339b_44a8 = DAT_339b_44a4 >> 1;
  DAT_339b_44aa = DAT_339b_44a8 + DAT_339b_44a2 + -1;
  DAT_339b_44ac = DAT_339b_44a4 + DAT_339b_44a2;
  DAT_339b_44ae = DAT_339b_44a8 + ((int)DAT_339b_40a2 >> 2);
  DAT_339b_44b0 = DAT_339b_44ae * 0x10;
  FUN_1c54_000a();
  FUN_1155_0032();
  return;
}

