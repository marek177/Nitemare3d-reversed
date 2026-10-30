
/* WARNING: Instruction at (ram,0x0001ff63) overlaps instruction at (ram,0x0001ff62)
    */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint __cdecl16far FUN_17f5_0db0(int param_1,int param_2,undefined2 *param_3,uint *param_4)

{
  int *piVar1;
  byte *pbVar2;
  undefined1 uVar3;
  byte bVar4;
  undefined2 uVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  undefined2 *puVar9;
  ulong uVar10;
  long lVar11;
  sbyte sVar12;
  int iVar13;
  uint uVar14;
  int iVar15;
  char cVar16;
  byte bVar19;
  int *piVar17;
  int iVar18;
  byte *pbVar20;
  int *piVar21;
  undefined1 *puVar22;
  undefined1 *puVar23;
  int *unaff_DI;
  char *pcVar24;
  char *pcVar25;
  uint *puVar26;
  uint in_stack_00000000;
  uint in_stack_00000002;
  undefined1 local_b0 [128];
  undefined1 local_30 [6];
  undefined4 uStack_2a;
  undefined4 uStack_26;
  undefined4 uStack_22;
  undefined4 uStack_1e;
  undefined2 uStack_1a;
  uint uStack_18;
  int iStack_16;
  undefined1 uStack_14;
  undefined1 uStack_13;
  int iStack_12;
  char *pcStack_10;
  undefined1 uStack_e;
  char cStack_d;
  char cStack_c;
  undefined1 uStack_b;
  int *piStack_a;
  undefined2 uStack_6;
  undefined1 uStack_4;
  bool bStack_3;
  
  uVar5 = DAT_3360_0018._2_2_;
  piVar21 = (int *)0x0;
  if (9 < param_1 - 2U) {
    piStack_a = (int *)0x8da6;
    FUN_17f5_05ca();
    piStack_a = (int *)0x0;
    cStack_c = 0xf5;
    uStack_b = 0x17;
    uStack_e = 0xb5;
    cStack_d = 0x8d;
    uVar8 = FUN_1bdd_03e6();
    return uVar8;
  }
  pcVar24 = (char *)0x1000;
  puVar26 = (uint *)((ulong)param_3 >> 0x10);
  iVar18 = (int)DAT_3360_43a6 >> 0xf;
  piVar17 = (int *)((param_1 - 2U) * 2);
  switch(param_1) {
  case 2:
    do {
      if (piVar17[3] < (int)unaff_DI) {
        do {
          if (((undefined2 *)uStack_26)[1] != 0) {
            cStack_c = '\x02';
            uStack_b = 0x27;
            piStack_a = (int *)pcVar24;
            FUN_1200_0410();
          }
          piVar21 = piVar17 + 9;
          iVar18 = uStack_2a._2_2_ + 1;
          uStack_2a = CONCAT22(iVar18,(undefined2)uStack_2a);
          if ((int)DAT_3360_4bba <= iVar18) {
            return DAT_3360_4bba;
          }
          iVar18 = *piVar21;
          uStack_26 = (undefined2 *)
                      CONCAT22(uStack_26._2_2_,
                               (undefined2 *)&DAT_3360_4166 + (uint)*(byte *)(iVar18 + 4) * 4);
          uVar8 = (uint)*(byte *)(iVar18 + 3);
          iStack_16 = uVar8 * 10 + ((undefined2 *)&DAT_3360_416c)[(uint)*(byte *)(iVar18 + 4) * 4];
          lVar11 = *(long *)(iStack_16 + 6);
          uStack_1a = (undefined2)lVar11;
          uStack_18 = (uint)((ulong)lVar11 >> 0x10);
          if (lVar11 == 0) {
            pcVar24 = (char *)0x1739;
            piStack_a = (int *)0x2546;
            uStack_1a = FUN_1739_0316();
            uStack_18 = uVar8;
          }
          if ((*(char *)(iVar18 + 6) == '\x02') ||
             ((*(char *)(iVar18 + 7) != '\0' && (*(char *)(iVar18 + 7) != '\x03')))) {
            uStack_13 = 0;
          }
          else {
            uStack_13 = 1;
          }
          iVar13 = DAT_3360_60ce;
          if (((0 < DAT_3360_60ce) && (DAT_3360_4164 == '\0')) &&
             ((*(char *)(iVar18 + 7) == '\0' || (*(char *)(iVar18 + 7) == '\x01')))) {
            iVar13 = 0;
          }
          bStack_3 = (bool)((*(byte *)(iVar18 + 5) & 0x20) >> 5);
          if ((*(char *)(iVar18 + 6) == '@') || (*(char *)(iVar18 + 6) == '?')) {
            bStack_3 = bStack_3 == false;
          }
          if ((*(char *)(iVar18 + 7) == '\0') || (*(char *)(iVar18 + 7) == '\x01')) {
            if (bStack_3 == false) {
              iVar15 = DAT_3360_3fba - *(int *)(iVar18 + 0xc);
            }
            else {
              iVar15 = (DAT_3360_3fba - *(int *)(iVar18 + 0x10)) + 0x80;
            }
            iVar7 = DAT_3360_3fbc - *(int *)(iVar18 + 0xe);
          }
          else {
            if (bStack_3 == false) {
              iVar15 = *(int *)(iVar18 + 0xe) - DAT_3360_3fbc;
            }
            else {
              iVar15 = (*(int *)(iVar18 + 0x12) - DAT_3360_3fbc) + -0x80;
            }
            iVar7 = *(int *)(iVar18 + 0xc) - DAT_3360_3fba;
          }
          uStack_22 = (int *)CONCAT22(iVar15,(int *)uStack_22);
          uStack_26 = (undefined2 *)CONCAT22(iVar18,(undefined2 *)uStack_26);
          if (DAT_3360_3fb4 == 0) {
            lVar11 = (long)iVar7 * (long)DAT_3360_400a;
            uVar5 = (undefined2)lVar11;
          }
          else {
            lVar11 = (long)iVar7 * (long)DAT_3360_4008;
            uVar5 = (undefined2)lVar11;
          }
          uStack_e = (undefined1)uVar5;
          cStack_d = (char)((uint)uVar5 >> 8);
          cStack_c = (char)((ulong)lVar11 >> 0x10);
          uStack_b = (undefined1)((ulong)lVar11 >> 0x18);
          pcStack_10 = (char *)0x1;
          uStack_1e = CONCAT22(piVar17[0xc] + -3,iVar13);
          iStack_12 = 0;
          unaff_DI = (int *)piVar17[10];
          piVar1 = piVar17 + 0xc;
          piVar17 = piVar21;
        } while (*piVar1 < (int)unaff_DI);
        uStack_22 = (int *)CONCAT22(iVar15,piVar21);
      }
      iVar18 = ((int *)uStack_22)[8];
      *(long *)((int *)uStack_22 + 7) =
           *(long *)((int *)uStack_22 + 7) + *(long *)((int *)uStack_22 + 5);
      cStack_c = (char)unaff_DI;
      cVar16 = cStack_c;
      uStack_b = (undefined1)((uint)unaff_DI >> 8);
      uVar3 = uStack_b;
      uStack_e = *(undefined1 *)(uStack_26._2_2_ + 7);
      cStack_d = 0;
      pcVar25 = (char *)s_Bad_color_code_in_instr_3360_1c21 + 0xf;
      iStack_12 = 0x2689;
      pcStack_10 = pcVar24;
      piStack_a = (int *)iVar18;
      FUN_1c30_070c();
      cStack_c = (char)((ulong)uStack_26 >> 0x10);
      uStack_b = (undefined1)((ulong)uStack_26 >> 0x18);
      uStack_e = 0x30;
      cStack_d = '\x1c';
      pcStack_10 = (char *)0x26aa;
      piStack_a = unaff_DI;
      iVar13 = FUN_1200_02bc();
      *piStack_a = iVar18 + DAT_3360_43aa;
      pcStack_10 = (char *)((int)pcStack_10 - 1);
      if ((pcStack_10 == (char *)0x0) || (iStack_12 != iVar13)) {
        piStack_a = (int *)uStack_1e;
        uStack_e = (undefined1)iVar13;
        cStack_d = (char)((uint)iVar13 >> 8);
        iStack_12 = uStack_1a;
        pcStack_10 = (char *)uStack_18;
        uStack_14 = 0x30;
        uStack_13 = 0x1c;
        pcVar25 = (char *)s__3Unfortunately_the_blast_impact_3360_10e4 + 0x71;
        iStack_16 = 0x26d7;
        cStack_c = cVar16;
        uStack_b = uVar3;
        pcStack_10 = (char *)FUN_1155_04d0();
      }
      unaff_DI = (int *)((int)unaff_DI + 1);
      piVar17 = (int *)uStack_22;
      pcVar24 = pcVar25;
      iStack_12 = iVar13;
    } while( true );
  case 3:
    cVar16 = (char)DAT_3360_0002;
    do {
      piStack_a = (int *)(int)cVar16;
      cStack_c = (char)pcVar24;
      uStack_b = (undefined1)((uint)pcVar24 >> 8);
      pcVar24 = (char *)0x1a9e;
      uStack_e = 0x4b;
      cStack_d = 0xf;
      uVar8 = FUN_1a9e_0152();
      uVar10 = (ulong)uVar8;
      *(char *)(piVar21 + 2) = (char)piVar21[2] + -1;
      do {
        do {
          piVar17 = piVar21;
          piVar21 = piVar17 + 3;
          unaff_DI = (int *)((int)unaff_DI + 1);
          if (*(int *)0x4 <= (int)unaff_DI) {
            return (uint)uVar10;
          }
        } while ((char)piVar17[5] == '\0');
        iVar18 = *piVar21 * 0x1c;
        uVar8 = (int)(char)piVar17[4] + *(int *)(iVar18 + 0x16);
        pcStack_10 = (char *)((int)*(char *)((int)piVar17 + 9) + *(int *)(iVar18 + 0x18));
        iVar13 = ((uint)pcStack_10 & 0xffc0) * 2 + ((int)(uVar8 & 0xffdf) >> 5);
        uStack_18 = iVar13 + 0x373e;
        iStack_16 = 0x2dec;
        uVar10 = *(ulong *)(iVar18 + 0x12);
      } while ((CONCAT22(0x2dec,uStack_18) != uVar10) &&
              ((((undefined1 *)&DAT_3360_cf52)[*(byte *)(iVar13 + 0x373f)] & 6) != 0));
      if (*(long *)(iVar18 + 0x12) != CONCAT22(0x2dec,uStack_18)) {
        *(undefined1 *)(iVar13 + 0x373f) = *(undefined1 *)((int)*(undefined4 *)(iVar18 + 0x12) + 1);
        *(undefined1 *)((int)*(undefined4 *)(iVar18 + 0x12) + 1) = 0;
      }
      *(uint *)(iVar18 + 0x16) = uVar8;
      *(uint *)(iVar18 + 0x18) = (uint)pcStack_10;
      *(undefined4 *)(iVar18 + 0x12) = CONCAT22(0x2dec,uStack_18);
      cVar16 = (char)piVar17[4];
    } while( true );
  case 4:
    piStack_a = (int *)0x8f18;
    FUN_1cdc_0720();
    piStack_a = (int *)((char *)s__d_of__d_3360_1cd8 + 4);
    cStack_c = 0x28;
    uStack_b = 0x8f;
    FUN_1bdd_03e6();
    FUN_1bdd_0270();
    iVar18 = 0;
    puVar9 = (undefined2 *)0x264e;
    piStack_a = (int *)0x2dec;
    if ((int)DAT_3360_60cc < 1) {
      return 0x264e;
    }
    do {
      uVar5 = DAT_3360_245c;
      iVar13 = puVar9[4] * 0x1c;
      if (((undefined1 *)&DAT_3360_d154)[*(byte *)*(undefined4 *)(iVar13 + 0x12)] == 'F') {
        *(undefined1 *)((int)puVar9 + 0xb) = 0x14;
        *(undefined1 *)(puVar9 + 6) = *(undefined1 *)(iVar13 + 10);
        puVar9[3] = 0x70;
        *(undefined1 *)((int)puVar9 + 0x13) = 3;
        iVar18 = -0x7063;
        uVar3 = FUN_10f6_008a();
        *(undefined1 *)(iVar13 + 10) = uVar3;
        cVar16 = *(char *)(iVar13 + 0xc);
        if (cVar16 == '\t') {
          uVar5 = *(undefined2 *)
                   (((undefined2 *)&DAT_3360_3b7a)[(uint)*(byte *)(iVar13 + 10) * 4] + 4);
LAB_17f5_10ab:
          *puVar9 = uVar5;
        }
        else {
          if (cVar16 == '\v') {
            uVar5 = *(undefined2 *)
                     (((undefined2 *)&DAT_3360_3b7a)[(uint)*(byte *)(iVar13 + 10) * 4] + 0x24);
            goto LAB_17f5_10ab;
          }
          if (cVar16 == '\f') {
            uVar5 = *(undefined2 *)
                     (((undefined2 *)&DAT_3360_3b7a)[(uint)*(byte *)(iVar13 + 10) * 4] + 0x14);
            goto LAB_17f5_10ab;
          }
        }
        *(undefined1 *)(iVar13 + 9) = *(undefined1 *)puVar9;
      }
      puVar9 = puVar9 + 0xd;
      iVar18 = iVar18 + 1;
      if ((int)DAT_3360_60cc <= iVar18) {
        return DAT_3360_60cc;
      }
    } while( true );
  case 5:
    do {
      piStack_a = (int *)0xff65;
      uVar8 = FUN_1f85_0178();
      uStack_22._2_2_ = (int *)((int)unaff_DI + 1);
      piVar21 = piVar21 + 1;
      if (cStack_d == '\0') break;
LAB_1f85_0700:
      if (DAT_3360_5656 <= (int)uStack_22._2_2_) break;
      unaff_DI = uStack_22._2_2_;
      uVar8 = uStack_1e._2_2_;
    } while (*(int *)(*piVar21 + 0x10) < (int)uStack_1e._2_2_);
    break;
  case 6:
    uVar5 = DAT_3360_012c;
    if (param_2 != 0) {
      uVar5 = DAT_3360_012a;
    }
    puVar22 = (undefined1 *)((in_stack_00000002 & 0xff) * 0x50 + (in_stack_00000000 >> 2));
    out(0x3c4,2);
    bVar4 = (byte)in_stack_00000000 & 3;
    out(0x3c5,'\x11' << bVar4 | 0x11U >> 8 - bVar4);
    uVar8 = CONCAT11((undefined1)param_1,(byte)in_stack_00000000) & 0xff03;
    pbVar20 = (byte *)((undefined2 *)param_3 + 1);
    cVar16 = (char)*param_3;
    bVar19 = (byte)((char)((uint)*param_3 >> 8) + 7U) >> 3;
    bVar4 = bVar19;
    puVar23 = puVar22;
    do {
      do {
        pbVar2 = pbVar20;
        pbVar20 = pbVar20 + 1;
        sVar12 = (sbyte)uVar8;
        uVar14 = (uint)*pbVar2 << sVar12;
        uVar6 = uVar14 | *pbVar2 >> 0x10 - sVar12;
        out(0x3c5,(char)uVar6);
        uVar3 = (undefined1)(uVar8 >> 8);
        *puVar22 = uVar3;
        out(0x3c5,(char)(uVar6 >> 4));
        puVar22[1] = uVar3;
        puVar22 = puVar22 + 2;
        out(0x3c5,(char)(uVar14 >> 8));
        *puVar22 = uVar3;
        bVar4 = bVar4 - 1;
      } while (bVar4 != 0);
      puVar22 = puVar23 + 0x50;
      cVar16 = cVar16 + -1;
      bVar4 = bVar19;
      puVar23 = puVar22;
    } while (cVar16 != '\0');
    return uVar14 >> 8;
  case 7:
    lVar11 = (long)DAT_3360_400a * ((0x4000 - uStack_2a) / (long)DAT_3360_4008);
    uVar8 = (uint)lVar11;
    uVar14 = (uint)((long)DAT_3360_4008 * (long)uStack_22);
    iVar13 = ((int)((ulong)lVar11 >> 0x10) -
             (int)((ulong)((long)DAT_3360_4008 * (long)uStack_22) >> 0x10)) - (uint)(uVar8 < uVar14)
    ;
    cStack_c = (char)DAT_3360_3522;
    uStack_b = (undefined1)((ulong)DAT_3360_3522 >> 8);
    piStack_a = (int *)((ulong)DAT_3360_3522 >> 0x10);
    uStack_e = (undefined1)iVar13;
    cStack_d = (char)((uint)iVar13 >> 8);
    lVar11 = (CONCAT13(cStack_d,CONCAT12(uStack_e,uVar8 - uVar14)) * DAT_3360_3522) /
             CONCAT22(pcStack_10,iStack_12);
    uVar8 = (uint)lVar11;
    DAT_3360_0014._0_2_ = uVar8 + DAT_3360_43a6;
    uVar8 = (int)((ulong)lVar11 >> 0x10) + iVar18 + (uint)CARRY2(uVar8,DAT_3360_43a6);
    if (((int)uVar8 < -1) || ((0x7fff < uVar8 && ((uint)DAT_3360_0014 < 0xc001)))) {
      DAT_3360_0014._0_2_ = 0xc001;
    }
    else if ((-1 < (int)uVar8) && ((0 < (int)uVar8 || (0x3fff < (uint)DAT_3360_0014)))) {
      DAT_3360_0014._0_2_ = 0x3fff;
    }
    if (CONCAT13(uStack_13,CONCAT12(uStack_14,iStack_16)) == 0x4000) {
      if (CONCAT22(iStack_12,piStack_a) == CONCAT13(uStack_b,CONCAT12(cStack_c,iVar13))) {
        if ((DAT_3360_3fae == 0x5a) || (DAT_3360_3fae == 0x10e)) {
          uStack_1e = 0x4000;
        }
        else {
          uStack_1e = (0x4000 - CONCAT22(uStack_18,uStack_1a)) / (long)DAT_3360_400a;
          iStack_12 = DAT_3360_400a;
        }
      }
      else if ((DAT_3360_3fae == 0) || (DAT_3360_3fae == 0xb4)) {
        piStack_a = (int *)0x4000;
        iStack_12 = 0;
      }
      else {
        lVar11 = (0x4000 - (long)uStack_26) / (long)DAT_3360_4008;
        piStack_a = (int *)lVar11;
        iStack_12 = (int)((ulong)lVar11 >> 0x10);
      }
      lVar11 = (long)DAT_3360_400a * CONCAT22(iStack_12,piStack_a);
      uVar8 = (uint)lVar11;
      iVar13 = (int)((ulong)lVar11 >> 0x10);
      lVar11 = DAT_3360_4008 * uStack_1e;
    }
    else {
      lVar11 = (long)DAT_3360_400a * CONCAT22(iStack_12,piStack_a);
      uVar8 = (uint)lVar11;
      iVar13 = (int)((ulong)lVar11 >> 0x10);
      lVar11 = DAT_3360_4008 * uStack_1e;
    }
    iVar13 = (iVar13 - (int)((ulong)lVar11 >> 0x10)) - (uint)(uVar8 < (uint)lVar11);
    uStack_6 = (undefined2)(CONCAT13(uStack_13,CONCAT12(uStack_14,iStack_16)) >> 0x10);
    uStack_e = (undefined1)iVar13;
    cStack_d = (char)((uint)iVar13 >> 8);
    lVar11 = (CONCAT13(cStack_d,CONCAT12(uStack_e,uVar8 - (uint)lVar11)) * DAT_3360_3522) /
             CONCAT22(uStack_6,iStack_16);
    uVar8 = (uint)lVar11;
    uVar14 = uVar8 + DAT_3360_43a6;
    uVar8 = (int)((ulong)lVar11 >> 0x10) + iVar18 + (uint)CARRY2(uVar8,DAT_3360_43a6);
    if (((int)uVar8 < -1) || ((0x7fff < uVar8 && (uVar14 < 0xc001)))) {
      uVar14 = 0xc001;
    }
    else if ((-1 < (int)uVar8) && ((0 < (int)uVar8 || (0x3fff < uVar14)))) {
      uVar14 = 0x3fff;
    }
    uVar8 = uVar14;
    if ((int)uVar14 < (int)(uint)DAT_3360_0014) {
      DAT_3360_0018._2_2_ = DAT_3360_0014._2_2_;
      DAT_3360_0014._2_2_ = uVar5;
      uVar8 = (uint)DAT_3360_0014;
      DAT_3360_0014._0_2_ = uVar14;
    }
    if (DAT_3360_43a0 < (int)(uint)DAT_3360_0014) {
      *(uint *)(param_1 + 0x18) = uVar8;
    }
    else {
      DAT_3360_0018._0_2_ = uVar8;
      if (DAT_3360_439e <= (int)uVar8) {
        return 1;
      }
    }
    return 0;
  case 8:
    bVar4 = in(3);
    uVar8 = (uint)bVar4;
    if (cStack_c != '\0') {
      iVar18 = (int)uStack_1e;
      do {
        if ((iVar18 < 0) || (uVar8 = uStack_18, *(int *)(*piVar21 + 0xc) <= (int)uStack_18)) break;
        piStack_a = (int *)0xff31;
        uVar8 = FUN_1f85_0178();
        iVar18 = iVar18 + -1;
        piVar21 = piVar21 + -1;
      } while (cStack_c != '\0');
    }
    piVar21 = (undefined2 *)&DAT_3360_5e26 + (int)uStack_22._2_2_;
    if (cStack_d != '\0') goto LAB_1f85_0700;
    break;
  case 9:
    if (DAT_3360_3b64 < 0) {
      DAT_3360_3b64 = FUN_1cdc_21f4(0x1000,1);
      uVar8 = FUN_1cdc_1676();
    }
    else {
      FUN_1273_0c80(DAT_3360_3b64,(char *)s_user_sav_3360_1ea5,local_30);
      FUN_219b_2888(local_b0,(char *)s_About_to__s_game____s__Press_ESC_3360_1eb3,0x1eae,local_30);
      uVar8 = FUN_1cdc_0720(local_b0);
      if ((char)uVar8 != '\x1b') {
        FUN_1273_10a8(DAT_3360_3b64,(char *)s_user_sav_3360_1ee0);
        FUN_1273_15a0(5);
        FUN_17f5_05ca(1);
        FUN_1b91_018e();
        FUN_1273_15a0(5);
        uVar8 = FUN_17f5_05ca(1);
        return uVar8;
      }
    }
    return uVar8;
  case 10:
    FUN_1bdd_00b4();
    FUN_1681_0194();
    FUN_1681_013c();
    FUN_1b91_0008();
    uVar8 = FUN_1739_0028();
    return uVar8;
  case 0xb:
    lVar11 = ((long)(int)((0x4000 - CONCAT13(uStack_b,CONCAT12(cStack_c,CONCAT11(cStack_d,uStack_e))
                                            )) / (long)DAT_3360_4008) * (long)DAT_3360_400a *
             DAT_3360_3522) / 0x4000;
    uVar8 = (uint)lVar11;
    iVar13 = uVar8 + DAT_3360_43a6;
    iVar18 = (int)((ulong)lVar11 >> 0x10) + iVar18 + (uint)CARRY2(uVar8,DAT_3360_43a6);
    uStack_4 = (undefined1)iVar18;
    bStack_3 = SUB21((uint)iVar18 >> 8,0);
    uVar8 = (int)(DAT_3360_352a / 0x4000) + DAT_3360_43aa;
    *param_4 = uVar8;
    if (CONCAT13(bStack_3,CONCAT12(uStack_4,iVar13)) < -0x3fff) {
      *puVar26 = 0xc001;
      return uVar8;
    }
    lVar11 = CONCAT13(bStack_3,CONCAT12(uStack_4,iVar13));
    if (0x3fff < lVar11) {
      lVar11 = 0x3fff;
    }
    *puVar26 = (uint)lVar11;
    return (uint)lVar11;
  }
  DAT_3360_4bbc = DAT_3360_4bbc + -1;
  DAT_3360_4bbe = DAT_3360_4bbe + 1;
  DAT_3360_4bc0 = DAT_3360_4bc0 + -1;
  DAT_3360_4bc2 = DAT_3360_4bc2 + 1;
  return uVar8;
}

