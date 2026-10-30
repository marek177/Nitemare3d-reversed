
void __cdecl16far FUN_1453_0330(int param_1,int param_2)

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
  FUN_1275_0bf8();
  FUN_1453_000c();
  iVar2 = FUN_21c2_248a(0xa6d);
  if (iVar2 != 0) {
    DAT_339b_3c6f = 0;
    DAT_339b_3c62 = 0x12;
  }
  iVar2 = 1;
  if (param_1 < 2) {
LAB_1453_04d9:
    FUN_1453_00d8();
    FUN_1d00_2722(local_6,CONCAT11(extraout_AH,local_7));
    FUN_1453_01da();
    return;
  }
LAB_1453_0373:
  piVar5 = (int *)(iVar2 * 2 + param_2);
  if (*(char *)*piVar5 != '-') {
    FUN_1453_031e();
  }
  uVar3 = (int)*(char *)(*piVar5 + 1) - 0x62;
  iVar1 = iVar2;
  if (0x16 < uVar3) goto override_jmp_1453_03a2_case_5;
                    /* WARNING: Switch is manually overridden */
  switch((undefined4)*(undefined2 *)(uVar3 * 2 + 0x3a8)) {
  case 0x14906:
    goto override_jmp_1453_03a2_case_5;
  case 0x14914:
    local_7 = 1;
    break;
  case 0x1491c:
    puVar7 = (undefined4 *)&DAT_339b_3c60;
    uVar6 = 0xa74;
    goto LAB_1453_03f2;
  case 0x14934:
    puVar7 = (undefined4 *)&DAT_339b_3c5c;
    uVar6 = 0xa77;
    goto LAB_1453_03f2;
  case 0x1493c:
    puVar7 = &local_6;
    uVar6 = 0xa7a;
    goto LAB_1453_03f2;
  case 0x14946:
    puVar7 = (undefined4 *)&DAT_339b_3c5e;
    uVar6 = 0xa7d;
LAB_1453_03f2:
    iVar2 = iVar2 + 1;
    FUN_21c2_27e4(*(undefined2 *)(iVar2 * 2 + param_2),uVar6,puVar7);
    break;
  case 0x1494e:
    iVar2 = iVar2 + 1;
    iVar4 = FUN_21c2_27e4(*(undefined2 *)(iVar2 * 2 + param_2),0xa80,(int)&local_6 + 2);
    iVar1 = iVar2;
    if (iVar4 == 0) goto override_jmp_1453_03a2_case_5;
    break;
  case 0x1496c:
    DAT_339b_3c70 = 1;
    break;
  case 0x14974:
    DAT_339b_3c67 = 0;
    break;
  case 0x1497c:
    DAT_339b_3c68 = 1;
    iVar4 = FUN_21c2_27e4(*(undefined2 *)((iVar2 + 1) * 2 + param_2),0xa83,
                          (undefined4 *)&DAT_339b_3c6a);
    iVar1 = iVar2 + 1;
    if (iVar4 == 1) {
      iVar2 = iVar2 + 2;
      iVar4 = FUN_21c2_27e4(*(undefined2 *)(iVar2 * 2 + param_2),0xa86,0x3c6c);
      iVar1 = iVar2;
      if (iVar4 == 1) break;
    }
    goto override_jmp_1453_03a2_case_5;
  case 0x149b6:
    DAT_339b_3c76 = 1;
    break;
  case 0x149be:
    DAT_339b_3c66 = 0;
    break;
  case 0x149c6:
    DAT_339b_3c6f = 0;
    DAT_339b_3c62 = 0x12;
    break;
  case 0x149d4:
    iVar2 = iVar2 + 1;
    FUN_21c2_27e4(*(undefined2 *)(iVar2 * 2 + param_2),0xa89,(undefined2 *)&DAT_339b_40a2);
    DAT_339b_40a2 = DAT_339b_40a2 & 0xfff8;
    FUN_1275_0b9a(DAT_339b_40a2);
    break;
  case 0x149fc:
    DAT_339b_3c6e = 0;
  }
LAB_1453_04d1:
  iVar2 = iVar2 + 1;
  if (param_1 <= iVar2) goto LAB_1453_04d9;
  goto LAB_1453_0373;
override_jmp_1453_03a2_case_5:
  iVar2 = iVar1;
  FUN_1453_031e();
  goto LAB_1453_04d1;
}

