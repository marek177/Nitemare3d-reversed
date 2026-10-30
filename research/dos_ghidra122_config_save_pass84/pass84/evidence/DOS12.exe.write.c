
/* WARNING: Unable to track spacebase fully for stack */

undefined2 FUN_21c2_1efe(undefined2 param_1,uint param_2,char *param_3,int param_4)

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
  uint uStack_12;
  undefined2 uStack_10;
  
  uVar4 = 0x21c2;
  if (DAT_339b_2116 <= param_2) {
LAB_21c2_1f11:
    uVar4 = FUN_21c2_05b7();
    return uVar4;
  }
  if (DAT_339b_2522 == -0x292a) {
    uVar4 = 0x2000;
    (*DAT_339b_2524)();
  }
  if ((((undefined1 *)&DAT_339b_2118)[param_2] & 0x20) != 0) {
    bVar9 = false;
    pcVar2 = (code *)swi(0x21);
    (*pcVar2)();
    if (bVar9) goto LAB_21c2_1f11;
  }
  if ((((undefined1 *)&DAT_339b_2118)[param_2] & 0x80) == 0) {
LAB_21c2_1fa9:
    uVar4 = FUN_21c2_200a();
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
    if (!bVar9) goto LAB_21c2_1fa9;
    uStack_12 = 0x3b80;
    pcVar7 = param_3;
    uStack_10 = uVar4;
    uVar5 = FUN_21c2_203e();
    if (uVar5 < 0xa9) {
      uStack_10 = 0x21c2;
      uStack_12 = 0x3bd2;
      uStack_10 = FUN_21c2_02c6();
      bVar9 = pcVar8 < pcVar7;
      if (pcVar8 != pcVar7) {
        pcVar2 = (code *)swi(0x21);
        uStack_12 = param_2;
        uVar5 = (*pcVar2)(iVar6);
        if ((bVar9) || (uVar5 < (uint)((int)pcVar8 - (int)pcVar7))) goto LAB_21c2_2002;
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
    *(undefined2 *)((int)&uStack_12 + iVar6) = unaff_SS;
    uVar4 = *(undefined2 *)((int)&uStack_12 + iVar6);
    do {
      pcVar1 = param_3;
      param_3 = param_3 + 1;
      cVar3 = *pcVar1;
      if (cVar3 == '\n') {
        cVar3 = '\r';
        if (pcVar7 == pcVar8) {
          *(undefined2 *)((int)&uStack_12 + iVar6) = 0x3bba;
          cVar3 = FUN_21c2_1fb2();
        }
        pcVar1 = pcVar7;
        pcVar7 = pcVar7 + 1;
        *pcVar1 = cVar3;
        cVar3 = '\n';
      }
      if (pcVar7 == pcVar8) {
        *(undefined2 *)((int)&uStack_12 + iVar6) = 0x3bc5;
        cVar3 = FUN_21c2_1fb2();
      }
      pcVar1 = pcVar7;
      pcVar7 = pcVar7 + 1;
      *pcVar1 = cVar3;
      param_4 = param_4 + -1;
    } while (param_4 != 0);
    *(undefined2 *)((int)&uStack_12 + iVar6) = 0x3baf;
    FUN_21c2_1fb2();
  }
LAB_21c2_2002:
  uVar4 = FUN_21c2_05b7();
  return uVar4;
}

