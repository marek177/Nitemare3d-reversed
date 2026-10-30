
void __cdecl16far FUN_1277_1808(undefined2 param_1,undefined4 param_2)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  undefined2 in_DX;
  char *pcVar4;
  
  pcVar4 = (char *)0x21d1;
  iVar1 = FUN_21d1_1c72(0x6c5,0x8000);
  if (iVar1 < 0) {
    pcVar4 = (char *)s_About_to__s_game____s__Press_ESC_3754_1f72 + 0x2b;
    FUN_1f9d_000c(0x6d5,0x6cd);
  }
  piVar2 = (int *)FUN_1277_1602(param_1,0);
  FUN_21d1_1bd6(pcVar4,iVar1,(int)*(undefined4 *)(piVar2 + 1),
                (int)((ulong)*(undefined4 *)(piVar2 + 1) >> 0x10));
  iVar3 = FUN_1f9d_009e(iVar1,(int)param_2,(int)((ulong)param_2 >> 0x10),*piVar2);
  if (*piVar2 != iVar3) {
    FUN_1f9d_000c(0x6f3,0x6eb);
  }
  FUN_21d1_1bb6((char *)s_About_to__s_game____s__Press_ESC_3754_1f72 + 0x2b,iVar1);
  return;
}

