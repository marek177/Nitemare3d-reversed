
void __cdecl16far FUN_21d1_2c06(void)

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
  
  pcVar3 = (char *)FUN_21d1_248a(0x2466);
  if ((pcVar3 != (char *)0x0) && (*pcVar3 != '\0')) {
    FUN_21d1_23b4(DAT_3754_2478,pcVar3,3);
    pcVar8 = pcVar3 + 3;
    cVar1 = *pcVar8;
    if (cVar1 == '-') {
      pcVar8 = pcVar3 + 4;
    }
    uVar6 = 0;
    uVar12 = 0;
    uVar11 = 0xe10;
    uVar4 = thunk_FUN_21d1_241a(pcVar8,0xe10,0);
    lVar9 = FUN_21d1_3ad8(uVar4,uVar6,uVar11,uVar12);
    DAT_3754_246c = (int)((ulong)lVar9 >> 0x10);
    DAT_3754_246a = (uint)lVar9;
    for (; (*pcVar8 == '+' || (('/' < *pcVar8 && (*pcVar8 < ':')))); pcVar8 = pcVar8 + 1) {
    }
    if (*pcVar8 == ':') {
      uVar6 = 0;
      uVar12 = 0;
      uVar11 = 0x3c;
      pcVar8 = pcVar8 + 1;
      uVar4 = thunk_FUN_21d1_241a(pcVar8,0x3c,0);
      lVar10 = FUN_21d1_3ad8(uVar4,uVar6,uVar11,uVar12);
      lVar9 = CONCAT22(DAT_3754_246c,DAT_3754_246a);
      iVar7 = (int)((ulong)lVar10 >> 0x10);
      lVar2 = lVar10 + lVar9;
      DAT_3754_246a = (uint)lVar2;
      DAT_3754_246c = (int)((ulong)lVar2 >> 0x10);
      for (; ('/' < *pcVar8 && (*pcVar8 < ':')); pcVar8 = pcVar8 + 1) {
      }
      lVar9 = lVar10 + lVar9;
      if (*pcVar8 == ':') {
        pcVar8 = pcVar8 + 1;
        uVar5 = thunk_FUN_21d1_241a(pcVar8);
        iVar7 = DAT_3754_246c + iVar7 + (uint)CARRY2(DAT_3754_246a,uVar5);
        for (; (lVar9 = CONCAT22(iVar7,DAT_3754_246a + uVar5), '/' < *pcVar8 &&
               (lVar9 = CONCAT22(iVar7,DAT_3754_246a + uVar5), *pcVar8 < ':')); pcVar8 = pcVar8 + 1)
        {
        }
      }
    }
    DAT_3754_246c = (int)((ulong)lVar9 >> 0x10);
    DAT_3754_246a = (uint)lVar9;
    if (cVar1 == '-') {
      lVar9 = CONCAT22(-(DAT_3754_246c + (uint)(DAT_3754_246a != 0)),-DAT_3754_246a);
    }
    DAT_3754_246c = (int)((ulong)lVar9 >> 0x10);
    DAT_3754_246a = (uint)lVar9;
    DAT_3754_246e = (int)*pcVar8;
    if (DAT_3754_246e == 0) {
      *DAT_3754_247a = 0;
    }
    else {
      FUN_21d1_23b4(DAT_3754_247a,pcVar8,3);
    }
  }
  return;
}

