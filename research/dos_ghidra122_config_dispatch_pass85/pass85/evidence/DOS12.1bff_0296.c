
void __cdecl16far FUN_1bff_0296(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  bool bVar5;
  int local_c6 [96];
  int local_6;
  int iStack_4;
  
  if ((DAT_339b_40ab != '\0') || (param_1 == 0)) {
    if (DAT_339b_1798 != 0) {
      FUN_21c2_2052((int)DAT_339b_1798,(int)((ulong)DAT_339b_1798 >> 0x10));
    }
    FUN_1bff_0280();
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
      FUN_1f8f_0002((char *)s_Tune__d_not_found_339b_179c,param_1);
    }
    iVar2 = FUN_21c2_2065(*piVar4);
    DAT_339b_1798 = CONCAT22(iVar3,iVar2);
    if (iVar3 != 0 || iVar2 != 0) {
      FUN_1275_0062(iVar2,iVar3,local_6,iStack_4,iVar1);
      if (param_1 == 0) {
        FUN_2093_000c(0x39,0,0,DAT_339b_1798._2_2_,(undefined2)DAT_339b_1798);
      }
      else if (local_c6[param_1 * 3 + 2] < 0) {
        FUN_2093_0b25((undefined2)DAT_339b_1798,DAT_339b_1798._2_2_);
      }
      else {
        FUN_2093_0b7a((undefined2)DAT_339b_1798,DAT_339b_1798._2_2_);
      }
      FUN_1bff_00a8();
    }
  }
  return;
}

