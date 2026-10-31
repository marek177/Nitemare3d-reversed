
void __cdecl16far FUN_21bc_2c06(void)

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
  
  pcVar3 = (char *)FUN_21bc_248a(0x2494);
  if ((pcVar3 != (char *)0x0) && (*pcVar3 != '\0')) {
    FUN_21bc_23b4(DAT_3395_24a6,pcVar3,3);
    pcVar8 = pcVar3 + 3;
    cVar1 = *pcVar8;
    if (cVar1 == '-') {
      pcVar8 = pcVar3 + 4;
    }
    uVar6 = 0;
    uVar12 = 0;
    uVar11 = 0xe10;
    uVar4 = thunk_FUN_21bc_241a(pcVar8,0xe10,0);
    lVar9 = FUN_21bc_3ad8(uVar4,uVar6,uVar11,uVar12);
    DAT_3395_249a = (int)((ulong)lVar9 >> 0x10);
    DAT_3395_2498 = (uint)lVar9;
    for (; (*pcVar8 == '+' || (('/' < *pcVar8 && (*pcVar8 < ':')))); pcVar8 = pcVar8 + 1) {
    }
    if (*pcVar8 == ':') {
      uVar6 = 0;
      uVar12 = 0;
      uVar11 = 0x3c;
      pcVar8 = pcVar8 + 1;
      uVar4 = thunk_FUN_21bc_241a(pcVar8,0x3c,0);
      lVar10 = FUN_21bc_3ad8(uVar4,uVar6,uVar11,uVar12);
      lVar9 = CONCAT22(DAT_3395_249a,DAT_3395_2498);
      iVar7 = (int)((ulong)lVar10 >> 0x10);
      lVar2 = lVar10 + lVar9;
      DAT_3395_2498 = (uint)lVar2;
      DAT_3395_249a = (int)((ulong)lVar2 >> 0x10);
      for (; ('/' < *pcVar8 && (*pcVar8 < ':')); pcVar8 = pcVar8 + 1) {
      }
      lVar9 = lVar10 + lVar9;
      if (*pcVar8 == ':') {
        pcVar8 = pcVar8 + 1;
        uVar5 = thunk_FUN_21bc_241a(pcVar8);
        iVar7 = DAT_3395_249a + iVar7 + (uint)CARRY2(DAT_3395_2498,uVar5);
        for (; (lVar9 = CONCAT22(iVar7,DAT_3395_2498 + uVar5), '/' < *pcVar8 &&
               (lVar9 = CONCAT22(iVar7,DAT_3395_2498 + uVar5), *pcVar8 < ':')); pcVar8 = pcVar8 + 1)
        {
        }
      }
    }
    DAT_3395_249a = (int)((ulong)lVar9 >> 0x10);
    DAT_3395_2498 = (uint)lVar9;
    if (cVar1 == '-') {
      lVar9 = CONCAT22(-(DAT_3395_249a + (uint)(DAT_3395_2498 != 0)),-DAT_3395_2498);
    }
    DAT_3395_249a = (int)((ulong)lVar9 >> 0x10);
    DAT_3395_2498 = (uint)lVar9;
    DAT_3395_249c = (int)*pcVar8;
    if (DAT_3395_249c == 0) {
      *DAT_3395_24a8 = 0;
    }
    else {
      FUN_21bc_23b4(DAT_3395_24a8,pcVar8,3);
    }
  }
  return;
}

