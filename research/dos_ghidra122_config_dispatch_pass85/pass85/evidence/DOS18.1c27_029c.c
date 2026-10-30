
void __cdecl16far FUN_1c27_029c(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  bool bVar5;
  int local_c6 [96];
  int local_6;
  int iStack_4;
  
  if ((DAT_376d_414d != '\0') || (param_1 == 0)) {
    if (DAT_376d_17ce != 0) {
      FUN_21ea_2056((int)DAT_376d_17ce,(int)((ulong)DAT_376d_17ce >> 0x10));
    }
    FUN_1c27_0286();
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
      FUN_1fb7_0000((char *)s_Tune__d_not_found_376d_17d2,param_1);
    }
    iVar2 = FUN_21ea_2069(*piVar4);
    DAT_376d_17ce = CONCAT22(iVar3,iVar2);
    if (iVar3 != 0 || iVar2 != 0) {
      FUN_1277_008a(iVar2,iVar3,local_6,iStack_4,iVar1);
      if (param_1 == 0) {
        FUN_20bc_0000(0x39,0,0,DAT_376d_17ce._2_2_,(undefined2)DAT_376d_17ce);
      }
      else if (local_c6[param_1 * 3 + 2] < 0) {
        FUN_20bc_0b19((undefined2)DAT_376d_17ce,DAT_376d_17ce._2_2_);
      }
      else {
        FUN_20bc_0b6e((undefined2)DAT_376d_17ce,DAT_376d_17ce._2_2_);
      }
      FUN_1c27_00ae();
    }
  }
  return;
}

