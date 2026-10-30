
void __cdecl16far FUN_1275_0b88(void)

{
  DAT_3395_44a2 = (int)DAT_3395_40a2 >> 1;
  DAT_3395_44a4 =
       (int)(CONCAT12((-(uint)(0x140 < DAT_3395_40a2) - ((int)DAT_3395_40a2 >> 0xf) & 1) != 0,
                      0x140 - DAT_3395_40a2) >> 1);
  DAT_3395_44a0 = DAT_3395_40a2;
  DAT_3395_44a6 = DAT_3395_44a4 + DAT_3395_40a2 + -1;
  DAT_3395_44a8 = DAT_3395_44a4 >> 1;
  DAT_3395_44aa = DAT_3395_44a8 + DAT_3395_44a2 + -1;
  DAT_3395_44ac = DAT_3395_44a4 + DAT_3395_44a2;
  DAT_3395_44ae = DAT_3395_44a8 + ((int)DAT_3395_40a2 >> 2);
  DAT_3395_44b0 = DAT_3395_44ae * 0x10;
  FUN_1c54_0008();
  FUN_1155_0032();
  return;
}

