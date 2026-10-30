
void __cdecl16far FUN_1476_0326(int param_1,int param_2)

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
  FUN_1277_0c6e();
  FUN_1476_0000();
  iVar2 = FUN_21ea_248e(0xa9f);
  if (iVar2 != 0) {
    DAT_376d_3ccf = 0;
    DAT_376d_3cc2 = 0x12;
  }
  iVar2 = 1;
  if (param_1 < 2) {
LAB_1476_04f1:
    FUN_1476_00ce();
    FUN_1d25_2750(local_6,CONCAT11(extraout_AH,local_7));
    FUN_1476_01d0();
    return;
  }
LAB_1476_0369:
  piVar5 = (int *)(iVar2 * 2 + param_2);
  if (*(char *)*piVar5 != '-') {
    FUN_1476_0314();
  }
  uVar3 = (int)*(char *)(*piVar5 + 1) - 0x61;
  iVar1 = iVar2;
  if (0x17 < uVar3) goto override_jmp_1476_0398_case_6;
                    /* WARNING: Switch is manually overridden */
  switch((undefined4)*(undefined2 *)(uVar3 * 2 + 0x39e)) {
  case 0x14b2e:
    goto override_jmp_1476_0398_case_6;
  case 0x14b3c:
    iVar2 = iVar2 + 1;
    FUN_21ea_27e8(*(undefined2 *)(iVar2 * 2 + param_2),0xaa6,(undefined2 *)&DAT_376d_3cdc);
    FUN_1277_0c6e();
    break;
  case 0x14b5a:
    local_7 = 1;
    break;
  case 0x14b62:
    puVar7 = (undefined4 *)&DAT_376d_3cc0;
    uVar6 = 0xaa9;
    goto LAB_1476_0408;
  case 0x14b7a:
    puVar7 = (undefined4 *)&DAT_376d_3cbc;
    uVar6 = 0xaac;
    goto LAB_1476_0408;
  case 0x14b82:
    puVar7 = &local_6;
    uVar6 = 0xaaf;
    goto LAB_1476_0408;
  case 0x14b8c:
    puVar7 = (undefined4 *)&DAT_376d_3cbe;
    uVar6 = 0xab2;
LAB_1476_0408:
    iVar2 = iVar2 + 1;
    FUN_21ea_27e8(*(undefined2 *)(iVar2 * 2 + param_2),uVar6,puVar7);
    break;
  case 0x14b94:
    iVar2 = iVar2 + 1;
    iVar4 = FUN_21ea_27e8(*(undefined2 *)(iVar2 * 2 + param_2),0xab5,(int)&local_6 + 2);
    iVar1 = iVar2;
    if (iVar4 == 0) goto override_jmp_1476_0398_case_6;
    break;
  case 0x14bb4:
    DAT_376d_3cd0 = 1;
    break;
  case 0x14bbc:
    DAT_376d_3cc7 = 0;
    break;
  case 0x14bc4:
    DAT_376d_3cc8 = 1;
    iVar4 = FUN_21ea_27e8(*(undefined2 *)((iVar2 + 1) * 2 + param_2),0xab8,
                          (undefined4 *)&DAT_376d_3cca);
    iVar1 = iVar2 + 1;
    if (iVar4 == 1) {
      iVar2 = iVar2 + 2;
      iVar4 = FUN_21ea_27e8(*(undefined2 *)(iVar2 * 2 + param_2),0xabb,0x3ccc);
      iVar1 = iVar2;
      if (iVar4 == 1) break;
    }
    goto override_jmp_1476_0398_case_6;
  case 0x14bfe:
    DAT_376d_3cd6 = 1;
    break;
  case 0x14c06:
    DAT_376d_3cc6 = 0;
    break;
  case 0x14c0e:
    DAT_376d_3ccf = 0;
    DAT_376d_3cc2 = 0x12;
    break;
  case 0x14c1c:
    iVar2 = iVar2 + 1;
    FUN_21ea_27e8(*(undefined2 *)(iVar2 * 2 + param_2),0xabe,(undefined2 *)&DAT_376d_4144);
    DAT_376d_4144 = DAT_376d_4144 & 0xfff8;
    FUN_1277_0bc2(DAT_376d_4144);
    break;
  case 0x14c44:
    DAT_376d_3cce = 0;
  }
LAB_1476_04e9:
  iVar2 = iVar2 + 1;
  if (param_1 <= iVar2) goto LAB_1476_04f1;
  goto LAB_1476_0369;
override_jmp_1476_0398_case_6:
  iVar2 = iVar1;
  FUN_1476_0314();
  goto LAB_1476_04e9;
}

