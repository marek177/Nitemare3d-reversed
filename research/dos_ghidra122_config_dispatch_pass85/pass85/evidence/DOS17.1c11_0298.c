
void __cdecl16far FUN_1c11_0298(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  bool bVar5;
  int local_c6 [96];
  int local_6;
  int iStack_4;
  
  if ((DAT_3754_40bd != '\0') || (param_1 == 0)) {
    if (DAT_3754_17a0 != 0) {
      FUN_21d1_2052((int)DAT_3754_17a0,(int)((ulong)DAT_3754_17a0 >> 0x10));
    }
    FUN_1c11_0282();
    FUN_1277_008a(local_c6);
    piVar4 = local_c6 + param_1 * 3;
    iVar1 = *piVar4;
    local_6 = local_c6[param_1 * 3 + 1];
    iVar3 = local_c6[param_1 * 3 + 2];
    if (iVar3 < 0) {
      bVar5 = local_6 != 0;
      local_6 = -local_6;
      iVar3 = -(iVar3 + (uint)bVar5);
    }
    iStack_4 = iVar3;
    if (*piVar4 == 0) {
      FUN_1f9d_000c((char *)s_Tune__d_not_found_3754_17a4,param_1);
    }
    iVar2 = FUN_21d1_2065(*piVar4);
    DAT_3754_17a0 = CONCAT22(iVar3,iVar2);
    if (iVar3 != 0 || iVar2 != 0) {
      FUN_1277_008a(iVar2,iVar3,local_6,iStack_4,iVar1);
      if (param_1 == 0) {
        FUN_20a2_000c(0x39,0,0,DAT_3754_17a0._2_2_,(undefined2)DAT_3754_17a0);
      }
      else if (local_c6[param_1 * 3 + 2] < 0) {
        FUN_20a2_0b25((undefined2)DAT_3754_17a0,DAT_3754_17a0._2_2_);
      }
      else {
        FUN_20a2_0b7a((undefined2)DAT_3754_17a0,DAT_3754_17a0._2_2_);
      }
      FUN_1c11_00aa();
    }
  }
  return;
}

