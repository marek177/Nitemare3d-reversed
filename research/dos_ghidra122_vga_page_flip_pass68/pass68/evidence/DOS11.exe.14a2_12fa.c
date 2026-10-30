
/* WARNING: Instruction at (ram,0x0001fc47) overlaps instruction at (ram,0x0001fc46)
    */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Restarted to delay deadcode elimination for space: stack */

uint * __cdecl16far
FUN_14a2_12fa(uint *param_1,uint *param_2,int param_3,undefined2 param_4,uint *param_5,byte param_6,
             uint param_7)

{
  byte *pbVar1;
  uint *puVar2;
  uint uVar3;
  uint *puVar4;
  long lVar5;
  int iVar6;
  uint *puVar7;
  ulong in_ECX;
  int in_DX;
  byte bVar8;
  uint uVar9;
  uint *in_BX;
  uint *unaff_SI;
  byte *pbVar10;
  uint *unaff_DI;
  undefined2 uVar11;
  uint *unaff_SS;
  bool bVar12;
  char cVar13;
  char cVar14;
  bool bVar15;
  byte abStack_7ffe [32722];
  byte local_2c;
  uint uStack_2a;
  uint *local_28;
  int iStack_26;
  uint uStack_24;
  int local_20;
  byte local_1e;
  uint *local_1c;
  undefined4 uStack_1a;
  undefined4 local_16;
  uint *puStack_12;
  byte *local_4;
  
  puVar7 = (uint *)0x3395;
  puStack_12 = (uint *)((char *)s_Close_remote_doors_3395_1498 + 10);
  local_16 = (uint *)CONCAT22(0x5d33,(uint *)local_16);
  uVar3 = FUN_1817_01bc();
  puVar4 = (uint *)(uint)(byte)param_1[8];
  if (puVar4 <= (uint *)(uVar3 & 0xff)) {
    *(byte *)(param_1 + 8) = 0;
    puStack_12 = (uint *)0x1817;
    local_16 = (uint *)CONCAT22(0x5d58,(uint *)local_16);
    FUN_1817_1ba8();
    if (DAT_3395_40ec != 1) {
      puStack_12 = (uint *)0x1817;
      local_16 = (uint *)CONCAT22(0x5d72,(uint *)local_16);
      FUN_1817_18e6();
    }
    puStack_12 = param_2._2_2_;
    local_16 = (uint *)CONCAT22((uint *)param_2,param_1);
    uStack_1a = (uint *)0x18175db1;
    FUN_14a2_0864();
    puStack_12 = (uint *)0x1817;
    local_16 = (uint *)CONCAT22(0x5dc1,(uint *)local_16);
    uVar3 = FUN_1817_012a();
    bVar12 = CARRY2((uint)DAT_3395_40de,uVar3);
    DAT_3395_40de._0_2_ = (uint)DAT_3395_40de + uVar3;
    DAT_3395_40de._2_2_ = DAT_3395_40de._2_2_ + ((int)uVar3 >> 0xf) + (uint)bVar12;
    FUN_1817_05ca();
    bVar8 = *(byte *)((int)param_1 + 0xd);
    *(byte *)((int)*(undefined4 *)(param_2._2_2_ + 6) + 1) = bVar8;
    return (uint *)(uint)bVar8;
  }
  if ((uint *)(uVar3 & 0xff) != (uint *)0x0) {
    if (*(byte *)((int)param_1 + 0xb) == 7) {
      puStack_12 = (uint *)0x1817;
      local_16 = (uint *)CONCAT22(0x5e08,(uint *)local_16);
      FUN_1817_1aa8();
    }
    local_4._0_1_ = (char)uVar3;
    *(byte *)(param_1 + 8) = (byte)param_1[8] - (char)local_4;
    *(byte *)(param_1 + 9) = 8;
    if ((byte)param_1[5] == 2) {
      puStack_12 = (uint *)0x1817;
      local_16 = (uint *)CONCAT22(0x5eef,(uint *)local_16);
      FUN_1817_1c0c();
      puStack_12 = param_2._2_2_;
      local_16 = (uint *)CONCAT22((uint *)param_2,param_1);
      uStack_1a = (uint *)0x18175f1f;
      puVar4 = (uint *)FUN_14a2_0864();
    }
    else {
      puVar4 = (uint *)0x0;
      if ((byte)param_1[5] != 4) {
        puStack_12 = (uint *)0x1817;
        local_16 = (uint *)CONCAT22(0x5e39,(uint *)local_16);
        local_4 = (byte *)FUN_1817_1c0c();
        uVar3 = *(byte *)((int)param_1 + 0xb) - 3;
        if (0x12 < uVar3) {
          *param_1 = *(uint *)(((undefined2 *)&DAT_3395_3c80)[(uint)(byte)param_2._2_2_[2] * 4] +
                               (int)local_4 * 2 + 0x3a);
          bVar8 = (byte)*param_1;
          *(byte *)((int)param_2._2_2_ + 3) = bVar8;
          if (*(byte *)((int)param_1 + 0xb) != 0) {
            bVar8 = *(byte *)((int)param_1 + 0xb);
            *(byte *)(param_1 + 6) = bVar8;
          }
          *(byte *)((int)param_1 + 0xb) = 0x15;
          return (uint *)(uint)bVar8;
        }
        uVar9 = uVar3 * 2;
        uVar11 = 0x1000;
        switch(uVar3) {
        case 0:
          puVar7 = (uint *)param_2;
        case 0xb:
          *(byte *)((int)register0x00000010 + 0x674 + (int)param_2._2_2_) =
               *(byte *)((int)register0x00000010 + 0x674 + (int)param_2._2_2_) | (byte)in_ECX;
          puVar4 = (uint *)(*(code *)*(undefined2 *)&DAT_3395_34ac)();
          if (puVar4 == (uint *)0x0) {
            puVar4 = (uint *)0x0;
          }
          return puVar4;
        default:
          return in_BX;
        case 2:
          return in_BX;
        case 3:
        case 0xe:
          while( true ) {
            if (param_2._2_2_[6] == 2) {
              param_2._2_2_[6] = 0;
              uVar3 = *param_2._2_2_;
              if ((uVar3 != 0) && (*(int *)(uVar3 + 0xc) < *(int *)(uVar3 + 0x10))) {
                *(int *)(uVar3 + 0xc) = *(int *)(uVar3 + 0xc) + 2;
                param_2._2_2_[6] = 2;
              }
              uVar3 = param_2._2_2_[1];
              if ((uVar3 != 0) && (*(int *)(uVar3 + 0xe) < *(int *)(uVar3 + 0x12))) {
                *(int *)(uVar3 + 0xe) = *(int *)(uVar3 + 0xe) + 2;
                param_2._2_2_[6] = 2;
              }
              uVar3 = param_2._2_2_[2];
              if ((uVar3 != 0) && (*(int *)(uVar3 + 0xc) < *(int *)(uVar3 + 0x10))) {
                *(int *)(uVar3 + 0xc) = *(int *)(uVar3 + 0xc) + 2;
                param_2._2_2_[6] = 2;
              }
              uVar3 = param_2._2_2_[3];
              if ((uVar3 != 0) && (*(int *)(uVar3 + 0xe) < *(int *)(uVar3 + 0x12))) {
                *(int *)(uVar3 + 0xe) = *(int *)(uVar3 + 0xe) + 2;
                param_2._2_2_[6] = 2;
              }
              if (param_2._2_2_[6] == 0) {
                iVar6 = 0;
                puVar4 = (uint *)0x34f6;
                if (0 < (int)*uStack_1a) {
                  do {
                    if (((((*puVar4 != 0) && (*param_2._2_2_ == *puVar4)) ||
                         ((puVar4[2] != 0 && (param_2._2_2_[2] == puVar4[2])))) ||
                        ((puVar4[1] != 0 && (param_2._2_2_[1] == puVar4[1])))) ||
                       ((puVar4[3] != 0 && (param_2._2_2_[3] == puVar4[3])))) {
                      if (*puVar4 != 0) {
                        *(byte *)(*puVar4 + 5) = *(byte *)(*puVar4 + 5) & 0xfe;
                      }
                      if (puVar4[1] != 0) {
                        *(byte *)(puVar4[1] + 5) = *(byte *)(puVar4[1] + 5) & 0xfe;
                      }
                      if (puVar4[2] != 0) {
                        *(byte *)(puVar4[2] + 5) = *(byte *)(puVar4[2] + 5) & 0xfe;
                      }
                      if (puVar4[3] != 0) {
                        *(byte *)(puVar4[3] + 5) = *(byte *)(puVar4[3] + 5) & 0xfe;
                      }
                      *(undefined1 *)((int)*(undefined4 *)(puVar4 + 4) + 1) = 0;
                      **(undefined1 **)(puVar4 + 4) = 0;
                      puVar4[6] = 0;
                    }
                    puVar4 = puVar4 + 7;
                    iVar6 = iVar6 + 1;
                  } while (iVar6 < (int)*uStack_1a);
                  puVar7 = unaff_SS;
                }
              }
            }
            param_2._2_2_ = param_2._2_2_ + 7;
            param_1 = (uint *)((int)param_1 + 1);
            if ((int)*uStack_1a <= (int)param_1) break;
            param_2._0_2_ = unaff_SI;
          }
          return param_1;
        case 4:
        case 0xf:
          puVar2 = param_2._2_2_ + uVar3;
          *puVar2 = *puVar2 + 1;
          if (*puVar2 == 0) {
            bVar8 = 0;
            local_4 = (byte *)0x3500;
            do {
              in_BX = (uint *)(uint)DAT_3395_40ef;
              if ((1 << (bVar8 & 0x1f) & (uint)in_BX) != 0) {
                uVar11 = 0x1d00;
                puStack_12 = (uint *)0x8a87;
                in_BX = (uint *)switchD_1000:9bc5::caseD_3d();
              }
              bVar8 = bVar8 + 1;
              local_4 = (byte *)((int)local_4 + 10);
            } while (local_4 < 0x3550);
            if (param_1 == (uint *)&DAT_3395_0001) {
              local_16 = (uint *)CONCAT22(0x8ab3,(uint *)local_16);
              puStack_12 = (uint *)uVar11;
              FUN_1d00_036a();
              puStack_12 = (uint *)0x1d00;
              local_16 = (uint *)CONCAT22(0x8ac6,(uint *)local_16);
              FUN_1d00_036a();
              puStack_12 = (uint *)0x1d00;
              FUN_1d00_036a();
              if (DAT_3395_3c7a != 0 || DAT_3395_3c78 != 0) {
                FUN_1275_0160();
                puStack_12 = (uint *)0xffff;
                FUN_1d00_03e4();
              }
              DAT_3395_410a = (DAT_3395_410a + 0x9c & -(DAT_3395_410a < 100)) + 100;
              uVar3 = (uint)DAT_3395_410a;
              FUN_1275_0160();
              FUN_1275_0160();
              uStack_1a = (uint *)0x12758b60;
              puStack_12 = (uint *)((uVar3 * 0x12) / 100);
              FUN_1d00_02c4();
              DAT_3395_410b = (DAT_3395_410b + 0x9c & -(DAT_3395_410b < 100)) + 100;
              uVar3 = (uint)DAT_3395_410b;
              if (DAT_3395_40f2 == '\0') {
                FUN_1275_0160();
              }
              else {
                FUN_1275_0160();
              }
              FUN_1275_0160();
              uStack_1a = (uint *)0x12758bca;
              puStack_12 = (uint *)((uVar3 * 0x12) / 100);
              FUN_1d00_02c4();
              FUN_1275_0160();
              puStack_12 = (uint *)((char *)s_3You_recover_to_witness_the_defu_3395_1233 + 0x42);
              local_16 = (uint *)0x8bfb00d3;
              FUN_1155_088e();
              puStack_12 = (uint *)0x1155;
              FUN_1155_088e();
              puStack_12 = (uint *)0x1155;
              local_16 = (uint *)CONCAT22(0x8c34,(int)local_16);
              FUN_21bc_278c();
              FUN_1275_0160();
              puStack_12 = (uint *)0x8c4a;
              FUN_1275_0160();
              puStack_12 = (uint *)&iStack_26;
              uStack_1a = (uint *)0x8c1275;
              local_1c = (uint *)0x8c61;
              in_BX = (uint *)FUN_1d00_0250();
            }
          }
          return in_BX;
        case 5:
        case 0x10:
          goto switchD_1000_5e53_caseD_5;
        case 6:
        case 0x11:
          return (uint *)DAT_3395_c95e;
        case 7:
          *(byte *)(param_2._2_2_ + (*(byte *)((int)param_1 + 0xb) - 0xfe0)) =
               (char)param_2._2_2_[*(byte *)((int)param_1 + 0xb) - 0xfe0] + (byte)in_ECX +
               CARRY2(uVar3,uVar3);
          local_20 = in_DX;
          pbVar10 = local_4 + (uint)*(byte *)(param_3 + 1) * in_DX;
          local_16._0_2_ = (uint *)((int)(uint *)local_16 - in_DX);
          local_16._2_2_ = 0x5e39;
          local_16 = (uint *)CONCAT22(0x5e39,(uint *)local_16);
          uStack_1a = (uint *)CONCAT22(param_1[8],(uint *)uStack_1a);
          local_1c = (uint *)((int)param_2._2_2_ * 2 + 0x4740);
          local_2c = (*(byte *)((int)*(undefined4 *)(param_1 + 1) + 5) & 0x10) >> 4;
          puVar4 = (uint *)(((uint)(uint *)param_2 & 0xff) * 0x50 + ((uint)param_2._2_2_ >> 2));
          out(0x3c4,2);
          bVar8 = (byte)((ulong)param_2 >> 0x10) & 3;
          local_1e = '\x11' << bVar8 | 0x11U >> 8 - bVar8;
          out(0x3c5,local_1e);
          param_2._0_2_ = DAT_3395_012c;
          local_28 = in_BX;
          unaff_SI = puVar4;
          local_4 = pbVar10;
          while( true ) {
            if ((local_2c != 0) || (*local_1c <= uStack_1a._2_2_)) {
              uVar3 = uStack_2a;
              puVar7 = puStack_12;
              do {
                if (*pbVar10 != 0x1f) {
                  *(byte *)puVar4 = *pbVar10;
                }
                puVar4 = puVar4 + 0x28;
                bVar12 = CARRY2(uVar3,uStack_24);
                uVar3 = uVar3 + uStack_24;
                pbVar10 = pbVar10 + (uint)bVar12 + iStack_26;
                puVar7 = (uint *)((int)puVar7 + -1);
                unaff_SI = (uint *)(abStack_7ffe + 0x7ffc);
              } while (puVar7 != (uint *)0x0);
            }
            puVar4 = (uint *)((int)(uint *)uStack_1a +
                             (uint)CARRY2((uint)local_28,uStack_24) + iStack_26);
            uStack_1a = (uint *)CONCAT22(uStack_1a._2_2_,puVar4);
            cVar14 = SBORROW2((int)puVar4,(int)(uint *)local_16);
            cVar13 = (int)puVar4 - (int)(uint *)local_16 < 0;
code_r0x00011d05:
            if (cVar14 == cVar13) break;
            pbVar10 = local_4 + ((uint)puVar4 & 0xff) * (uint)local_16._2_1_;
            local_1c = local_1c + 1;
            bVar12 = (char)local_1e < '\0';
            local_1e = local_1e << 1 | bVar12;
            out(0x3c5,local_1e);
            puVar4 = unaff_SI;
            if (bVar12) {
              puVar4 = (uint *)((int)unaff_SI + 1);
            }
            param_1 = (uint *)((int)param_1 + -1);
            if (param_1 == (uint *)0x0) {
              return (uint *)(uint)local_1e;
            }
          }
          return puVar4;
        case 8:
          cVar14 = SCARRY2((int)param_1,1);
          cVar13 = (int)((int)param_1 + 1) < 0;
          FUN_1611_022f();
          bVar8 = in(in_DX);
          puVar4 = (uint *)(uint)bVar8;
          unaff_DI = puVar7;
          goto code_r0x00011d05;
        case 9:
          param_1[4] = (uint)((int)in_BX + (int)param_2._2_2_);
          lVar5 = (long)(int)(param_1[1] - (int)(uint *)param_2) * *(long *)(param_1 + 5);
          param_2._2_2_ =
               (uint *)((int)param_2._2_2_ + ((int)((ulong)lVar5 >> 0x10) - DAT_3395_44b0));
          param_1[7] = (uint)lVar5;
          param_1[8] = (uint)param_2._2_2_;
          return param_2._2_2_;
        case 10:
          do {
            cVar13 = *(char *)((int)in_BX + 7);
            if (cVar13 == '\0') {
              if ((char)param_3 == '\0') {
                return in_BX;
              }
              bVar12 = (char)param_3 == '\a';
LAB_1fa7_0434:
              if (bVar12) {
                return in_BX;
              }
            }
            else {
              if (cVar13 == '\x01') {
                if ((char)param_3 == '\x03') {
                  return in_BX;
                }
                bVar12 = (char)param_3 == '\x04';
                goto LAB_1fa7_0434;
              }
              if (cVar13 == '\x02') {
                if ((char)param_3 == '\x01') {
                  return in_BX;
                }
                bVar12 = (char)param_3 == '\x02';
                goto LAB_1fa7_0434;
              }
              if (cVar13 == '\x03') {
                if ((char)param_3 == '\x05') {
                  return in_BX;
                }
                if ((char)param_3 == '\x06') {
                  return in_BX;
                }
              }
            }
            puStack_12 = (uint *)0xfeda;
            in_BX = (uint *)FUN_1fa7_0318();
            if (in_BX == (uint *)0x0) {
              FUN_1f89_0002();
              return (uint *)0x0;
            }
          } while( true );
        case 0xd:
          FUN_21bc_1bd6();
          FUN_21bc_1e14();
          iVar6 = FUN_21bc_3ccf();
          if (iVar6 == 0) {
            FUN_1f89_0002();
          }
          FUN_21bc_1bd6();
          if ((byte)*(uint *)param_2 != 0) {
            pbVar10 = (byte *)0x0;
            do {
              param_2._2_2_ = (uint *)(uint)param_6;
              puStack_12 = (uint *)&DAT_3395_21bc;
              FUN_1275_0422();
              pbVar1 = pbVar10;
              pbVar10 = pbVar10 + 1;
            } while ((int)pbVar10 < (int)(uint)*pbVar1);
          }
          return param_2._2_2_;
        case 0x12:
          pbVar10 = (byte *)((int)param_2._2_2_ + -1);
          do {
            uVar3 = (int)in_ECX - 1;
            if (uVar3 == 0) {
              cVar13 = (char)uVar9;
              bVar8 = cVar13 << 1 | cVar13 < '\0';
              uVar9 = (uint)bVar8;
              out(0x3c5,bVar8);
              if (cVar13 < '\0') {
                local_4 = local_4 + 1;
              }
              param_1 = (uint *)((int)unaff_DI + (int)param_5);
              unaff_SI = (uint *)((int)unaff_SI + -1);
              if (unaff_SI == (uint *)0x0) {
                return param_5;
              }
              pbVar10 = local_4;
              uVar3 = param_7;
              unaff_DI = param_1;
            }
            in_ECX = (ulong)uVar3;
            puVar2 = param_1;
            param_1 = (uint *)((int)param_1 + 1);
            *pbVar10 = (byte)*puVar2;
            pbVar10 = pbVar10 + 0x50;
          } while( true );
        }
      }
    }
  }
  return puVar4;
switchD_1000_5e53_caseD_5:
  if ((int)uVar9 < 0) {
    param_1 = (uint *)param_1[0x1f];
  }
code_r0x0001fc4a:
  if (in_BX == (uint *)&DAT_3395_0001) {
    if (*(byte *)((int)param_1 + 7) == 0) {
      if (*(int *)(uVar9 + 0x10) < (int)param_1[8]) {
LAB_1fa7_027c:
        uVar3 = param_1[9];
        uVar9 = *(uint *)(uVar9 + 0x12);
        bVar15 = SBORROW2(uVar9,uVar3);
        iVar6 = uVar9 - uVar3;
        bVar12 = uVar9 == uVar3;
        goto LAB_1fa7_0282;
      }
    }
    else if ((*(byte *)((int)param_1 + 7) == 1) && (*(int *)(uVar9 + 0x10) < (int)param_1[8])) {
LAB_1fa7_028e:
      bVar12 = SBORROW2(*(int *)(uVar9 + 0xe),param_1[7]);
      iVar6 = *(int *)(uVar9 + 0xe) - param_1[7];
      goto LAB_1fa7_0294;
    }
  }
  else if (in_BX + -1 == (uint *)0x0) {
    if (*(byte *)((int)param_1 + 7) == 0) {
      if ((int)param_1[6] < *(int *)(uVar9 + 0xc)) goto LAB_1fa7_027c;
    }
    else if ((*(byte *)((int)param_1 + 7) == 1) && ((int)param_1[6] < *(int *)(uVar9 + 0xc)))
    goto LAB_1fa7_028e;
  }
LAB_1fa7_0298:
  while( true ) {
    while( true ) {
      param_2._2_2_ = param_2._2_2_ + 1;
      uVar3 = (int)in_ECX - 1;
      in_ECX = (ulong)uVar3;
      if (uVar3 == 0) {
        if (DAT_3395_44be < 1) {
          return (uint *)0x1;
        }
        return (uint *)0x0;
      }
      if (*param_2._2_2_ != 0) break;
      *param_2._2_2_ = (uint)param_1;
      DAT_3395_44be = DAT_3395_44be + -1;
    }
    uVar9 = *param_2._2_2_;
    if (*(byte *)(uVar9 + 7) != 0) break;
    if (*(byte *)((int)param_1 + 7) == 2) goto LAB_1fa7_01f6;
    if ((*(byte *)((int)param_1 + 7) == 3) && ((int)param_1[8] < *(int *)(uVar9 + 0x10)))
    goto LAB_1fa7_020c;
  }
  in_BX = (uint *)(*(byte *)(uVar9 + 7) - 1);
  if (in_BX == (uint *)0x0) {
    if (*(byte *)((int)param_1 + 7) == 2) {
      if ((int)param_1[6] <= *(int *)(uVar9 + 0xc)) goto LAB_1fa7_0298;
    }
    else if ((*(byte *)((int)param_1 + 7) != 3) || (*(int *)(uVar9 + 0x10) <= (int)param_1[8]))
    goto LAB_1fa7_0298;
    bVar12 = SBORROW2(*(int *)(uVar9 + 0x12),param_1[9]);
    iVar6 = *(int *)(uVar9 + 0x12) - param_1[9];
LAB_1fa7_0294:
    if (bVar12 != iVar6 < 0) goto LAB_1fa7_0296;
    goto LAB_1fa7_0298;
  }
  goto code_r0x0001fc4a;
LAB_1fa7_01f6:
  if (*(int *)(uVar9 + 0xc) < (int)param_1[6]) {
LAB_1fa7_020c:
    uVar3 = param_1[7];
    uVar9 = *(uint *)(uVar9 + 0xe);
    bVar15 = SBORROW2(uVar9,uVar3);
    iVar6 = uVar9 - uVar3;
    bVar12 = uVar9 == uVar3;
LAB_1fa7_0282:
    if (!bVar12 && bVar15 == iVar6 < 0) {
LAB_1fa7_0296:
      *param_2._2_2_ = (uint)param_1;
    }
  }
  goto LAB_1fa7_0298;
}

