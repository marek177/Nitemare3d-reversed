
void __cdecl16far FUN_144e_0320(int param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  undefined1 extraout_AH;
  int *piVar4;
  undefined2 uVar5;
  undefined4 *puVar6;
  undefined1 local_7;
  undefined4 local_6;
  
  local_7 = 0;
  local_6 = 0x10001;
  FUN_1273_0bc0();
  FUN_144e_0004();
  iVar1 = FUN_219b_2586(0xa10);
  if (iVar1 != 0) {
    DAT_3360_3b69 = 0;
    DAT_3360_3b62 = 0x12;
  }
  iVar1 = 1;
  if (1 < param_1) {
    do {
      piVar4 = (int *)(iVar1 * 2 + param_2);
      if (*(char *)*piVar4 != '-') {
        FUN_144e_030e();
      }
      uVar2 = (int)*(char *)(*piVar4 + 1) - 0x62;
      if (0x16 < uVar2) {
override_jmp_144e_0392_case_5:
        FUN_144e_030e();
        goto LAB_144e_0485;
      }
                    /* WARNING: Switch is manually overridden */
      switch((undefined4)*(undefined2 *)(uVar2 * 2 + 0x398)) {
      case 0x148a6:
        goto override_jmp_144e_0392_case_5;
      case 0x148b4:
        local_7 = 1;
        break;
      case 0x148bc:
        puVar6 = (undefined4 *)&DAT_3360_3b60;
        uVar5 = 0xa17;
        goto LAB_144e_03e2;
      case 0x148d4:
        puVar6 = (undefined4 *)&DAT_3360_3b5c;
        uVar5 = 0xa1a;
        goto LAB_144e_03e2;
      case 0x148dc:
        puVar6 = &local_6;
        uVar5 = 0xa1d;
        goto LAB_144e_03e2;
      case 0x148e6:
        puVar6 = (undefined4 *)&DAT_3360_3b5e;
        uVar5 = 0xa20;
LAB_144e_03e2:
        iVar1 = iVar1 + 1;
        FUN_219b_28e0(*(undefined2 *)(iVar1 * 2 + param_2),uVar5,puVar6);
        break;
      case 0x148ee:
        iVar1 = iVar1 + 1;
        iVar3 = FUN_219b_28e0(*(undefined2 *)(iVar1 * 2 + param_2),0xa23,(int)&local_6 + 2);
        if (iVar3 == 0) goto override_jmp_144e_0392_case_5;
        break;
      case 0x1490a:
        DAT_3360_3b6a = 1;
        break;
      case 0x14912:
        DAT_3360_3b67 = 0;
        break;
      case 0x1491a:
        DAT_3360_3b70 = 1;
        break;
      case 0x14922:
        DAT_3360_3b66 = 0;
        break;
      case 0x1492a:
        DAT_3360_3b69 = 0;
        DAT_3360_3b62 = 0x12;
        break;
      case 0x14938:
        iVar1 = iVar1 + 1;
        FUN_219b_28e0(*(undefined2 *)(iVar1 * 2 + param_2),0xa26,(undefined2 *)&DAT_3360_3f9c);
        DAT_3360_3f9c = DAT_3360_3f9c & 0xfff8;
        FUN_1273_0b62(DAT_3360_3f9c);
        break;
      case 0x14960:
        DAT_3360_3b68 = 0;
      }
LAB_144e_0485:
      iVar1 = iVar1 + 1;
    } while (iVar1 < param_1);
  }
  FUN_144e_00da();
  FUN_1cdc_26de(local_6,CONCAT11(extraout_AH,local_7));
  FUN_144e_01e2();
  return;
}

