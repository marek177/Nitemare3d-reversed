
void __cdecl16far FUN_1277_1790(undefined2 param_1,undefined4 param_2)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  undefined2 in_DX;
  char *pcVar4;
  
  pcVar4 = (char *)0x21c7;
  iVar1 = FUN_21c7_1c76(0x6c5,0x8000);
  if (iVar1 < 0) {
    pcVar4 = (char *)s_About_to__s_game____s__Press_ESC_374a_1f6e + 0x26;
    FUN_1f94_0000(0x6d5,0x6cd);
  }
  piVar2 = (int *)FUN_1277_158a(param_1,0);
  FUN_21c7_1bda(pcVar4,iVar1,(int)*(undefined4 *)(piVar2 + 1),
                (int)((ulong)*(undefined4 *)(piVar2 + 1) >> 0x10));
  iVar3 = FUN_1f94_0092(iVar1,(int)param_2,(int)((ulong)param_2 >> 0x10),*piVar2);
  if (*piVar2 != iVar3) {
    FUN_1f94_0000(0x6f3,0x6eb);
  }
  FUN_21c7_1bba((char *)s_About_to__s_game____s__Press_ESC_374a_1f6e + 0x26,iVar1);
  return;
}

