
void __cdecl16far FUN_1273_1730(undefined2 param_1,undefined4 param_2)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  undefined2 in_DX;
  char *pcVar4;
  
  pcVar4 = (char *)0x219b;
  iVar1 = FUN_219b_1d6e(0x677,0x8000);
  if (iVar1 < 0) {
    pcVar4 = (char *)s_Copyright_1992__David_P_Gray__Gr_3360_1f3f + 0x28;
    FUN_1f67_000a(0x687,0x67f);
  }
  piVar2 = (int *)FUN_1273_152a(param_1,0);
  FUN_219b_1cd2(pcVar4,iVar1,(int)*(undefined4 *)(piVar2 + 1),
                (int)((ulong)*(undefined4 *)(piVar2 + 1) >> 0x10));
  iVar3 = FUN_1f67_009c(iVar1,(int)param_2,(int)((ulong)param_2 >> 0x10),*piVar2);
  if (*piVar2 != iVar3) {
    FUN_1f67_000a(0x6a5,0x69d);
  }
  FUN_219b_1cb2((char *)s_Copyright_1992__David_P_Gray__Gr_3360_1f3f + 0x28,iVar1);
  return;
}

