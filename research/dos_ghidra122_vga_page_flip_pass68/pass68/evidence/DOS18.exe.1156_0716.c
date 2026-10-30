
uint __cdecl16far switchD_1000:f9f4::caseD_0(void)

{
  uint *puVar1;
  byte *pbVar2;
  int *piVar3;
  undefined2 uVar4;
  undefined1 uVar5;
  uint uVar6;
  undefined2 uVar7;
  int iVar8;
  byte bVar9;
  int iVar10;
  int in_BX;
  uint uVar11;
  int unaff_BP;
  char *pcVar12;
  char *pcVar13;
  undefined2 unaff_SS;
  bool bVar14;
  
  *(undefined2 *)(unaff_BP + -0x16) = *(undefined2 *)(in_BX + 0x10);
  *(int *)(unaff_BP + -0x1a) = *(int *)(unaff_BP + -10) * 2 + 0x47e2;
  *(byte *)(unaff_BP + -0x2a) = (*(byte *)((int)*(undefined4 *)(in_BX + 2) + 5) & 0x10) >> 4;
  uVar7 = DAT_376d_012e;
  uVar6 = *(uint *)(unaff_BP + -10);
  pcVar13 = (char *)((*(uint *)(unaff_BP + -0xc) & 0xff) * 0x50 + (uVar6 >> 2));
  *(undefined2 *)(unaff_BP + -6) = pcVar13;
  out(0x3c4,2);
  bVar9 = (byte)uVar6 & 3;
  bVar9 = '\x11' << bVar9 | 0x11U >> 8 - bVar9;
  *(byte *)(unaff_BP + -0x1c) = bVar9;
  out(0x3c5,bVar9);
  uVar4 = *(undefined2 *)(unaff_BP + -4);
  pcVar12 = (char *)*(undefined2 *)(unaff_BP + -2);
  while( true ) {
    if ((*(char *)(unaff_BP + -0x2a) != '\0') ||
       (*(uint *)*(undefined2 *)(unaff_BP + -0x1a) <= *(uint *)(unaff_BP + -0x16))) {
      uVar6 = *(uint *)(unaff_BP + -0x22);
      iVar8 = *(int *)(unaff_BP + -0x24);
      uVar11 = *(uint *)(unaff_BP + -0x28);
      iVar10 = *(int *)(unaff_BP + -0x10);
      do {
        if (*pcVar12 != '\x1f') {
          *pcVar13 = *pcVar12;
        }
        pcVar13 = pcVar13 + 0x50;
        bVar14 = CARRY2(uVar11,uVar6);
        uVar11 = uVar11 + uVar6;
        pcVar12 = pcVar12 + (uint)bVar14 + iVar8;
        iVar10 = iVar10 + -1;
      } while (iVar10 != 0);
    }
    uVar11 = *(uint *)(unaff_BP + -0x22);
    puVar1 = (uint *)(unaff_BP + -0x26);
    uVar6 = *puVar1;
    *puVar1 = *puVar1 + uVar11;
    *(int *)(unaff_BP + -0x18) =
         *(int *)(unaff_BP + -0x18) + *(int *)(unaff_BP + -0x24) + (uint)CARRY2(uVar6,uVar11);
    uVar6 = *(uint *)(unaff_BP + -0x18);
    if (*(int *)(unaff_BP + -0x14) <= (int)uVar6) break;
    iVar8 = (uVar6 & 0xff) * (uint)*(byte *)(unaff_BP + -0x12);
    pcVar12 = (char *)(*(int *)(unaff_BP + -2) + iVar8);
    *(int *)(unaff_BP + -0x1a) = *(int *)(unaff_BP + -0x1a) + 2;
    pbVar2 = (byte *)(unaff_BP + -0x1c);
    bVar9 = *pbVar2;
    *pbVar2 = *pbVar2 << 1 | (char)bVar9 < '\0';
    uVar5 = *(undefined1 *)(unaff_BP + -0x1c);
    out(0x3c5,uVar5);
    if ((char)bVar9 < '\0') {
      *(int *)(unaff_BP + -6) = *(int *)(unaff_BP + -6) + 1;
    }
    pcVar13 = (char *)*(undefined2 *)(unaff_BP + -6);
    piVar3 = (int *)(unaff_BP + -0xe);
    *piVar3 = *piVar3 + -1;
    if (*piVar3 == 0) {
      return CONCAT11((char)((uint)iVar8 >> 8),uVar5);
    }
  }
  return uVar6;
}

