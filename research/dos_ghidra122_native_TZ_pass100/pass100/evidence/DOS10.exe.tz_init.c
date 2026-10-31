
void __cdecl16far FUN_219b_2cca(void)

{
  char cVar1;
  long lVar2;
  char *pcVar3;
  undefined2 uVar4;
  uint uVar5;
  undefined2 uVar6;
  int iVar7;
  char *pcVar8;
  long lVar9;
  long lVar10;
  undefined2 uVar11;
  undefined2 uVar12;
  
  pcVar3 = (char *)FUN_219b_2586(0x239c);
  if ((pcVar3 != (char *)0x0) && (*pcVar3 != '\0')) {
    FUN_219b_24b0(DAT_3360_23ae,pcVar3,3);
    pcVar8 = pcVar3 + 3;
    cVar1 = *pcVar8;
    if (cVar1 == '-') {
      pcVar8 = pcVar3 + 4;
    }
    uVar6 = 0;
    uVar12 = 0;
    uVar11 = 0xe10;
    uVar4 = thunk_FUN_219b_2516(pcVar8,0xe10,0);
    lVar9 = FUN_219b_3b9c(uVar4,uVar6,uVar11,uVar12);
    DAT_3360_23a2 = (int)((ulong)lVar9 >> 0x10);
    DAT_3360_23a0 = (uint)lVar9;
    for (; (*pcVar8 == '+' || (('/' < *pcVar8 && (*pcVar8 < ':')))); pcVar8 = pcVar8 + 1) {
    }
    if (*pcVar8 == ':') {
      uVar6 = 0;
      uVar12 = 0;
      uVar11 = 0x3c;
      pcVar8 = pcVar8 + 1;
      uVar4 = thunk_FUN_219b_2516(pcVar8,0x3c,0);
      lVar10 = FUN_219b_3b9c(uVar4,uVar6,uVar11,uVar12);
      lVar9 = CONCAT22(DAT_3360_23a2,DAT_3360_23a0);
      iVar7 = (int)((ulong)lVar10 >> 0x10);
      lVar2 = lVar10 + lVar9;
      DAT_3360_23a0 = (uint)lVar2;
      DAT_3360_23a2 = (int)((ulong)lVar2 >> 0x10);
      for (; ('/' < *pcVar8 && (*pcVar8 < ':')); pcVar8 = pcVar8 + 1) {
      }
      lVar9 = lVar10 + lVar9;
      if (*pcVar8 == ':') {
        pcVar8 = pcVar8 + 1;
        uVar5 = thunk_FUN_219b_2516(pcVar8);
        iVar7 = DAT_3360_23a2 + iVar7 + (uint)CARRY2(DAT_3360_23a0,uVar5);
        for (; (lVar9 = CONCAT22(iVar7,DAT_3360_23a0 + uVar5), '/' < *pcVar8 &&
               (lVar9 = CONCAT22(iVar7,DAT_3360_23a0 + uVar5), *pcVar8 < ':')); pcVar8 = pcVar8 + 1)
        {
        }
      }
    }
    DAT_3360_23a2 = (int)((ulong)lVar9 >> 0x10);
    DAT_3360_23a0 = (uint)lVar9;
    if (cVar1 == '-') {
      lVar9 = CONCAT22(-(DAT_3360_23a2 + (uint)(DAT_3360_23a0 != 0)),-DAT_3360_23a0);
    }
    DAT_3360_23a2 = (int)((ulong)lVar9 >> 0x10);
    DAT_3360_23a0 = (uint)lVar9;
    DAT_3360_23a4 = (int)*pcVar8;
    if (DAT_3360_23a4 == 0) {
      *DAT_3360_23b0 = 0;
    }
    else {
      FUN_219b_24b0(DAT_3360_23b0,pcVar8,3);
    }
  }
  return;
}

