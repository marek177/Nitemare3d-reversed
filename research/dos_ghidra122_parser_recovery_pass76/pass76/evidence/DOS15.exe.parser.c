
void __cdecl16far FUN_1458_0328(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  undefined1 extraout_AH;
  int *piVar5;
  undefined2 uVar6;
  undefined4 *puVar7;
  undefined1 local_7;
  undefined4 local_6;
  
  local_7 = 0;
  local_6 = 0x10001;
  FUN_1277_0c20();
  FUN_1458_0004();
  iVar2 = FUN_21c7_248e(0xa71);
  if (iVar2 != 0) {
    DAT_374a_3c3f = 0;
    DAT_374a_3c32 = 0x12;
  }
  iVar2 = 1;
  if (param_1 < 2) {
LAB_1458_04d1:
    FUN_1458_00d0();
    FUN_1d05_2720(local_6,CONCAT11(extraout_AH,local_7));
    FUN_1458_01d2();
    return;
  }
LAB_1458_036b:
  piVar5 = (int *)(iVar2 * 2 + param_2);
  if (*(char *)*piVar5 != '-') {
    FUN_1458_0316();
  }
  uVar3 = (int)*(char *)(*piVar5 + 1) - 0x62;
  iVar1 = iVar2;
  if (0x16 < uVar3) goto override_jmp_1458_039a_case_5;
                    /* WARNING: Switch is manually overridden */
  switch((undefined4)*(undefined2 *)(uVar3 * 2 + 0x3a0)) {
  case 0x1494e:
    goto override_jmp_1458_039a_case_5;
  case 0x1495c:
    local_7 = 1;
    break;
  case 0x14964:
    puVar7 = (undefined4 *)&DAT_374a_3c30;
    uVar6 = 0xa78;
    goto LAB_1458_03ea;
  case 0x1497c:
    puVar7 = (undefined4 *)&DAT_374a_3c2c;
    uVar6 = 0xa7b;
    goto LAB_1458_03ea;
  case 0x14984:
    puVar7 = &local_6;
    uVar6 = 0xa7e;
    goto LAB_1458_03ea;
  case 0x1498e:
    puVar7 = (undefined4 *)&DAT_374a_3c2e;
    uVar6 = 0xa81;
LAB_1458_03ea:
    iVar2 = iVar2 + 1;
    FUN_21c7_27e8(*(undefined2 *)(iVar2 * 2 + param_2),uVar6,puVar7);
    break;
  case 0x14996:
    iVar2 = iVar2 + 1;
    iVar4 = FUN_21c7_27e8(*(undefined2 *)(iVar2 * 2 + param_2),0xa84,(int)&local_6 + 2);
    iVar1 = iVar2;
    if (iVar4 == 0) goto override_jmp_1458_039a_case_5;
    break;
  case 0x149b4:
    DAT_374a_3c40 = 1;
    break;
  case 0x149bc:
    DAT_374a_3c37 = 0;
    break;
  case 0x149c4:
    DAT_374a_3c38 = 1;
    iVar4 = FUN_21c7_27e8(*(undefined2 *)((iVar2 + 1) * 2 + param_2),0xa87,
                          (undefined4 *)&DAT_374a_3c3a);
    iVar1 = iVar2 + 1;
    if (iVar4 == 1) {
      iVar2 = iVar2 + 2;
      iVar4 = FUN_21c7_27e8(*(undefined2 *)(iVar2 * 2 + param_2),0xa8a,0x3c3c);
      iVar1 = iVar2;
      if (iVar4 == 1) break;
    }
    goto override_jmp_1458_039a_case_5;
  case 0x149fe:
    DAT_374a_3c46 = 1;
    break;
  case 0x14a06:
    DAT_374a_3c36 = 0;
    break;
  case 0x14a0e:
    DAT_374a_3c3f = 0;
    DAT_374a_3c32 = 0x12;
    break;
  case 0x14a1c:
    iVar2 = iVar2 + 1;
    FUN_21c7_27e8(*(undefined2 *)(iVar2 * 2 + param_2),0xa8d,(undefined4 *)&DAT_374a_4072);
    DAT_374a_4072._0_2_ = (uint)DAT_374a_4072 & 0xfff8;
    FUN_1277_0bc2((uint)DAT_374a_4072);
    break;
  case 0x14a44:
    DAT_374a_3c3e = 0;
  }
LAB_1458_04c9:
  iVar2 = iVar2 + 1;
  if (param_1 <= iVar2) goto LAB_1458_04d1;
  goto LAB_1458_036b;
override_jmp_1458_039a_case_5:
  iVar2 = iVar1;
  FUN_1458_0316();
  goto LAB_1458_04c9;
}

