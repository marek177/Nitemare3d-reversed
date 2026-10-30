
/* WARNING: Instruction at (ram,0x00018007) overlaps instruction at (ram,0x00018006)
    */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint * __cdecl16far
FUN_1452_0334(int param_1,byte *param_2,undefined2 param_3,undefined2 param_4,undefined2 param_5,
             uint *param_6,undefined2 param_7,int param_8)

{
  byte *pbVar1;
  byte *pbVar2;
  uint *puVar3;
  undefined1 *puVar4;
  int *piVar5;
  undefined4 *puVar6;
  int *piVar7;
  undefined4 *puVar8;
  uint uVar9;
  undefined4 uVar10;
  char *pcVar11;
  undefined1 uVar12;
  undefined1 uVar13;
  char cVar14;
  undefined1 uVar15;
  undefined1 uVar16;
  undefined1 uVar17;
  undefined1 uVar18;
  undefined1 uVar19;
  undefined1 uVar20;
  undefined1 uVar21;
  char cVar22;
  undefined1 uVar23;
  int *piVar24;
  int iVar25;
  int iVar26;
  uint uVar27;
  undefined1 extraout_AH;
  undefined1 extraout_AH_00;
  undefined2 uVar28;
  uint *puVar29;
  undefined1 extraout_AH_01;
  undefined2 extraout_var;
  undefined2 extraout_var_00;
  undefined2 extraout_var_01;
  long lVar30;
  long lVar31;
  long lVar32;
  int iVar33;
  byte *pbVar34;
  uint uVar35;
  uint *puVar36;
  int *piVar37;
  int *in_ECX;
  undefined4 *puVar38;
  undefined1 *in_EDX;
  byte bVar39;
  undefined2 *puVar40;
  uint *puVar41;
  long *plVar42;
  undefined4 *puVar43;
  undefined2 unaff_SI;
  byte *pbVar44;
  undefined1 *puVar45;
  undefined1 *puVar46;
  int *piVar47;
  undefined4 *puVar48;
  undefined2 unaff_DI;
  undefined1 *unaff_ES;
  char *pcVar49;
  undefined2 unaff_SS;
  undefined2 in_FS;
  bool bVar50;
  byte abStack_7ffe [32368];
  long alStack_18e [65];
  uint uStack_8a;
  undefined1 *puStack_88;
  uint uStack_86;
  undefined1 auStack_82 [4];
  int iStack_7e;
  uint uStack_7c;
  int iStack_76;
  byte bStack_74;
  char cStack_73;
  int iStack_72;
  long lStack_32;
  long lStack_2e;
  undefined2 uStack_2a;
  int iStack_28;
  undefined4 uStack_26;
  undefined4 uStack_22;
  char *pcStack_1e;
  char *pcStack_1c;
  char cStack_1a;
  undefined1 uStack_19;
  byte *pbStack_18;
  undefined2 uStack_16;
  undefined2 uStack_14;
  undefined2 uStack_12;
  undefined2 uStack_10;
  undefined1 uStack_e;
  undefined1 uStack_d;
  undefined4 local_a;
  undefined4 local_6;
  
  uStack_e = (undefined1)unaff_SI;
  uStack_d = (undefined1)((uint)unaff_SI >> 8);
  local_a = (uint *)(ulong)(uint3)local_a;
  local_6 = (int *)0x10001;
  uStack_10._0_1_ = 0x52;
  uStack_10._1_1_ = 0x14;
  uStack_12._0_1_ = 0x6c;
  uStack_12._1_1_ = 0x48;
  FUN_1275_0be6();
  uStack_10._0_1_ = 0x75;
  uStack_10._1_1_ = 0x12;
  uStack_12._0_1_ = 0x70;
  uStack_12._1_1_ = 0x48;
  FUN_1452_000a();
  uStack_10._0_1_ = 99;
  uStack_10._1_1_ = 10;
  uStack_12._0_1_ = 'u';
  uStack_12._1_1_ = 0x12;
  uStack_14._0_1_ = 0x78;
  uStack_14._1_1_ = 0x48;
  iVar26 = FUN_21bc_248a();
  if (iVar26 != 0) {
    DAT_3395_3c6f = 0;
    DAT_3395_3c62 = 0x12;
  }
  pbVar44 = (byte *)&DAT_3395_0001;
  local_6._3_1_ = 0;
  uVar28 = extraout_var;
  if (1 < param_1) {
    do {
      puVar3 = local_a;
      uVar21 = uStack_10._1_1_;
      uVar20 = (byte)uStack_10;
      uVar23 = uStack_12._1_1_;
      cVar22 = (byte)uStack_12;
      puVar41 = (uint *)(param_2 + (int)pbVar44 * 2);
      local_a = (uint *)CONCAT22(local_a._2_2_,puVar41);
      uStack_10._0_1_ = (byte)param_2;
      uVar15 = (byte)uStack_10;
      uStack_10._1_1_ = (char)((uint)param_2 >> 8);
      uVar18 = uStack_10._1_1_;
      uStack_12._0_1_ = (byte)param_1;
      cVar14 = (byte)uStack_12;
      uStack_12._1_1_ = (undefined1)((uint)param_1 >> 8);
      uVar12 = uStack_12._1_1_;
      if (*(char *)*puVar41 != '-') {
        uStack_14._0_1_ = 0xbc;
        uStack_14._1_1_ = 0x21;
        uStack_16._0_1_ = 0xaf;
        uStack_16._1_1_ = 0x48;
        FUN_1452_0322();
        uVar28 = extraout_var_00;
        cVar22 = (byte)uStack_12;
        uVar23 = uStack_12._1_1_;
        uVar20 = (byte)uStack_10;
        uVar21 = uStack_10._1_1_;
      }
      uStack_10._1_1_ = uVar21;
      uStack_10._0_1_ = uVar20;
      uStack_12._1_1_ = uVar23;
      uStack_12._0_1_ = cVar22;
      uVar17 = uStack_10._1_1_;
      uVar21 = (byte)uStack_10;
      uVar20 = uStack_16._1_1_;
      uVar23 = (byte)uStack_16;
      pcVar11 = (char *)CONCAT22(pcStack_1c,pcStack_1e);
      iVar26 = CONCAT11(uStack_d,uStack_e);
      puVar36 = (uint *)*puVar41;
      uVar27 = (int)*(char *)((int)puVar36 + 1) - 0x62;
      if (uVar27 < 0x17) {
        bVar50 = CARRY2(uVar27,uVar27);
        puVar40 = (undefined2 *)(uVar27 * 2);
        puVar29 = (uint *)CONCAT22(uVar28,puVar36);
        pcVar49 = (char *)0x1000;
        cVar22 = (char)puVar36;
        bVar39 = (byte)((ulong)in_EDX >> 8);
        puVar45 = (undefined1 *)in_EDX;
        uStack_10._0_1_ = (byte)pbVar44;
        uVar16 = (byte)uStack_10;
        uStack_10._1_1_ = (char)((uint)pbVar44 >> 8);
        uVar19 = uStack_10._1_1_;
        uStack_16._0_1_ = (byte)unaff_SS;
        uVar12 = (byte)uStack_16;
        uStack_16._1_1_ = (undefined1)((uint)unaff_SS >> 8);
        uVar13 = uStack_16._1_1_;
        uStack_16._0_1_ = uVar23;
        uStack_16._1_1_ = uVar20;
        switch(uVar27) {
        default:
          uStack_10._0_1_ = 0x80;
          uStack_10._1_1_ = 0;
          *(int *)(pbVar44 + (int)puVar40) = *(int *)(pbVar44 + (int)puVar40) + (int)puVar36;
          uStack_12 = (uint *)auStack_82;
          uStack_14._0_1_ = 0;
          uStack_14._1_1_ = 0x10;
          pcVar49 = (char *)&DAT_3395_21bc;
          uStack_16._0_1_ = 0x99;
          uStack_16._1_1_ = 0x44;
          iVar26 = FUN_21bc_06fc();
          if (iVar26 != 1) {
            uStack_e = 0xc6;
            uStack_d = 7;
            uStack_10._0_1_ = 0xbc;
            uStack_10._1_1_ = 0x21;
            pcVar49 = (char *)s_About_to__s_game____s__Press_ESC_3395_1f66 + 0x23;
            uStack_12._0_1_ = 0xaa;
            uStack_12._1_1_ = 0x44;
            FUN_1f89_0002();
          }
          if (iStack_7e != -0x50ef) {
            uStack_e = SUB21(pcVar49,0);
            uStack_d = (undefined1)((uint)pcVar49 >> 8);
            pcVar49 = (char *)s_About_to__s_game____s__Press_ESC_3395_1f66 + 0x23;
            uStack_10._0_1_ = 0xbc;
            uStack_10._1_1_ = 0x44;
            FUN_1f89_0002();
          }
          uStack_86 = 0;
          break;
        case 1:
          param_2 = param_2 + (int)pbVar44;
          do {
            *puVar45 = 1;
            puVar45 = puVar45 + 0x12;
            pbVar44 = pbVar44 + -1;
          } while (pbVar44 != (byte *)0x0);
          ((char *)s_3You_recover_to_witness_the_defu_3395_1233 + 0xc9)[(int)param_2 * 0x12] = '\0';
          uStack_12._0_1_ = 8;
          uStack_12._1_1_ = 0;
          uStack_10._0_1_ = 1;
          uStack_10._1_1_ = 0;
          uStack_14._0_1_ = 0;
          uStack_14._1_1_ = 0x10;
          uStack_16._0_1_ = 0x3f;
          uStack_16._1_1_ = 0xeb;
          uVar28 = FUN_1275_0160();
          uStack_12._0_1_ = (byte)uVar28;
          uStack_12._1_1_ = (undefined1)((uint)uVar28 >> 8);
          uStack_14 = (int *)((int)param_2 * 0xb);
          pbStack_18 = (byte *)0x30;
          uStack_16._0_1_ = 0x41;
          uStack_16._1_1_ = 0;
          cStack_1a = 100;
          uStack_19 = 0;
          pcStack_1c = (char *)s_3You_recover_to_witness_the_defu_3395_1233 + 0x42;
          pcStack_1e = (char *)0xeb5c;
          FUN_1155_097e();
          uStack_10._0_1_ = 0xdd;
          uStack_10._1_1_ = 0x2c;
          uStack_12._0_1_ = 0xfc;
          uStack_12._1_1_ = 0x12;
          uStack_14._0_1_ = 0x55;
          uStack_14._1_1_ = 0x11;
          uStack_16._0_1_ = 0x69;
          uStack_16._1_1_ = 0xeb;
          iVar26 = FUN_1d00_191a();
          if (iVar26 == 0x17) {
            puVar36 = (uint *)0x0;
            pcVar49 = (char *)s_3You_recover_to_witness_the_defu_3395_1233 + 0xc9;
            if (local_a._2_2_ != (undefined4 *)0x0) {
              do {
                if (pcVar49[4] != '\0') {
                  puVar41 = puVar36;
                }
                pcVar49 = pcVar49 + 0x12;
                puVar36 = (uint *)((int)puVar36 + 1);
              } while ((int)puVar36 < (int)local_a._2_2_);
              local_a = (uint *)ZEXT24(puVar41);
            }
          }
          return (uint *)local_a;
        case 2:
          uStack_10._0_1_ = 0x43;
          uStack_10._1_1_ = 0;
          uStack_12._0_1_ = 0;
          uStack_12._1_1_ = 0x10;
          uStack_14._0_1_ = 0xd;
          uStack_14._1_1_ = 0x90;
          puVar41 = (uint *)FUN_1bff_040a();
          return puVar41;
        case 4:
          if (DAT_3395_141a != -1) {
            DAT_3395_141a = DAT_3395_141a + '\x01';
          }
          return (uint *)((uint)puVar36 & 0xff00);
        case 5:
          param_2[-0x4d] = param_2[-0x4d] + bVar39;
          uStack_10._0_1_ = 0xdd;
          uStack_10._1_1_ = 0x2c;
          uStack_12._0_1_ = 0xae;
          uStack_12._1_1_ = 0xf;
          uStack_14._0_1_ = 0;
          uStack_14._1_1_ = 0x10;
          uStack_16._0_1_ = 0x53;
          uStack_16._1_1_ = 0xf6;
          iVar26 = FUN_1d00_191a();
          if (iVar26 == 6) {
            return (uint *)0x0;
          }
          return (uint *)(iVar26 + -0xe);
        case 6:
          *(char *)&DAT_3395_40e8 = cVar22;
          uStack_10._1_1_ = cVar22 >> 7;
          uStack_12._0_1_ = 10;
          uStack_12._1_1_ = 0x14;
          uStack_14 = (int *)&uStack_26;
          uStack_16._0_1_ = 0;
          uStack_16._1_1_ = 0x10;
          pbStack_18 = (byte *)0x8938;
          uStack_10._0_1_ = cVar22;
          FUN_21bc_278c();
          uStack_12._0_1_ = 0;
          uStack_12._1_1_ = 0;
          uStack_10._0_1_ = 1;
          uStack_10._1_1_ = 0;
          uStack_14._0_1_ = 0xbc;
          uStack_14._1_1_ = 0x21;
          uStack_16._0_1_ = 0x46;
          uStack_16._1_1_ = 0x89;
          uVar28 = FUN_1275_0160();
          uStack_12._0_1_ = (byte)uVar28;
          uStack_12._1_1_ = (undefined1)((uint)uVar28 >> 8);
          uStack_14._0_1_ = 0xb;
          uStack_14._1_1_ = 0;
          uStack_16._0_1_ = 0x75;
          uStack_16._1_1_ = 0x12;
          pbStack_18 = (byte *)0x8951;
          uVar28 = FUN_1275_0160();
          uStack_14._0_1_ = (char)uVar28;
          uStack_14._1_1_ = (char)((uint)uVar28 >> 8);
          pbStack_18 = (byte *)&uStack_26;
          pcStack_1c = (char *)0xb1;
          cStack_1a = 0x14;
          uStack_19 = 0;
          pcStack_1e = (char *)0x6d;
          uStack_22 = (byte *)0x12758967;
          uStack_16._0_1_ = uVar12;
          uStack_16._1_1_ = uVar13;
          puVar41 = (uint *)FUN_1d00_0250();
          if (param_2 != (byte *)&DAT_3395_0001) {
            return puVar41;
          }
          DAT_3395_410c = (DAT_3395_410c + 0x9c & -(DAT_3395_410c < 100)) + 100;
          uStack_10._1_1_ = 0;
          uStack_12._0_1_ = 0xd;
          uStack_12._1_1_ = 0x14;
          uStack_14 = (int *)&uStack_26;
          uStack_16._0_1_ = 0;
          uStack_16._1_1_ = 0x1d;
          pbStack_18 = (byte *)0x898e;
          uStack_10._0_1_ = DAT_3395_410c;
          FUN_21bc_278c();
          uStack_12._0_1_ = 0;
          uStack_12._1_1_ = 0;
          uStack_10._0_1_ = 1;
          uStack_10._1_1_ = 0;
          uStack_14._0_1_ = 0xbc;
          uStack_14._1_1_ = 0x21;
          uStack_16._0_1_ = 0x9c;
          uStack_16._1_1_ = 0x89;
          uVar28 = FUN_1275_0160();
          uStack_12._0_1_ = (byte)uVar28;
          uStack_12._1_1_ = (undefined1)((uint)uVar28 >> 8);
          uStack_14._0_1_ = 0xb;
          uStack_14._1_1_ = 0;
          uStack_16._0_1_ = 0x75;
          uStack_16._1_1_ = 0x12;
          pbStack_18 = (byte *)0x89a7;
          uVar28 = FUN_1275_0160();
          uStack_14._0_1_ = (char)uVar28;
          uStack_14._1_1_ = (char)((uint)uVar28 >> 8);
          pbStack_18 = (byte *)&uStack_26;
          pcStack_1c = (char *)0xbe;
          cStack_1a = 0x14;
          uStack_19 = 0;
          pcStack_1e = (char *)0x6d;
          uStack_22 = (byte *)0x127589bd;
          uStack_16._0_1_ = uVar12;
          uStack_16._1_1_ = uVar13;
          FUN_1d00_0250();
          if (DAT_3395_40eb != 0xff) {
            uStack_10 = (uint)DAT_3395_40eb * 10 + 0x34b0;
            uStack_14._0_1_ = 0x87;
            uStack_14._1_1_ = 0;
            uStack_12._0_1_ = 0xa2;
            uStack_12._1_1_ = 0;
            uStack_16._0_1_ = 0;
            uStack_16._1_1_ = 0x1d;
            pbStack_18 = (byte *)0x89eb;
            switchD_1000:9bc5::caseD_3d();
          }
          if ((DAT_3395_40ee & 1) != 0) {
            uStack_10._0_1_ = 0xd8;
            uStack_10._1_1_ = 0x34;
            uStack_14._0_1_ = 0xa7;
            uStack_14._1_1_ = 0;
            uStack_12._0_1_ = 0xa2;
            uStack_12._1_1_ = 0;
            uStack_16._0_1_ = 0;
            uStack_16._1_1_ = 0x1d;
            pbStack_18 = (byte *)0x8a0a;
            switchD_1000:9bc5::caseD_3d();
          }
          if ((DAT_3395_40ee & 2) != 0) {
            uStack_10._0_1_ = 0xe2;
            uStack_10._1_1_ = 0x34;
            uStack_14._0_1_ = 0xbd;
            uStack_14._1_1_ = 0;
            uStack_12._0_1_ = 0xa2;
            uStack_12._1_1_ = 0;
            uStack_16._0_1_ = 0;
            uStack_16._1_1_ = 0x1d;
            pbStack_18 = (byte *)0x8a22;
            switchD_1000:9bc5::caseD_3d();
          }
          if ((DAT_3395_40ee & 4) != 0) {
            uStack_10._0_1_ = 0xec;
            uStack_10._1_1_ = 0x34;
            uStack_14._0_1_ = 0xa7;
            uStack_14._1_1_ = 0;
            uStack_12._0_1_ = 0xb6;
            uStack_12._1_1_ = 0;
            uStack_16._0_1_ = 0;
            uStack_16._1_1_ = 0x1d;
            pbStack_18 = (byte *)0x8a3a;
            switchD_1000:9bc5::caseD_3d();
          }
          if ((DAT_3395_40ee & 8) != 0) {
            uStack_10._0_1_ = 0xf6;
            uStack_10._1_1_ = 0x34;
            uStack_14._0_1_ = 0xbd;
            uStack_14._1_1_ = 0;
            uStack_12._0_1_ = 0xb6;
            uStack_12._1_1_ = 0;
            uStack_16._0_1_ = 0;
            uStack_16._1_1_ = 0x1d;
            pbStack_18 = (byte *)0x8a52;
            switchD_1000:9bc5::caseD_3d();
          }
          bVar39 = 0;
          local_6 = (int *)(s_SB_DSP_not_detected___defaulting_3395_1773 + 0x10);
          iVar26 = 0xd3;
          do {
            puVar41 = (uint *)(uint)DAT_3395_40ef;
            if ((1 << (bVar39 & 0x1f) & (uint)puVar41) != 0) {
              uStack_10._0_1_ = (byte)((ulong)local_6 >> 0x10);
              uStack_10._1_1_ = (char)((ulong)local_6 >> 0x18);
              uStack_12._0_1_ = 0xa2;
              uStack_12._1_1_ = 0;
              uStack_14._0_1_ = (char)iVar26;
              uStack_14._1_1_ = (char)((uint)iVar26 >> 8);
              uStack_16._0_1_ = 0;
              uStack_16._1_1_ = 0x1d;
              pbStack_18 = (byte *)0x8a87;
              puVar41 = (uint *)switchD_1000:9bc5::caseD_3d();
            }
            iVar26 = iVar26 + 0x16;
            bVar39 = bVar39 + 1;
            uVar27 = (int)local_6._2_2_ + 10;
            local_6 = (int *)((ulong)uVar27 << 0x10);
          } while (uVar27 < 0x3550);
          if (param_1 == 1) {
            uStack_10._0_1_ = 0;
            uStack_10._1_1_ = 0;
            uStack_12._0_1_ = 0x14;
            uStack_12._1_1_ = 0x35;
            uStack_16._0_1_ = 8;
            uStack_16._1_1_ = 0;
            uStack_14._0_1_ = 4;
            uStack_14._1_1_ = 0;
            pbStack_18 = (byte *)0x1d00;
            cStack_1a = 0xb3;
            uStack_19 = 0x8a;
            FUN_1d00_036a();
            uStack_10._0_1_ = 0;
            uStack_10._1_1_ = 0;
            uStack_12._0_1_ = 0x1e;
            uStack_12._1_1_ = 0x35;
            uStack_16._0_1_ = 0x22;
            uStack_16._1_1_ = 1;
            uStack_14._0_1_ = 4;
            uStack_14._1_1_ = 0;
            pbStack_18 = (byte *)0x1d00;
            cStack_1a = 0xc6;
            uStack_19 = 0x8a;
            FUN_1d00_036a();
            uStack_10._0_1_ = 0;
            uStack_10._1_1_ = 0;
            uStack_12._0_1_ = 0x28;
            uStack_12._1_1_ = 0x35;
            uStack_16._0_1_ = 0x8b;
            uStack_16._1_1_ = 0;
            uStack_14._0_1_ = 4;
            uStack_14._1_1_ = 0;
            pbStack_18 = (byte *)0x1d00;
            cStack_1a = -0x27;
            uStack_19 = 0x8a;
            FUN_1d00_036a();
            if (DAT_3395_3c7a != 0 || DAT_3395_3c78 != 0) {
              uStack_10._0_1_ = 0xc;
              uStack_10._1_1_ = 0;
              uStack_12._0_1_ = 0;
              uStack_12._1_1_ = 0x1d;
              uStack_14._0_1_ = 0xec;
              uStack_14._1_1_ = 0x8a;
              uVar28 = FUN_1275_0160();
              uStack_10._0_1_ = (byte)uVar28;
              uStack_10._1_1_ = (char)((uint)uVar28 >> 8);
              uStack_14._0_1_ = (char)_DAT_3395_3c78;
              uStack_14._1_1_ = (char)((ulong)_DAT_3395_3c78 >> 8);
              uStack_12._0_1_ = (byte)((ulong)_DAT_3395_3c78 >> 0x10);
              uStack_12._1_1_ = (undefined1)((ulong)_DAT_3395_3c78 >> 0x18);
              pbStack_18 = (byte *)0xffff;
              uStack_16._0_1_ = 0x17;
              uStack_16._1_1_ = 0;
              cStack_1a = 'u';
              uStack_19 = 0x12;
              pcStack_1c = (char *)0x8b00;
              FUN_1d00_03e4();
            }
            pcVar49 = (char *)0x1d00;
            DAT_3395_410a = (DAT_3395_410a + 0x9c & -(DAT_3395_410a < 100)) + 100;
            pbVar44 = (byte *)(((uint)DAT_3395_410a * 0x12) / 100);
            bVar50 = DAT_3395_40f3 == '\0';
            param_2 = (byte *)&DAT_3395_0001;
code_r0x00018b28:
            if (bVar50) {
              uStack_10._0_1_ = 4;
            }
            else {
              uStack_10._0_1_ = 0xc;
            }
            uStack_10._1_1_ = 0;
            uStack_12._0_1_ = 0;
            uStack_12._1_1_ = (undefined1)((uint)pcVar49 >> 8);
            uStack_14._0_1_ = 0x35;
            uStack_14._1_1_ = 0x8b;
            uVar23 = FUN_1275_0160();
            uStack_10._0_1_ = 0;
            uStack_10._1_1_ = 0;
            uStack_12._0_1_ = 0x75;
            uStack_12._1_1_ = 0x12;
            uStack_14._0_1_ = 0x42;
            uStack_14._1_1_ = 0x8b;
            uVar28 = FUN_1275_0160();
            uStack_10._0_1_ = (byte)uVar28;
            uStack_10._1_1_ = (char)((uint)uVar28 >> 8);
            uStack_12._1_1_ = uStack_10._1_1_;
            uStack_14._0_1_ = 7;
            uStack_14._1_1_ = 0;
            uStack_16 = (undefined4 *)-(int)(pbVar44 + -0x12);
            pcStack_1c = (char *)0xe9;
            cStack_1a = 0xb5;
            uStack_19 = 0;
            pcStack_1e = (char *)s_3You_recover_to_witness_the_defu_3395_1233 + 0x42;
            uStack_22 = (byte *)CONCAT22(0x8b60,(byte *)uStack_22);
            pbStack_18 = pbVar44;
            uStack_12._0_1_ = uVar23;
            puVar41 = (uint *)FUN_1d00_02c4();
            if (param_2 == (byte *)&DAT_3395_0001) {
              DAT_3395_410b = (DAT_3395_410b + 0x9c & -(DAT_3395_410b < 100)) + 100;
              uVar27 = ((uint)DAT_3395_410b * 0x12) / 100;
              if (DAT_3395_40f2 == '\0') {
                uStack_10._0_1_ = 2;
                uStack_10._1_1_ = 0;
                uStack_12._0_1_ = 0;
                uStack_12._1_1_ = 0x1d;
                uStack_14._0_1_ = 0x9d;
                uStack_14._1_1_ = 0x8b;
                cVar22 = FUN_1275_0160();
                cVar22 = cVar22 + -5;
              }
              else {
                uStack_10._0_1_ = 10;
                uStack_10._1_1_ = 0;
                uStack_12._0_1_ = 0;
                uStack_12._1_1_ = 0x1d;
                uStack_14._0_1_ = 0x91;
                uStack_14._1_1_ = 0x8b;
                cVar22 = FUN_1275_0160();
              }
              uStack_10._0_1_ = 0;
              uStack_10._1_1_ = 0;
              uStack_12._0_1_ = 0x75;
              uStack_12._1_1_ = 0x12;
              uStack_14._0_1_ = 0xac;
              uStack_14._1_1_ = 0x8b;
              uVar28 = FUN_1275_0160();
              uStack_10._0_1_ = (byte)uVar28;
              uStack_10._1_1_ = (char)((uint)uVar28 >> 8);
              uStack_12._1_1_ = uStack_10._1_1_;
              uStack_14._0_1_ = 7;
              uStack_14._1_1_ = 0;
              uStack_16 = (undefined4 *)-(uVar27 - 0x12);
              pcStack_1c = (char *)0xd3;
              cStack_1a = 0xb5;
              uStack_19 = 0;
              pcStack_1e = (char *)s_3You_recover_to_witness_the_defu_3395_1233 + 0x42;
              uStack_22 = (byte *)CONCAT22(0x8bca,(byte *)uStack_22);
              pbStack_18 = (byte *)uVar27;
              uStack_12._0_1_ = cVar22;
              FUN_1d00_02c4();
              uStack_10._0_1_ = 1;
              uStack_10._1_1_ = 0;
              if (DAT_3395_3c72 == '\0') {
                uStack_12._0_1_ = 7;
              }
              else {
                uStack_12._0_1_ = 0xf;
              }
              uStack_12._1_1_ = 0;
              uStack_14._0_1_ = 0;
              uStack_14._1_1_ = 0x1d;
              uStack_16._0_1_ = 0xe9;
              uStack_16._1_1_ = 0x8b;
              uVar28 = FUN_1275_0160();
              uStack_12._1_1_ = (undefined1)((uint)uVar28 >> 8);
              uStack_16._0_1_ = 0xdc;
              uStack_16._1_1_ = 0;
              uStack_14._0_1_ = 0xc2;
              uStack_14._1_1_ = 0;
              pbStack_18 = (byte *)((char *)s_3You_recover_to_witness_the_defu_3395_1233 + 0x42);
              cStack_1a = 0xfb;
              uStack_19 = 0x8b;
              uStack_12._0_1_ = (char)uVar28;
              FUN_1155_088e();
              uStack_10._0_1_ = 0;
              uStack_10._1_1_ = 0;
              uStack_16._0_1_ = 0xdc;
              uStack_16._1_1_ = 0;
              uStack_14._0_1_ = 0xc2;
              uStack_14._1_1_ = 0;
              pbStack_18 = (byte *)0x1155;
              cStack_1a = 0xf;
              uStack_19 = 0x8c;
              uStack_12._0_1_ = (char)uVar28;
              uStack_12._1_1_ = extraout_AH_01;
              FUN_1155_088e();
              uStack_12._0_1_ = (byte)DAT_3395_40bc;
              uStack_12._1_1_ = (undefined1)((ulong)DAT_3395_40bc >> 8);
              uStack_10._0_1_ = (byte)((ulong)DAT_3395_40bc >> 0x10);
              uStack_10._1_1_ = (char)((ulong)DAT_3395_40bc >> 0x18);
              uStack_14._0_1_ = 0x10;
              uStack_14._1_1_ = 0x14;
              uStack_16 = &uStack_26;
              pbStack_18 = (byte *)0x1155;
              cStack_1a = 0x34;
              uStack_19 = 0x8c;
              FUN_21bc_278c();
              uStack_12._0_1_ = 0;
              uStack_12._1_1_ = 0;
              uStack_10._0_1_ = 0;
              uStack_10._1_1_ = 0;
              uStack_14._0_1_ = 0xbc;
              uStack_14._1_1_ = 0x21;
              uStack_16._0_1_ = 0x3f;
              uStack_16._1_1_ = 0x8c;
              uVar28 = FUN_1275_0160();
              uStack_12._0_1_ = (byte)uVar28;
              uStack_12._1_1_ = (undefined1)((uint)uVar28 >> 8);
              uStack_14._0_1_ = 0xb;
              uStack_14._1_1_ = 0;
              uStack_16._0_1_ = 0x75;
              uStack_16._1_1_ = 0x12;
              pbStack_18 = (byte *)0x8c4a;
              uVar28 = FUN_1275_0160();
              uStack_14._0_1_ = (char)uVar28;
              uStack_14._1_1_ = (char)((uint)uVar28 >> 8);
              pbStack_18 = (byte *)&uStack_26;
              pcStack_1c = (char *)0xc0;
              cStack_1a = 0x13;
              uStack_19 = 0;
              pcStack_1e = (char *)0x8c;
              uStack_22 = (byte *)0x12758c61;
              uStack_16._0_1_ = uVar12;
              uStack_16._1_1_ = uVar13;
              puVar41 = (uint *)FUN_1d00_0250();
            }
          }
          return puVar41;
        case 7:
          return puVar36;
        case 9:
          bVar50 = (byte)(cVar22 + pbVar44[(int)puVar40]) == '\0';
          while( true ) {
            uStack_12._0_1_ = (byte)pcVar49;
            uVar23 = (byte)uStack_12;
            uStack_12._1_1_ = (undefined1)((uint)pcVar49 >> 8);
            uVar12 = uStack_12._1_1_;
            if (!bVar50) {
              uStack_10._0_1_ = (byte)puVar40;
              uStack_10._1_1_ = (char)((uint)puVar40 >> 8);
              uStack_12._0_1_ = (byte)((ulong)uStack_26 >> 0x10);
              uStack_12._1_1_ = (undefined1)((ulong)uStack_26 >> 0x18);
              uStack_16._0_1_ = 2;
              uStack_16._1_1_ = 0x27;
              uStack_14._0_1_ = uVar23;
              uStack_14._1_1_ = uVar12;
              FUN_1200_0410();
            }
            pbVar44 = param_2 + 0x12;
            iVar26 = iStack_28 + 1;
            _uStack_2a = CONCAT22(iVar26,uStack_2a);
            if ((int)DAT_3395_4cc0 <= iVar26) break;
            iVar26 = *(int *)pbVar44;
            uStack_26 = (undefined2 *)
                        CONCAT22(uStack_26._2_2_,
                                 (undefined2 *)&DAT_3395_426c + (uint)*(byte *)(iVar26 + 4) * 4);
            pbVar34 = (byte *)(uint)*(byte *)(iVar26 + 3);
            uStack_16 = (undefined4 *)
                        ((int)pbVar34 * 10 +
                        ((undefined2 *)&DAT_3395_4272)[(uint)*(byte *)(iVar26 + 4) * 4]);
            lVar30 = *(long *)((int)uStack_16 + 6);
            cStack_1a = (char)lVar30;
            uStack_19 = (undefined1)((ulong)lVar30 >> 8);
            pbStack_18 = (byte *)((ulong)lVar30 >> 0x10);
            if (lVar30 == 0) {
              pcVar49 = (char *)s_Unable_to_force_DSP_detection_3395_1739 + 9;
              uStack_14._0_1_ = 0x46;
              uStack_14._1_1_ = 0x25;
              uStack_12._0_1_ = uVar23;
              uStack_12._1_1_ = uVar12;
              uStack_10 = (int)uStack_16;
              uVar28 = FUN_1742_03fe();
              cStack_1a = (char)uVar28;
              uStack_19 = (undefined1)((uint)uVar28 >> 8);
              pbStack_18 = pbVar34;
            }
            pcStack_1e = DAT_3395_61d4;
            if (((0 < (int)DAT_3395_61d4) && (DAT_3395_426a == '\0')) &&
               ((*(char *)(iVar26 + 7) == '\0' || (*(char *)(iVar26 + 7) == '\x01')))) {
              pcStack_1e = (char *)0x0;
            }
            bVar50 = (bool)((*(byte *)(iVar26 + 5) & 0x20) >> 5);
            if ((*(char *)(iVar26 + 6) == '@') || (*(char *)(iVar26 + 6) == '?')) {
              bVar50 = bVar50 == false;
            }
            if ((*(char *)(iVar26 + 7) == '\0') || (*(char *)(iVar26 + 7) == '\x01')) {
              if (bVar50 == false) {
                iVar33 = DAT_3395_40c0 - *(int *)(iVar26 + 0xc);
              }
              else {
                iVar33 = (DAT_3395_40c0 - *(int *)(iVar26 + 0x10)) + 0x80;
              }
              iVar25 = DAT_3395_40c2 - *(int *)(iVar26 + 0xe);
            }
            else {
              if (bVar50 == false) {
                iVar33 = *(int *)(iVar26 + 0xe) - DAT_3395_40c2;
              }
              else {
                iVar33 = (*(int *)(iVar26 + 0x12) - DAT_3395_40c2) + -0x80;
              }
              iVar25 = *(int *)(iVar26 + 0xc) - DAT_3395_40c0;
            }
            uStack_22 = (byte *)CONCAT22(iVar33,(byte *)uStack_22);
            uStack_26 = (undefined2 *)CONCAT22(iVar26,(undefined2 *)uStack_26);
            if (DAT_3395_40ba == 0) {
              lVar30 = (long)iVar25 * (long)DAT_3395_4110;
              uVar28 = (undefined2)lVar30;
            }
            else {
              lVar30 = (long)iVar25 * (long)DAT_3395_410e;
              uVar28 = (undefined2)lVar30;
            }
            uStack_e = (undefined1)uVar28;
            uStack_d = (undefined1)((uint)uVar28 >> 8);
            pcStack_1c = (char *)(*(int *)(param_2 + 0x18) + -3);
            iVar26 = *(int *)(param_2 + 0x14);
            pbVar34 = param_2 + 0x18;
            param_2 = pbVar44;
            if (iVar26 <= *(int *)pbVar34) {
              uStack_22 = (byte *)CONCAT22(iVar33,pbVar44);
              piVar24 = (int *)(iVar26 * 2 + 0x4740);
              do {
                uVar27 = *(uint *)((byte *)uStack_22 + 0x10);
                *(long *)((byte *)uStack_22 + 0xe) =
                     *(long *)((byte *)uStack_22 + 0xe) + *(long *)((byte *)uStack_22 + 10);
                iVar33 = (uVar27 >> 4) + DAT_3395_44ae;
                uStack_12._0_1_ = uStack_e;
                uStack_12._1_1_ = uStack_d;
                uStack_10._0_1_ = (byte)((ulong)lVar30 >> 0x10);
                uStack_10._1_1_ = (char)((ulong)lVar30 >> 0x18);
                uStack_14._0_1_ = (char)uVar27;
                uStack_14._1_1_ = (char)(uVar27 >> 8);
                uStack_16._0_1_ = (byte)iVar26;
                uVar23 = (byte)uStack_16;
                uStack_16._1_1_ = (undefined1)((uint)iVar26 >> 8);
                uVar12 = uStack_16._1_1_;
                pbStack_18 = (byte *)(uint)*(byte *)(uStack_26._2_2_ + 7);
                cStack_1a = (char)pcVar49;
                uStack_19 = (undefined1)((uint)pcVar49 >> 8);
                pcVar49 = (char *)s_Climb_down_3395_1c4d + 7;
                pcStack_1c = (char *)0x2689;
                iVar25 = FUN_1c54_0710();
                iVar25 = iVar25 + uStack_22._2_2_;
                if (uStack_14._1_1_ != '\0') {
                  iVar25 = -iVar25;
                }
                uStack_10._0_1_ = *(undefined1 *)CONCAT11(uStack_16._1_1_,(byte)uStack_16);
                uStack_10._1_1_ = 0;
                uStack_12._0_1_ = (byte)iVar25;
                uStack_12._1_1_ = (undefined1)((uint)iVar25 >> 8);
                uStack_16._0_1_ = (byte)((ulong)uStack_26 >> 0x10);
                uStack_16._1_1_ = (undefined1)((ulong)uStack_26 >> 0x18);
                pbStack_18 = (byte *)((char *)s_Climb_down_3395_1c4d + 7);
                cStack_1a = -0x56;
                uStack_19 = 0x26;
                uStack_14._0_1_ = uVar23;
                uStack_14._1_1_ = uVar12;
                pbVar44 = (byte *)FUN_1200_02bc();
                *piVar24 = uVar27 + DAT_3395_44b0;
                if ((CONCAT11(uStack_10._1_1_,(byte)uStack_10) == 1) ||
                   ((byte *)CONCAT11(uStack_12._1_1_,(byte)uStack_12) != pbVar44)) {
                  uStack_12._0_1_ = (byte)pcStack_1e;
                  uStack_12._1_1_ = (undefined1)((uint)pcStack_1e >> 8);
                  uStack_10._0_1_ = (byte)pcStack_1c;
                  uStack_10._1_1_ = (char)((uint)pcStack_1c >> 8);
                  pcStack_1c = (char *)CONCAT11(uStack_19,cStack_1a);
                  cStack_1a = (char)pbVar44;
                  uStack_19 = (undefined1)((uint)pbVar44 >> 8);
                  pcStack_1e = (char *)s_Climb_down_3395_1c4d + 7;
                  pcVar49 = (char *)0x1155;
                  uStack_22 = (byte *)CONCAT22(0x26d7,(byte *)uStack_22);
                  pbStack_18 = pbVar44;
                  uStack_16._0_1_ = uVar23;
                  uStack_16._1_1_ = uVar12;
                  uStack_14 = (int *)iVar33;
                  FUN_1155_04d0();
                }
                piVar24 = piVar24 + 1;
                iVar26 = iVar26 + 1;
              } while (iVar26 <= *(int *)((byte *)uStack_22 + 6));
              param_2 = (byte *)uStack_22;
            }
            bVar50 = ((undefined2 *)uStack_26)[1] == 0;
            puVar40 = (undefined2 *)uStack_26;
          }
          return DAT_3395_4cc0;
        case 10:
          goto switchD_1000_48c6_caseD_a;
        case 0xb:
          uStack_10._0_1_ = 0;
          uStack_10._1_1_ = 0x10;
          uStack_12._0_1_ = 0x8e;
          uStack_12._1_1_ = 0x46;
          FUN_1452_0080();
        case 8:
          uStack_e = 1;
          uStack_d = 0;
          uStack_10._0_1_ = 0;
          uStack_10._1_1_ = 0x10;
          uStack_12._0_1_ = 0x98;
          uStack_12._1_1_ = 0x46;
          FUN_1275_030e();
          uStack_e = 0;
          uStack_d = 0;
          uStack_10._0_1_ = 0x75;
          uStack_10._1_1_ = 0x12;
          uStack_12._0_1_ = 0xa2;
          uStack_12._1_1_ = 0x46;
          FUN_1817_05ca();
          uStack_e = 0x17;
          uStack_d = 0x18;
          uStack_10._0_1_ = 0xaa;
          uStack_10._1_1_ = 0x46;
          FUN_1275_027e();
          uStack_e = 0x75;
          uStack_d = 0x12;
          uStack_10._0_1_ = 0xaf;
          uStack_10._1_1_ = 0x46;
          FUN_1275_0aa6();
          DAT_3395_3c71 = 0;
          uStack_e = 0x81;
          uStack_d = 8;
          uStack_10._0_1_ = 0x75;
          uStack_10._1_1_ = 0x12;
          uStack_12._0_1_ = 0xbb;
          uStack_12._1_1_ = 0x46;
          puVar41 = (uint *)FUN_1452_0080();
          return puVar41;
        case 0xc:
          uStack_10._0_1_ = 0;
          uStack_10._1_1_ = 0x10;
          uStack_12._0_1_ = 7;
          uStack_12._1_1_ = 0xc1;
          FUN_208d_05e2();
          uStack_10._0_1_ = 0x8d;
          uStack_10._1_1_ = 0x20;
          uStack_12._0_1_ = 0xc;
          uStack_12._1_1_ = 0xc1;
          DAT_3395_3618 = FUN_208d_0646();
          uStack_10._0_1_ = 0x8d;
          uStack_10._1_1_ = 0x20;
          uStack_12._0_1_ = 0x14;
          uStack_12._1_1_ = 0xc1;
          puVar41 = (uint *)FUN_208d_0678();
          DAT_3395_17a5 = 1;
          if (cVar22 == '\0') {
            DAT_3395_40ab = '\0';
          }
          if ((int)pbVar44 < 1) {
            DAT_3395_3c67 = '\0';
          }
          if ((DAT_3395_40ac == '\0') || (DAT_3395_3c67 == '\0')) {
            DAT_3395_17a4 = '\0';
          }
          else {
            DAT_3395_17a4 = '\x01';
          }
          DAT_3395_361a = puVar41;
          if (DAT_3395_17a4 == '\0') {
            uStack_10._0_1_ = 0x8d;
            uStack_10._1_1_ = 0x20;
            uStack_12._0_1_ = 0x57;
            uStack_12._1_1_ = 0xc1;
            puVar41 = (uint *)FUN_208d_070e();
          }
          if (cVar22 != '\0') {
            uStack_10._0_1_ = 0;
            uStack_10._1_1_ = 0;
            uStack_12._0_1_ = 0x8d;
            uStack_12._1_1_ = 0x20;
            uStack_14._0_1_ = 0x65;
            uStack_14._1_1_ = 0xc1;
            puVar41 = (uint *)FUN_1bff_0294();
          }
          if (DAT_3395_40ab != '\0') {
            uStack_10._0_1_ = 0x8d;
            uStack_10._1_1_ = 0x20;
            uStack_12._0_1_ = 0x53;
            uStack_12._1_1_ = 0xc2;
            puVar41 = (uint *)FUN_1bff_00a6();
          }
          return puVar41;
        case 0xd:
          pbVar44[(int)puVar40] = pbVar44[(int)puVar40] + cVar22 + bVar50;
          *(byte *)(*(int *)pbVar44 + 5) = *(byte *)(*(int *)pbVar44 + 5) | 1;
          *(byte *)(*(int *)(pbVar44 + 2) + 5) = *(byte *)(*(int *)(pbVar44 + 2) + 5) | 1;
          if (*(char *)(*(int *)pbVar44 + 7) == '\x02') {
            iVar26 = 0x40;
          }
          else {
            iVar26 = 1;
          }
          uStack_12 = (uint *)(iVar26 * 2 + *(int *)(pbVar44 + 4));
          uVar28 = *(undefined2 *)(pbVar44 + 6);
          if ((((undefined1 *)&DAT_3395_cf58)[*(byte *)uStack_12] & 8) != 0) {
            uStack_10._0_1_ = (byte)uVar28;
            uStack_10._1_1_ = (char)((uint)uVar28 >> 8);
            uStack_14._0_1_ = 0;
            uStack_14._1_1_ = 0x10;
            uStack_16._0_1_ = 0x61;
            uStack_16._1_1_ = 6;
            piVar24 = (int *)FUN_1000_0000();
            local_6 = (int *)CONCAT22(uVar28,piVar24);
            iVar26 = *(int *)(pbVar44 + 8);
            piVar24[4] = iVar26;
            if (iVar26 == 3) {
              *(byte *)(*local_6 + 5) = *(byte *)(*local_6 + 5) | 1;
              *(byte *)(piVar24[1] + 5) = *(byte *)(piVar24[1] + 5) | 1;
            }
          }
          if (*(char *)(*(int *)pbVar44 + 7) == '\x02') {
            iVar26 = 0x40;
          }
          else {
            iVar26 = 1;
          }
          uStack_12 = (uint *)-(iVar26 * 2 - *(int *)(pbVar44 + 4));
          uVar28 = *(undefined2 *)(pbVar44 + 6);
          if ((((undefined1 *)&DAT_3395_cf58)[(byte)*uStack_12] & 8) != 0) {
            uStack_10._0_1_ = (byte)uVar28;
            uStack_10._1_1_ = (char)((uint)uVar28 >> 8);
            uStack_14._0_1_ = 0;
            uStack_14._1_1_ = 0x10;
            uStack_16._0_1_ = 0xc5;
            uStack_16._1_1_ = 6;
            piVar24 = (int *)FUN_1000_0000();
            uStack_12 = *(uint **)(pbVar44 + 8);
            piVar24[4] = (int)uStack_12;
            if (uStack_12 == (uint *)((int)(undefined2 *)&DAT_3395_0002 + 1)) {
              *(byte *)(*piVar24 + 5) = *(byte *)(*piVar24 + 5) | 1;
              *(byte *)(piVar24[1] + 5) = *(byte *)(piVar24[1] + 5) | 1;
            }
          }
          return uStack_12;
        case 0xe:
          uStack_10._0_1_ = (byte)uVar28;
          uStack_10._1_1_ = (char)((uint)uVar28 >> 8);
          uStack_14._0_1_ = (char)puVar40;
          uStack_14._1_1_ = (char)((uint)puVar40 >> 8);
          lVar30 = CONCAT13(uStack_14._1_1_,CONCAT12((char)uStack_14,(int)(int *)in_ECX + 1)) *
                   CONCAT13(uStack_10._1_1_,CONCAT12((byte)uStack_10,puVar36));
          cStack_1a = (char)lVar30;
          uStack_19 = (undefined1)((ulong)lVar30 >> 8);
          pbStack_18 = (byte *)((ulong)lVar30 >> 0x10);
          uStack_10._0_1_ = (byte)((ulong)(long)DAT_3395_4110 >> 0x10);
          uStack_10._1_1_ = (char)((ulong)(long)DAT_3395_4110 >> 0x18);
          lVar31 = lStack_2e * CONCAT13(uStack_10._1_1_,CONCAT12((byte)uStack_10,DAT_3395_4110));
          if (lStack_2e == lStack_32) {
            lVar32 = (long)DAT_3395_410e * (long)local_a;
            cStack_1a = (char)lVar32;
            uStack_19 = (undefined1)((ulong)lVar32 >> 8);
            pbStack_18 = (byte *)((ulong)lVar32 >> 0x10);
            uStack_26 = (undefined2 *)lVar31;
          }
          else {
            uStack_26 = (undefined2 *)((long)DAT_3395_4110 * (long)CONCAT22(pcStack_1c,pcStack_1e));
          }
          lVar32 = lVar31 + lVar30;
          uStack_12._0_1_ = (byte)lVar32;
          uStack_12._1_1_ = (undefined1)((ulong)lVar32 >> 8);
          uStack_10._0_1_ = (byte)((ulong)lVar32 >> 0x10);
          uStack_10._1_1_ = (char)((ulong)lVar32 >> 0x18);
          uVar27 = (int)(undefined2 *)uStack_26 + CONCAT11(uStack_19,cStack_1a);
          iVar26 = uStack_26._2_2_ + (int)pbStack_18 +
                   (uint)CARRY2((uint)(undefined2 *)uStack_26,CONCAT11(uStack_19,cStack_1a));
          if ((lVar32 < 0x10000) && ((lVar32 < 0 || ((uint)lVar32 < 0x4000)))) {
            uStack_12._0_1_ = 0;
            uStack_12._1_1_ = 0x40;
            uStack_10._0_1_ = 0;
            uStack_10._1_1_ = 0;
          }
          if ((iVar26 < 1) && ((iVar26 < 0 || (uVar27 < 0x4000)))) {
            uVar27 = 0x4000;
            iVar26 = 0;
          }
          uStack_14._1_1_ = (char)((uint)iVar26 >> 8);
          uStack_14._0_1_ = (char)iVar26;
          *(int *)(pbVar44 + 0x16) =
               (int)(DAT_3395_3624 /
                    CONCAT13(uStack_10._1_1_,
                             CONCAT12((byte)uStack_10,CONCAT11(uStack_12._1_1_,(byte)uStack_12)))) +
               DAT_3395_44b0;
          uVar27 = (int)(DAT_3395_3624 / CONCAT13(uStack_14._1_1_,CONCAT12((char)uStack_14,uVar27)))
                   + DAT_3395_44b0;
          *(uint *)(pbVar44 + 0x1a) = uVar27;
          lVar32 = DAT_3395_361c;
          if ((*(int *)(pbVar44 + 0x16) <= (int)param_2) || ((int)uVar27 <= (int)param_2)) {
            uStack_14._0_1_ = (char)(DAT_3395_410e >> 0xf);
            if (CONCAT13(uStack_10._1_1_,
                         CONCAT12((byte)uStack_10,CONCAT11(uStack_12._1_1_,(byte)uStack_12))) ==
                0x4000) {
              if (local_a == (uint *)CONCAT22(unaff_DI,(uint *)CONCAT11(uStack_d,uStack_e))) {
                if ((DAT_3395_40b4 == 0x5a) || (DAT_3395_40b4 == 0x10e)) {
                  uStack_22 = (byte *)0x4000;
                }
                else {
                  uStack_10._0_1_ = (byte)((ulong)(long)DAT_3395_4110 >> 0x10);
                  uStack_10._1_1_ = (char)((ulong)(long)DAT_3395_4110 >> 0x18);
                  uStack_22 = (byte *)((0x4000 - lVar30) /
                                      CONCAT13(uStack_10._1_1_,
                                               CONCAT12((byte)uStack_10,DAT_3395_4110)));
                }
              }
              else if ((DAT_3395_40b4 == 0) || (DAT_3395_40b4 == 0xb4)) {
                uStack_e = 0;
                uStack_d = 0x40;
                unaff_DI = 0;
              }
              else {
                uStack_10._0_1_ = (byte)((ulong)(long)DAT_3395_410e >> 0x10);
                uStack_10._1_1_ = (char)((ulong)(long)DAT_3395_410e >> 0x18);
                lVar30 = (0x4000 - lVar31) /
                         CONCAT13(uStack_10._1_1_,CONCAT12((byte)uStack_10,DAT_3395_410e));
                uStack_e = (undefined1)lVar30;
                uStack_d = (undefined1)((ulong)lVar30 >> 8);
                unaff_DI = (undefined2)((ulong)lVar30 >> 0x10);
              }
              lVar30 = (long)DAT_3395_4110 * CONCAT22(unaff_DI,CONCAT11(uStack_d,uStack_e));
              uStack_12._0_1_ = (byte)uStack_22;
              uStack_12._1_1_ = (undefined1)((ulong)uStack_22 >> 8);
              uStack_10._0_1_ = (byte)((ulong)uStack_22 >> 0x10);
              uStack_10._1_1_ = (char)((ulong)uStack_22 >> 0x18);
              uVar27 = (uint)lVar30;
              iVar26 = (int)((ulong)lVar30 >> 0x10);
              lVar30 = CONCAT13((char)uStack_14,CONCAT12((char)uStack_14,DAT_3395_410e)) *
                       (long)uStack_22;
            }
            else {
              lVar30 = (long)DAT_3395_4110 * CONCAT22(unaff_DI,CONCAT11(uStack_d,uStack_e));
              uStack_12._0_1_ = (byte)uStack_22;
              uStack_12._1_1_ = (undefined1)((ulong)uStack_22 >> 8);
              uStack_10._0_1_ = (byte)((ulong)uStack_22 >> 0x10);
              uStack_10._1_1_ = (char)((ulong)uStack_22 >> 0x18);
              uVar27 = (uint)lVar30;
              iVar26 = (int)((ulong)lVar30 >> 0x10);
              lVar30 = CONCAT13((char)uStack_14,CONCAT12((char)uStack_14,DAT_3395_410e)) *
                       (long)uStack_22;
            }
            iVar33 = uVar27 - (uint)lVar30;
            iVar26 = (iVar26 - (int)((ulong)lVar30 >> 0x10)) - (uint)(uVar27 < (uint)lVar30);
            lVar30 = (CONCAT22(iVar26,iVar33) * DAT_3395_361c) /
                     CONCAT13(uStack_10._1_1_,
                              CONCAT12((byte)uStack_10,CONCAT11(uStack_12._1_1_,(byte)uStack_12)));
            uVar27 = (uint)lVar30;
            uVar35 = uVar27 + DAT_3395_44ac;
            uVar27 = (int)((ulong)lVar30 >> 0x10) + ((int)DAT_3395_44ac >> 0xf) +
                     (uint)CARRY2(uVar27,DAT_3395_44ac);
            if (((int)uVar27 < -1) || ((0x7fff < uVar27 && (uVar35 < 0xc001)))) {
              (pbVar44 + 0x14)[0] = 1;
              (pbVar44 + 0x14)[1] = 0xc0;
            }
            else {
              if ((-1 < (int)uVar27) && ((0 < (int)uVar27 || (0x3fff < uVar35)))) {
                uVar35 = 0x3fff;
              }
              *(uint *)(pbVar44 + 0x14) = uVar35;
            }
            uStack_14._0_1_ = (char)(DAT_3395_410e >> 0xf);
            if (lVar32 == 0x4000) {
              if (local_a == (uint *)CONCAT22(unaff_DI,(uint *)CONCAT11(uStack_d,uStack_e))) {
                if ((DAT_3395_40b4 == 0x5a) || (DAT_3395_40b4 == 0x10e)) {
                  pcVar11 = (char *)0x4000;
                }
                else {
                  uStack_10._0_1_ = (byte)((ulong)(long)DAT_3395_4110 >> 0x10);
                  uStack_10._1_1_ = (char)((ulong)(long)DAT_3395_4110 >> 0x18);
                  pcVar11 = (char *)((0x4000 - CONCAT22(iVar26,iVar33)) /
                                    CONCAT13(uStack_10._1_1_,CONCAT12((byte)uStack_10,DAT_3395_4110)
                                            ));
                }
              }
              else if ((DAT_3395_40b4 == 0) || (DAT_3395_40b4 == 0xb4)) {
                local_a = (uint *)0x4000;
              }
              else {
                uStack_10._0_1_ = (byte)((ulong)(long)DAT_3395_410e >> 0x10);
                uStack_10._1_1_ = (char)((ulong)(long)DAT_3395_410e >> 0x18);
                local_a = (uint *)((0x4000 - (long)uStack_26) /
                                  CONCAT13(uStack_10._1_1_,CONCAT12((byte)uStack_10,DAT_3395_410e)))
                ;
                pcVar11 = (char *)CONCAT22(pcStack_1c,pcStack_1e);
              }
              uVar27 = (uint)((long)DAT_3395_4110 * (long)local_a);
              iVar26 = (int)((ulong)((long)DAT_3395_4110 * (long)local_a) >> 0x10);
              lVar30 = CONCAT13((char)uStack_14,CONCAT12((char)uStack_14,DAT_3395_410e)) *
                       (long)pcVar11;
            }
            else {
              uStack_10._0_1_ = (byte)pcStack_1c;
              uStack_10._1_1_ = (char)((uint)pcStack_1c >> 8);
              uVar27 = (uint)((long)DAT_3395_4110 * (long)local_a);
              iVar26 = (int)((ulong)((long)DAT_3395_4110 * (long)local_a) >> 0x10);
              lVar30 = CONCAT13((char)uStack_14,CONCAT12((char)uStack_14,DAT_3395_410e)) *
                       CONCAT13(uStack_10._1_1_,CONCAT12((byte)uStack_10,pcStack_1e));
            }
            lVar30 = (CONCAT22((iVar26 - (int)((ulong)lVar30 >> 0x10)) -
                               (uint)(uVar27 < (uint)lVar30),uVar27 - (uint)lVar30) * DAT_3395_361c)
                     / CONCAT13((char)uStack_14,CONCAT12((char)uStack_14,DAT_3395_410e));
            uVar27 = (uint)lVar30;
            uVar35 = uVar27 + DAT_3395_44ac;
            uVar27 = (int)((ulong)lVar30 >> 0x10) + ((int)DAT_3395_44ac >> 0xf) +
                     (uint)CARRY2(uVar27,DAT_3395_44ac);
            if (((int)uVar27 < -1) || ((0x7fff < uVar27 && (uVar35 < 0xc001)))) {
              uVar35 = 0xc001;
            }
            else if ((-1 < (int)uVar27) && ((0 < (int)uVar27 || (0x3fff < uVar35)))) {
              uVar35 = 0x3fff;
            }
            if ((int)uVar35 < *(int *)(pbVar44 + 0x14)) {
              *(uint *)(pbVar44 + 0x14) = *(uint *)(pbVar44 + 0x14) ^ uVar35;
              uVar35 = uVar35 ^ *(uint *)(pbVar44 + 0x14);
              *(uint *)(pbVar44 + 0x14) = *(uint *)(pbVar44 + 0x14) ^ uVar35;
              uVar27 = *(uint *)(pbVar44 + 0x16);
              uVar9 = *(uint *)(pbVar44 + 0x1a);
              *(uint *)(pbVar44 + 0x1a) = *(uint *)(pbVar44 + 0x1a) ^ uVar27 ^ uVar9;
              *(uint *)(pbVar44 + 0x16) = uVar27 ^ uVar9 ^ *(uint *)(pbVar44 + 0x1a);
            }
            uVar27 = DAT_3395_44a6;
            if ((int)DAT_3395_44a6 < *(int *)(pbVar44 + 0x14)) {
              *(uint *)(param_1 + 0x18) = uVar35;
            }
            else {
              *(uint *)(pbVar44 + 0x18) = uVar35;
              if (DAT_3395_44a4 <= (int)uVar35) {
                return (uint *)(uint *)CONCAT31((uint3)(byte)(uVar27 >> 8),1);
              }
            }
          }
          return (uint *)(uVar27 & 0xff00);
        case 0xf:
          FUN_1d00_04fe();
          FUN_1452_01a0();
          if (cVar14 == '\0') {
            FUN_1d00_1600();
          }
          else {
            uStack_e = (undefined1)DAT_3395_61ca;
            uStack_d = (undefined1)((uint)DAT_3395_61ca >> 8);
            uStack_10._0_1_ = 0x97;
            uStack_10._1_1_ = 8;
            uStack_12._0_1_ = 0;
            uStack_12._1_1_ = 0x1d;
            uStack_14._0_1_ = 0x65;
            uStack_14._1_1_ = 0x47;
            FUN_21bc_07e0();
            uStack_e = 0xbc;
            uStack_d = 0x21;
            uStack_10._0_1_ = 0x7c;
            uStack_10._1_1_ = 0x47;
            FUN_21bc_07e0();
            uStack_e = 0x93;
            uStack_d = 0x47;
            FUN_21bc_07e0();
            uStack_e = 0xaa;
            uStack_d = 0x47;
            FUN_21bc_07e0();
            if (DAT_3395_3c6e != '\0') {
              uStack_e = 200;
              uStack_d = 0x47;
              FUN_21bc_07e0();
            }
            uStack_e = (undefined1)DAT_3395_df52;
            uStack_d = (undefined1)((ulong)DAT_3395_df52 >> 8);
            uStack_10._0_1_ = 0xbc;
            uStack_10._1_1_ = 0x21;
            uStack_12._0_1_ = 0xe1;
            uStack_12._1_1_ = 0x47;
            uVar28 = FUN_1689_0b90();
            uStack_10._0_1_ = (byte)uVar28;
            uStack_10._1_1_ = (char)((uint)uVar28 >> 8);
            uStack_12._0_1_ = 0x7c;
            uStack_12._1_1_ = 9;
            uStack_14._0_1_ = 0x42;
            uStack_14._1_1_ = 0x17;
            uStack_16._0_1_ = 0xea;
            uStack_16._1_1_ = 0x47;
            FUN_21bc_07e0();
            uStack_e = (undefined1)DAT_3395_df5e;
            uStack_d = (undefined1)((ulong)DAT_3395_df5e >> 8);
            uStack_10._0_1_ = 0xbc;
            uStack_10._1_1_ = 0x21;
            uStack_12._0_1_ = 3;
            uStack_12._1_1_ = 0x48;
            uVar28 = FUN_1689_0b94();
            uStack_10._0_1_ = (byte)uVar28;
            uStack_10._1_1_ = (char)((uint)uVar28 >> 8);
            uStack_12._0_1_ = 0xc2;
            uStack_12._1_1_ = 9;
            uStack_14._0_1_ = 0x42;
            uStack_14._1_1_ = 0x17;
            uStack_16._0_1_ = 0xc;
            uStack_16._1_1_ = 0x48;
            FUN_21bc_07e0();
            uStack_e = (undefined1)DAT_3395_df6a;
            uStack_d = (undefined1)((ulong)DAT_3395_df6a >> 8);
            uStack_10._0_1_ = 0xbc;
            uStack_10._1_1_ = 0x21;
            uStack_12._0_1_ = 0x25;
            uStack_12._1_1_ = 0x48;
            uVar28 = FUN_1689_0b98();
            uStack_10._0_1_ = (byte)uVar28;
            uStack_10._1_1_ = (char)((uint)uVar28 >> 8);
            uStack_12._0_1_ = '\b';
            uStack_12._1_1_ = 10;
            uStack_14._0_1_ = 0x42;
            uStack_14._1_1_ = 0x17;
            uStack_16._0_1_ = 0x2e;
            uStack_16._1_1_ = 0x48;
            FUN_21bc_07e0();
          }
          puVar41 = (uint *)FUN_21bc_01eb();
          return puVar41;
        case 0x10:
          pbVar2 = param_2 + (int)register0x00000010 + 0xc44;
          bVar39 = (byte)in_ECX & 7;
          *pbVar2 = *pbVar2 >> bVar39 | *pbVar2 << 8 - bVar39;
          return (uint *)((int)puVar36 - 1U & (uint)puVar45);
        case 0x11:
          pbVar44[(int)puVar40 + 1] = pbVar44[(int)puVar40 + 1] + cVar22;
          uStack_10._0_1_ = uVar21;
          uStack_10._1_1_ = uVar17;
          do {
            if ((int *)&DAT_3395_3c80 < local_6._2_2_) {
              plVar42 = alStack_18e;
              in_ECX = (int *)((ulong)local_6 & 0xffff);
              do {
                if (local_a._3_1_ != '\0') break;
                if (CONCAT13(uStack_d,CONCAT12(uStack_e,CONCAT11(uStack_10._1_1_,(byte)uStack_10)))
                    == *plVar42) {
                  param_2[4] = (byte)in_ECX;
                  local_a = (uint *)CONCAT13(1,(uint3)local_a);
                }
                plVar42 = plVar42 + 1;
                uVar27 = (int)(int *)in_ECX + 1;
                in_ECX = (int *)(ulong)uVar27;
              } while (uVar27 < uStack_12);
            }
            piVar37 = in_ECX;
            if (local_a._3_1_ == '\0') {
              uStack_10._0_1_ = 0;
              uStack_10._1_1_ = 0;
              uStack_12 = (uint *)&iStack_76;
              uStack_16._0_1_ = *param_2;
              piVar37 = (int *)CONCAT31((int3)((ulong)in_ECX >> 8),(byte)uStack_16);
              uStack_16._1_1_ = (undefined1)((ulong)in_ECX >> 8);
              pbStack_18 = (byte *)CONCAT11(uStack_d,uStack_e);
              cStack_1a = '\0';
              uStack_19 = 0;
              pcStack_1c = (char *)0x0;
              uStack_22 = (byte *)CONCAT22(0x307f,(byte *)uStack_22);
              pcStack_1e = pcVar49;
              uStack_14 = (int *)uStack_12;
              iVar26 = FUN_1275_054a();
              local_6._2_2_[1] = iVar26;
              local_6._2_2_[-1] = iStack_76;
              local_6._2_2_[-2] = (uint)bStack_74;
              *local_6._2_2_ = 0;
              param_2[4] = (byte)uStack_12;
              uStack_12._0_1_ = 0;
              uStack_12._1_1_ = (undefined1)((uint)pcVar49 >> 8);
              if (cStack_73 == '\0') {
                if ((param_2[5] & 8) != 0) {
                  uStack_10._0_1_ = 0x29;
                  uStack_10._1_1_ = 5;
                  pcVar49 = (char *)s_About_to__s_game____s__Press_ESC_3395_1f66 + 0x23;
                  uStack_14._0_1_ = 2;
                  uStack_14._1_1_ = 0x31;
                  FUN_1f89_0002();
                }
              }
              else {
                uStack_10._0_1_ = 0x5a;
                uStack_10._1_1_ = 0;
                pcVar49 = (char *)&DAT_3395_21bc;
                uStack_14._0_1_ = 0xb9;
                uStack_14._1_1_ = 0x30;
                iVar26 = FUN_21bc_3ccf();
                *local_6._2_2_ = iVar26;
                if (*local_6._2_2_ == 0) {
                  uStack_10._0_1_ = 0xf7;
                  uStack_10._1_1_ = 4;
                  uStack_12._0_1_ = 5;
                  uStack_12._1_1_ = 5;
                  uStack_14._0_1_ = 0xbc;
                  uStack_14._1_1_ = 0x21;
                  pcVar49 = (char *)s_About_to__s_game____s__Press_ESC_3395_1f66 + 0x23;
                  uStack_16._0_1_ = 0xd4;
                  uStack_16._1_1_ = 0x30;
                  FUN_1f89_0002();
                }
                piVar47 = (int *)*local_6._2_2_;
                piVar24 = &iStack_76;
                uStack_10._0_1_ = 0x95;
                uStack_10._1_1_ = 0x33;
                for (piVar37 = (int *)0x16; (int *)piVar37 != (int *)0x0;
                    piVar37 = (int *)(ulong)((int)(int *)piVar37 - 1)) {
                  piVar7 = piVar47;
                  piVar47 = piVar47 + 2;
                  piVar5 = piVar24;
                  piVar24 = piVar24 + 2;
                  *(undefined4 *)piVar7 = *(undefined4 *)piVar5;
                }
                *piVar47 = *piVar24;
              }
              *(ulong *)pbStack_18 =
                   CONCAT13(uStack_d,CONCAT12(uStack_e,CONCAT11(uStack_10._1_1_,(byte)uStack_10)));
              local_6 = (int *)(ZEXT24(local_6._2_2_ + 4) << 0x10);
              pbStack_18 = (byte *)((int)pbStack_18 + 4);
            }
            uStack_12 = (uint *)((int)uStack_14 + 1);
            uStack_16._0_1_ = (byte)pcVar49;
            uStack_14._0_1_ = (byte)uStack_16;
            uStack_16._1_1_ = (undefined1)((uint)pcVar49 >> 8);
            uStack_14._1_1_ = uStack_16._1_1_;
            if (DAT_3395_61cc <= uStack_12) {
              uStack_12._0_1_ = 5;
              uStack_12._1_1_ = 0;
              uStack_10._0_1_ = 0;
              uStack_10._1_1_ = 0;
              uStack_16._0_1_ = 0x33;
              uStack_16._1_1_ = 0x31;
              DAT_3395_4120 = FUN_10f6_0054();
              DAT_3395_4126 = 5;
              DAT_3395_4125 = ((undefined1 *)&DAT_3395_d058)[DAT_3395_4120];
              DAT_3395_d45b = (byte)uStack_12;
              uVar27 = (uint)DAT_3395_4120;
              iVar26 = CONCAT11(uStack_12._1_1_,(byte)uStack_12);
              if (((undefined1 *)&DAT_3395_d35a)[uVar27] == '\x05') {
                puVar40 = (undefined2 *)&DAT_3395_3c82 +
                          CONCAT11(uStack_12._1_1_,(byte)uStack_12) * 4;
                local_a._2_2_ = (undefined4 *)(uVar27 * 4 + (int)pcStack_1c);
                do {
                  uStack_10._0_1_ = 0;
                  uStack_10._1_1_ = 0;
                  uStack_12 = (uint *)&iStack_76;
                  uStack_16._0_1_ = (byte)uVar27;
                  uStack_16._1_1_ = (undefined1)(uVar27 >> 8);
                  uVar10 = *local_a._2_2_;
                  cStack_1a = (char)uVar10;
                  uStack_19 = (undefined1)((ulong)uVar10 >> 8);
                  pbStack_18 = (byte *)((ulong)uVar10 >> 0x10);
                  pcStack_1c = (char *)uVar10;
                  pcStack_1e = (char *)s_3I_m_sorry__that_is_not_the_corr_3395_10f1 + 5;
                  uStack_22 = (byte *)CONCAT22(0x318d,(byte *)uStack_22);
                  uStack_14 = (int *)uStack_12;
                  uVar28 = FUN_1275_054a();
                  *puVar40 = uVar28;
                  puVar40[-2] = iStack_76;
                  puVar40[-3] = (uint)bStack_74;
                  local_a._2_2_ = local_a._2_2_ + 1;
                  puVar40 = puVar40 + 4;
                  pcVar49 = (undefined1 *)&DAT_3395_d35b + uVar27;
                  uVar27 = uVar27 + 1;
                  iVar26 = (int)uStack_12 + 1;
                } while (*pcVar49 == '\x05');
              }
              DAT_3395_61d0 = iVar26;
              DAT_3395_411e = 0;
              puVar38 = (undefined4 *)&DAT_3395_413c;
              do {
                puVar43 = (undefined4 *)&DAT_3395_4112;
                puVar48 = puVar38;
                for (iVar26 = 10; iVar26 != 0; iVar26 = iVar26 + -1) {
                  puVar8 = puVar48;
                  puVar48 = puVar48 + 1;
                  puVar6 = puVar43;
                  puVar43 = puVar43 + 1;
                  *puVar8 = *puVar6;
                }
                *(undefined2 *)puVar48 = *(undefined2 *)puVar43;
                puVar38 = (undefined4 *)((int)puVar38 + 0x2a);
              } while (puVar38 < (undefined4 *)0x4262);
              uStack_10._0_1_ = cStack_1a;
              uStack_10._1_1_ = uStack_19;
              uStack_12._0_1_ = 0xf6;
              uStack_12._1_1_ = 0x10;
              uStack_14._0_1_ = 0xe4;
              uStack_14._1_1_ = 0x31;
              FUN_21bc_1bb6();
              uStack_12._0_1_ = (byte)pcStack_1c;
              uStack_12._1_1_ = (undefined1)((uint)pcStack_1c >> 8);
              uStack_14._0_1_ = 0xbc;
              uStack_14._1_1_ = 0x21;
              uStack_16._0_1_ = 0xef;
              uStack_16._1_1_ = 0x31;
              puVar41 = (uint *)FUN_21bc_3cae();
              return puVar41;
            }
            uStack_10._0_1_ = (byte)DAT_3395_61cc;
            uStack_10._1_1_ = (char)(DAT_3395_61cc >> 8);
            uStack_14._0_1_ = 2;
            uStack_14._1_1_ = 0;
            pcVar49 = (char *)0x1d00;
            pbStack_18 = (byte *)0x2ffe;
            FUN_1d00_087e();
            param_2 = (byte *)CONCAT11(uStack_16._1_1_,(byte)uStack_16);
            local_a = (uint *)(ulong)DAT_3395_254c;
            uVar10 = *(undefined4 *)((uint)*param_2 * 4 + (int)pcStack_1c);
            uStack_10._0_1_ = (byte)uVar10;
            uStack_10._1_1_ = (char)((ulong)uVar10 >> 8);
            uStack_e = (undefined1)((ulong)uVar10 >> 0x10);
            uStack_d = (undefined1)((ulong)uVar10 >> 0x18);
            local_6 = (int *)((ulong)local_6 & 0xffff0000);
            in_ECX = piVar37;
          } while( true );
        case 0x12:
          goto switchD_1000_48c6_caseD_12;
        case 0x13:
          bVar50 = puVar36 == (uint *)0xffff;
          goto code_r0x00018b28;
        case 0x14:
          goto switchD_1000_48c6_caseD_14;
        case 0x15:
          uStack_10._0_1_ = (byte)((ulong)puVar3 >> 0x10);
          uVar20 = (byte)uStack_10;
          uStack_12 = (uint *)(*(int *)(param_2 + 0x10) + -0x10);
          uStack_14._0_1_ = (char)param_4;
          uVar23 = (char)uStack_14;
          uStack_14._1_1_ = (char)((uint)param_4 >> 8);
          uVar12 = uStack_14._1_1_;
          pbStack_18 = param_2;
          pcStack_1c = (char *)0x1000;
          pcStack_1e = (char *)0x4f4a;
          cStack_1a = uVar16;
          uStack_19 = uStack_10._1_1_;
          uStack_16._0_1_ = uVar15;
          uStack_16._1_1_ = uVar18;
          uStack_10._1_1_ = 0;
          cVar22 = FUN_14a2_0250();
          if (cVar22 == '\0') {
            uStack_12 = (uint *)(*(int *)(param_2 + 0x10) + 0x10);
            pbStack_18 = param_2;
            pcStack_1c = (char *)0x1000;
            pcStack_1e = (char *)0x4f69;
            cStack_1a = uVar16;
            uStack_19 = uVar19;
            uStack_16._0_1_ = uVar15;
            uStack_16._1_1_ = uVar18;
            uStack_14._0_1_ = uVar23;
            uStack_14._1_1_ = uVar12;
            uStack_10._0_1_ = uVar20;
            uStack_10._1_1_ = 0;
            cVar22 = FUN_14a2_0250();
            if (cVar22 == '\0') goto LAB_14a2_055a;
          }
          local_6 = (int *)0x1010001;
LAB_14a2_055a:
          if (local_6._2_1_ == '\0') {
            iVar26 = (int)(char)pbVar44[0x13];
          }
          else {
            iVar26 = 0;
          }
          if (local_6._3_1_ == '\0') {
            local_a._2_2_ = (undefined4 *)(int)(char)pbVar44[0x14];
          }
          else {
            local_a._2_2_ = (undefined4 *)0x0;
          }
          if ((pbVar44[0xb] != 8) || ((local_6._2_1_ == '\0' && (local_6._3_1_ == '\0')))) {
            uStack_10._0_1_ = (byte)local_a._2_2_;
            uVar17 = (byte)uStack_10;
            uStack_10._1_1_ = (char)((uint)local_a._2_2_ >> 8);
            uVar13 = uStack_10._1_1_;
            uStack_12._0_1_ = (byte)iVar26;
            uVar20 = (byte)uStack_12;
            uStack_12._1_1_ = (undefined1)((uint)iVar26 >> 8);
            uVar21 = uStack_12._1_1_;
            uVar10 = *(undefined4 *)(param_2 + 0x10);
            uStack_16._0_1_ = (byte)uVar10;
            uStack_16._1_1_ = (undefined1)((ulong)uVar10 >> 8);
            uStack_14._0_1_ = (char)((ulong)uVar10 >> 0x10);
            uStack_14._1_1_ = (char)((ulong)uVar10 >> 0x18);
            pbStack_18 = (byte *)0x1000;
            cStack_1a = 0xd4;
            uStack_19 = 0x4f;
            FUN_1611_04ba();
            *(int *)(param_2 + 0x10) = *(int *)(param_2 + 0x10) + iVar26;
            *(int *)(param_2 + 0x12) = *(int *)(param_2 + 0x12) + (int)local_a._2_2_;
            pbStack_18 = (byte *)((char *)s_Error_opening_file__s_3395_160b + 6);
            pcVar49 = (char *)s_Configure_game____3395_1ab0 + 0xe;
            cStack_1a = 0xf1;
            uStack_19 = 0x4f;
            uStack_16._0_1_ = uVar15;
            uStack_16._1_1_ = uVar18;
            uStack_14._0_1_ = uVar23;
            uStack_14._1_1_ = uVar12;
            uStack_12._0_1_ = uVar20;
            uStack_12._1_1_ = uVar21;
            uStack_10._0_1_ = uVar17;
            uStack_10._1_1_ = uVar13;
            FUN_1abe_015a();
          }
          if (((pbVar44[0xb] == 6) && (local_6._2_1_ != '\0')) && (local_6._3_1_ != '\0')) {
            uStack_10._0_1_ = (byte)pcVar49;
            uStack_10._1_1_ = (char)((uint)pcVar49 >> 8);
            pcVar49 = (char *)s_About_to__s_game____s__Press_ESC_3395_1f66 + 0x23;
            uStack_12._0_1_ = 0xf;
            uStack_12._1_1_ = 0x50;
            uVar27 = FUN_1f89_0196();
            if ((uVar27 & 1) == 0) {
              local_a._2_2_ = (undefined4 *)-(int)(char)pbVar44[0x14];
              pbVar44[0x14] = (byte)local_a._2_2_;
            }
            else {
              iVar26 = -(int)(char)pbVar44[0x13];
              pbVar44[0x13] = (byte)iVar26;
            }
          }
          if (((iVar26 != 0) || (local_a._2_2_ != (undefined4 *)0x0)) &&
             (param_2[3] = param_2[3] + 1, (uint)pbVar44[1] + (uint)*pbVar44 <= (uint)param_2[3])) {
            param_2[3] = *pbVar44;
          }
          uStack_10._0_1_ = (byte)local_a._2_2_;
          uStack_10._1_1_ = (char)((uint)local_a._2_2_ >> 8);
          uStack_12._0_1_ = (byte)iVar26;
          uStack_12._1_1_ = (undefined1)((uint)iVar26 >> 8);
          cStack_1a = 0x80;
          uStack_19 = 0x50;
          pbStack_18 = (byte *)pcVar49;
          uStack_16._0_1_ = uVar16;
          uStack_16._1_1_ = uVar19;
          uStack_14._0_1_ = uVar15;
          uStack_14._1_1_ = uVar18;
          FUN_14a2_00ac();
          iVar26 = (*(uint *)(param_2 + 0x12) & 0xffc0) * 2 +
                   ((int)(*(uint *)(param_2 + 0x10) & 0xffdf) >> 5);
          *(int *)(param_2 + 0xc) = iVar26 + 0x373e;
          (param_2 + 0xe)[0] = 0x21;
          (param_2 + 0xe)[1] = 0x2e;
          pbVar44[0xd] = *(byte *)(iVar26 + 0x373f);
          *(byte *)(iVar26 + 0x373f) = *param_2;
          uVar10 = *(undefined4 *)(param_2 + 0xc);
          uStack_12._0_1_ = (byte)uVar10;
          uStack_12._1_1_ = (undefined1)((ulong)uVar10 >> 8);
          uStack_10._0_1_ = (byte)((ulong)uVar10 >> 0x10);
          uStack_10._1_1_ = (char)((ulong)uVar10 >> 0x18);
          uStack_14._0_1_ = (char)pcVar49;
          uStack_14._1_1_ = (char)((uint)pcVar49 >> 8);
          uStack_16._0_1_ = 0xd6;
          uStack_16._1_1_ = 0x50;
          iVar26 = FUN_10f6_017c();
          puVar41 = (uint *)0x0;
          if (iVar26 + 1 != 0) {
            local_a._0_1_ = (byte)iVar26;
            puVar41 = (uint *)CONCAT11((char)((uint)(iVar26 + 1) >> 8),(byte)local_a);
            pbVar44[0xe] = (byte)local_a;
          }
          return puVar41;
        case 0x16:
          *(byte *)((int)puVar40 + 0x29) = *(byte *)((int)puVar40 + 0x29) | bVar39;
code_r0x00018009:
          pbVar44[3] = pbVar44[3] + 1;
          if (*(int *)in_ECX <= (int)(uint)pbVar44[3]) {
            pbVar44[3] = 0;
          }
          puVar3 = (uint *)((int *)in_ECX + 1);
          iVar26 = DAT_3395_07e4 + (uint)CARRY2(DAT_3395_07e2,*puVar3);
          *(uint *)(pbVar44 + 8) = DAT_3395_07e2 + *puVar3;
          *(int *)(pbVar44 + 10) = iVar26;
LAB_17c7_03c2:
          local_6 = (int *)CONCAT22(local_6._2_2_,unaff_ES);
          uStack_10._1_1_ = (char)param_2;
          uStack_e = (undefined1)((uint)param_2 >> 8);
          uStack_12._1_1_ = SUB21(pcVar49,0);
          uStack_10._0_1_ = (byte)((uint)pcVar49 >> 8);
          uStack_14._1_1_ = 0x3a;
          uStack_12._0_1_ = 0x80;
          FUN_17c7_026e();
          uVar27 = *(int *)(pbVar44 + 0x10) - DAT_3395_40c0 >> 0xf;
          if ((int)((*(int *)(pbVar44 + 0x10) - DAT_3395_40c0 ^ uVar27) - uVar27) < 0x15) {
            uVar27 = *(int *)(pbVar44 + 0x12) - DAT_3395_40c2 >> 0xf;
            puVar41 = (uint *)((*(int *)(pbVar44 + 0x12) - DAT_3395_40c2 ^ uVar27) - uVar27);
            if ((int)puVar41 < 0x15) goto LAB_17c7_043b;
          }
          do {
            uStack_10._1_1_ = (char)unaff_ES;
            uStack_e = (undefined1)((uint)unaff_ES >> 8);
            uStack_12._1_1_ = SUB21(pbVar44,0);
            uStack_10._0_1_ = (byte)((uint)pbVar44 >> 8);
            uStack_14._1_1_ = (char)pcVar49;
            uStack_12._0_1_ = (byte)((uint)pcVar49 >> 8);
            pcVar49 = (char *)s_Configure_game____3395_1ab0 + 0xe;
            uStack_16._1_1_ = 0xa8;
            uStack_14._0_1_ = 0x80;
            puVar41 = (uint *)FUN_1abe_0430();
LAB_17c7_043b:
            while( true ) {
              do {
                pbVar34 = param_2;
                param_2 = pbVar34 + 0x2a;
                uVar27 = (int)local_6._2_2_ - 1;
                local_6 = (int *)((ulong)uVar27 << 0x10);
                if (uVar27 == 0) {
                  return puVar41;
                }
                pbVar44 = pbVar34 + 0x38;
                unaff_ES = (undefined1 *)0x3395;
                bVar39 = pbVar34[0x3c];
                in_ECX = (int *)ZEXT24((undefined2 *)&DAT_3395_3c7c + (uint)bVar39 * 4);
                if (pbVar34[0x36] == 1) {
                  if (*(ulong *)(pbVar34 + 0x40) <= _DAT_3395_07e2) goto code_r0x00018009;
                  goto LAB_17c7_03c2;
                }
                puVar41 = (uint *)(pbVar34[0x36] - 2);
              } while (puVar41 != (uint *)0x0);
              if (*(ulong *)(pbVar34 + 0x40) <= _DAT_3395_07e2) {
                pbVar34[0x3b] = pbVar34[0x3b] + 1;
                iVar26 = DAT_3395_07e4 +
                         (uint)CARRY2(DAT_3395_07e2,((undefined2 *)&DAT_3395_3c7e)[(uint)bVar39 * 4]
                                     );
                *(uint *)(pbVar34 + 0x40) =
                     DAT_3395_07e2 + ((undefined2 *)&DAT_3395_3c7e)[(uint)bVar39 * 4];
                *(int *)(pbVar34 + 0x42) = iVar26;
              }
              puVar41 = (uint *)(uint)pbVar34[0x3b];
              if ((int)puVar41 < (int)((undefined2 *)&DAT_3395_3c7c)[(uint)bVar39 * 4]) break;
              pbVar34[0x36] = 0;
            }
            local_6 = (int *)CONCAT22(uVar27,(undefined1 *)0x3395);
          } while( true );
        }
        goto LAB_140d_0414;
      }
      uStack_14._0_1_ = 0xbc;
      uStack_14._1_1_ = 0x21;
      uStack_16._0_1_ = 2;
      uStack_16._1_1_ = 0x49;
      uStack_12._0_1_ = cVar14;
      uStack_12._1_1_ = uVar12;
      uStack_10._0_1_ = uVar15;
      uStack_10._1_1_ = uVar18;
      FUN_1452_0322();
      pbVar44 = pbVar44 + 1;
      uVar28 = extraout_var_01;
    } while ((int)pbVar44 < param_1);
  }
  uStack_10._0_1_ = 0xbc;
  uStack_10._1_1_ = 0x21;
  uStack_12._0_1_ = 1;
  uStack_12._1_1_ = 0x4a;
  FUN_1452_00d6();
  uStack_10._0_1_ = 0;
  uStack_14._0_1_ = 1;
  uStack_14._1_1_ = 0;
  uStack_12._0_1_ = 1;
  uStack_16._0_1_ = 0xbc;
  uStack_16._1_1_ = 0x21;
  pbStack_18 = (byte *)0x4a0e;
  uStack_12._1_1_ = local_6._3_1_;
  uStack_10._1_1_ = extraout_AH;
  FUN_1d00_26c2();
  uStack_10._0_1_ = 0;
  uStack_10._1_1_ = 0;
  uStack_12._0_1_ = 0;
  uStack_14._0_1_ = 0;
  uStack_14._1_1_ = 0x1d;
  uStack_16._0_1_ = 0x1b;
  uStack_16._1_1_ = 0x4a;
  uStack_12._1_1_ = extraout_AH_00;
  puVar41 = (uint *)FUN_1452_01de();
  return puVar41;
switchD_1000_48c6_caseD_14:
  do {
    uStack_10._0_1_ = 0x72;
    uStack_10._1_1_ = 0;
    uStack_12._0_1_ = (byte)pcVar49;
    uStack_12._1_1_ = (undefined1)((uint)pcVar49 >> 8);
    uStack_14._0_1_ = 0x65;
    uStack_14._1_1_ = 2;
    FUN_1f89_0002();
    pbVar44 = (byte *)CONCAT11(uStack_10._1_1_,(byte)uStack_10);
    do {
      piVar37 = (int *)CONCAT13(uStack_12._1_1_,
                                CONCAT12((byte)uStack_12,CONCAT11(uStack_14._1_1_,(char)uStack_14)))
      ;
      iVar26 = *piVar37 * 0x12;
      piVar24 = (int *)(iVar26 + 0x3076);
      *piVar37 = *piVar37 + 1;
      ((int *)CONCAT22(0x2e21,piVar24))[0] = 0;
      ((int *)CONCAT22(0x2e21,piVar24))[1] = 0;
      local_6._3_1_ = '\0';
      if (DAT_3395_61ca < 1) {
        local_6._0_2_ = (undefined1 *)&DAT_3395_61f8;
        local_6._2_2_ = (int *)0x0;
        iVar33 = (int)local_6._2_2_;
      }
      else {
        local_6._0_2_ = (undefined1 *)&DAT_3395_61f8;
        iVar33 = 0;
        do {
          if ((((((undefined1 *)local_6)[5] & 8) != 0) &&
              ((undefined4 *)(*(int *)((undefined1 *)local_6 + 0xc) >> 6) == local_a._2_2_)) &&
             ((uint *)(*(int *)((undefined1 *)local_6 + 0xe) >> 6) == (uint *)local_a)) {
            *(undefined1 **)CONCAT22(0x2e21,piVar24) = (undefined1 *)local_6;
            break;
          }
          local_6._0_2_ = (undefined1 *)local_6 + 0x1c;
          iVar33 = iVar33 + 1;
        } while (iVar33 < DAT_3395_61ca);
      }
      do {
        puVar45 = (undefined1 *)local_6;
        iVar33 = iVar33 + 1;
        local_6._0_2_ = puVar45 + 0x1c;
        if (DAT_3395_61ca <= iVar33) goto code_r0x00010318;
      } while ((((puVar45[0x21] & 8) == 0) ||
               ((undefined4 *)(*(int *)(puVar45 + 0x28) >> 6) != local_a._2_2_)) ||
              ((uint *)(*(int *)(puVar45 + 0x2a) >> 6) != (uint *)local_a));
      *(undefined2 *)(iVar26 + 0x3078) = (undefined1 *)local_6;
code_r0x00010318:
      if ((*piVar24 == 0) || (*(int *)(iVar26 + 0x3078) == 0)) {
        uStack_e = 0x89;
        uStack_d = 0;
        uStack_10._0_1_ = 0x89;
        uStack_10._1_1_ = 0x1f;
        uStack_12._0_1_ = 0x30;
        uStack_12._1_1_ = 3;
        FUN_1f89_0002();
        pbVar44 = (byte *)CONCAT11(uStack_10._1_1_,(byte)uStack_10);
      }
      pcVar49 = (char *)s_About_to__s_game____s__Press_ESC_3395_1f66 + 0x23;
      *(undefined4 *)(iVar26 + 0x307a) =
           CONCAT13(uStack_16._1_1_,CONCAT12((byte)uStack_16,pbStack_18));
      *(undefined2 *)(iVar26 + 0x307e) = 1;
      *(undefined1 *)(iVar26 + 0x3086) = 0;
      cStack_1a = *(char *)(*piVar24 + 7);
      if (((cStack_1a == '\0') && ((((undefined1 *)&DAT_3395_cf58)[pbVar44[2]] & 8) != 0)) ||
         ((cStack_1a == '\x02' && ((((undefined1 *)&DAT_3395_cf58)[pbVar44[0x80]] & 8) != 0)))) {
        local_6._3_1_ = '\x01';
      }
      if (local_6._3_1_ == '\0') {
        uVar28 = *(undefined2 *)(puVar45 + 0x28);
      }
      else {
        uVar28 = *(undefined2 *)(puVar45 + 0x2c);
      }
      *(undefined2 *)(iVar26 + 0x3082) = uVar28;
      if (local_6._3_1_ == '\0') {
        uVar28 = *(undefined2 *)(puVar45 + 0x2a);
      }
      else {
        uVar28 = *(undefined2 *)(puVar45 + 0x2e);
      }
      *(undefined2 *)(iVar26 + 0x3084) = uVar28;
      puVar41 = (uint *)(CONCAT11((char)((uint)uVar28 >> 8),
                                  local_6._3_1_ << 5 ^ *(byte *)(*piVar24 + 5)) & 0xff20);
      pbVar2 = (byte *)(*piVar24 + 5);
      *pbVar2 = *pbVar2 ^ (byte)puVar41;
      pbVar2 = (byte *)(*(int *)(iVar26 + 0x3078) + 5);
      *pbVar2 = *pbVar2 ^ (local_6._3_1_ << 5 ^ *(byte *)(*(int *)(iVar26 + 0x3078) + 5)) & 0x20;
      pbStack_18 = pbVar44;
      do {
        pbStack_18 = pbStack_18 + 2;
        iVar26 = (int)local_a._2_2_ + 1;
        local_a = (uint *)CONCAT22(iVar26,(uint *)local_a);
        if (0x3f < iVar26) {
          if (0x3f < (int)(uint *)local_a + 1) {
            return puVar41;
          }
          local_a = (uint *)ZEXT24((byte *)((int)(uint *)local_a + 1));
        }
        uStack_16._0_1_ = (byte)DAT_3395_254a;
        uStack_16._1_1_ = (undefined1)((uint)DAT_3395_254a >> 8);
      } while ((((undefined1 *)&DAT_3395_cf58)[*pbStack_18] & 8) == 0);
      pbVar44 = pbStack_18;
    } while (*(int *)CONCAT13(uStack_12._1_1_,
                              CONCAT12((byte)uStack_12,CONCAT11(uStack_14._1_1_,(char)uStack_14))) <
             0x40);
    uStack_e = 0x40;
    uStack_d = 0;
  } while( true );
switchD_1000_48c6_caseD_12:
  do {
    uStack_10._0_1_ = 0xb1;
    uStack_10._1_1_ = 0;
    uStack_12._0_1_ = (byte)pcVar49;
    uStack_12._1_1_ = (undefined1)((uint)pcVar49 >> 8);
    pcVar49 = (char *)s_About_to__s_game____s__Press_ESC_3395_1f66 + 0x23;
    uStack_14._0_1_ = 0x5a;
    uStack_14._1_1_ = 5;
    FUN_1f89_0002();
    do {
      iVar26 = DAT_2e21_0004 * 6;
      puVar41 = (uint *)(iVar26 + 0x36b6);
      DAT_2e21_0004 = DAT_2e21_0004 + 1;
      *puVar41 = (uint)pbVar44;
      *(undefined1 *)(iVar26 + 0x36ba) = 0;
      pbVar34 = param_2;
      do {
        param_2 = pbVar34 + 0x1c;
        pbVar44 = pbVar44 + 1;
        if (*(int *)&DAT_3395_61cc <= (int)pbVar44) {
          return puVar41;
        }
        pbVar1 = pbVar34 + 0x22;
        pbVar34 = param_2;
      } while (*pbVar1 != 0x28);
    } while (DAT_2e21_0004 < 0xc);
    uStack_e = 0xc;
    uStack_d = 0;
  } while( true );
LAB_140d_0414:
  if (uStack_7c <= uStack_86) {
LAB_140d_044e:
    uStack_e = SUB21(pcVar49,0);
    uStack_d = (undefined1)((uint)pcVar49 >> 8);
    uStack_10._0_1_ = 0x27;
    uStack_10._1_1_ = 0x45;
    puVar41 = (uint *)FUN_21bc_05fa();
    return puVar41;
  }
  pcVar49 = (char *)s_MAXOBJ_exceeded___d__3395_1683 + 6;
  uStack_e = 0xf2;
  uStack_d = 0x44;
  cVar22 = FUN_1689_01dc();
  if (cVar22 != '\0') goto LAB_140d_044e;
  do {
    puVar45 = (undefined1 *)in_EDX;
    uStack_e = 0xfb;
    uStack_d = 0x44;
    uVar27 = FUN_1bb2_0090();
    puVar46 = (undefined1 *)(iStack_72 * 0xf >> 0xf);
    in_EDX = (undefined1 *)ZEXT24(puVar46);
    if (puVar46 < puVar45 + (-(uint)(uVar27 < uStack_8a) - (int)puStack_88)) break;
  } while ((puVar45 + (-(uint)(uVar27 < uStack_8a) - (int)puStack_88) < puVar46) ||
          (uVar27 - uStack_8a < (uint)(iStack_72 * 0xf)));
  pcVar49 = (char *)s_Omnipotent__all_powerful__3395_1b9b + 0x17;
  uStack_e = 0xcd;
  uStack_d = 0x44;
  uStack_8a = FUN_1bb2_0090();
  puStack_88 = (undefined1 *)in_EDX;
  uStack_e = 0xb2;
  uStack_d = 0x1b;
  uStack_10._0_1_ = 0xdd;
  uStack_10._1_1_ = 0x44;
  FUN_140d_0326();
  uStack_86 = uStack_86 + 1;
  goto LAB_140d_0414;
switchD_1000_48c6_caseD_a:
  while( true ) {
    out(0x3c5,(char)puVar29);
    if (bVar50) {
      local_6 = (int *)CONCAT22((int)local_6._2_2_ + 1,(undefined1 *)local_6);
    }
    puVar45 = (undefined1 *)local_6 + (int)param_6;
    local_6 = (int *)CONCAT22(local_6._2_2_,puVar45);
    iVar26 = iVar26 + -1;
    if (iVar26 == 0) break;
    puVar46 = (undefined1 *)local_6._2_2_;
    iVar33 = param_8;
    do {
      puVar4 = puVar45;
      puVar45 = puVar45 + 1;
      *puVar46 = *puVar4;
      puVar46 = puVar46 + 0x50;
      iVar33 = iVar33 + -1;
    } while (iVar33 != 0);
    bVar50 = (char)puVar40 < '\0';
    bVar39 = (char)puVar40 << 1 | bVar50;
    puVar40 = (undefined2 *)(uint)bVar39;
    puVar29 = (uint *)(ulong)bVar39;
  }
  return param_6;
}

