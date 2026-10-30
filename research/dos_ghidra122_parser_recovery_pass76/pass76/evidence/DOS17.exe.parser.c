
void __cdecl16far FUN_145f_0332(int param_1,int param_2)

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
  FUN_1277_0c70();
  FUN_145f_000c();
  iVar2 = FUN_21d1_248a(0xa71);
  if (iVar2 != 0) {
    DAT_3754_3c3f = 0;
    DAT_3754_3c32 = 0x12;
  }
  iVar2 = 1;
  if (param_1 < 2) {
LAB_145f_04fd:
    FUN_145f_00da();
    FUN_1d0f_271c(local_6,CONCAT11(extraout_AH,local_7));
    FUN_145f_01dc();
    return;
  }
LAB_145f_0375:
  piVar5 = (int *)(iVar2 * 2 + param_2);
  if (*(char *)*piVar5 != '-') {
    FUN_145f_0320();
  }
  uVar3 = (int)*(char *)(*piVar5 + 1) - 0x61;
  iVar1 = iVar2;
  if (0x17 < uVar3) goto override_jmp_145f_03a4_case_6;
                    /* WARNING: Switch is manually overridden */
  switch((undefined4)*(undefined2 *)(uVar3 * 2 + 0x3aa)) {
  case 0x149ca:
    goto override_jmp_145f_03a4_case_6;
  case 0x149d8:
    iVar2 = iVar2 + 1;
    FUN_21d1_27e4(*(undefined2 *)(iVar2 * 2 + param_2),0xa78,(undefined2 *)&DAT_3754_3c4c);
    FUN_1277_0c70();
    break;
  case 0x149f6:
    local_7 = 1;
    break;
  case 0x149fe:
    puVar7 = (undefined4 *)&DAT_3754_3c30;
    uVar6 = 0xa7b;
    goto LAB_145f_0414;
  case 0x14a16:
    puVar7 = (undefined4 *)&DAT_3754_3c2c;
    uVar6 = 0xa7e;
    goto LAB_145f_0414;
  case 0x14a1e:
    puVar7 = &local_6;
    uVar6 = 0xa81;
    goto LAB_145f_0414;
  case 0x14a28:
    puVar7 = (undefined4 *)&DAT_3754_3c2e;
    uVar6 = 0xa84;
LAB_145f_0414:
    iVar2 = iVar2 + 1;
    FUN_21d1_27e4(*(undefined2 *)(iVar2 * 2 + param_2),uVar6,puVar7);
    break;
  case 0x14a30:
    iVar2 = iVar2 + 1;
    iVar4 = FUN_21d1_27e4(*(undefined2 *)(iVar2 * 2 + param_2),0xa87,(int)&local_6 + 2);
    iVar1 = iVar2;
    if (iVar4 == 0) goto override_jmp_145f_03a4_case_6;
    break;
  case 0x14a50:
    DAT_3754_3c40 = 1;
    break;
  case 0x14a58:
    DAT_3754_3c37 = 0;
    break;
  case 0x14a60:
    DAT_3754_3c38 = 1;
    iVar4 = FUN_21d1_27e4(*(undefined2 *)((iVar2 + 1) * 2 + param_2),0xa8a,
                          (undefined4 *)&DAT_3754_3c3a);
    iVar1 = iVar2 + 1;
    if (iVar4 == 1) {
      iVar2 = iVar2 + 2;
      iVar4 = FUN_21d1_27e4(*(undefined2 *)(iVar2 * 2 + param_2),0xa8d,0x3c3c);
      iVar1 = iVar2;
      if (iVar4 == 1) break;
    }
    goto override_jmp_145f_03a4_case_6;
  case 0x14a9a:
    DAT_3754_3c46 = 1;
    break;
  case 0x14aa2:
    DAT_3754_3c36 = 0;
    break;
  case 0x14aaa:
    DAT_3754_3c3f = 0;
    DAT_3754_3c32 = 0x12;
    break;
  case 0x14ab8:
    iVar2 = iVar2 + 1;
    FUN_21d1_27e4(*(undefined2 *)(iVar2 * 2 + param_2),0xa90,(undefined2 *)&DAT_3754_40b4);
    DAT_3754_40b4 = DAT_3754_40b4 & 0xfff8;
    FUN_1277_0bc2(DAT_3754_40b4);
    break;
  case 0x14ae0:
    DAT_3754_3c3e = 0;
  }
LAB_145f_04f5:
  iVar2 = iVar2 + 1;
  if (param_1 <= iVar2) goto LAB_145f_04fd;
  goto LAB_145f_0375;
override_jmp_145f_03a4_case_6:
  iVar2 = iVar1;
  FUN_145f_0320();
  goto LAB_145f_04f5;
}

