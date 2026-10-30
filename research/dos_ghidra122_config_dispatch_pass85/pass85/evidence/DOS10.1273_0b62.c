
void __cdecl16far FUN_1273_0b62(void)

{
  DAT_3360_439c = (int)DAT_3360_3f9c >> 1;
  DAT_3360_439e =
       (int)(CONCAT12((-(uint)(0x140 < DAT_3360_3f9c) - ((int)DAT_3360_3f9c >> 0xf) & 1) != 0,
                      0x140 - DAT_3360_3f9c) >> 1);
  DAT_3360_439a = DAT_3360_3f9c;
  DAT_3360_43a0 = DAT_3360_439e + DAT_3360_3f9c + -1;
  DAT_3360_43a2 = DAT_3360_439e >> 1;
  DAT_3360_43a4 = DAT_3360_43a2 + DAT_3360_439c + -1;
  DAT_3360_43a6 = DAT_3360_439e + DAT_3360_439c;
  DAT_3360_43a8 = DAT_3360_43a2 + ((int)DAT_3360_3f9c >> 2);
  DAT_3360_43aa = DAT_3360_43a8 * 0x10;
  FUN_1c30_0004();
  FUN_1155_0032();
  return;
}

