
/* WARNING: Instruction at (ram,0x00010301) overlaps instruction at (ram,0x00010300)
    */
/* WARNING: Unable to track spacebase fully for stack */
/* WARNING: Removing unreachable block (ram,0x0001b80f) */
/* WARNING: Removing unreachable block (ram,0x0001b7f1) */

undefined1 * __cdecl16far FUN_1681_05de(void)

{
  int *piVar1;
  byte *pbVar2;
  undefined2 uVar3;
  long lVar4;
  undefined2 *puVar5;
  ulong uVar6;
  undefined1 uVar7;
  char cVar8;
  byte bVar9;
  int iVar10;
  uint uVar11;
  undefined1 *puVar12;
  uint uVar13;
  undefined2 uVar14;
  int iVar15;
  int iVar16;
  int iVar17;
  undefined1 *puVar18;
  ulong uVar19;
  undefined3 uVar21;
  ulong uVar20;
  int iVar22;
  ulong in_ECX;
  uint uVar23;
  uint uVar24;
  ulong in_EDX;
  undefined1 *in_BX;
  undefined4 *puVar25;
  byte *pbVar26;
  undefined4 *puVar27;
  ulong in_ESI;
  ulong uVar28;
  int *piVar29;
  ulong in_EDI;
  uint unaff_ES;
  undefined1 *unaff_SS;
  char *pcVar30;
  undefined4 uVar31;
  undefined1 local_c [2];
  undefined1 local_a [2];
  undefined1 local_8 [2];
  undefined1 local_6 [2];
  undefined2 local_4;
  
  uVar19 = ZEXT24(local_6 + 4);
  uVar31 = CONCAT22((int)in_EDI,(int)in_ESI);
  local_4 = local_a;
  if (DAT_3360_3b6e != 1) {
    return local_4;
  }
  if (DAT_3360_0adf != '\0') {
    in_ECX = ZEXT24(local_6);
    FUN_17e9_003c(local_6,local_8,local_c);
    DAT_3360_336e = *(int *)((int)uVar19 + -4);
    DAT_3360_3370 = *(int *)((int)uVar19 + -6);
  }
  DAT_3360_0adf = 0;
  uVar13 = FUN_1681_0390(uVar31);
  iVar10 = (int)uVar19;
  *(uint *)(iVar10 + -8) = uVar13;
  uVar20 = (ulong)uVar13;
  if (uVar13 == 0) goto LAB_1681_07a8;
  bVar9 = *(byte *)(iVar10 + -8);
  uVar13 = (uint)bVar9;
  uVar20 = 0;
  *(uint *)(iVar10 + -0x18) = uVar13;
  if (uVar13 == 0x2b) {
    if (((byte)DAT_3360_3da8 & 0x40) != 0) {
      DAT_3360_3fdf = DAT_3360_3fdf + '\x01';
    }
LAB_1681_077d:
    uVar13 = FUN_17f5_05ca(6);
  }
  else {
    if (bVar9 < 0x2b) {
      if (uVar13 == 0x1b) {
        DAT_3360_3b6e = 0;
        goto LAB_1681_07a8;
      }
      if (0x1b < uVar13) goto LAB_1681_07a8;
      if (bVar9 != 0) {
        uVar20 = 0;
        if (bVar9 == 9) {
          uVar13 = FUN_17f5_26e8();
          uVar20 = (ulong)uVar13;
        }
        goto LAB_1681_07a8;
      }
LAB_1681_0672:
      uVar13 = (uint)*(byte *)(iVar10 + -7);
      uVar20 = 0;
      if (uVar13 == 0x86) {
        uVar13 = FUN_17f5_0d1c();
        uVar20 = (ulong)uVar13;
      }
      else if (uVar13 < 0x87) {
        uVar13 = uVar13 - 0x3b;
        uVar20 = (ulong)uVar13;
        if (uVar13 < 10) {
          uVar11 = uVar13 * 2;
          puVar18 = (undefined1 *)ZEXT24(in_BX);
          puVar27 = (undefined4 *)(ulong)uVar11;
          iVar17 = (int)in_ESI;
          iVar22 = (int)in_EDI;
          switch(uVar13) {
          case 0:
            pbVar2 = (byte *)(iVar10 + iVar17 + 0x16c);
            bVar9 = *pbVar2;
            *pbVar2 = *pbVar2 + (byte)uVar11;
            if (CARRY1(bVar9,(byte)uVar11)) {
              pcVar30 = (char *)s_Not_for_re_distribution_3360_12c8;
            }
            else {
              piVar1 = (int *)(iVar10 + iVar22 + 0x12);
              *piVar1 = *piVar1 + iVar17;
              pcVar30 = (char *)s_Shareware_version_3360_12e0;
            }
            FUN_1cdc_0116(0xffff,0x8c,pcVar30,(undefined1 *)&DAT_3360_3360,in_BX);
            uVar14 = FUN_1273_016c(0x10006);
            FUN_1cdc_0116(0xffff,0xa0,(char *)s_Copyright_1994__David_P__Gray__3360_12f2,
                          (undefined1 *)&DAT_3360_3360,uVar14);
            puVar12 = (undefined1 *)FUN_1cdc_016a();
            return puVar12;
          case 1:
            if (((SCARRY2(uVar13,uVar13) == (int)uVar11 < 0) && (0x3a < *(byte *)(iVar17 + 6))) ||
               (uVar13 = 1 << (*(byte *)(iVar17 + 1) & 0x1f), puVar18 = (undefined1 *)(ulong)uVar13,
               (DAT_3360_3fe9 & uVar13) != 0)) {
              puVar12 = (undefined1 *)puVar18;
              if ((*(byte *)(iVar17 + 6) < 0x3b) || (0x3c < *(byte *)(iVar17 + 6))) {
                *(undefined1 *)(iVar22 + 0x10) = 1;
                puVar12 = (undefined1 *)
                          FUN_1000_0598(iVar22,(int)in_EDX,
                                        (int)CONCAT31((int3)((ulong)puVar18 >> 8),
                                                      (undefined1)DAT_3360_3fb0));
                return puVar12;
              }
            }
            else {
              puVar12 = (undefined1 *)FUN_17f5_1f0e(*(undefined1 *)(iVar17 + 1));
            }
            return puVar12;
          case 2:
            *(undefined2 *)(iVar17 + 4) = 0;
            while( true ) {
              *(undefined4 *)*(undefined4 *)puVar27 = 0;
              puVar25 = (undefined4 *)puVar27 + 1;
              puVar27 = (undefined4 *)ZEXT24(puVar25);
              if ((undefined4 *)0x3399 < puVar25) break;
              *(undefined2 *)((int)*puVar25 + 4) = 0;
            }
            puVar25 = (undefined4 *)&DAT_3360_339a;
            do {
              *(undefined2 *)((int)*puVar25 + 4) = 0;
              puVar5 = (undefined2 *)*puVar25;
              ((undefined2 *)puVar5)[1] = 0;
              *puVar5 = 0;
              puVar25 = puVar25 + 1;
            } while (puVar25 < (undefined4 *)&DAT_3360_33aa);
            DAT_3360_33ae = 0;
            return (undefined1 *)0x0;
          case 3:
            DAT_3360_b007 = SUB21(in_BX,0);
            uVar20 = ZEXT24(in_BX);
            uVar28 = (ulong)unaff_ES;
            while( true ) {
              uVar13 = (uint)CONCAT31((int3)(uVar20 >> 8),
                                      ((undefined1 *)&DAT_3360_cf52)
                                      [*(byte *)((int)(undefined4 *)puVar27 + 1)]);
              iVar10 = (int)uVar19;
              *(undefined1 *)(iVar10 + -0x15) =
                   ((undefined1 *)&DAT_3360_cf52)[*(byte *)((int)(undefined4 *)puVar27 + 1)];
              if (((*(byte *)(iVar10 + -0x15) & 2) != 0) &&
                 ((*(byte *)(iVar10 + -0x15) & 0x20) == 0)) break;
              do {
                iVar10 = (int)uVar19;
                uVar13 = *(uint *)(iVar10 + 0xe);
                *(int *)(iVar10 + -0xc) = *(int *)(iVar10 + -0xc) + 1;
                if ((int)uVar13 <= *(int *)(iVar10 + -0xc)) goto LAB_1a9e_0e10;
                if (*(char *)(iVar10 + -5) == '\0') {
                  in_EDI = (ulong)(uint)((int)in_EDI + *(int *)(iVar10 + -8));
                }
                else {
                  uVar28 = (ulong)(uint)((int)uVar28 + *(int *)(iVar10 + -10));
                }
                if (*(int *)(iVar10 + -0x18) < 0) {
                  uVar20 = (ulong)*(uint *)(iVar10 + -0x12);
                  *(int *)(iVar10 + -0x18) = *(int *)(iVar10 + -0x18) + *(uint *)(iVar10 + -0x12);
                }
                else {
                  uVar20 = (ulong)*(uint *)(iVar10 + -0x14);
                  *(int *)(iVar10 + -0x18) = *(int *)(iVar10 + -0x18) + *(uint *)(iVar10 + -0x14);
                  if (*(char *)(iVar10 + -5) == '\0') {
                    uVar28 = (ulong)(uint)((int)uVar28 + *(int *)(iVar10 + -10));
                  }
                  else {
                    in_EDI = (ulong)(uint)((int)in_EDI + *(int *)(iVar10 + -8));
                  }
                }
                uVar14 = DAT_3360_2462;
                uVar21 = (undefined3)(uVar20 >> 8);
                if ((*(int *)(iVar10 + -0xe) == (int)uVar28) &&
                   (*(int *)(iVar10 + -0x10) == (int)in_EDI)) {
                  return (undefined1 *)(undefined1 *)CONCAT31(uVar21,1);
                }
                pbVar26 = (byte *)(((int)in_EDI * 0x40 + (int)uVar28) * 2 + 0x373e);
                *(undefined2 *)(iVar10 + -4) = pbVar26;
                *(undefined2 *)(iVar10 + -2) = uVar14;
                uVar20 = CONCAT31(uVar21,((undefined1 *)&DAT_3360_ce52)[*pbVar26]);
                uVar13 = (uint)uVar20;
                *(undefined1 *)(iVar10 + -6) = ((undefined1 *)&DAT_3360_ce52)[*pbVar26];
                if ((*(byte *)(iVar10 + -6) & 2) != 0) {
                  if ((*(byte *)(iVar10 + -6) & 4) != 0) goto LAB_1a9e_0e10;
                  if ((*(byte *)(iVar10 + -6) & 8) != 0) {
                    uVar14 = FUN_1000_0000(*(undefined2 *)(iVar10 + -4),uVar14);
                    uVar13 = FUN_1000_01e0(uVar14,(int)in_EDX);
                    uVar20 = (ulong)uVar13;
                    if ((char)uVar13 == '\0') goto LAB_1a9e_0e10;
                  }
                }
              } while (*(char *)((int)uVar19 + 0x10) == '\0');
              uVar6 = *(ulong *)((int)uVar19 + -4);
              unaff_ES = (uint)(uVar6 >> 0x10);
              puVar27 = (undefined4 *)(uVar6 & 0xffff);
            }
LAB_1a9e_0e10:
            return (undefined1 *)(uVar13 & 0xff00);
          case 4:
            return in_BX;
          case 5:
            *(undefined2 *)(uVar11 + iVar22 + -2) = 0x1000;
            do {
              iVar17 = (int)uVar19;
              iVar10 = *(int *)(iVar17 + -8) + 1;
              if (0x3f < iVar10) {
                return (undefined1 *)puVar18;
              }
              *(undefined2 *)(iVar17 + -6) = 0;
              *(int *)(iVar17 + -8) = iVar10;
              do {
                uVar14 = DAT_3360_2452;
                iVar10 = (int)uVar19;
                pbVar26 = (byte *)*(undefined2 *)(iVar10 + -0xe);
                *(undefined2 *)(iVar10 + -0x16) = pbVar26;
                *(undefined2 *)(iVar10 + -0x14) = uVar14;
                if ((((undefined1 *)&DAT_3360_ce52)[*pbVar26] & 8) != 0) {
                  if (0x3f < *(int *)*(undefined4 *)(iVar10 + -0x12)) {
                    FUN_1f67_000a(0x72,0x40);
                  }
                  iVar10 = (int)uVar19;
                  piVar1 = (int *)*(undefined4 *)(iVar10 + -0x12);
                  *(int *)(iVar10 + -0xc) = *piVar1 * 0x12 + 0x3076;
                  *(undefined2 *)(iVar10 + -10) = 0x2dec;
                  *piVar1 = *piVar1 + 1;
                  *(undefined4 *)*(undefined4 *)(iVar10 + -0xc) = 0;
                  *(undefined2 *)(iVar10 + -2) = 0;
                  *(undefined2 *)(iVar10 + -4) = (undefined1 *)&DAT_3360_60f2;
                  if (DAT_3360_60c4 < 1) {
                    iVar17 = *(int *)(iVar10 + -4);
                    iVar22 = *(int *)(iVar10 + -2);
                  }
                  else {
                    iVar17 = *(int *)(iVar10 + -4);
                    iVar22 = 0;
                    do {
                      if ((((*(byte *)(iVar17 + 5) & 8) != 0) &&
                          (*(int *)(iVar17 + 0xc) >> 6 == *(int *)(iVar10 + -6))) &&
                         (*(int *)(iVar17 + 0xe) >> 6 == *(int *)(iVar10 + -8))) {
                        *(int *)*(undefined4 *)(iVar10 + -0xc) = iVar17;
                        break;
                      }
                      iVar17 = iVar17 + 0x1c;
                      iVar22 = iVar22 + 1;
                    } while (iVar22 < DAT_3360_60c4);
                  }
                  uVar13 = iVar17 + 0x1c;
                  in_ESI = (ulong)uVar13;
                  in_ECX = (ulong)(iVar22 + 1U);
                  if ((int)(iVar22 + 1U) < DAT_3360_60c4) {
                    in_EDX = (ulong)*(uint *)(iVar10 + -6);
                    puVar27 = (undefined4 *)(ulong)*(uint *)(iVar10 + -8);
                    do {
                      uVar13 = (uint)in_ESI;
                      if ((((*(byte *)(uVar13 + 5) & 8) != 0) &&
                          (*(int *)(uVar13 + 0xc) >> 6 == (int)in_EDX)) &&
                         ((undefined4 *)(*(int *)(uVar13 + 0xe) >> 6) == (undefined4 *)puVar27)) {
                        piVar29 = (int *)*(int *)((int)uVar19 + -0xc);
                        piVar29[1] = uVar13;
                        goto LAB_1000_0318;
                      }
                      in_ESI = (ulong)(uVar13 + 0x1c);
                      in_ECX = (ulong)((int)in_ECX + 1);
switchD_1000_6e9f_caseD_7:
                      uVar13 = (uint)in_ESI;
                    } while ((int)in_ECX < DAT_3360_60c4);
                  }
                  piVar29 = (int *)*(int *)((int)uVar19 + -0xc);
LAB_1000_0318:
                  uVar14 = *(undefined2 *)((int)uVar19 + -10);
                  if ((*piVar29 == 0) || (piVar29[1] == 0)) {
                    FUN_1f67_000a(0x89);
                  }
                  iVar10 = (int)uVar19;
                  uVar14 = *(undefined2 *)(iVar10 + -10);
                  *(undefined4 *)(piVar29 + 2) = *(undefined4 *)(iVar10 + -0x16);
                  piVar29[4] = 1;
                  *(undefined1 *)(piVar29 + 8) = 0;
                  cVar8 = *(char *)(*piVar29 + 7);
                  *(char *)(iVar10 + -0x18) = cVar8;
                  if (((cVar8 == '\0') &&
                      ((((undefined1 *)&DAT_3360_ce52)[*(byte *)(*(int *)(iVar10 + -0xe) + 2)] & 8)
                       != 0)) ||
                     ((*(char *)(iVar10 + -0x18) == '\x02' &&
                      ((((undefined1 *)&DAT_3360_ce52)[*(byte *)(*(int *)(iVar10 + -0xe) + 0x80)] &
                       8) != 0)))) {
                    *(undefined1 *)(iVar10 + -1) = 1;
                  }
                  else {
                    *(undefined1 *)(iVar10 + -1) = 0;
                  }
                  if (*(char *)(iVar10 + -1) == '\0') {
                    iVar17 = *(int *)(uVar13 + 0xc);
                  }
                  else {
                    iVar17 = *(int *)(uVar13 + 0x10);
                  }
                  piVar29[6] = iVar17;
                  if (*(char *)(iVar10 + -1) == '\0') {
                    iVar17 = *(int *)(uVar13 + 0xe);
                  }
                  else {
                    iVar17 = *(int *)(uVar13 + 0x12);
                  }
                  piVar29[7] = iVar17;
                  uVar14 = *(undefined2 *)(iVar10 + -10);
                  bVar9 = *(char *)(iVar10 + -1) << 5;
                  puVar18 = (undefined1 *)
                            ((ulong)CONCAT11((char)((uint)iVar17 >> 8),
                                             bVar9 ^ *(byte *)(*piVar29 + 5)) & 0xffffff20);
                  pbVar2 = (byte *)(*piVar29 + 5);
                  *pbVar2 = *pbVar2 ^ (byte)puVar18;
                  pbVar2 = (byte *)(piVar29[1] + 5);
                  *pbVar2 = *pbVar2 ^ (bVar9 ^ *(byte *)(piVar29[1] + 5)) & 0x20;
                }
                iVar10 = (int)uVar19;
                *(int *)(iVar10 + -0xe) = *(int *)(iVar10 + -0xe) + 2;
                *(int *)(iVar10 + -6) = *(int *)(iVar10 + -6) + 1;
              } while (*(int *)(iVar10 + -6) < 0x40);
            } while( true );
          case 6:
            uVar20 = (ulong)(iVar17 + 1);
            uVar7 = in((int)in_EDX);
            uVar14 = CONCAT11((char)((uint)in_BX >> 8),uVar7);
            puVar12 = (undefined1 *)&DAT_3360_3360;
            do {
              *(undefined2 *)((int)uVar19 + -0x12) = (int)uVar20;
              *(undefined2 *)((int)uVar19 + -0x10) = uVar14;
              do {
                iVar17 = (int)uVar20;
                uVar20 = (ulong)(iVar17 + 0x12);
                iVar10 = (int)uVar19;
                *(int *)(iVar10 + -10) = *(int *)(iVar10 + -10) + 1;
                if (*(int *)0x0 <= *(int *)(iVar10 + -10)) {
                  return (undefined1 *)*(undefined2 *)(iVar10 + -0x12);
                }
                uVar14 = *(undefined2 *)(iVar10 + 8);
                uVar3 = *(undefined2 *)(iVar10 + -0x14);
                uVar13 = (*(int *)(iVar17 + 0x1e) >> 6) - (*(int *)((int)in_EDI + 0x10) >> 6);
                *(uint *)(iVar10 + -4) = uVar13;
                uVar11 = (*(int *)(iVar17 + 0x20) >> 6) - (*(int *)((int)in_EDI + 0x12) >> 6);
                *(uint *)(iVar10 + -6) = uVar11;
                iVar17 = ((uVar11 ^ (int)uVar11 >> 0xf) - ((int)uVar11 >> 0xf)) +
                         ((uVar13 ^ (int)uVar13 >> 0xf) - ((int)uVar13 >> 0xf));
                *(int *)(iVar10 + -2) = iVar17;
                puVar12 = unaff_SS;
              } while ((*(int *)(iVar10 + -8) <= iVar17) || (cVar8 = FUN_1a9e_0cb4(), cVar8 == '\0')
                      );
              iVar10 = (int)uVar19;
              *(undefined2 *)(iVar10 + -8) = *(undefined2 *)(iVar10 + -2);
              uVar14 = *(undefined2 *)(iVar10 + -0x14);
            } while( true );
          case 7:
            goto switchD_1000_6e9f_caseD_7;
          case 8:
            do {
              iVar17 = (int)in_EDI;
              iVar10 = (int)in_ESI;
              if (*(int *)((int)uVar19 + -0x10) == iVar10) goto LAB_1200_06dd;
              do {
                iVar22 = (int)uVar19;
                iVar17 = (int)in_EDI;
                iVar10 = (int)in_ESI;
                uVar14 = FUN_1155_04d0(*(undefined4 *)(iVar22 + -0x18),iVar10,iVar17,
                                       *(undefined2 *)(iVar22 + -6),
                                       (int)*(undefined4 *)(iVar22 + -0x1c),
                                       (int)((ulong)*(undefined4 *)(iVar22 + -0x1c) >> 0x10));
                *(undefined2 *)((int)uVar19 + -0xe) = uVar14;
LAB_1200_06dd:
                iVar22 = (int)uVar19;
                *(int *)(iVar22 + -0x10) = iVar10;
                *(int *)(iVar22 + -8) = *(int *)(iVar22 + -8) + 2;
                uVar13 = iVar17 + 1;
                if (*(int *)(*(uint *)(iVar22 + -0x20) + 6) < (int)uVar13) {
                  uVar20 = (ulong)*(uint *)(iVar22 + -0x20);
                  do {
                    iVar17 = (int)uVar20;
                    iVar10 = *(int *)((int)uVar19 + -0x24);
                    if (*(int *)(iVar10 + 2) != 0) {
                      FUN_1200_0410(*(undefined2 *)((int)uVar19 + -0x22),iVar10);
                    }
                    puVar12 = DAT_3360_4bba;
                    uVar20 = ZEXT24((int *)(iVar17 + 0x12));
                    iVar10 = (int)uVar19;
                    *(int *)(iVar10 + -0x26) = *(int *)(iVar10 + -0x26) + 1;
                    if ((int)puVar12 <= *(int *)(iVar10 + -0x26)) {
                      return puVar12;
                    }
                    iVar17 = *(int *)(iVar17 + 0x12);
                    bVar9 = *(byte *)(iVar17 + 4);
                    *(undefined2 *)(iVar10 + -0x24) = (undefined2 *)&DAT_3360_4166 + (uint)bVar9 * 4
                    ;
                    uVar13 = (uint)*(byte *)(iVar17 + 3);
                    iVar22 = uVar13 * 10 + ((undefined2 *)&DAT_3360_416c)[(uint)bVar9 * 4];
                    *(int *)(iVar10 + -0x14) = iVar22;
                    lVar4 = *(long *)(iVar22 + 6);
                    *(long *)(iVar10 + -0x18) = lVar4;
                    if (lVar4 == 0) {
                      uVar14 = FUN_1739_0316(iVar22);
                      *(undefined2 *)((int)uVar19 + -0x18) = uVar14;
                      *(uint *)((int)uVar19 + -0x16) = uVar13;
                    }
                    iVar10 = (int)uVar19;
                    if ((*(char *)(iVar17 + 6) == '\x02') ||
                       ((*(char *)(iVar17 + 7) != '\0' && (*(char *)(iVar17 + 7) != '\x03')))) {
                      *(undefined1 *)(iVar10 + -0x11) = 0;
                    }
                    else {
                      *(undefined1 *)(iVar10 + -0x11) = 1;
                    }
                    iVar22 = DAT_3360_60ce;
                    *(int *)(iVar10 + -0x1c) = DAT_3360_60ce;
                    if (((0 < iVar22) && (DAT_3360_4164 == '\0')) &&
                       ((*(char *)(iVar17 + 7) == '\0' || (*(char *)(iVar17 + 7) == '\x01')))) {
                      *(undefined2 *)(iVar10 + -0x1c) = 0;
                    }
                    *(byte *)(iVar10 + -1) = (*(byte *)(iVar17 + 5) & 0x20) >> 5;
                    if ((*(char *)(iVar17 + 6) == '@') || (*(char *)(iVar17 + 6) == '?')) {
                      *(bool *)(iVar10 + -1) = *(char *)(iVar10 + -1) == '\0';
                    }
                    if ((*(char *)(iVar17 + 7) == '\0') || (*(char *)(iVar17 + 7) == '\x01')) {
                      if (*(char *)(iVar10 + -1) == '\0') {
                        iVar22 = DAT_3360_3fba - *(int *)(iVar17 + 0xc);
                      }
                      else {
                        iVar22 = (DAT_3360_3fba - *(int *)(iVar17 + 0x10)) + 0x80;
                      }
                      *(int *)(iVar10 + -0x1e) = iVar22;
                      iVar22 = DAT_3360_3fbc - *(int *)(iVar17 + 0xe);
                      *(int *)(iVar10 + -2) = iVar22;
                    }
                    else {
                      if (*(char *)(iVar10 + -1) == '\0') {
                        iVar15 = *(int *)(iVar17 + 0xe) - DAT_3360_3fbc;
                      }
                      else {
                        iVar15 = (*(int *)(iVar17 + 0x12) - DAT_3360_3fbc) + -0x80;
                      }
                      iVar22 = *(int *)(iVar17 + 0xc) - DAT_3360_3fba;
                      *(int *)(iVar10 + -2) = iVar22;
                      *(int *)(iVar10 + -0x1e) = iVar15;
                    }
                    *(int *)(iVar10 + -0x22) = iVar17;
                    if (DAT_3360_3fb4 == 0) {
                      lVar4 = (long)*(int *)(iVar10 + -2) * (long)DAT_3360_400a;
                      uVar14 = (undefined2)lVar4;
                    }
                    else {
                      lVar4 = (long)iVar22 * (long)DAT_3360_4008;
                      uVar14 = (undefined2)lVar4;
                    }
                    *(undefined2 *)(iVar10 + -0xc) = uVar14;
                    *(undefined2 *)(iVar10 + -10) = (int)((ulong)lVar4 >> 0x10);
                    *(undefined2 *)(iVar10 + -0xe) = 1;
                    iVar22 = (int)uVar20;
                    *(int *)(iVar10 + -0x1a) = *(int *)(iVar22 + 6) + -3;
                    *(undefined2 *)(iVar10 + -0x10) = 0;
                    iVar17 = *(int *)(iVar22 + 2);
                    *(int *)(iVar10 + -4) = iVar17;
                  } while (*(int *)(iVar22 + 6) < iVar17);
                  *(int *)(iVar10 + -0x20) = iVar22;
                  *(int *)(iVar10 + -8) = iVar17 * 2 + 0x463a;
                  uVar13 = *(uint *)(iVar10 + -4);
                }
                in_EDI = (ulong)uVar13;
                iVar17 = (int)uVar19;
                iVar10 = *(int *)(iVar17 + -0x20);
                *(undefined2 *)(iVar17 + -2) = *(undefined2 *)(iVar10 + 0x10);
                *(long *)(iVar10 + 0xe) = *(long *)(iVar10 + 0xe) + *(long *)(iVar10 + 10);
                *(int *)(iVar17 + -6) = (*(uint *)(iVar17 + -2) >> 4) + DAT_3360_43a8;
                iVar10 = FUN_1c30_070c(*(undefined1 *)(*(int *)(iVar17 + -0x22) + 7),uVar13,
                                       *(undefined2 *)(iVar17 + -2),
                                       (int)*(undefined4 *)(iVar17 + -0xc),
                                       (int)((ulong)*(undefined4 *)(iVar17 + -0xc) >> 0x10));
                iVar17 = (int)uVar19;
                iVar10 = iVar10 + *(int *)(iVar17 + -0x1e);
                if (*(char *)(iVar17 + -0x11) != '\0') {
                  iVar10 = -iVar10;
                }
                uVar13 = FUN_1200_02bc(*(undefined2 *)(iVar17 + -0x22),(int)in_EDI,iVar10,
                                       *(undefined1 *)*(undefined2 *)(iVar17 + -0x14));
                in_ESI = (ulong)uVar13;
                iVar10 = (int)uVar19;
                *(int *)*(undefined2 *)(iVar10 + -8) = *(int *)(iVar10 + -2) + DAT_3360_43aa;
                piVar1 = (int *)(iVar10 + -0xe);
                *piVar1 = *piVar1 + -1;
              } while (*piVar1 == 0);
            } while( true );
          case 9:
            LOCK();
            *(undefined1 *)(iVar10 + -1) = (char)(uVar11 >> 8);
            UNLOCK();
            if (in_BX == (undefined1 *)0x0) {
              FUN_1f67_000a(0x770,*(undefined2 *)(iVar10 + 6));
            }
            iVar10 = FUN_219b_06f4((int)uVar19 + -0x80,0x80,1,*(undefined2 *)((int)uVar19 + -0x82));
            if (iVar10 != 1) {
              FUN_1f67_000a(0x786,*(undefined2 *)((int)uVar19 + 6));
            }
            if (*(int *)((int)uVar19 + -0x7c) != -0x50ef) {
              FUN_1f67_000a(0x79c);
            }
            *(undefined2 *)((int)uVar19 + -0x84) = 0;
          }
          while (iVar10 = (int)uVar19, *(uint *)(iVar10 + -0x84) < *(uint *)(iVar10 + -0x7a)) {
            cVar8 = FUN_1681_01d8();
            iVar10 = (int)uVar19;
            if (cVar8 != '\0') break;
            do {
              iVar10 = (int)in_EDX;
              uVar11 = FUN_1b91_0098();
              iVar17 = (int)uVar19;
              uVar23 = (iVar10 - *(int *)(iVar17 + -0x86)) -
                       (uint)(uVar11 < *(uint *)(iVar17 + -0x88));
              uVar13 = *(int *)(iVar17 + -0x70) * 0xf;
              uVar24 = (int)uVar13 >> 0xf;
              in_EDX = (ulong)uVar24;
              if (uVar24 < uVar23) break;
            } while ((uVar23 < uVar24) || (uVar11 - *(uint *)(iVar17 + -0x88) < uVar13));
            uVar14 = FUN_1b91_0098();
            iVar10 = (int)uVar19;
            *(undefined2 *)(iVar10 + -0x88) = uVar14;
            *(undefined2 *)(iVar10 + -0x86) = (int)in_EDX;
            FUN_1408_0330(*(undefined2 *)(iVar10 + -0x82));
            piVar1 = (int *)((int)uVar19 + -0x84);
            *piVar1 = *piVar1 + 1;
          }
          puVar12 = (undefined1 *)FUN_219b_05f2(*(undefined2 *)(iVar10 + -0x82));
          return puVar12;
        }
      }
      goto LAB_1681_07a8;
    }
    if (uVar13 == 0x2d) {
      if (((byte)DAT_3360_3da8 & 0x40) != 0) {
        DAT_3360_3fdf = DAT_3360_3fdf + -1;
      }
      goto LAB_1681_077d;
    }
    uVar20 = (ulong)(uVar13 - 0x31);
    if ((int)(uVar13 - 0x2d) < 4) goto LAB_1681_07a8;
    if (uVar13 != 0x39 && 7 < (int)(uVar13 - 0x31)) {
      uVar20 = (ulong)(uVar13 - 0xe0);
      if (uVar13 - 0xe0 != 0) goto LAB_1681_07a8;
      goto LAB_1681_0672;
    }
    iVar17 = *(int *)(iVar10 + -0x18) + -0x31;
    uVar13 = 1 << ((byte)iVar17 & 0x1f);
    uVar20 = (ulong)uVar13;
    if ((DAT_3360_3fea & uVar13) == 0) goto LAB_1681_07a8;
    uVar13 = FUN_17f5_0cae(iVar17);
  }
  uVar20 = (ulong)uVar13;
LAB_1681_07a8:
  if (((byte)DAT_3360_3da8 & 0x20) == 0) {
    iVar17 = (int)DAT_3360_43b2;
  }
  else {
    iVar17 = (int)DAT_3360_43b2 * 2;
  }
  if (((byte)DAT_3360_3da8 & 0x20) == 0) {
    iVar22 = DAT_3360_43b2._2_2_;
  }
  else {
    iVar22 = DAT_3360_43b2._2_2_ * 2;
  }
  if (((byte)DAT_3360_3da8 & 0x40) != 0) {
    iVar17 = 1;
  }
  uVar19 = CONCAT31((int3)(uVar20 >> 8),(byte)DAT_3360_3da8) & 0xffffff40;
  if (((byte)DAT_3360_3da8 & 0x40) != 0) {
    iVar22 = 1;
  }
  if (((byte)DAT_3360_3da8 & 2) != 0) {
    uVar13 = FUN_1609_05a6(DAT_3360_3fae,0,iVar17);
    uVar19 = (ulong)uVar13;
  }
  if (((byte)DAT_3360_3da8 & 4) != 0) {
    uVar13 = FUN_1609_05a6((DAT_3360_3fae + 0xb4) % 0x168,0,iVar17);
    uVar19 = (ulong)uVar13;
  }
  if (((byte)DAT_3360_3da8 & 8) != 0) {
    if ((DAT_3360_3da8._1_1_ & 1) == 0) {
      uVar13 = FUN_1c30_0068(DAT_3360_3fae - iVar22);
      uVar19 = (ulong)uVar13;
    }
    else {
      uVar13 = FUN_1609_05a6((DAT_3360_3fae + 0x10e) % 0x168,1,iVar17);
      uVar19 = (ulong)uVar13;
    }
  }
  if (((byte)DAT_3360_3da8 & 0x10) != 0) {
    if ((DAT_3360_3da8._1_1_ & 1) == 0) {
      uVar13 = FUN_1c30_0068(DAT_3360_3fae + iVar22);
      uVar19 = (ulong)uVar13;
    }
    else {
      uVar13 = FUN_1609_05a6((DAT_3360_3fae + 0x5a) % 0x168,1,iVar17);
      uVar19 = (ulong)uVar13;
    }
  }
  *(byte *)(iVar10 + -2) = (byte)DAT_3360_3da8 >> 7;
  uVar19 = CONCAT31((int3)(uVar19 >> 8),DAT_3360_3da8._1_1_) & 0xffffff02;
  bVar9 = (byte)uVar19 >> 1;
  uVar19 = CONCAT31((int3)(uVar19 >> 8),bVar9);
  *(byte *)(iVar10 + -1) = bVar9;
  if (DAT_3360_3fa4 != '\0') {
    FUN_17e9_003c(iVar10 + -4,iVar10 + -6,iVar10 + -10);
    if (*(int *)(iVar10 + -6) < DAT_3360_3370) {
      uVar14 = FUN_1681_05a2(iVar17,DAT_3360_3370 - *(int *)(iVar10 + -6));
      FUN_1609_05a6(DAT_3360_3fae,0,uVar14);
    }
    if (DAT_3360_3370 < *(int *)(iVar10 + -6)) {
      uVar14 = FUN_1681_05a2(iVar17,*(int *)(iVar10 + -6) - DAT_3360_3370);
      FUN_1609_05a6((DAT_3360_3fae + 0xb4) % 0x168,0,uVar14);
    }
    if (*(int *)(iVar10 + -4) < DAT_3360_336e) {
      if (((DAT_3360_3da8._1_1_ & 1) == 0) && ((*(byte *)(iVar10 + -10) & 2) == 0)) {
        iVar15 = FUN_1681_05a2(iVar22,DAT_3360_336e - *(int *)(iVar10 + -4) >> 1);
        FUN_1c30_0068(-(iVar15 - DAT_3360_3fae));
      }
      else {
        uVar14 = FUN_1681_05a2(iVar17,DAT_3360_336e - *(int *)(iVar10 + -4));
        FUN_1609_05a6((DAT_3360_3fae + 0x10e) % 0x168,1,uVar14);
      }
    }
    iVar15 = *(int *)(iVar10 + -4);
    if (DAT_3360_336e < iVar15) {
      if (((DAT_3360_3da8._1_1_ & 1) == 0) && ((*(byte *)(iVar10 + -10) & 2) == 0)) {
        iVar15 = FUN_1681_05a2(iVar22,iVar15 - DAT_3360_336e >> 1);
        FUN_1c30_0068(iVar15 + DAT_3360_3fae);
      }
      else {
        uVar14 = FUN_1681_05a2(iVar17,iVar15 - DAT_3360_336e);
        FUN_1609_05a6((DAT_3360_3fae + 0x5a) % 0x168,1,uVar14);
      }
    }
    if ((((*(int *)(iVar10 + -4) <= DAT_3360_439e) || (DAT_3360_43a0 <= *(int *)(iVar10 + -4))) ||
        (*(int *)(iVar10 + -6) <= DAT_3360_43a2)) || (DAT_3360_43a4 <= *(int *)(iVar10 + -6))) {
      iVar15 = DAT_3360_43a8 >> 1;
      *(int *)(iVar10 + -6) = iVar15;
      iVar16 = DAT_3360_43a6 >> 1;
      *(int *)(iVar10 + -4) = iVar16;
      FUN_17e9_0070(iVar16,iVar15);
    }
    DAT_3360_336e = *(int *)(iVar10 + -4);
    DAT_3360_3370 = *(int *)(iVar10 + -6);
    *(byte *)(iVar10 + -2) = *(byte *)(iVar10 + -2) | 1U - ((*(byte *)(iVar10 + -10) & 1) == 0);
    uVar19 = 0;
    *(byte *)(iVar10 + -1) = *(byte *)(iVar10 + -1) | 1U - ((*(byte *)(iVar10 + -10) & 2) == 0);
  }
  if (DAT_3360_3fa7 != '\0') {
    uVar13 = FUN_1bdd_04da(iVar10 + -0x16);
    if (*(int *)(iVar10 + -0x14) < -10) {
      uVar14 = FUN_1681_05c0(iVar17,-*(int *)(iVar10 + -0x14));
      uVar13 = FUN_1609_05a6(DAT_3360_3fae,0,uVar14);
    }
    if (10 < *(int *)(iVar10 + -0x14)) {
      uVar14 = FUN_1681_05c0(iVar17,*(undefined2 *)(iVar10 + -0x14));
      uVar13 = FUN_1609_05a6((DAT_3360_3fae + 0xb4) % 0x168,0,uVar14);
    }
    uVar19 = (ulong)uVar13;
    if (*(int *)(iVar10 + -0x16) < -10) {
      if (((DAT_3360_3da8._1_1_ & 1) == 0) && (*(int *)(iVar10 + -0x10) == 0)) {
        iVar15 = FUN_1681_05c0(iVar22,-*(int *)(iVar10 + -0x16) >> 1);
        uVar13 = FUN_1c30_0068(-(iVar15 - DAT_3360_3fae));
        uVar19 = (ulong)uVar13;
      }
      else {
        uVar14 = FUN_1681_05c0(iVar17,-*(int *)(iVar10 + -0x16));
        uVar13 = FUN_1609_05a6((DAT_3360_3fae + 0x10e) % 0x168,1,uVar14);
        uVar19 = (ulong)uVar13;
      }
    }
    if (10 < *(int *)(iVar10 + -0x16)) {
      if (((DAT_3360_3da8._1_1_ & 1) == 0) && (*(int *)(iVar10 + -0x10) == 0)) {
        iVar17 = FUN_1681_05c0(iVar22,*(int *)(iVar10 + -0x16) >> 1);
        uVar13 = FUN_1c30_0068(iVar17 + DAT_3360_3fae);
        uVar19 = (ulong)uVar13;
      }
      else {
        uVar14 = FUN_1681_05c0(iVar17,*(undefined2 *)(iVar10 + -0x16));
        uVar13 = FUN_1609_05a6((DAT_3360_3fae + 0x5a) % 0x168,1,uVar14);
        uVar19 = (ulong)uVar13;
      }
    }
    *(byte *)(iVar10 + -2) = *(byte *)(iVar10 + -2) | *(byte *)(iVar10 + -0x12);
    uVar19 = CONCAT31((int3)(uVar19 >> 8),*(byte *)(iVar10 + -0x10));
    *(byte *)(iVar10 + -1) = *(byte *)(iVar10 + -1) | *(byte *)(iVar10 + -0x10);
  }
  if (*(char *)(iVar10 + -2) != '\0') {
    uVar13 = FUN_17f5_0c58(0,(int)CONCAT31((int3)(uVar19 >> 8),DAT_3360_0ae1 == '\0'));
    uVar19 = (ulong)uVar13;
    if ((char)uVar13 != '\0') {
      uVar13 = FUN_1609_05fe();
      uVar19 = (ulong)uVar13;
    }
  }
  if ((*(char *)(iVar10 + -1) != '\0') &&
     (uVar19 = CONCAT31((int3)(uVar19 >> 8),*(char *)(iVar10 + -1)),
     DAT_3360_0ae0 != *(char *)(iVar10 + -1))) {
    uVar13 = FUN_1000_06fa();
    uVar19 = (ulong)uVar13;
  }
  DAT_3360_0ae1 = *(undefined1 *)(iVar10 + -2);
  DAT_3360_0ae0 = *(undefined1 *)(iVar10 + -1);
  return (undefined1 *)(undefined1 *)CONCAT31((int3)(uVar19 >> 8),*(undefined1 *)(iVar10 + -1));
}

