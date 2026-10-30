
void __cdecl16far FUN_1277_196c(undefined2 param_1,undefined4 param_2)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  undefined2 in_DX;
  char *pcVar4;
  
  pcVar4 = (char *)0x21ea;
  iVar1 = FUN_21ea_1c76(0x6f2,0x8000);
  if (iVar1 < 0) {
    pcVar4 = (char *)s_About_to__s_game____s__Press_ESC_376d_1fac + 0xb;
    FUN_1fb7_0000(0x702,0x6fa);
  }
  piVar2 = (int *)FUN_1277_1766(param_1,0);
  FUN_21ea_1bda(pcVar4,iVar1,(int)*(undefined4 *)(piVar2 + 1),
                (int)((ulong)*(undefined4 *)(piVar2 + 1) >> 0x10));
  iVar3 = FUN_1fb7_0092(iVar1,(int)param_2,(int)((ulong)param_2 >> 0x10),*piVar2);
  if (*piVar2 != iVar3) {
    FUN_1fb7_0000(0x720,0x718);
  }
  FUN_21ea_1bba((char *)s_About_to__s_game____s__Press_ESC_376d_1fac + 0xb,iVar1);
  return;
}

