
/* WARNING: Instruction at (ram,0x0001f62b) overlaps instruction at (ram,0x0001f62a)
    */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint __cdecl16far FUN_1817_2966(uint param_1)

{
  char *pcVar1;
  undefined4 *puVar2;
  char cVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  undefined4 in_EAX;
  long lVar7;
  int in_CX;
  int iVar8;
  ulong in_EDX;
  char in_BL;
  byte bVar9;
  undefined4 *unaff_SI;
  undefined4 *puVar10;
  char *unaff_DI;
  undefined2 unaff_ES;
  char *pcVar11;
  long lStack_26;
  long lStack_22;
  undefined4 uStack_1e;
  long lStack_1a;
  undefined2 uStack_16;
  char *pcStack_14;
  long *plStack_12;
  undefined2 uStack_e;
  undefined2 uStack_c;
  uint local_6;
  undefined1 local_4;
  char cStack_3;
  
  iVar6 = DAT_3395_410e;
  if (5 < param_1) {
    return local_6;
  }
  pcVar11 = (char *)0x1000;
  switch(param_1) {
  case 0:
    break;
  case 1:
    do {
      if ((DAT_3395_575a < 0x14e) && (puVar10 = unaff_SI, DAT_3395_575c < 0x14e))
      goto LAB_1fa7_0104;
      do {
        pcVar11 = (char *)s_About_to__s_game____s__Press_ESC_3395_1f66 + 0x23;
        FUN_1f89_0002();
        puVar10 = unaff_SI;
LAB_1fa7_0104:
        unaff_SI = puVar10 + 7;
        unaff_DI = unaff_DI + 1;
        if (DAT_3395_61ca <= (int)unaff_DI) {
          plStack_12 = (long *)&DAT_3395_575e;
          uStack_16 = 0xfb94;
          pcStack_14 = pcVar11;
          FUN_21bc_3090();
          plStack_12 = (long *)&DAT_3395_59f8;
          pcStack_14 = (char *)&DAT_3395_21bc;
          uStack_16 = 0xfbab;
          FUN_21bc_3090();
          plStack_12 = (long *)&DAT_3395_5c92;
          pcStack_14 = (char *)&DAT_3395_21bc;
          uStack_16 = 0xfbc2;
          FUN_21bc_3090();
          plStack_12 = (long *)&DAT_3395_5f2c;
          pcStack_14 = (char *)&DAT_3395_21bc;
          uStack_16 = 0xfbd9;
          uVar5 = FUN_21bc_3090();
          return uVar5;
        }
        cVar3 = *(char *)((int)puVar10 + 0x23);
        if (cVar3 == '\0') {
          ((undefined2 *)&DAT_3395_575e)[DAT_3395_5756] = unaff_SI;
          DAT_3395_5756 = DAT_3395_5756 + 1;
        }
        else if (cVar3 == '\x01') {
          ((undefined2 *)&DAT_3395_59f8)[DAT_3395_5758] = unaff_SI;
          DAT_3395_5758 = DAT_3395_5758 + 1;
        }
        else if (cVar3 == '\x02') {
          ((undefined2 *)&DAT_3395_5c92)[DAT_3395_575a] = unaff_SI;
          DAT_3395_575a = DAT_3395_575a + 1;
        }
        else if (cVar3 == '\x03') {
          ((undefined2 *)&DAT_3395_5f2c)[DAT_3395_575c] = unaff_SI;
          DAT_3395_575c = DAT_3395_575c + 1;
        }
      } while ((0x14d < DAT_3395_5756) || (0x14d < DAT_3395_5758));
    } while( true );
  case 2:
    unaff_DI[5] = unaff_DI[5] << 1;
    do {
      if (unaff_SI != (undefined4 *)&DAT_3395_0001) goto LAB_1d00_263c;
      do {
        unaff_DI[5] = '\x01';
LAB_1d00_263c:
        do {
          unaff_SI = (undefined4 *)((int)unaff_SI + 1);
          unaff_DI = unaff_DI + 0x12;
          if (*unaff_DI == '\0') {
            iVar6 = FUN_1d00_191a();
            if (iVar6 == 6) {
              return 0;
            }
            return iVar6 - 0xe;
          }
          pcStack_14 = (char *)0xf60c;
          plStack_12 = (long *)pcVar11;
          FUN_21bc_278c();
          pcVar11 = (char *)&DAT_3395_21bc;
          iVar6 = FUN_21bc_3990();
          uVar5 = (uint)in_EDX;
        } while (iVar6 != 0);
        pcVar11 = (char *)0x1817;
        uVar4 = FUN_1817_2966();
        in_EDX = (ulong)(uVar5 | uVar4);
      } while ((uVar5 | uVar4) != 0);
    } while( true );
  case 3:
    lVar7 = CONCAT22((int)((ulong)in_EAX >> 0x10),DAT_3395_4110) * CONCAT22(uStack_c,uStack_e);
    uVar5 = (uint)lVar7;
    uVar4 = (uint)(DAT_3395_410e * lStack_22);
    iVar8 = uVar5 - uVar4;
    uStack_e = (undefined2)((ulong)DAT_3395_361c >> 0x10);
    lVar7 = (CONCAT22(((int)((ulong)lVar7 >> 0x10) -
                      (int)((ulong)(DAT_3395_410e * lStack_22) >> 0x10)) - (uint)(uVar5 < uVar4),
                      iVar8) * DAT_3395_361c) / (long)CONCAT22(DAT_3395_410e,plStack_12);
    uVar5 = (uint)lVar7;
    uVar4 = uVar5 + DAT_3395_44ac;
    uVar5 = (int)((ulong)lVar7 >> 0x10) + ((int)DAT_3395_44ac >> 0xf) +
            (uint)CARRY2(uVar5,DAT_3395_44ac);
    if (((int)uVar5 < -1) || ((0x7fff < uVar5 && (uVar4 < 0xc001)))) {
      *(undefined2 *)(unaff_SI + 5) = 0xc001;
    }
    else {
      if ((-1 < (int)uVar5) && ((0 < (int)uVar5 || (0x3fff < uVar4)))) {
        uVar4 = 0x3fff;
      }
      *(uint *)(unaff_SI + 5) = uVar4;
    }
    if (CONCAT22(iVar8,uStack_16) == 0x4000) {
      if (CONCAT22(unaff_SI,iVar6) == CONCAT22(plStack_12,uStack_e)) {
        puVar10 = unaff_SI;
        if ((DAT_3395_40b4 == 0x5a) || (DAT_3395_40b4 == 0x10e)) {
          uStack_1e = 0x4000;
        }
        else {
          iVar6 = DAT_3395_4110 >> 0xf;
          uStack_1e = (0x4000 - lStack_1a) / (long)DAT_3395_4110;
        }
      }
      else if ((DAT_3395_40b4 == 0) || (DAT_3395_40b4 == 0xb4)) {
        iVar6 = 0x4000;
        puVar10 = (undefined4 *)0x0;
      }
      else {
        lVar7 = (0x4000 - lStack_26) / (long)DAT_3395_410e;
        iVar6 = (int)lVar7;
        puVar10 = (undefined4 *)((ulong)lVar7 >> 0x10);
      }
      lVar7 = (long)DAT_3395_4110 * CONCAT22(puVar10,iVar6);
      uVar5 = (uint)lVar7;
      iVar6 = (int)((ulong)lVar7 >> 0x10);
      lVar7 = DAT_3395_410e * uStack_1e;
    }
    else {
      lVar7 = (long)DAT_3395_4110 * CONCAT22(unaff_SI,iVar6);
      uVar5 = (uint)lVar7;
      iVar6 = (int)((ulong)lVar7 >> 0x10);
      lVar7 = DAT_3395_410e * uStack_1e;
    }
    lVar7 = (CONCAT22((iVar6 - (int)((ulong)lVar7 >> 0x10)) - (uint)(uVar5 < (uint)lVar7),
                      uVar5 - (uint)lVar7) * DAT_3395_361c) / CONCAT22(iVar8,uStack_16);
    uVar5 = (uint)lVar7;
    uVar4 = uVar5 + DAT_3395_44ac;
    uVar5 = (int)((ulong)lVar7 >> 0x10) + ((int)DAT_3395_44ac >> 0xf) +
            (uint)CARRY2(uVar5,DAT_3395_44ac);
    if (((int)uVar5 < -1) || ((0x7fff < uVar5 && (uVar4 < 0xc001)))) {
      uVar4 = 0xc001;
    }
    else if ((-1 < (int)uVar5) && ((0 < (int)uVar5 || (0x3fff < uVar4)))) {
      uVar4 = 0x3fff;
    }
    if ((int)uVar4 < *(int *)(unaff_SI + 5)) {
      *(uint *)(unaff_SI + 5) = *(uint *)(unaff_SI + 5) ^ uVar4;
      uVar4 = uVar4 ^ *(uint *)(unaff_SI + 5);
      *(uint *)(unaff_SI + 5) = *(uint *)(unaff_SI + 5) ^ uVar4;
      uVar5 = *(uint *)((int)unaff_SI + 0x16) ^ *(uint *)((int)unaff_SI + 0x1a);
      *(uint *)((int)unaff_SI + 0x1a) = *(uint *)((int)unaff_SI + 0x1a) ^ uVar5;
      *(uint *)((int)unaff_SI + 0x16) = uVar5 ^ *(uint *)((int)unaff_SI + 0x1a);
    }
    bVar9 = (byte)((uint)DAT_3395_44a6 >> 8);
    if (DAT_3395_44a6 < *(int *)(unaff_SI + 5)) {
      *(uint *)(param_1 + 0x18) = uVar4;
    }
    else {
      *(uint *)(unaff_SI + 6) = uVar4;
      if (DAT_3395_44a4 <= (int)uVar4) {
        return (uint)CONCAT31((uint3)bVar9,1);
      }
    }
    return (uint)bVar9 << 8;
  case 4:
    plStack_12 = (long *)0x6d;
    pcStack_14 = (char *)0x1000;
    uStack_16 = 0x8967;
    uVar5 = FUN_1d00_0250();
    if (unaff_DI != (char *)&DAT_3395_0001) {
      return uVar5;
    }
    DAT_3395_410c = (DAT_3395_410c + 0x9c & -(DAT_3395_410c < 100)) + 100;
    FUN_21bc_278c();
    FUN_1275_0160();
    FUN_1275_0160();
    plStack_12 = (long *)0x6d;
    pcStack_14 = (char *)s_3You_recover_to_witness_the_defu_3395_1233 + 0x42;
    uStack_16 = 0x89bd;
    FUN_1d00_0250();
    if (DAT_3395_40eb != -1) {
      switchD_1000:9bc5::caseD_3d();
    }
    if ((DAT_3395_40ee & 1) != 0) {
      switchD_1000:9bc5::caseD_3d();
    }
    if ((DAT_3395_40ee & 2) != 0) {
      switchD_1000:9bc5::caseD_3d();
    }
    if ((DAT_3395_40ee & 4) != 0) {
      switchD_1000:9bc5::caseD_3d();
    }
    if ((DAT_3395_40ee & 8) != 0) {
      switchD_1000:9bc5::caseD_3d();
    }
    bVar9 = 0;
    uVar5 = 0x3500;
    do {
      uVar4 = (uint)DAT_3395_40ef;
      if ((1 << (bVar9 & 0x1f) & uVar4) != 0) {
        uVar4 = switchD_1000:9bc5::caseD_3d();
      }
      bVar9 = bVar9 + 1;
      uVar5 = uVar5 + 10;
    } while (uVar5 < 0x3550);
    if (param_1 != 1) {
      return uVar4;
    }
    FUN_1d00_036a();
    FUN_1d00_036a();
    FUN_1d00_036a();
    unaff_DI = (char *)&DAT_3395_0001;
    uVar5 = 0;
    if (DAT_3395_3c7a == 0 && DAT_3395_3c78 == 0) goto LAB_1817_0993;
    break;
  case 5:
    pcVar1 = (char *)(param_1 * 2 + (int)unaff_SI);
    *pcVar1 = *pcVar1 + in_BL;
    for (; in_CX != 0; in_CX = in_CX + -1) {
      pcVar1 = unaff_DI;
      unaff_DI = unaff_DI + 4;
      puVar2 = unaff_SI;
      unaff_SI = unaff_SI + 1;
      *(undefined4 *)pcVar1 = *puVar2;
    }
    FUN_1689_0198();
    uVar5 = FUN_1bff_00d8();
    if (cStack_3 != '\0') {
      uVar5 = FUN_1bff_0294();
    }
    return uVar5;
  }
  FUN_1275_0160();
  plStack_12 = (long *)0xffff;
  pcStack_14 = (char *)s_3You_recover_to_witness_the_defu_3395_1233 + 0x42;
  uStack_16 = 0x8b00;
  uVar5 = FUN_1d00_03e4();
LAB_1817_0993:
  if (unaff_DI == (char *)&DAT_3395_0001) {
    DAT_3395_410a = (DAT_3395_410a + 0x9c & -(DAT_3395_410a < 100)) + 100;
    uVar5 = (uint)DAT_3395_410a;
    FUN_1275_0160();
    FUN_1275_0160();
    uStack_16 = 0xe9;
    pcStack_14 = (char *)0xb5;
    lStack_1a = 0x12758b60;
    plStack_12 = (long *)((uVar5 * 0x12) / 100);
    FUN_1d00_02c4();
    DAT_3395_410b = (DAT_3395_410b + 0x9c & -(DAT_3395_410b < 100)) + 100;
    uVar5 = (uint)DAT_3395_410b;
    if (DAT_3395_40f2 == '\0') {
      FUN_1275_0160();
    }
    else {
      FUN_1275_0160();
    }
    FUN_1275_0160();
    uStack_16 = 0xd3;
    pcStack_14 = (char *)0xb5;
    lStack_1a = 0x12758bca;
    plStack_12 = (long *)((uVar5 * 0x12) / 100);
    FUN_1d00_02c4();
    FUN_1275_0160();
    plStack_12 = (long *)((char *)s_3You_recover_to_witness_the_defu_3395_1233 + 0x42);
    pcStack_14 = (char *)0x8bfb;
    FUN_1155_088e();
    plStack_12 = (long *)0x1155;
    pcStack_14 = (char *)0x8c0f;
    FUN_1155_088e();
    plStack_12 = (long *)0x1155;
    pcStack_14 = (char *)0x8c34;
    FUN_21bc_278c();
    FUN_1275_0160();
    plStack_12 = (long *)0x8c4a;
    FUN_1275_0160();
    plStack_12 = &lStack_26;
    uStack_16 = 0xc0;
    pcStack_14 = (char *)0x13;
    lStack_1a = 0x8c1275;
    uStack_1e = CONCAT22(0x8c61,(undefined2)uStack_1e);
    uVar5 = FUN_1d00_0250();
  }
  return uVar5;
}

