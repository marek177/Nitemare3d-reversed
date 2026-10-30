
/* WARNING: Unable to track spacebase fully for stack */

undefined2 FUN_21c7_1f02(undefined2 param_1,undefined2 *param_2,char *param_3,int param_4)

{
  char *pcVar1;
  code *pcVar2;
  char cVar3;
  undefined2 uVar4;
  uint uVar5;
  int iVar6;
  char *pcVar7;
  char *pcVar8;
  undefined2 unaff_SS;
  bool bVar9;
  undefined2 *puStack_12;
  undefined2 uStack_10;
  
  uVar4 = 0x21c7;
  if (DAT_374a_20e8 <= param_2) {
LAB_21c7_1f15:
    uVar4 = FUN_21c7_05bb();
    return uVar4;
  }
  if (DAT_374a_24f4 == -0x292a) {
    uVar4 = 0x2000;
    (*DAT_374a_24f6)();
  }
  if ((((undefined1 *)&DAT_374a_20ea)[(int)param_2] & 0x20) != 0) {
    bVar9 = false;
    pcVar2 = (code *)swi(0x21);
    (*pcVar2)();
    if (bVar9) goto LAB_21c7_1f15;
  }
  if ((((undefined1 *)&DAT_374a_20ea)[(int)param_2] & 0x80) == 0) {
LAB_21c7_1fad:
    uVar4 = FUN_21c7_200e();
    return uVar4;
  }
  bVar9 = true;
  iVar6 = param_4;
  pcVar8 = param_3;
  if (param_4 != 0) {
    do {
      if (iVar6 == 0) break;
      iVar6 = iVar6 + -1;
      pcVar1 = pcVar8;
      pcVar8 = pcVar8 + 1;
      bVar9 = *pcVar1 == '\n';
    } while (!bVar9);
    if (!bVar9) goto LAB_21c7_1fad;
    puStack_12 = (undefined2 *)0x3bd4;
    pcVar7 = param_3;
    uStack_10 = uVar4;
    uVar5 = FUN_21c7_2042();
    if (uVar5 < 0xa9) {
      uStack_10 = 0x21c7;
      puStack_12 = (undefined2 *)&DAT_374a_3c26;
      uStack_10 = FUN_21c7_02ca();
      bVar9 = pcVar8 < pcVar7;
      if (pcVar8 != pcVar7) {
        pcVar2 = (code *)swi(0x21);
        puStack_12 = param_2;
        uVar5 = (*pcVar2)(iVar6);
        if ((bVar9) || (uVar5 < (uint)((int)pcVar8 - (int)pcVar7))) goto LAB_21c7_2006;
      }
      return uStack_10;
    }
    pcVar8 = (char *)&uStack_10;
    iVar6 = 0x200;
    if (uVar5 < 0x228) {
      iVar6 = 0x80;
    }
    iVar6 = -iVar6;
    pcVar7 = (char *)((int)&uStack_10 + iVar6);
    *(undefined2 *)((int)&puStack_12 + iVar6) = unaff_SS;
    uVar4 = *(undefined2 *)((int)&puStack_12 + iVar6);
    do {
      pcVar1 = param_3;
      param_3 = param_3 + 1;
      cVar3 = *pcVar1;
      if (cVar3 == '\n') {
        cVar3 = '\r';
        if (pcVar7 == pcVar8) {
          *(undefined2 *)((int)&puStack_12 + iVar6) = (undefined2 *)&DAT_374a_3c0e;
          cVar3 = FUN_21c7_1fb6();
        }
        pcVar1 = pcVar7;
        pcVar7 = pcVar7 + 1;
        *pcVar1 = cVar3;
        cVar3 = '\n';
      }
      if (pcVar7 == pcVar8) {
        *(undefined2 *)((int)&puStack_12 + iVar6) = 0x3c19;
        cVar3 = FUN_21c7_1fb6();
      }
      pcVar1 = pcVar7;
      pcVar7 = pcVar7 + 1;
      *pcVar1 = cVar3;
      param_4 = param_4 + -1;
    } while (param_4 != 0);
    *(undefined2 *)((int)&puStack_12 + iVar6) = 0x3c03;
    FUN_21c7_1fb6();
  }
LAB_21c7_2006:
  uVar4 = FUN_21c7_05bb();
  return uVar4;
}

