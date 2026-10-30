
/* WARNING: Instruction at (ram,0x00010550) overlaps instruction at (ram,0x0001054f)
    */
/* WARNING: Type propagation algorithm not settling */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int ** __cdecl16far FUN_1699_05d8(int param_1,undefined2 param_2)

{
  byte *pbVar1;
  uint uVar2;
  char cVar3;
  undefined1 uVar4;
  int **ppiVar5;
  undefined2 uVar6;
  int iVar7;
  char *pcVar8;
  uint uVar9;
  int ******in_CX;
  int iVar10;
  int iVar11;
  int **in_BX;
  byte bVar12;
  byte *unaff_SI;
  byte *pbVar13;
  byte *unaff_DI;
  undefined2 unaff_ES;
  int ******ppppppiVar14;
  int ******ppppppiVar15;
  undefined2 unaff_SS;
  bool bVar16;
  char *in_stack_0000ffd8;
  int *******pppppppiStack_26;
  byte *pbStack_22;
  undefined4 local_1a;
  int local_16;
  byte local_14;
  char cStack_13;
  char *local_12;
  int iStack_10;
  byte local_c;
  undefined1 uStack_b;
  int *local_a;
  int local_8;
  int ******local_6;
  undefined2 local_4;
  
  ppppppiVar14 = (int ******)((char *)s_MAXGUARD_exceeded___d__3754_1692 + 7);
  local_4 = &local_a;
  if (DAT_3754_3c44 != 1) {
    return local_4;
  }
  if (DAT_3754_0b2e != '\0') {
    in_CX = (int ******)&local_6;
    pppppppiStack_26 = (int *******)((char *)s_MAXGUARD_exceeded___d__3754_1692 + 7);
    ppppppiVar14 = (int ******)0x181b;
    in_stack_0000ffd8 = (char *)0x6f95;
    FUN_181b_0032();
    DAT_3754_343a = (int *****)local_6;
    DAT_3754_343c = local_8;
  }
  DAT_3754_0b2e = '\0';
  local_a = (int *)FUN_1699_038a();
  uVar2 = (uint)local_a >> 8;
  if (local_a == (int *)0x0) goto LAB_1699_07a2;
  uVar9 = (uint)local_a & 0xff;
  local_1a = (ulong)CONCAT22(local_1a._2_2_,local_a) & 0xffff00ff;
  if (uVar9 == 0x2b) {
    if (((byte)DAT_3754_3ec0 & 0x40) != 0) {
      DAT_3754_40f7 = DAT_3754_40f7 + '\x01';
    }
LAB_1699_0777:
    FUN_1826_05d4();
  }
  else {
    if ((byte)local_a < 0x2b) {
      if (uVar9 == 0x1b) {
        DAT_3754_3c44 = 0;
        goto LAB_1699_07a2;
      }
      if (0x1b < uVar9) goto LAB_1699_07a2;
      if ((byte)local_a != 0) {
        if ((byte)local_a == 9) {
          ppppppiVar14 = (int ******)0x1826;
          FUN_1826_271c();
        }
        goto LAB_1699_07a2;
      }
LAB_1699_066c:
      if (uVar2 == 0x86) {
        ppppppiVar14 = (int ******)0x1826;
        FUN_1826_0d1c();
      }
      else if ((uVar2 < 0x87) && (uVar9 = uVar2 - 0x3b, uVar9 < 10)) {
        bVar16 = SCARRY2(uVar9,uVar9);
        iVar10 = uVar9 * 2;
        switch(uVar9) {
        case 0:
        case 4:
          do {
            FUN_1f9d_000c();
            do {
              iVar10 = DAT_31e0_0004 * 6;
              ppiVar5 = (int **)(iVar10 + 0x36b6);
              DAT_31e0_0004 = DAT_31e0_0004 + 1;
              *ppiVar5 = (int *)unaff_SI;
              *(undefined1 *)(iVar10 + 0x36ba) = 0;
              pbVar13 = unaff_DI;
              do {
                unaff_DI = pbVar13 + 0x1c;
                unaff_SI = unaff_SI + 1;
                if (*(int *)&DAT_3754_61de <= (int)unaff_SI) {
                  return ppiVar5;
                }
                pbVar1 = pbVar13 + 0x22;
                pbVar13 = unaff_DI;
              } while (*pbVar1 != 0x28);
            } while (DAT_31e0_0004 < 0xc);
          } while( true );
        case 1:
          do {
            unaff_DI[iVar10 + -0x1daa] = unaff_DI[iVar10 + -0x1daa] - 1;
            pbStack_22 = unaff_DI;
            while( true ) {
              if (DAT_3754_40cc == 0) {
                iVar10 = (int)((ulong)((long)(int)local_4 * (long)DAT_3754_4122) >> 0x10);
              }
              else {
                iVar10 = (int)((ulong)((long)(int)in_BX * (long)DAT_3754_4120) >> 0x10);
              }
              iStack_10 = 1;
              local_12 = (char *)0x0;
              ppppppiVar14 = *(int *******)(pbStack_22 + 2);
              iVar11 = iVar10;
              local_6 = ppppppiVar14;
              if ((int)ppppppiVar14 <= *(int *)(pbStack_22 + 6)) {
                local_a = (int *)((int)ppppppiVar14 * 2 + 0x4752);
                do {
                  local_4 = *(int ***)(pbStack_22 + 0x10);
                  *(long *)(pbStack_22 + 0xe) =
                       *(long *)(pbStack_22 + 0xe) + *(long *)(pbStack_22 + 10);
                  local_8 = ((uint)local_4 >> 4) + DAT_3754_44c0;
                  pppppppiStack_26 = (int *******)ppppppiVar14;
                  iVar7 = FUN_1c63_070c(*(undefined1 *)((int)local_4 + 7));
                  pbStack_22 = (byte *)(iVar7 + iVar10);
                  if (cStack_13 != '\0') {
                    pbStack_22 = (byte *)-(int)pbStack_22;
                  }
                  in_stack_0000ffd8 = (char *)s_Level_read_ok_3754_1c61 + 2;
                  pppppppiStack_26 = (int *******)ppppppiVar14;
                  pcVar8 = (char *)FUN_1201_02ba();
                  *local_a = (int)local_4 + DAT_3754_44c2;
                  iStack_10 = iStack_10 + -1;
                  if ((iStack_10 == 0) || (local_12 != pcVar8)) {
                    in_stack_0000ffd8 = pcVar8;
                    pppppppiStack_26 = (int *******)ppppppiVar14;
                    iStack_10 = FUN_1156_04ce((int)local_1a,(int)(local_1a >> 0x10));
                    pbStack_22 = unaff_SI;
                  }
                  local_a = local_a + 1;
                  ppppppiVar14 = (int ******)((int)ppppppiVar14 + 1);
                  local_12 = pcVar8;
                } while ((int)ppppppiVar14 <= *(int *)(pbStack_22 + 6));
              }
              if (pppppppiStack_26[1] != (int ******)0x0) {
                pppppppiStack_26 = (int *******)0x2724;
                FUN_1201_040e();
              }
              unaff_DI = pbStack_22 + 0x12;
              in_stack_0000ffd8 = in_stack_0000ffd8 + 1;
              if ((int)DAT_3754_4cd2 <= (int)in_stack_0000ffd8) {
                return DAT_3754_4cd2;
              }
              iVar7 = *(int *)unaff_DI;
              bVar12 = *(byte *)(iVar7 + 4);
              pppppppiStack_26 = (int *******)((undefined2 *)&DAT_3754_427e + (uint)bVar12 * 4);
              if ((int)*pppppppiStack_26 <= (int)(uint)*(byte *)(iVar7 + 3)) {
                *(char *)(iVar7 + 3) = *(char *)pppppppiStack_26 + -1;
              }
              iVar10 = (uint)*(byte *)(iVar7 + 3) * 10 +
                       ((undefined2 *)&DAT_3754_4284)[(uint)bVar12 * 4];
              local_1a = *(ulong *)(iVar10 + 6);
              if (local_1a == 0) {
                uVar6 = FUN_1751_0404();
                local_1a = CONCAT22(iVar11,uVar6);
              }
              if ((*(char *)(iVar7 + 6) == '\x02') ||
                 ((*(char *)(iVar7 + 7) != '\0' && (*(char *)(iVar7 + 7) != '\x03')))) {
                cStack_13 = '\0';
              }
              else {
                cStack_13 = '\x01';
              }
              unaff_SI = DAT_3754_61e6;
              if (((0 < (int)DAT_3754_61e6) && (DAT_3754_427c == '\0')) &&
                 ((*(char *)(iVar7 + 7) == '\0' || (*(char *)(iVar7 + 7) == '\x01')))) {
                unaff_SI = (byte *)0x0;
              }
              if ((*(char *)(iVar7 + 7) != '\0') && (*(char *)(iVar7 + 7) != '\x01')) break;
              local_4 = (int **)(DAT_3754_40d2._2_2_ - *(int *)(iVar7 + 0xe));
              pbStack_22 = unaff_DI;
              in_BX = local_4;
            }
            local_4 = (int **)(*(int *)(iVar7 + 0xc) - (int)DAT_3754_40d2);
            in_BX = local_4;
          } while( true );
        case 2:
          *(int **)unaff_SI = in_BX[uVar2 - 0x1e];
          bVar12 = *unaff_SI;
          unaff_DI[3] = bVar12;
          if (unaff_SI[0xb] != 0) {
            bVar12 = unaff_SI[0xb];
            unaff_SI[0xc] = bVar12;
          }
          unaff_SI[0xb] = 0x15;
          return (int **)(uint)bVar12;
        case 3:
          while( true ) {
            if (*(int *)unaff_SI == 0) {
              local_6 = (int ******)((int)local_6 + *(int *)(unaff_SI + 10));
            }
            else {
              unaff_DI = unaff_DI + *(int *)(unaff_SI + 8);
            }
            iVar10 = *(int *)(unaff_SI + 2);
            bVar16 = false;
switchD_1000_7019_caseD_8:
            if (bVar16 == iVar10 < 0) {
              *(int *)(unaff_SI + 2) = *(int *)(unaff_SI + 2) + *(int *)(unaff_SI + 6);
              if (*(int *)unaff_SI == 0) {
                unaff_DI = unaff_DI + *(int *)(unaff_SI + 8);
              }
              else {
                local_6 = (int ******)((int)local_6 + *(int *)(unaff_SI + 10));
              }
            }
            else {
              *(int *)(unaff_SI + 2) = *(int *)(unaff_SI + 2) + *(int *)(unaff_SI + 4);
            }
            pppppppiStack_26 =
                 (int *******)
                 (((uint)local_6 & 0xffc0) * 2 + ((int)((uint)unaff_DI & 0xffdf) >> 5) + 0x373e);
            cVar3 = FUN_17d7_00b8();
            if (cVar3 != '\0') break;
            local_4 = (int **)((int)local_4 + 1);
            if (DAT_3754_44ce <= (int)local_4) {
LAB_17d7_0332:
              iVar10 = CONCAT11(uStack_b,local_c);
              *(char *)(iVar10 + 0x1a) = *(char *)(iVar10 + 0x1a) + '\x01';
              if ('\x14' < *(char *)(iVar10 + 0x1a)) {
                *(undefined1 *)(iVar10 + 0x1a) = 0x14;
              }
              *(undefined2 *)(iVar10 + 0x10) = unaff_DI;
              *(uint *)(iVar10 + 0x12) = (uint)local_6;
              return (int **)(int *****)local_6;
            }
          }
          iVar10 = CONCAT11(uStack_b,local_c);
          *(undefined1 *)(param_1 + 0xc) = 2;
          *(undefined1 *)(iVar10 + 3) = 0;
          uVar4 = FUN_1826_0b1e();
          *(undefined1 *)(iVar10 + 4) = uVar4;
          *(byte *)(iVar10 + 5) = *(byte *)(iVar10 + 5) | 0x10;
          goto LAB_17d7_0332;
        case 5:
          return (int **)((uint)local_4 >> 8);
        case 6:
          ppiVar5 = (int **)FUN_1c63_0068();
          break;
        case 7:
          pppppppiStack_26 = (int *******)0x8b31;
          ppiVar5 = (int **)FUN_1d0f_0302();
          if ((DAT_3754_4100 & 8) != 0) {
            pppppppiStack_26 = (int *******)0x8b49;
            ppiVar5 = (int **)FUN_1d0f_0302();
          }
          if (unaff_DI == (byte *)0x0) {
            bVar12 = 0;
            local_4 = (int **)0x34d4;
            local_6 = (int ******)0xd3;
            do {
              ppiVar5 = (int **)(uint)DAT_3754_4101;
              if ((1 << (bVar12 & 0x1f) & (uint)ppiVar5) != 0) {
                pppppppiStack_26 = (int *******)0x8b7d;
                ppiVar5 = (int **)FUN_1d0f_0302();
              }
              bVar12 = bVar12 + 1;
              local_4 = (int **)((int)local_4 + 10);
            } while (local_4 < 0x3524);
            if (param_1 == 0) {
              pppppppiStack_26 = (int *******)((char *)s_Bad_color_code_in_instr_3754_1d01 + 0xe);
              FUN_1d0f_0366();
              pppppppiStack_26 = (int *******)((char *)s_Bad_color_code_in_instr_3754_1d01 + 0xe);
              FUN_1d0f_0366();
              pppppppiStack_26 = (int *******)((char *)s_Bad_color_code_in_instr_3754_1d01 + 0xe);
              FUN_1d0f_0366();
              if (DAT_3754_3c4a != 0 || DAT_3754_3c48 != 0) {
                FUN_1277_0188();
                pppppppiStack_26 = (int *******)0xffff;
                FUN_1d0f_03e0();
              }
              DAT_3754_411c = (DAT_3754_411c + 0x9c & -(DAT_3754_411c < 100)) + 100;
              uVar2 = (uint)DAT_3754_411c;
              uVar4 = FUN_1277_0188();
              local_4._1_1_ = uVar4;
              FUN_1277_0188();
              pppppppiStack_26 = (int *******)((uVar2 * 0x12) / 100);
              FUN_1d0f_02c0(0xe9,0xb5);
              DAT_3754_411d = (DAT_3754_411d + 0x9c & -(DAT_3754_411d < 100)) + 100;
              uVar2 = (uint)DAT_3754_411d;
              if (DAT_3754_4104 == '\0') {
                cVar3 = FUN_1277_0188();
                local_4._1_1_ = cVar3 + -5;
              }
              else {
                local_4._1_1_ = FUN_1277_0188();
              }
              FUN_1277_0188();
              pppppppiStack_26 = (int *******)((uVar2 * 0x12) / 100);
              FUN_1d0f_02c0(0xd3,0xb5);
              local_4._1_1_ = FUN_1277_0188();
              pppppppiStack_26 =
                   (int *******)((char *)s_T7You_recover_to_witness_the_def_3754_122c + 0x4b);
              FUN_1156_088c();
              pppppppiStack_26 =
                   (int *******)((char *)s_T7QUICK__Destroy_the_plasma_core_3754_1150 + 6);
              FUN_1156_088c();
              pppppppiStack_26 =
                   (int *******)((char *)s_T7QUICK__Destroy_the_plasma_core_3754_1150 + 6);
              FUN_21d1_278c();
              FUN_1277_0188();
              pppppppiStack_26 = (int *******)0x8d3a;
              FUN_1277_0188();
              pppppppiStack_26 = (int *******)&pppppppiStack_26;
              ppiVar5 = (int **)FUN_1d0f_024c(0x8c,0xc0,0x13);
            }
          }
          return ppiVar5;
        case 8:
          goto switchD_1000_7019_caseD_8;
        case 9:
          if (((int)in_CX + 1U & 0xff & (uint)in_BX) == 0) {
            return in_BX;
          }
          if (((unaff_SI[6] < 0x39) || (0x3a < unaff_SI[6])) ||
             (in_BX = (int **)(1 << (unaff_SI[1] & 0x1f)), ((uint)DAT_3754_4101 & (uint)in_BX) != 0)
             ) {
            if ((unaff_SI[6] < 0x3b) || (0x3c < unaff_SI[6])) {
              unaff_DI[0x10] = 1;
              pppppppiStack_26 = (int *******)0x1000;
              ppiVar5 = (int **)FUN_1000_0598();
              return ppiVar5;
            }
            return in_BX;
          }
          ppiVar5 = (int **)FUN_1826_1f3a();
        }
        return ppiVar5;
      }
      goto LAB_1699_07a2;
    }
    if (uVar9 == 0x2d) {
      if (((byte)DAT_3754_3ec0 & 0x40) != 0) {
        DAT_3754_40f7 = DAT_3754_40f7 + -1;
      }
      goto LAB_1699_0777;
    }
    if ((int)(uVar9 - 0x2d) < 4) goto LAB_1699_07a2;
    if (uVar9 != 0x39 && 7 < (int)(uVar9 - 0x31)) {
      if (uVar9 != 0xe0) goto LAB_1699_07a2;
      goto LAB_1699_066c;
    }
    if (((uint)DAT_3754_4102 & 1 << ((byte)((int)local_1a + -0x31) & 0x1f)) == 0)
    goto LAB_1699_07a2;
    FUN_1826_0cae();
  }
  ppppppiVar14 = (int ******)0x1826;
LAB_1699_07a2:
  ppppppiVar15 = ppppppiVar14;
  if (((byte)DAT_3754_3ec0 & 2) != 0) {
    ppppppiVar15 = (int ******)0x1621;
    pppppppiStack_26 = (int *******)ppppppiVar14;
    FUN_1621_05a0();
  }
  ppppppiVar14 = ppppppiVar15;
  if (((byte)DAT_3754_3ec0 & 4) != 0) {
    ppppppiVar14 = (int ******)0x1621;
    pppppppiStack_26 = (int *******)ppppppiVar15;
    FUN_1621_05a0();
  }
  ppppppiVar15 = ppppppiVar14;
  if (((byte)DAT_3754_3ec0 & 8) != 0) {
    if ((DAT_3754_3ec0._1_1_ & 1) == 0) {
      ppppppiVar15 = (int ******)((char *)s_Level_read_ok_3754_1c61 + 2);
      FUN_1c63_0068();
    }
    else {
      ppppppiVar15 = (int ******)0x1621;
      pppppppiStack_26 = (int *******)ppppppiVar14;
      FUN_1621_05a0();
    }
  }
  ppppppiVar14 = ppppppiVar15;
  if (((byte)DAT_3754_3ec0 & 0x10) != 0) {
    if ((DAT_3754_3ec0._1_1_ & 1) == 0) {
      ppppppiVar14 = (int ******)((char *)s_Level_read_ok_3754_1c61 + 2);
      FUN_1c63_0068();
    }
    else {
      ppppppiVar14 = (int ******)0x1621;
      pppppppiStack_26 = (int *******)ppppppiVar15;
      FUN_1621_05a0();
    }
  }
  local_4 = (int **)CONCAT11((DAT_3754_3ec0._1_1_ & 2) >> 1,(byte)DAT_3754_3ec0 >> 7);
  if (DAT_3754_40bc != '\0') {
    ppppppiVar15 = (int ******)0x181b;
    pppppppiStack_26 = (int *******)ppppppiVar14;
    FUN_181b_0032();
    if (local_8 < DAT_3754_343c) {
      pppppppiStack_26 = (int *******)0x7255;
      FUN_1699_059c();
      pppppppiStack_26 = (int *******)0x181b;
      ppppppiVar15 = (int ******)0x1621;
      FUN_1621_05a0();
    }
    ppppppiVar14 = ppppppiVar15;
    if (DAT_3754_343c < local_8) {
      pppppppiStack_26 = (int *******)0x727a;
      FUN_1699_059c();
      ppppppiVar14 = (int ******)0x1621;
      pppppppiStack_26 = (int *******)ppppppiVar15;
      FUN_1621_05a0();
    }
    ppppppiVar15 = ppppppiVar14;
    if ((int)local_6 < (int)DAT_3754_343a) {
      if (((DAT_3754_3ec0._1_1_ & 1) == 0) && ((local_c & 2) == 0)) {
        pppppppiStack_26 = (int *******)0x72b9;
        FUN_1699_059c();
        ppppppiVar15 = (int ******)((char *)s_Level_read_ok_3754_1c61 + 2);
        FUN_1c63_0068();
      }
      else {
        pppppppiStack_26 = (int *******)0x72da;
        FUN_1699_059c();
        ppppppiVar15 = (int ******)0x1621;
        pppppppiStack_26 = (int *******)ppppppiVar14;
        FUN_1621_05a0();
      }
    }
    if ((int)DAT_3754_343a < (int)local_6) {
      if (((DAT_3754_3ec0._1_1_ & 1) == 0) && ((local_c & 2) == 0)) {
        pppppppiStack_26 = (int *******)0x7317;
        FUN_1699_059c();
        FUN_1c63_0068();
      }
      else {
        pppppppiStack_26 = (int *******)0x7334;
        FUN_1699_059c();
        pppppppiStack_26 = (int *******)ppppppiVar15;
        FUN_1621_05a0();
      }
    }
    if (((((int)local_6 <= DAT_3754_44b6) || (DAT_3754_44b8 <= (int)local_6)) ||
        (local_8 <= DAT_3754_44ba)) || (DAT_3754_44bc <= local_8)) {
      local_8 = DAT_3754_44c0 >> 1;
      local_6 = (int ******)(DAT_3754_44be >> 1);
      pppppppiStack_26 = (int *******)0x7386;
      FUN_181b_0066();
    }
    DAT_3754_343a = (int *****)local_6;
    DAT_3754_343c = local_8;
    local_4 = (int **)CONCAT11(local_4._1_1_ | 1U - ((local_c & 2) == 0),
                               (byte)local_4 | 1U - ((local_c & 1) == 0));
  }
  if (DAT_3754_40bf != '\0') {
    ppppppiVar14 = (int ******)((char *)s_Climb_up_3754_1c0c + 5);
    FUN_1c11_04ca();
    if (local_16 < -10) {
      pppppppiStack_26 = (int *******)0x73db;
      FUN_1699_05ba();
      pppppppiStack_26 = (int *******)((char *)s_Climb_up_3754_1c0c + 5);
      ppppppiVar14 = (int ******)0x1621;
      FUN_1621_05a0();
    }
    ppppppiVar15 = ppppppiVar14;
    if (10 < local_16) {
      pppppppiStack_26 = (int *******)0x73fb;
      FUN_1699_05ba();
      ppppppiVar15 = (int ******)0x1621;
      pppppppiStack_26 = (int *******)ppppppiVar14;
      FUN_1621_05a0();
    }
    ppppppiVar14 = ppppppiVar15;
    if (local_1a._2_2_ < -10) {
      if (((DAT_3754_3ec0._1_1_ & 1) == 0) && (local_12 == (char *)0x0)) {
        pppppppiStack_26 = (int *******)0x7436;
        FUN_1699_05ba();
        ppppppiVar14 = (int ******)((char *)s_Level_read_ok_3754_1c61 + 2);
        FUN_1c63_0068();
      }
      else {
        pppppppiStack_26 = (int *******)0x7455;
        FUN_1699_05ba();
        ppppppiVar14 = (int ******)0x1621;
        pppppppiStack_26 = (int *******)ppppppiVar15;
        FUN_1621_05a0();
      }
    }
    if (10 < local_1a._2_2_) {
      if (((DAT_3754_3ec0._1_1_ & 1) == 0) && (local_12 == (char *)0x0)) {
        pppppppiStack_26 = (int *******)0x748e;
        FUN_1699_05ba();
        FUN_1c63_0068();
      }
      else {
        pppppppiStack_26 = (int *******)0x74a8;
        FUN_1699_05ba();
        pppppppiStack_26 = (int *******)ppppppiVar14;
        FUN_1621_05a0();
      }
    }
    local_4 = (int **)CONCAT11(local_4._1_1_ | (byte)local_12,(byte)local_4 | local_14);
  }
  if ((byte)local_4 != '\0') {
    pppppppiStack_26 = (int *******)0x74e6;
    cVar3 = FUN_1826_0c58();
    if (cVar3 != '\0') {
      FUN_1621_05f8();
    }
  }
  if ((local_4._1_1_ != 0) && (DAT_3754_0b2f != local_4._1_1_)) {
    FUN_1000_0704();
  }
  DAT_3754_0b30 = (byte)local_4;
  DAT_3754_0b2f = local_4._1_1_;
  return (int **)(uint)local_4._1_1_;
}

