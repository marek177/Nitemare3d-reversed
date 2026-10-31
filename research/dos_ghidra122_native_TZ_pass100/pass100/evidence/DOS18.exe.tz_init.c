
void __cdecl16far FUN_21ea_2c0a(void)

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
  
  pcVar3 = (char *)FUN_21ea_248e(0x24a0);
  if ((pcVar3 != (char *)0x0) && (*pcVar3 != '\0')) {
    FUN_21ea_23b8(DAT_376d_24b2,pcVar3,3);
    pcVar8 = pcVar3 + 3;
    cVar1 = *pcVar8;
    if (cVar1 == '-') {
      pcVar8 = pcVar3 + 4;
    }
    uVar6 = 0;
    uVar12 = 0;
    uVar11 = 0xe10;
    uVar4 = thunk_FUN_21ea_241e(pcVar8,0xe10,0);
    lVar9 = FUN_21ea_3adc(uVar4,uVar6,uVar11,uVar12);
    DAT_376d_24a6 = (int)((ulong)lVar9 >> 0x10);
    DAT_376d_24a4 = (uint)lVar9;
    for (; (*pcVar8 == '+' || (('/' < *pcVar8 && (*pcVar8 < ':')))); pcVar8 = pcVar8 + 1) {
    }
    if (*pcVar8 == ':') {
      uVar6 = 0;
      uVar12 = 0;
      uVar11 = 0x3c;
      pcVar8 = pcVar8 + 1;
      uVar4 = thunk_FUN_21ea_241e(pcVar8,0x3c,0);
      lVar10 = FUN_21ea_3adc(uVar4,uVar6,uVar11,uVar12);
      lVar9 = CONCAT22(DAT_376d_24a6,DAT_376d_24a4);
      iVar7 = (int)((ulong)lVar10 >> 0x10);
      lVar2 = lVar10 + lVar9;
      DAT_376d_24a4 = (uint)lVar2;
      DAT_376d_24a6 = (int)((ulong)lVar2 >> 0x10);
      for (; ('/' < *pcVar8 && (*pcVar8 < ':')); pcVar8 = pcVar8 + 1) {
      }
      lVar9 = lVar10 + lVar9;
      if (*pcVar8 == ':') {
        pcVar8 = pcVar8 + 1;
        uVar5 = thunk_FUN_21ea_241e(pcVar8);
        iVar7 = DAT_376d_24a6 + iVar7 + (uint)CARRY2(DAT_376d_24a4,uVar5);
        for (; (lVar9 = CONCAT22(iVar7,DAT_376d_24a4 + uVar5), '/' < *pcVar8 &&
               (lVar9 = CONCAT22(iVar7,DAT_376d_24a4 + uVar5), *pcVar8 < ':')); pcVar8 = pcVar8 + 1)
        {
        }
      }
    }
    DAT_376d_24a6 = (int)((ulong)lVar9 >> 0x10);
    DAT_376d_24a4 = (uint)lVar9;
    if (cVar1 == '-') {
      lVar9 = CONCAT22(-(DAT_376d_24a6 + (uint)(DAT_376d_24a4 != 0)),-DAT_376d_24a4);
    }
    DAT_376d_24a6 = (int)((ulong)lVar9 >> 0x10);
    DAT_376d_24a4 = (uint)lVar9;
    DAT_376d_24a8 = (int)*pcVar8;
    if (DAT_376d_24a8 == 0) {
      *DAT_376d_24b4 = 0;
    }
    else {
      FUN_21ea_23b8(DAT_376d_24b4,pcVar8,3);
    }
  }
  return;
}

