
/* WARNING: Instruction at (ram,0x00010e80) overlaps instruction at (ram,0x00010e7f)
    */
/* WARNING: Restarted to delay deadcode elimination for space: stack */

uint __cdecl16far FUN_1818_1404(uint param_1,uint param_2,undefined1 param_3)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined1 uVar3;
  uint uVar4;
  undefined1 extraout_AH;
  char *pcVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  ulong uVar9;
  byte bVar10;
  uint in_CX;
  undefined2 extraout_DX;
  int in_DX;
  int iVar11;
  uint in_BX;
  char *pcVar12;
  int *piVar13;
  int *unaff_SI;
  char *pcVar14;
  undefined1 *unaff_DI;
  uint *puVar15;
  undefined2 uVar16;
  undefined2 unaff_ES;
  char *pcVar17;
  undefined2 unaff_SS;
  char cVar18;
  char cVar19;
  bool bVar20;
  bool bVar21;
  int aiStack_7ffe [16305];
  undefined1 local_9c [112];
  char cStack_2c;
  uint uStack_2a;
  uint uStack_28;
  int iStack_26;
  uint uStack_24;
  char *pcStack_22;
  char *pcStack_20;
  undefined4 uStack_1e;
  int *piStack_1a;
  int local_12;
  int local_10;
  undefined4 uStack_a;
  undefined4 local_6;
  
  local_6 = local_6 & 0xffffff;
  if (8 < param_1) {
    return 0;
  }
  cVar19 = SCARRY2(param_1,param_1);
  cVar18 = (int)(param_1 * 2) < 0;
  switch(param_1) {
  case 0:
    *(char *)(unaff_SI + param_1) = (char)unaff_SI[param_1] + (char)in_BX;
    return 0;
  case 1:
    return in_CX;
  case 2:
    FUN_1612_026c();
    FUN_1612_021f();
    uVar3 = in(extraout_DX);
    uVar7 = CONCAT11(extraout_AH,uVar3);
    break;
  case 3:
    unaff_DI[(int)register0x00000010 + 0x26ce] = unaff_DI[(int)register0x00000010 + 0x26ce] + -1;
    cVar18 = (char)unaff_SI[1];
    pcStack_20 = (char *)0x1000;
    do {
      uVar7 = (int)cVar18 + *(int *)(in_DX + 0x10);
      uVar4 = (int)*(char *)((int)unaff_SI + 3) + *(int *)(in_DX + 0x12);
      iVar6 = (uVar4 & 0xffc0) * 2 + ((int)(uVar7 & 0xffdf) >> 5);
      uStack_a = CONCAT22(0x2e27,iVar6 + 0x373e);
      uVar9 = *(ulong *)(in_DX + 0xc);
      uVar16 = (undefined2)(local_6 >> 0x10);
      if (CONCAT22(0x2e27,iVar6 + 0x373e) == uVar9) {
LAB_1000_0ef1:
        iVar11 = (int)local_6;
        if (*(long *)(in_DX + 0xc) != uStack_a) {
          *(undefined1 *)(iVar6 + 0x373f) = *(undefined1 *)((int)*(undefined4 *)(in_DX + 0xc) + 1);
          *(undefined1 *)((int)*(undefined4 *)(iVar11 + 0xc) + 1) = 0;
        }
        *(uint *)(iVar11 + 0x10) = uVar7;
        *(uint *)(iVar11 + 0x12) = uVar4;
        *(long *)(iVar11 + 0xc) = uStack_a;
        piStack_1a = (int *)(int)(char)unaff_SI[1];
        uStack_1e = (char *)local_6;
        pcVar12 = (char *)s_Load_game____339b_1ab4 + 10;
        pcStack_22 = (char *)0xf4b;
        uVar7 = FUN_1abe_015c();
        uVar9 = (ulong)uVar7;
        *(char *)(unaff_SI + 2) = (char)unaff_SI[2] + -1;
      }
      else {
        pcVar12 = pcStack_20;
        if ((((undefined1 *)&DAT_339b_d068)[*(byte *)(iVar6 + 0x373f)] & 6) == 0)
        goto LAB_1000_0ef1;
      }
      do {
        piVar13 = unaff_SI;
        unaff_SI = piVar13 + 3;
        unaff_DI = unaff_DI + 1;
        if (*(int *)0x4 <= (int)unaff_DI) {
          return (uint)uVar9;
        }
      } while ((char)piVar13[5] == '\0');
      in_DX = *unaff_SI * 0x1c + 6;
      in_CX = 0x2e27;
      local_6 = CONCAT22(0x2e27,in_DX);
      cVar18 = (char)piVar13[4];
      pcStack_20 = pcVar12;
    } while( true );
  case 4:
    piStack_1a = (int *)0x8a5b;
    uVar7 = FUN_1d00_0308();
    if (unaff_DI == (undefined1 *)0x0) {
      bVar10 = 0;
      uVar4 = 0x34fc;
      do {
        uVar7 = (uint)DAT_339b_40ef;
        if ((1 << (bVar10 & 0x1f) & uVar7) != 0) {
          piStack_1a = (int *)0x8a8f;
          uVar7 = FUN_1d00_0308();
        }
        bVar10 = bVar10 + 1;
        uVar4 = uVar4 + 10;
      } while (uVar4 < 0x354c);
      if (param_1 == 0) {
        piStack_1a = (int *)((char *)s_Bad_color_code_in_instr_339b_1cf5 + 0xb);
        uStack_1e = (char *)CONCAT22(0x8aba,(char *)uStack_1e);
        FUN_1d00_036c();
        piStack_1a = (int *)((char *)s_Bad_color_code_in_instr_339b_1cf5 + 0xb);
        uStack_1e = (char *)CONCAT22(0x8acd,(char *)uStack_1e);
        FUN_1d00_036c();
        piStack_1a = (int *)((char *)s_Bad_color_code_in_instr_339b_1cf5 + 0xb);
        uStack_1e = (char *)CONCAT22(0x8ae0,(char *)uStack_1e);
        FUN_1d00_036c();
        if (DAT_339b_3c78._2_2_ != 0 || (int)DAT_339b_3c78 != 0) {
          FUN_1275_0160();
          piStack_1a = (int *)0xffff;
          uStack_1e = (char *)0x12758b07;
          FUN_1d00_03e6();
        }
        DAT_339b_410a = (DAT_339b_410a + 0x9c & -(DAT_339b_410a < 100)) + 100;
        uVar7 = (uint)DAT_339b_410a;
        FUN_1275_0160();
        FUN_1275_0160();
        uStack_1e = (char *)0xb500e9;
        pcStack_20 = (char *)s_3You_recover_to_witness_the_defu_339b_1223 + 0x52;
        pcStack_22 = (char *)0x8b66;
        piStack_1a = (int *)((uVar7 * 0x12) / 100);
        FUN_1d00_02c6();
        DAT_339b_410b = (DAT_339b_410b + 0x9c & -(DAT_339b_410b < 100)) + 100;
        uVar7 = (uint)DAT_339b_410b;
        if (DAT_339b_40f2 == '\0') {
          FUN_1275_0160();
        }
        else {
          FUN_1275_0160();
        }
        FUN_1275_0160();
        uStack_1e = (char *)0xb500d3;
        pcStack_20 = (char *)s_3You_recover_to_witness_the_defu_339b_1223 + 0x52;
        pcStack_22 = (char *)0x8bd0;
        piStack_1a = (int *)((uVar7 * 0x12) / 100);
        FUN_1d00_02c6();
        FUN_1275_0160();
        piStack_1a = (int *)((char *)s_3You_recover_to_witness_the_defu_339b_1223 + 0x52);
        uStack_1e = (char *)CONCAT22(0x8bff,(char *)uStack_1e);
        FUN_1155_088e();
        piStack_1a = (int *)((char *)s_3QUICK__Destroy_the_plasma_core__339b_1147 + 0xe);
        uStack_1e = (char *)CONCAT22(0x8c13,(char *)uStack_1e);
        FUN_1155_088e();
        piStack_1a = (int *)((char *)s_3QUICK__Destroy_the_plasma_core__339b_1147 + 0xe);
        uStack_1e = (char *)CONCAT22(0x8c36,(char *)uStack_1e);
        FUN_21c2_278c();
        FUN_1275_0160();
        piStack_1a = (int *)0x8c4c;
        FUN_1275_0160();
        piStack_1a = &iStack_26;
        uStack_1e = (char *)0x1300c0;
        pcStack_20 = (char *)0x8c;
        pcStack_22 = (char *)s_3You_recover_to_witness_the_defu_339b_1223 + 0x52;
        uStack_24 = 0x8c63;
        uVar7 = FUN_1d00_0252();
      }
    }
    return uVar7;
  case 5:
    if ((*(byte *)(param_1 + 5) & 1) != 0) {
      piStack_1a = (int *)0x1000;
      uStack_1e = (char *)CONCAT22(0xfc57,(char *)uStack_1e);
      uVar7 = FUN_1c54_02ee();
      uVar9 = (ulong)uVar7;
      if ((char)uVar7 != '\0') {
        uVar7 = *(uint *)(param_1 + 0x18);
        if ((int)DAT_339b_44a6 < (int)*(uint *)(param_1 + 0x18)) {
          uVar7 = DAT_339b_44a6;
        }
        uVar9 = (ulong)uVar7;
        iVar6 = *(int *)(param_1 + 0x14);
        if (*(int *)(param_1 + 0x14) < DAT_339b_44a4) {
          iVar6 = DAT_339b_44a4;
        }
        puVar15 = (uint *)(iVar6 * 2 + 0x44c0);
        if (iVar6 <= (int)uVar7) {
          uVar7 = (uVar7 - iVar6) + 1;
          uVar9 = (ulong)uVar7;
          do {
            if (*puVar15 == 0) {
              *puVar15 = param_1;
              DAT_339b_44be = DAT_339b_44be + -1;
              goto LAB_1fad_0298;
            }
            uVar4 = *puVar15;
            uVar8 = (uint)*(byte *)(uVar4 + 7);
            if (uVar8 == 0) {
              if (*(byte *)(param_1 + 7) == 2) {
                uVar9 = (ulong)*(uint *)(param_1 + 0xc);
                if (*(int *)(uVar4 + 0xc) < (int)*(uint *)(param_1 + 0xc)) goto LAB_1fad_020c;
              }
              else {
                uVar8 = *(byte *)(param_1 + 7) - 3;
                uVar9 = (ulong)uVar8;
                if ((uVar8 == 0) &&
                   (uVar9 = (ulong)*(uint *)(param_1 + 0x10),
                   (int)*(uint *)(param_1 + 0x10) < *(int *)(uVar4 + 0x10))) {
LAB_1fad_020c:
                  uVar8 = *(uint *)(param_1 + 0xe);
                  uVar4 = *(uint *)(uVar4 + 0xe);
                  bVar20 = SBORROW2(uVar4,uVar8);
                  iVar6 = uVar4 - uVar8;
                  bVar21 = uVar4 == uVar8;
LAB_1fad_0282:
                  uVar9 = (ulong)uVar8;
                  if (!bVar21 && bVar20 == iVar6 < 0) goto LAB_1fad_0296;
                }
              }
            }
            else {
              if (uVar8 == 1) {
                if (*(byte *)(param_1 + 7) == 2) {
                  uVar9 = (ulong)*(uint *)(param_1 + 0xc);
                  if (*(int *)(uVar4 + 0xc) < (int)*(uint *)(param_1 + 0xc)) goto LAB_1fad_023a;
                }
                else {
                  uVar8 = *(byte *)(param_1 + 7) - 3;
                  uVar9 = (ulong)uVar8;
                  if ((uVar8 == 0) &&
                     (uVar9 = (ulong)*(uint *)(param_1 + 0x10),
                     (int)*(uint *)(param_1 + 0x10) < *(int *)(uVar4 + 0x10))) {
LAB_1fad_023a:
                    uVar8 = *(uint *)(param_1 + 0x12);
                    bVar21 = SBORROW2(*(int *)(uVar4 + 0x12),uVar8);
                    iVar6 = *(int *)(uVar4 + 0x12) - uVar8;
                    goto LAB_1fad_0294;
                  }
                }
                goto LAB_1fad_0298;
              }
              if (uVar8 != 2) {
                uVar9 = (ulong)(uVar8 - 3);
                if (uVar8 - 3 == 0) {
                  if (*(byte *)(param_1 + 7) == 0) {
                    uVar9 = (ulong)*(uint *)(param_1 + 0xc);
                    if ((int)*(uint *)(param_1 + 0xc) < *(int *)(uVar4 + 0xc)) goto LAB_1fad_027c;
                  }
                  else {
                    uVar8 = *(byte *)(param_1 + 7) - 1;
                    uVar9 = (ulong)uVar8;
                    if ((uVar8 == 0) &&
                       (uVar9 = (ulong)*(uint *)(param_1 + 0xc),
                       (int)*(uint *)(param_1 + 0xc) < *(int *)(uVar4 + 0xc))) goto LAB_1fad_028e;
                  }
                }
                goto LAB_1fad_0298;
              }
              if (*(byte *)(param_1 + 7) == 0) {
                uVar9 = (ulong)*(uint *)(param_1 + 0x10);
                if ((int)*(uint *)(param_1 + 0x10) <= *(int *)(uVar4 + 0x10)) goto LAB_1fad_0298;
LAB_1fad_027c:
                uVar8 = *(uint *)(param_1 + 0x12);
                uVar4 = *(uint *)(uVar4 + 0x12);
                bVar20 = SBORROW2(uVar4,uVar8);
                iVar6 = uVar4 - uVar8;
                bVar21 = uVar4 == uVar8;
                goto LAB_1fad_0282;
              }
              uVar8 = *(byte *)(param_1 + 7) - 1;
              uVar9 = (ulong)uVar8;
              if ((uVar8 != 0) ||
                 (uVar9 = (ulong)*(uint *)(param_1 + 0x10),
                 (int)*(uint *)(param_1 + 0x10) <= *(int *)(uVar4 + 0x10))) goto LAB_1fad_0298;
LAB_1fad_028e:
              uVar8 = *(uint *)(param_1 + 0xe);
              bVar21 = SBORROW2(*(int *)(uVar4 + 0xe),uVar8);
              iVar6 = *(int *)(uVar4 + 0xe) - uVar8;
LAB_1fad_0294:
              uVar9 = (ulong)uVar8;
              if (bVar21 == iVar6 < 0) goto LAB_1fad_0298;
LAB_1fad_0296:
              *puVar15 = param_1;
            }
LAB_1fad_0298:
            puVar15 = puVar15 + 1;
            uVar7 = uVar7 - 1;
          } while (uVar7 != 0);
        }
      }
      in_BX = (uint)uVar9;
      if (DAT_339b_44be < 1) {
        return (uint)CONCAT31((int3)(uVar9 >> 8),1);
      }
    }
    return in_BX & 0xff00;
  case 6:
    piStack_1a = (int *)0xe42e;
    FUN_1d00_0170();
    uStack_a = CONCAT22(1,(undefined2)uStack_a);
    piStack_1a = (int *)0xe442;
    pcVar5 = (char *)FUN_1818_2958();
    cVar18 = *pcVar5;
    pcVar12 = pcVar5;
    while (cVar18 != '\0') {
      if (*pcVar12 == '#') {
        uStack_a = uStack_a & 0xffff;
      }
      pcVar12 = pcVar12 + 1;
      cVar18 = *pcVar12;
    }
    piStack_1a = (int *)0xe47d;
    FUN_1155_0256();
    piStack_1a = (int *)0xe488;
    FUN_1275_15d8();
    uStack_1e = (char *)CONCAT22(pcVar5,(char *)s_3You_recover_to_witness_the_defu_339b_1223 + 0x52)
    ;
    pcStack_20 = (char *)0xe498;
    FUN_1d00_1266();
    piStack_1a = (int *)0xe4a2;
    FUN_1155_0256();
    piStack_1a = (int *)0xe4ad;
    FUN_1275_15d8();
    pcVar12 = pcVar5;
    do {
      pcVar17 = (char *)s_MAXGUARD_exceeded___d__339b_168a;
      cVar18 = FUN_168a_03c6();
      iVar6 = (int)cVar18;
      if (iVar6 == 0x44) {
        piStack_1a = (int *)s_Thanks__Printing_order_txt____To_339b_1dcf;
        uStack_1e = (char *)0x168ae4fa;
        FUN_1d00_0534();
        piStack_1a = (int *)0xe505;
        FUN_1bb2_00ac();
        piStack_1a = (int *)local_9c;
        uStack_1e = (char *)0x1bb2e518;
        FUN_21c2_278c();
        pcVar17 = (char *)0x21c2;
        piStack_1a = (int *)0xe525;
        FUN_21c2_38e6();
        goto LAB_1d00_152e;
      }
      if (iVar6 < 0x45) {
        if (iVar6 == 0x1b) {
          uStack_a = 0x100;
        }
      }
      else if (0x47 < iVar6) {
        if (iVar6 == 0x49 || iVar6 + -0x48 < 1) {
          if (pcVar12 != pcVar5) {
            for (pcVar12 = pcVar12 + -2; (pcVar12 != pcVar5 && (*pcVar12 != '#'));
                pcVar12 = pcVar12 + -1) {
            }
            if (pcVar12 != pcVar5) {
              pcVar12 = pcVar12 + 1;
            }
LAB_1d00_152e:
            uStack_1e = (char *)CONCAT22(pcVar12,pcVar17);
            pcStack_20 = (char *)0xe536;
            piStack_1a = (int *)in_DX;
            FUN_1d00_1266();
          }
        }
        else if ((6 < iVar6 + -0x49) && (iVar6 == 0x51 || iVar6 + -0x50 < 1)) {
          pcVar14 = pcVar12 + 1;
          cVar18 = *pcVar14;
          while ((cVar18 != '\0' && (*pcVar14 != '#'))) {
            pcVar14 = pcVar14 + 1;
            cVar18 = *pcVar14;
          }
          if (*pcVar14 != '\0') {
            pcVar12 = pcVar14 + 1;
            goto LAB_1d00_152e;
          }
        }
      }
      if (uStack_a._1_1_ != '\0') {
        FUN_1f8f_004e();
        piStack_1a = (int *)((char *)s_user_sav_339b_1f8e + 1);
        uStack_1e = (char *)CONCAT22(0xe5e6,(char *)uStack_1e);
        FUN_1453_0082();
        piStack_1a = (int *)((char *)s_class__d__strength__d__strategy___339b_140d + 0x46);
        uStack_1e = (char *)CONCAT22(0xe5f2,(char *)uStack_1e);
        FUN_21c2_2052();
        piStack_1a = (int *)0xe5fb;
        uVar7 = FUN_1d00_0170();
        return uVar7;
      }
    } while( true );
  case 7:
    return (in_BX - *(int *)(unaff_DI + (int)register0x00000010 + 0x6c2)) -
           (uint)CARRY2(param_1,param_1);
  case 8:
    if ((char)in_BX != '\0') {
      in_BX = DAT_339b_012a;
    }
    out(0x3c4,2);
    bVar10 = (byte)param_1 & 3;
    out(0x3c5,'\x11' << bVar10 | 0x11U >> 8 - bVar10);
    *(undefined1 *)((param_2 & 0xff) * 0x50 + (param_1 >> 2)) = param_3;
    return CONCAT11((byte)(param_1 >> 10),param_3);
  }
  do {
    uVar1 = uStack_1e;
    if (cVar19 == cVar18) {
      return uVar7;
    }
    iVar6 = (uVar7 & 0xff) * ((uint)unaff_DI & 0xff);
    pcVar12 = (char *)(local_6._2_2_ + iVar6);
    cVar18 = (char)uStack_1e;
    bVar10 = cVar18 << 1 | cVar18 < '\0';
    uStack_1e = (char *)CONCAT31(uStack_1e._1_3_,bVar10);
    uVar2 = uStack_1e;
    out(0x3c5,bVar10);
    if (cVar18 < '\0') {
      uStack_a = (ulong)((int)uStack_a._2_2_ + 1) << 0x10;
    }
    local_10 = local_10 + -1;
    if (local_10 == 0) {
      return CONCAT11((char)((uint)iVar6 >> 8),bVar10);
    }
    if (cStack_2c == '\0') {
      uStack_1e._2_2_ = SUB42(uVar1,2);
      if ((char *)*uStack_1e._2_2_ < (char *)s_Bad_color_code_in_instr_339b_1cf5 + 0xd)
      goto LAB_1155_0781;
    }
    else {
LAB_1155_0781:
      iVar6 = local_12;
      uVar7 = uStack_2a;
      pcVar5 = uStack_a._2_2_;
      do {
        if (*pcVar12 != '\x1f') {
          *pcVar5 = *pcVar12;
        }
        pcVar5 = pcVar5 + 0x50;
        bVar21 = CARRY2(uVar7,uStack_24);
        uVar7 = uVar7 + uStack_24;
        pcVar12 = pcVar12 + (uint)bVar21 + iStack_26;
        iVar6 = iVar6 + -1;
        unaff_DI = local_9c + 0x9a;
      } while (iVar6 != 0);
    }
    bVar21 = CARRY2(uStack_28,uStack_24);
    uStack_28 = uStack_28 + uStack_24;
    uVar7 = (int)piStack_1a + iStack_26 + (uint)bVar21;
    cVar19 = SBORROW2(uVar7,0x1d04);
    cVar18 = (int)(uVar7 + 0xe2fc) < 0;
    uStack_1e = (char *)uVar2;
    piStack_1a = (int *)uVar7;
  } while( true );
}

