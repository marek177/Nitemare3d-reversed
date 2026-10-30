
void __cdecl16far FUN_1275_1756(undefined2 param_1,undefined4 param_2)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  undefined2 in_DX;
  char *pcVar4;
  
  pcVar4 = (char *)&DAT_3395_21bc;
  iVar1 = FUN_21bc_1c72(0x6b6,0x8000);
  if (iVar1 < 0) {
    pcVar4 = (char *)s_About_to__s_game____s__Press_ESC_3395_1f66 + 0x23;
    FUN_1f89_0002(0x6c6,0x6be);
  }
  piVar2 = (int *)FUN_1275_1550(param_1,0);
  FUN_21bc_1bd6(pcVar4,iVar1,(int)*(undefined4 *)(piVar2 + 1),
                (int)((ulong)*(undefined4 *)(piVar2 + 1) >> 0x10));
  iVar3 = FUN_1f89_0094(iVar1,(int)param_2,(int)((ulong)param_2 >> 0x10),*piVar2);
  if (*piVar2 != iVar3) {
    FUN_1f89_0002(0x6e4,0x6dc);
  }
  FUN_21bc_1bb6((char *)s_About_to__s_game____s__Press_ESC_3395_1f66 + 0x23,iVar1);
  return;
}

