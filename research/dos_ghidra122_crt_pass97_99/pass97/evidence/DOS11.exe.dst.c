
undefined2 __cdecl16far FUN_21bc_2d00(int param_1)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  undefined2 uVar4;
  int local_4;
  
  if (((*(int *)(param_1 + 10) < 0x43) || (*(int *)(param_1 + 8) < 3)) ||
     (9 < *(int *)(param_1 + 8))) goto LAB_21bc_2db7;
  if ((*(int *)(param_1 + 8) < 4) || (8 < *(int *)(param_1 + 8))) {
    uVar1 = *(uint *)(param_1 + 10);
    if (((int)uVar1 < 0x57) || (*(int *)(param_1 + 8) != 3)) {
      local_4 = *(int *)(*(int *)(param_1 + 8) * 2 + 0x247c);
    }
    else {
      local_4 = *(int *)(*(int *)(param_1 + 8) * 2 + 0x247a) + 7;
    }
    if ((uVar1 & 3) == 0) {
      local_4 = local_4 + 1;
    }
    uVar1 = (uVar1 - 0x46) * 0x16d + ((int)(uVar1 - 1) >> 2) + local_4;
    iVar2 = FUN_21bc_3b0a(uVar1 - 0xd,((int)uVar1 >> 0xf) - (uint)(uVar1 < 0xd),7,0);
    iVar3 = -(iVar2 - local_4);
    if (*(int *)(param_1 + 8) == 3) {
      if ((iVar3 < *(int *)(param_1 + 0xe)) ||
         ((-*(int *)(param_1 + 0xe) == iVar2 - local_4 && (1 < *(int *)(param_1 + 4)))))
      goto LAB_21bc_2da5;
    }
    else if ((*(int *)(param_1 + 0xe) < iVar3) ||
            ((*(int *)(param_1 + 0xe) == iVar3 && (*(int *)(param_1 + 4) < 1)))) goto LAB_21bc_2da5;
LAB_21bc_2db7:
    uVar4 = 0;
  }
  else {
LAB_21bc_2da5:
    uVar4 = 1;
  }
  return uVar4;
}

