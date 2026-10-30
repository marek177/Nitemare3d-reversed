
void __cdecl16far FUN_1bff_0294(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  bool bVar5;
  int local_c6 [96];
  int local_6;
  int iStack_4;
  
  if ((DAT_3395_40ab != '\0') || (param_1 == 0)) {
    if (DAT_3395_17a6 != 0) {
      FUN_21bc_2052((int)DAT_3395_17a6,(int)((ulong)DAT_3395_17a6 >> 0x10));
    }
    FUN_1bff_027e();
    FUN_1275_0062(local_c6);
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
      FUN_1f89_0002((char *)s_Tune__d_not_found_3395_17aa,param_1);
    }
    iVar2 = FUN_21bc_2065(*piVar4);
    DAT_3395_17a6 = CONCAT22(iVar3,iVar2);
    if (iVar3 != 0 || iVar2 != 0) {
      FUN_1275_0062(iVar2,iVar3,local_6,iStack_4,iVar1);
      if (param_1 == 0) {
        FUN_208d_000c(0x39,0,0,DAT_3395_17a6._2_2_,(undefined2)DAT_3395_17a6);
      }
      else if (local_c6[param_1 * 3 + 2] < 0) {
        FUN_208d_0b25((undefined2)DAT_3395_17a6,DAT_3395_17a6._2_2_);
      }
      else {
        FUN_208d_0b7a((undefined2)DAT_3395_17a6,DAT_3395_17a6._2_2_);
      }
      FUN_1bff_00a6();
    }
  }
  return;
}

