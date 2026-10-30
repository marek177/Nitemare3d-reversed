
void __cdecl16far FUN_1275_1768(undefined2 param_1,undefined4 param_2)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  undefined2 in_DX;
  char *pcVar4;
  
  pcVar4 = (char *)0x21c2;
  iVar1 = FUN_21c2_1c72(0x6c1,0x8000);
  if (iVar1 < 0) {
    pcVar4 = (char *)s_user_sav_339b_1f8e + 1;
    FUN_1f8f_0002(0x6d1,0x6c9);
  }
  piVar2 = (int *)FUN_1275_1562(param_1,0);
  FUN_21c2_1bd6(pcVar4,iVar1,(int)*(undefined4 *)(piVar2 + 1),
                (int)((ulong)*(undefined4 *)(piVar2 + 1) >> 0x10));
  iVar3 = FUN_1f8f_0094(iVar1,(int)param_2,(int)((ulong)param_2 >> 0x10),*piVar2);
  if (*piVar2 != iVar3) {
    FUN_1f8f_0002(0x6ef,0x6e7);
  }
  FUN_21c2_1bb6((char *)s_user_sav_339b_1f8e + 1,iVar1);
  return;
}

