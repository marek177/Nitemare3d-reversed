
/* WARNING: Unable to track spacebase fully for stack */

undefined1 * FUN_21bc_1efe(undefined2 param_1,uint param_2,char *param_3,int param_4)

{
  char *pcVar1;
  code *pcVar2;
  char cVar3;
  undefined1 *puVar4;
  uint uVar5;
  int iVar6;
  char *pcVar7;
  undefined1 **ppuVar8;
  char *pcVar9;
  undefined2 uVar10;
  undefined2 unaff_SS;
  bool bVar11;
  uint uStack_12;
  undefined1 *puStack_10;
  
  puVar4 = (undefined1 *)&DAT_3395_21bc;
  if (DAT_3395_211a <= param_2) {
LAB_21bc_1f11:
    puVar4 = (undefined1 *)FUN_21bc_05b7();
    return puVar4;
  }
  if (DAT_3395_2526 == -0x292a) {
    puVar4 = (undefined1 *)0x2000;
    (*DAT_3395_2528)();
  }
  if ((((undefined1 *)&DAT_3395_211c)[param_2] & 0x20) != 0) {
    bVar11 = false;
    pcVar2 = (code *)swi(0x21);
    (*pcVar2)();
    if (bVar11) goto LAB_21bc_1f11;
  }
  if ((((undefined1 *)&DAT_3395_211c)[param_2] & 0x80) == 0) {
LAB_21bc_1fa9:
    puVar4 = (undefined1 *)FUN_21bc_200a();
    return puVar4;
  }
  bVar11 = true;
  iVar6 = param_4;
  pcVar9 = param_3;
  if (param_4 != 0) {
    do {
      if (iVar6 == 0) break;
      iVar6 = iVar6 + -1;
      pcVar1 = pcVar9;
      pcVar9 = pcVar9 + 1;
      bVar11 = *pcVar1 == '\n';
    } while (!bVar11);
    if (!bVar11) goto LAB_21bc_1fa9;
    uStack_12 = 0x3b20;
    pcVar7 = param_3;
    puStack_10 = puVar4;
    uVar5 = FUN_21bc_203e();
    if (uVar5 < 0xa9) {
      puStack_10 = (undefined1 *)&DAT_3395_21bc;
      uStack_12 = 0x3b72;
      puStack_10 = (undefined1 *)FUN_21bc_02c6();
      bVar11 = pcVar9 < pcVar7;
      if (pcVar9 != pcVar7) {
        pcVar2 = (code *)swi(0x21);
        uStack_12 = param_2;
        uVar5 = (*pcVar2)(iVar6);
        if ((bVar11) || (uVar5 < (uint)((int)pcVar9 - (int)pcVar7))) goto LAB_21bc_2002;
      }
      return puStack_10;
    }
    ppuVar8 = &puStack_10;
    iVar6 = 0x200;
    if (uVar5 < 0x228) {
      iVar6 = 0x80;
    }
    iVar6 = -iVar6;
    pcVar9 = (char *)((int)&puStack_10 + iVar6);
    *(undefined2 *)((int)&uStack_12 + iVar6) = unaff_SS;
    uVar10 = *(undefined2 *)((int)&uStack_12 + iVar6);
    do {
      pcVar1 = param_3;
      param_3 = param_3 + 1;
      cVar3 = *pcVar1;
      if (cVar3 == '\n') {
        cVar3 = '\r';
        if ((undefined1 **)pcVar9 == ppuVar8) {
          *(undefined2 *)((int)&uStack_12 + iVar6) = 0x3b5a;
          cVar3 = FUN_21bc_1fb2();
        }
        pcVar1 = pcVar9;
        pcVar9 = pcVar9 + 1;
        *pcVar1 = cVar3;
        cVar3 = '\n';
      }
      if ((undefined1 **)pcVar9 == ppuVar8) {
        *(undefined2 *)((int)&uStack_12 + iVar6) = 0x3b65;
        cVar3 = FUN_21bc_1fb2();
      }
      pcVar1 = pcVar9;
      pcVar9 = pcVar9 + 1;
      *pcVar1 = cVar3;
      param_4 = param_4 + -1;
    } while (param_4 != 0);
    *(undefined2 *)((int)&uStack_12 + iVar6) = 0x3b4f;
    FUN_21bc_1fb2();
  }
LAB_21bc_2002:
  puVar4 = (undefined1 *)FUN_21bc_05b7();
  return puVar4;
}

