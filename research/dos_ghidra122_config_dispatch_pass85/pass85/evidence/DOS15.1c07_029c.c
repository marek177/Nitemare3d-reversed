
void __cdecl16far FUN_1c07_029c(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  bool bVar5;
  int local_c6 [96];
  int local_6;
  int iStack_4;
  
  if ((DAT_374a_407b != '\0') || (param_1 == 0)) {
    if (DAT_374a_179c != 0) {
      FUN_21c7_2056((int)DAT_374a_179c,(int)((ulong)DAT_374a_179c >> 0x10));
    }
    FUN_1c07_0286();
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
      FUN_1f94_0000((char *)s_Tune__d_not_found_374a_17a0,param_1);
    }
    iVar2 = FUN_21c7_2069(*piVar4);
    DAT_374a_179c = CONCAT22(iVar3,iVar2);
    if (iVar3 != 0 || iVar2 != 0) {
      FUN_1277_008a(iVar2,iVar3,local_6,iStack_4,iVar1);
      if (param_1 == 0) {
        FUN_2099_0000(0x39,0,0,DAT_374a_179c._2_2_,(undefined2)DAT_374a_179c);
      }
      else if (local_c6[param_1 * 3 + 2] < 0) {
        FUN_2099_0b19((undefined2)DAT_374a_179c,DAT_374a_179c._2_2_);
      }
      else {
        FUN_2099_0b6e((undefined2)DAT_374a_179c,DAT_374a_179c._2_2_);
      }
      FUN_1c07_00ae();
    }
  }
  return;
}

