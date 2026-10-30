
/* WARNING: Unable to track spacebase fully for stack */

undefined2 FUN_21ea_1f02(undefined2 param_1,uint param_2,char *param_3,int param_4)

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
  
  uVar4 = 0x21ea;
  if (DAT_376d_2126 <= param_2) {
LAB_21ea_1f15:
    uVar4 = FUN_21ea_05bb();
    return uVar4;
  }
  if (DAT_376d_2532 == -0x292a) {
    uVar4 = 0x2000;
    (*DAT_376d_2534)();
  }
  if ((((undefined1 *)&DAT_376d_2128)[param_2] & 0x20) != 0) {
    bVar9 = false;
    pcVar2 = (code *)swi(0x21);
    (*pcVar2)();
    if (bVar9) goto LAB_21ea_1f15;
  }
  if ((((undefined1 *)&DAT_376d_2128)[param_2] & 0x80) == 0) {
LAB_21ea_1fad:
    uVar4 = FUN_21ea_200e();
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
    if (!bVar9) goto LAB_21ea_1fad;
    uStack_12 = 0x3e04;
    pcVar7 = param_3;
    uStack_10 = uVar4;
    uVar5 = FUN_21ea_2042();
    if (uVar5 < 0xa9) {
      uStack_10 = 0x21ea;
      uStack_12 = 0x3e56;
      uStack_10 = FUN_21ea_02ca();
      bVar9 = pcVar8 < pcVar7;
      if (pcVar8 != pcVar7) {
        pcVar2 = (code *)swi(0x21);
        uStack_12 = param_2;
        uVar5 = (*pcVar2)(iVar6);
        if ((bVar9) || (uVar5 < (uint)((int)pcVar8 - (int)pcVar7))) goto LAB_21ea_2006;
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
          *(undefined2 *)((int)&uStack_12 + iVar6) = 0x3e3e;
          cVar3 = FUN_21ea_1fb6();
        }
        pcVar1 = pcVar7;
        pcVar7 = pcVar7 + 1;
        *pcVar1 = cVar3;
        cVar3 = '\n';
      }
      if (pcVar7 == pcVar8) {
        *(undefined2 *)((int)&uStack_12 + iVar6) = 0x3e49;
        cVar3 = FUN_21ea_1fb6();
      }
      pcVar1 = pcVar7;
      pcVar7 = pcVar7 + 1;
      *pcVar1 = cVar3;
      param_4 = param_4 + -1;
    } while (param_4 != 0);
    *(undefined2 *)((int)&uStack_12 + iVar6) = 0x3e33;
    FUN_21ea_1fb6();
  }
LAB_21ea_2006:
  uVar4 = FUN_21ea_05bb();
  return uVar4;
}

