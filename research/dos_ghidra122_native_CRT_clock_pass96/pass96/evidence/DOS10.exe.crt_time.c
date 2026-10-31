
void __cdecl16far FUN_219b_2bae(undefined2 *param_1)

{
  undefined2 uVar1;
  int iVar2;
  undefined1 local_24 [4];
  uint local_20;
  uint local_1e;
  int local_1c;
  int local_1a;
  int local_16;
  byte local_12;
  char local_11;
  undefined1 local_10;
  byte local_f;
  byte local_e;
  byte local_d;
  int local_c;
  uint local_8;
  uint local_6;
  uint local_4;
  
  FUN_219b_2cb8();
  uVar1 = FUN_219b_3b02(DAT_3360_23a0,DAT_3360_23a2,0x3c,0);
  param_1[3] = uVar1;
  FUN_219b_3ace(&local_e);
  FUN_219b_3ae8(&local_12);
  if ((local_12 == 0) && (local_11 == '\0')) {
    FUN_219b_3ace(&local_e);
  }
  local_4 = local_c - 0x7bc;
  local_1a = local_c + -0x76c;
  local_1e = (uint)local_e;
  local_6 = (uint)local_d;
  local_1c = local_6 - 1;
  local_16 = local_1e + *(int *)(local_1c * 2 + 0x2382);
  if (((local_4 & 3) == 0) && (2 < local_d)) {
    local_16 = local_16 + 1;
  }
  local_20 = (uint)local_12;
  param_1[2] = (uint)local_f * 10;
  iVar2 = local_16;
  local_8 = local_1e;
  uVar1 = FUN_219b_2e84(local_4,local_6,local_1e,local_12,local_11,local_10);
  *param_1 = uVar1;
  param_1[1] = iVar2;
  if ((DAT_3360_23a4 == 0) || (iVar2 = FUN_219b_2dc4(local_24), iVar2 == 0)) {
    param_1[4] = 0;
    return;
  }
  param_1[4] = 1;
  return;
}

