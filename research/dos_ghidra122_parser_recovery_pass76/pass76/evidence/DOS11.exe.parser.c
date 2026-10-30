
void __cdecl16far FUN_1452_0334(int param_1,int param_2)

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
  FUN_1275_0be6();
  FUN_1452_000a();
  iVar2 = FUN_21bc_248a(0xa63);
  if (iVar2 != 0) {
    DAT_3395_3c6f = 0;
    DAT_3395_3c62 = 0x12;
  }
  iVar2 = 1;
  if (param_1 < 2) {
LAB_1452_04dd:
    FUN_1452_00d6();
    FUN_1d00_26c2(local_6,CONCAT11(extraout_AH,local_7));
    FUN_1452_01de();
    return;
  }
LAB_1452_0377:
  piVar5 = (int *)(iVar2 * 2 + param_2);
  if (*(char *)*piVar5 != '-') {
    FUN_1452_0322();
  }
  uVar3 = (int)*(char *)(*piVar5 + 1) - 0x62;
  iVar1 = iVar2;
  if (0x16 < uVar3) goto override_jmp_1452_03a6_case_5;
                    /* WARNING: Switch is manually overridden */
  switch((undefined4)*(undefined2 *)(uVar3 * 2 + 0x3ac)) {
  case 0x148fa:
    goto override_jmp_1452_03a6_case_5;
  case 0x14908:
    local_7 = 1;
    break;
  case 0x14910:
    puVar7 = (undefined4 *)&DAT_3395_3c60;
    uVar6 = 0xa6a;
    goto LAB_1452_03f6;
  case 0x14928:
    puVar7 = (undefined4 *)&DAT_3395_3c5c;
    uVar6 = 0xa6d;
    goto LAB_1452_03f6;
  case 0x14930:
    puVar7 = &local_6;
    uVar6 = 0xa70;
    goto LAB_1452_03f6;
  case 0x1493a:
    puVar7 = (undefined4 *)&DAT_3395_3c5e;
    uVar6 = 0xa73;
LAB_1452_03f6:
    iVar2 = iVar2 + 1;
    FUN_21bc_27e4(*(undefined2 *)(iVar2 * 2 + param_2),uVar6,puVar7);
    break;
  case 0x14942:
    iVar2 = iVar2 + 1;
    iVar4 = FUN_21bc_27e4(*(undefined2 *)(iVar2 * 2 + param_2),0xa76,(int)&local_6 + 2);
    iVar1 = iVar2;
    if (iVar4 == 0) goto override_jmp_1452_03a6_case_5;
    break;
  case 0x14960:
    DAT_3395_3c70 = 1;
    break;
  case 0x14968:
    DAT_3395_3c67 = 0;
    break;
  case 0x14970:
    DAT_3395_3c68 = 1;
    iVar4 = FUN_21bc_27e4(*(undefined2 *)((iVar2 + 1) * 2 + param_2),0xa79,
                          (undefined4 *)&DAT_3395_3c6a);
    iVar1 = iVar2 + 1;
    if (iVar4 == 1) {
      iVar2 = iVar2 + 2;
      iVar4 = FUN_21bc_27e4(*(undefined2 *)(iVar2 * 2 + param_2),0xa7c,0x3c6c);
      iVar1 = iVar2;
      if (iVar4 == 1) break;
    }
    goto override_jmp_1452_03a6_case_5;
  case 0x149aa:
    DAT_3395_3c76 = 1;
    break;
  case 0x149b2:
    DAT_3395_3c66 = 0;
    break;
  case 0x149ba:
    DAT_3395_3c6f = 0;
    DAT_3395_3c62 = 0x12;
    break;
  case 0x149c8:
    iVar2 = iVar2 + 1;
    FUN_21bc_27e4(*(undefined2 *)(iVar2 * 2 + param_2),0xa7f,(undefined2 *)&DAT_3395_40a2);
    DAT_3395_40a2 = DAT_3395_40a2 & 0xfff8;
    FUN_1275_0b88(DAT_3395_40a2);
    break;
  case 0x149f0:
    DAT_3395_3c6e = 0;
  }
LAB_1452_04d5:
  iVar2 = iVar2 + 1;
  if (param_1 <= iVar2) goto LAB_1452_04dd;
  goto LAB_1452_0377;
override_jmp_1452_03a6_case_5:
  iVar2 = iVar1;
  FUN_1452_0322();
  goto LAB_1452_04d5;
}

