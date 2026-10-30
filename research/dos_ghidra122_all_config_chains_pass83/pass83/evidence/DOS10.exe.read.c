
/* WARNING: Removing unreachable block (ram,0x000239a7) */
/* WARNING: Removing unreachable block (ram,0x0002399c) */

void FUN_219b_1f10(undefined2 param_1,uint param_2,undefined2 param_3,int param_4)

{
  char *pcVar1;
  char cVar2;
  code *pcVar3;
  char cVar6;
  undefined2 uVar4;
  undefined1 extraout_AH;
  undefined1 extraout_AH_00;
  int iVar5;
  undefined1 extraout_AH_01;
  int iVar7;
  uint extraout_DX;
  char *pcVar8;
  char *pcVar9;
  undefined1 uVar10;
  bool bVar11;
  undefined4 uVar12;
  
  if (((DAT_3360_2022 <= param_2) || (param_4 == 0)) ||
     ((((undefined1 *)&DAT_3360_2024)[param_2] & 2) != 0)) {
LAB_219b_1f8d:
    FUN_219b_05af();
    return;
  }
  uVar10 = DAT_3360_242e < 0xd6d6;
  if (DAT_3360_242e == 0xd6d6) {
    (*DAT_3360_2430)();
  }
  pcVar3 = (code *)swi(0x21);
  uVar12 = (*pcVar3)();
  pcVar9 = (char *)((ulong)uVar12 >> 0x10);
  if ((((bool)uVar10) || ((((undefined1 *)&DAT_3360_2024)[param_2] & 0x80) == 0)) ||
     (((undefined1 *)&DAT_3360_2024)[param_2] = ((undefined1 *)&DAT_3360_2024)[param_2] & 0xfb,
     (int)uVar12 == 0)) goto LAB_219b_1f8d;
  uVar4 = 0xd00;
  if (*pcVar9 == '\n') {
    ((undefined1 *)&DAT_3360_2024)[param_2] = ((undefined1 *)&DAT_3360_2024)[param_2] | 4;
  }
LAB_219b_1f72:
  pcVar8 = (char *)((ulong)uVar12 >> 0x10);
  iVar7 = (int)uVar12;
  pcVar1 = pcVar8 + 1;
  cVar2 = *pcVar8;
  cVar6 = (char)((uint)uVar4 >> 8);
  uVar4 = CONCAT11(cVar6,cVar2);
  if (cVar2 == cVar6) {
    if (iVar7 != 1) {
      if (*pcVar1 != '\n') goto LAB_219b_1f82;
      goto LAB_219b_1f85;
    }
    bVar11 = false;
    if ((((undefined1 *)&DAT_3360_2024)[param_2] & 0x40) == 0) {
      pcVar3 = (code *)swi(0x21);
      iVar5 = (*pcVar3)();
      if (!bVar11) {
        uVar10 = 0;
        if (iVar5 != 0) {
          pcVar3 = (code *)swi(0x21);
          (*pcVar3)();
          iVar7 = 1;
          uVar10 = extraout_AH_01;
        }
        uVar4 = CONCAT11(uVar10,0xd);
        goto LAB_219b_1f82;
      }
      goto LAB_219b_1f8d;
    }
    pcVar3 = (code *)swi(0x21);
    (*pcVar3)();
    bVar11 = false;
    uVar10 = extraout_AH;
    if ((extraout_DX & 0x20) == 0) {
      pcVar3 = (code *)swi(0x21);
      (*pcVar3)();
      uVar10 = extraout_AH_00;
      if (bVar11) goto LAB_219b_1f8d;
    }
    uVar4 = CONCAT11(uVar10,10);
  }
  else if (cVar2 == '\x1a') {
    ((undefined1 *)&DAT_3360_2024)[param_2] = ((undefined1 *)&DAT_3360_2024)[param_2] | 2;
    goto LAB_219b_1f8d;
  }
LAB_219b_1f82:
  *pcVar9 = (char)uVar4;
  pcVar9 = pcVar9 + 1;
LAB_219b_1f85:
  uVar12 = CONCAT22(pcVar1,iVar7 + -1);
  if (iVar7 + -1 == 0) goto LAB_219b_1f8d;
  goto LAB_219b_1f72;
}

