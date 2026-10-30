
int * FUN_1cdc_21f4(undefined2 param_1,char param_2)

{
  int *piVar1;
  int *piVar2;
  undefined1 uVar3;
  int iVar4;
  uint uVar5;
  int *piVar6;
  int *piVar7;
  undefined1 *unaff_SS;
  char cStack_1a9;
  int local_1a4 [205];
  int local_a;
  int *local_8;
  int local_6;
  undefined2 uStack_4;
  
  FUN_1cdc_0400();
  FUN_1cdc_016a();
  local_a = 0;
  local_6 = 0x1086;
  uStack_4 = 0x2ca8;
  local_8 = local_1a4;
  do {
    *(uint *)(local_6 + 0xe) = (uint)local_8;
    *(undefined2 *)(local_6 + 0x10) = unaff_SS;
    iVar4 = FUN_1273_0c80(local_a,(char *)s_user_sav_3360_1e07);
    *(int *)(local_6 + 2) = iVar4;
    if (iVar4 < 0) {
      piVar7 = (int *)s____Empty_slot____3360_1e10;
      piVar6 = local_8;
      for (iVar4 = 6; iVar4 != 0; iVar4 = iVar4 + -1) {
        piVar2 = piVar6;
        piVar6 = piVar6 + 2;
        piVar1 = piVar7;
        piVar7 = piVar7 + 2;
        *(undefined4 *)piVar2 = *(undefined4 *)piVar1;
      }
      *piVar6 = *piVar7;
      *(char *)(piVar6 + 1) = (char)piVar7[1];
    }
    if (*(int *)(local_6 + 2) < 0) {
      uVar3 = 6;
    }
    else {
      uVar3 = 1;
    }
    *(undefined1 *)(local_6 + 5) = uVar3;
    local_6 = local_6 + 0x12;
    local_a = local_a + 1;
    local_8 = (int *)((int)local_8 + 0x29);
  } while (local_8 < &local_a);
  uVar5 = FUN_1cdc_1936();
  if (uVar5 == 0x16) {
LAB_1cdc_22ce:
    piVar7 = (int *)0xffff;
    unaff_SS = (undefined1 *)&DAT_3360_3360;
  }
  else {
    piVar7 = local_8;
    if (uVar5 < 0x17) {
      if ((char)uVar5 == '\x03') {
        piVar6 = (int *)0x0;
        iVar4 = 0x1086;
        do {
          if (*(char *)(iVar4 + 4) != '\0') {
            piVar7 = piVar6;
          }
          iVar4 = iVar4 + 0x12;
          piVar6 = (int *)((int)piVar6 + 1);
        } while ((int)piVar6 < 10);
        goto LAB_1cdc_22d1;
      }
      if ((char)uVar5 == '\x06') goto LAB_1cdc_22ce;
    }
    unaff_SS = (undefined1 *)&DAT_3360_3360;
  }
LAB_1cdc_22d1:
  if (-1 < (int)piVar7) {
    if (((param_2 == '\0') ||
        ((*(uint *)((char *)s__3QUICK__Destroy_the_plasma_core_3360_1088 + (int)piVar7 * 0x12) &
         0xff) != *(uint *)&DAT_3360_60c2)) ||
       (cStack_1a9 = (char)(*(uint *)((char *)s__3QUICK__Destroy_the_plasma_core_3360_1088 +
                                     (int)piVar7 * 0x12) >> 8),
       (int)cStack_1a9 != *(int *)&DAT_3360_60c0)) {
      FUN_1cdc_095a(*(uint *)((char *)s__3QUICK__Destroy_the_plasma_core_3360_1088 +
                             (int)piVar7 * 0x12) & 0xff,
                    (int)(char)(*(uint *)((char *)s__3QUICK__Destroy_the_plasma_core_3360_1088 +
                                         (int)piVar7 * 0x12) >> 8));
    }
    FUN_1273_10a8(piVar7,(char *)s_user_sav_3360_1e2b);
  }
  FUN_1cdc_016a();
  return piVar7;
}

