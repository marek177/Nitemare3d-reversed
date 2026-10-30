
/* WARNING: Instruction at (ram,0x00017dfd) overlaps instruction at (ram,0x00017dfc)
    */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined1 * __cdecl16far
FUN_17f5_2966(uint param_1,undefined2 param_2,undefined2 param_3,undefined2 param_4)

{
  byte *pbVar1;
  byte bVar2;
  undefined2 uVar3;
  bool bVar4;
  char cVar5;
  char cVar6;
  int iVar7;
  int *piVar8;
  undefined1 *puVar9;
  undefined1 *puVar10;
  undefined1 *puVar11;
  int iVar12;
  undefined1 *puVar13;
  int iVar14;
  uint uVar15;
  uint in_BX;
  byte *unaff_SI;
  undefined1 *unaff_DI;
  undefined1 *unaff_ES;
  char *pcVar16;
  char *pcVar17;
  undefined1 *unaff_SS;
  char cStackY_1a9;
  undefined4 local_1a8;
  undefined4 uStackY_18;
  int *in_stack_0000ffec;
  byte *in_stack_0000fff0;
  char *pcVar18;
  undefined1 uVar19;
  undefined1 uStack_9;
  undefined1 *local_6;
  undefined2 uStack_4;
  
  if (5 < param_1) {
    return puVar9;
  }
  piVar8 = (int *)(param_1 * 2);
  puVar11 = (undefined1 *)(ulong)in_BX;
  pcVar17 = (char *)0x1000;
  switch(param_1) {
  case 0:
    cVar5 = (char)((ulong)local_6 >> 0x10);
    if ((unaff_SI[0x14] == 0) ||
       ((cVar6 = FUN_1499_0244(), cVar6 == '\0' && (cVar6 = FUN_1499_0244(), cVar6 == '\0')))) {
      bVar4 = false;
    }
    else {
      bVar4 = true;
    }
    if (cVar5 == '\0') {
      iVar14 = (int)(char)unaff_SI[0x13];
    }
    else {
      iVar14 = 0;
    }
    if (bVar4) {
      iVar7 = 0;
    }
    else {
      iVar7 = (int)(char)unaff_SI[0x14];
    }
    if ((unaff_SI[0xb] != 8) || ((cVar5 == '\0' && (!bVar4)))) {
      FUN_1609_04b6((int)*(undefined4 *)(unaff_DI + 0x10),
                    (int)((ulong)*(undefined4 *)(unaff_DI + 0x10) >> 0x10),iVar14,(char)iVar7);
      *(int *)(unaff_DI + 0x10) = *(int *)(unaff_DI + 0x10) + iVar14;
      *(int *)(unaff_DI + 0x12) = *(int *)(unaff_DI + 0x12) + iVar7;
      FUN_1a9e_0152();
    }
    if (((unaff_SI[0xb] == 6) && (cVar5 != '\0')) && (bVar4)) {
      iVar14 = 0x4f73;
      uVar15 = FUN_1f67_019e();
      if ((uVar15 & 1) == 0) {
        iVar7 = -(int)(char)unaff_SI[0x14];
        unaff_SI[0x14] = (byte)iVar7;
      }
      else {
        iVar14 = -(int)(char)unaff_SI[0x13];
        unaff_SI[0x13] = (byte)iVar14;
      }
    }
    if (((iVar14 != 0) || (iVar7 != 0)) &&
       (unaff_DI[3] = unaff_DI[3] + '\x01',
       (uint)unaff_SI[1] + (uint)*unaff_SI <= (uint)(byte)unaff_DI[3])) {
      unaff_DI[3] = *unaff_SI;
    }
    FUN_1499_00ac();
    iVar14 = (*(uint *)(unaff_DI + 0x12) & 0xffc0) * 2 +
             ((int)(*(uint *)(unaff_DI + 0x10) & 0xffdf) >> 5);
    *(int *)(unaff_DI + 0xc) = iVar14 + 0x373e;
    *(undefined2 *)(unaff_DI + 0xe) = 0x2dec;
    unaff_SI[0xd] = *(byte *)(iVar14 + 0x373f);
    *(undefined1 *)(iVar14 + 0x373f) = *unaff_DI;
    iVar14 = FUN_10f6_017c((int)*(undefined4 *)(unaff_DI + 0xc),
                           (char)((ulong)*(undefined4 *)(unaff_DI + 0xc) >> 0x10));
    puVar9 = (undefined1 *)0x0;
    if (iVar14 + 1 != 0) {
      puVar9 = (undefined1 *)CONCAT11((char)((uint)(iVar14 + 1) >> 8),(byte)iVar14);
      unaff_SI[0xe] = (byte)iVar14;
    }
    return puVar9;
  case 1:
    do {
      if (0x3f < (int)piVar8) {
        return (undefined1 *)puVar11;
      }
      iVar14 = 0;
      uVar19 = SUB21(piVar8,0);
      uStack_9 = (undefined1)((uint)piVar8 >> 8);
      do {
        uStackY_18 = (byte *)CONCAT22(DAT_3360_2452,in_stack_0000fff0);
        if ((((undefined1 *)&DAT_3360_ce52)[*in_stack_0000fff0] & 8) != 0) {
          pcVar16 = pcVar17;
          if (0x3f < *in_stack_0000ffec) {
            uVar19 = 0x40;
            uStack_9 = 0;
            pcVar16 = (char *)s_Copyright_1992__David_P_Gray__Gr_3360_1f3f + 0x28;
            in_stack_0000fff0 = (byte *)((char *)s_Error_opening_file__s_3360_0253 + 0x12);
            FUN_1f67_000a(0x72);
          }
          iVar7 = *in_stack_0000ffec * 0x12;
          piVar8 = (int *)(iVar7 + 0x3076);
          *in_stack_0000ffec = *in_stack_0000ffec + 1;
          ((int *)CONCAT22(0x2dec,piVar8))[0] = 0;
          ((int *)CONCAT22(0x2dec,piVar8))[1] = 0;
          uStack_4._1_1_ = '\0';
          if (DAT_3360_60c4 < 1) {
            puVar9 = (undefined1 *)&DAT_3360_60f2;
            uStack_4 = 0;
            iVar12 = uStack_4;
          }
          else {
            puVar9 = (undefined1 *)&DAT_3360_60f2;
            iVar12 = 0;
            do {
              if ((((puVar9[5] & 8) != 0) && (*(int *)(puVar9 + 0xc) >> 6 == iVar14)) &&
                 (*(int *)(puVar9 + 0xe) >> 6 == CONCAT11(uStack_9,uVar19))) {
                *(undefined1 **)CONCAT22(0x2dec,piVar8) = puVar9;
                break;
              }
              puVar9 = puVar9 + 0x1c;
              iVar12 = iVar12 + 1;
            } while (iVar12 < DAT_3360_60c4);
          }
          puVar9 = puVar9 + 0x1c;
          iVar12 = iVar12 + 1;
          if (iVar12 < DAT_3360_60c4) {
            do {
              if ((((puVar9[5] & 8) != 0) && (*(int *)(puVar9 + 0xc) >> 6 == iVar14)) &&
                 (*(int *)(puVar9 + 0xe) >> 6 == CONCAT11(uStack_9,uVar19))) {
                *(undefined2 *)(iVar7 + 0x3078) = puVar9;
                break;
              }
              puVar9 = puVar9 + 0x1c;
              iVar12 = iVar12 + 1;
            } while (iVar12 < DAT_3360_60c4);
          }
          if (*piVar8 == 0) {
LAB_1000_0328:
            uVar19 = 0x89;
            uStack_9 = 0;
            pcVar17 = (char *)s_Copyright_1992__David_P_Gray__Gr_3360_1f3f + 0x28;
            FUN_1f67_000a();
            pcVar18 = pcVar16;
          }
          else {
            pcVar17 = pcVar16;
            pcVar18 = (char *)0x2dec;
            if (*(int *)(iVar7 + 0x3078) == 0) goto LAB_1000_0328;
          }
          *(undefined4 *)(iVar7 + 0x307a) = uStackY_18;
          *(undefined2 *)(iVar7 + 0x307e) = 1;
          *(undefined1 *)(iVar7 + 0x3086) = 0;
          if (((*(char *)(*piVar8 + 7) == '\0') &&
              ((((undefined1 *)&DAT_3360_ce52)[in_stack_0000fff0[2]] & 8) != 0)) ||
             ((*(char *)(*piVar8 + 7) == '\x02' &&
              ((((undefined1 *)&DAT_3360_ce52)[in_stack_0000fff0[0x80]] & 8) != 0)))) {
            uStack_4._1_1_ = '\x01';
          }
          if (uStack_4._1_1_ == '\0') {
            uVar3 = *(undefined2 *)(puVar9 + 0xc);
          }
          else {
            uVar3 = *(undefined2 *)(puVar9 + 0x10);
          }
          *(undefined2 *)(iVar7 + 0x3082) = uVar3;
          if (uStack_4._1_1_ == '\0') {
            uVar3 = *(undefined2 *)(puVar9 + 0xe);
          }
          else {
            uVar3 = *(undefined2 *)(puVar9 + 0x12);
          }
          *(undefined2 *)(iVar7 + 0x3084) = uVar3;
          puVar11 = (undefined1 *)
                    ((ulong)CONCAT11((char)((uint)uVar3 >> 8),
                                     uStack_4._1_1_ << 5 ^ *(byte *)(*piVar8 + 5)) & 0xffffff20);
          pbVar1 = (byte *)(*piVar8 + 5);
          *pbVar1 = *pbVar1 ^ (byte)puVar11;
          pbVar1 = (byte *)(*(int *)(iVar7 + 0x3078) + 5);
          *pbVar1 = *pbVar1 ^ (uStack_4._1_1_ << 5 ^ *(byte *)(*(int *)(iVar7 + 0x3078) + 5)) & 0x20
          ;
        }
        in_stack_0000fff0 = in_stack_0000fff0 + 2;
        iVar14 = iVar14 + 1;
      } while (iVar14 < 0x40);
      piVar8 = (int *)(CONCAT11(uStack_9,uVar19) + 1);
    } while( true );
  case 3:
    FUN_206c_0004(0x39);
    puVar9 = (undefined1 *)FUN_1bdd_0082();
    return puVar9;
  case 4:
    FUN_144e_006e();
    FUN_1681_0194(0);
    FUN_144e_006e(0x83c);
    FUN_1273_031a(1);
    FUN_17f5_05ca(0);
    FUN_1273_028a();
    FUN_1273_0a80();
    DAT_3360_3b6b = 0;
    puVar9 = (undefined1 *)FUN_144e_006e(0x846);
    return puVar9;
  case 5:
switchD_1000_a8c6_caseD_5:
    iVar14 = DAT_3360_07a4 + (uint)CARRY2((uint)(undefined1 *)puVar11,piVar8[1]);
    *(undefined1 **)(unaff_SI + 8) = (undefined1 *)puVar11 + piVar8[1];
    *(int *)(unaff_SI + 10) = iVar14;
LAB_17a5_03c2:
    local_6 = (undefined1 *)CONCAT22(uStack_4,unaff_ES);
    FUN_17a5_026e((char)unaff_DI);
    uVar15 = *(int *)(unaff_SI + 0x10) - DAT_3360_3fba >> 0xf;
    if ((int)((*(int *)(unaff_SI + 0x10) - DAT_3360_3fba ^ uVar15) - uVar15) < 0x15) {
      uVar15 = *(int *)(unaff_SI + 0x12) - DAT_3360_3fbc >> 0xf;
      puVar10 = (undefined1 *)((*(int *)(unaff_SI + 0x12) - DAT_3360_3fbc ^ uVar15) - uVar15);
      if ((int)puVar10 < 0x15) goto LAB_17a5_043b;
    }
    do {
      puVar10 = (undefined1 *)FUN_1a9e_0428(unaff_SI,(char)unaff_ES);
LAB_17a5_043b:
      while( true ) {
        do {
          puVar13 = unaff_DI;
          unaff_DI = puVar13 + 0x2a;
          uVar15 = uStack_4 - 1;
          local_6 = (undefined1 *)((ulong)uVar15 << 0x10);
          if (uVar15 == 0) {
            return puVar10;
          }
          unaff_SI = puVar13 + 0x38;
          unaff_ES = (undefined1 *)&DAT_3360_3360;
          bVar2 = puVar13[0x3c];
          piVar8 = (undefined2 *)&DAT_3360_3b76 + (uint)bVar2 * 4;
          if ((byte)puVar13[0x36] == 1) {
            if (_DAT_3360_07a2 < *(ulong *)(puVar13 + 0x40)) goto LAB_17a5_03c2;
            puVar13[0x3b] = puVar13[0x3b] + '\x01';
            if (*piVar8 <= (int)(uint)(byte)puVar13[0x3b]) {
              puVar13[0x3b] = 0;
            }
            puVar11 = (undefined1 *)(_DAT_3360_07a2 & 0xffff);
            goto switchD_1000_a8c6_caseD_5;
          }
          puVar10 = (undefined1 *)((byte)puVar13[0x36] - 2);
        } while (puVar10 != (undefined1 *)0x0);
        if (*(ulong *)(puVar13 + 0x40) <= _DAT_3360_07a2) {
          puVar13[0x3b] = puVar13[0x3b] + '\x01';
          iVar14 = DAT_3360_07a4 +
                   (uint)CARRY2(DAT_3360_07a2,((undefined2 *)&DAT_3360_3b78)[(uint)bVar2 * 4]);
          *(uint *)(puVar13 + 0x40) =
               DAT_3360_07a2 + ((undefined2 *)&DAT_3360_3b78)[(uint)bVar2 * 4];
          *(int *)(puVar13 + 0x42) = iVar14;
        }
        puVar10 = (undefined1 *)(uint)(byte)puVar13[0x3b];
        if ((int)puVar10 < *piVar8) break;
        puVar13[0x36] = 0;
      }
      local_6 = (undefined1 *)((ulong)uVar15 << 0x10);
    } while( true );
  }
  puVar10 = (undefined1 *)((ulong)local_1a8 >> 0x10);
  puVar9 = puVar10;
  uVar15 = FUN_1cdc_1936();
  if (uVar15 == 0x16) {
LAB_1cdc_22ce:
    puVar9 = (undefined1 *)0xffff;
    unaff_SS = (undefined1 *)&DAT_3360_3360;
  }
  else {
    if (uVar15 < 0x17) {
      if ((char)uVar15 == '\x03') {
        puVar13 = (undefined1 *)0x0;
        iVar14 = (int)local_1a8;
        do {
          if (*(char *)(iVar14 + 4) != '\0') {
            puVar9 = puVar13;
          }
          iVar14 = iVar14 + 0x12;
          puVar13 = puVar13 + 1;
        } while ((int)puVar13 < 10);
        goto LAB_1cdc_22d1;
      }
      if ((char)uVar15 == '\x06') goto LAB_1cdc_22ce;
    }
    unaff_SS = (undefined1 *)&DAT_3360_3360;
  }
LAB_1cdc_22d1:
  if (-1 < (int)puVar9) {
    if ((((char)param_1 == '\0') ||
        ((*(uint *)((char *)s__3QUICK__Destroy_the_plasma_core_3360_1088 + (int)puVar9 * 0x12) &
         0xff) != *(uint *)&DAT_3360_60c2)) ||
       (cStackY_1a9 = (char)(*(uint *)((char *)s__3QUICK__Destroy_the_plasma_core_3360_1088 +
                                      (int)puVar9 * 0x12) >> 8),
       (int)cStackY_1a9 != *(int *)&DAT_3360_60c0)) {
      FUN_1cdc_095a((char)*(undefined2 *)
                           ((char *)s__3QUICK__Destroy_the_plasma_core_3360_1088 +
                           (int)puVar9 * 0x12),
                    (int)(char)((uint)*(undefined2 *)
                                       ((char *)s__3QUICK__Destroy_the_plasma_core_3360_1088 +
                                       (int)puVar9 * 0x12) >> 8));
    }
    FUN_1273_10a8((char)puVar9,(char *)s_user_sav_3360_1e2b);
  }
  FUN_1cdc_016a(2);
  return puVar9;
}

