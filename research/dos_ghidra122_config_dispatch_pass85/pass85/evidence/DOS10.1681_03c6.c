
uint __cdecl16far FUN_1681_03c6(void)

{
  int iVar1;
  uint uVar2;
  uint *puVar3;
  uint local_16;
  int local_14;
  int local_12;
  int local_c;
  int local_a;
  byte local_8 [2];
  uint local_6;
  uint *local_4;
  
  local_4 = &local_6;
  puVar3 = local_4;
  if (DAT_3360_3fa4 != '\0') {
    puVar3 = (uint *)(DAT_3360_43a8 >> 1);
    local_c = DAT_3360_43a6 >> 1;
    FUN_17e9_0070(local_c,puVar3);
  }
  local_4 = puVar3;
  do {
    local_6 = FUN_1681_0390();
    if (DAT_3360_3fa4 != '\0') {
      FUN_17e9_003c(&local_c,&local_a,local_8);
      iVar1 = FUN_1681_05a2(100);
      if (10 < iVar1) {
        if ((int)puVar3 < local_a) {
          return 0x50;
        }
        return 0x48;
      }
      if (((local_8[0] & 1) == 0) && (DAT_3360_0add != 0)) {
        local_6 = CONCAT11(local_6._1_1_,0xd);
      }
      if (((local_8[0] & 2) != 0) && (DAT_3360_0ade == '\0')) {
        local_6 = CONCAT11(local_6._1_1_,0x1b);
      }
      DAT_3360_0add = local_8[0] & 1;
      if (((local_8[0] & 2) == 0) && ((char)local_6 != '\r')) {
        DAT_3360_0ade = '\0';
      }
      else {
        DAT_3360_0ade = '\x01';
      }
    }
    if (DAT_3360_3fa7 != '\0') {
      FUN_1bdd_04da();
      uVar2 = (int)local_16 >> 0xf;
      if (0x14 < (int)((local_16 ^ uVar2) - uVar2)) {
        FUN_1b91_00b2();
        FUN_1bdd_04da();
        if (0x14 < (int)((local_16 ^ uVar2) - uVar2)) {
          if ((int)local_16 < 0) {
            return 0x48;
          }
          return 0x50;
        }
      }
      if ((local_14 == 0) && (DAT_3360_0adb != '\0')) {
        local_6 = CONCAT11(local_6._1_1_,0xd);
      }
      if ((local_12 != 0) && (DAT_3360_0adc == '\0')) {
        local_6 = CONCAT11(local_6._1_1_,0x1b);
      }
      DAT_3360_0adb = (char)local_14;
      if ((local_12 == 0) && ((char)local_6 != '\r')) {
        DAT_3360_0adc = '\0';
      }
      else {
        DAT_3360_0adc = '\x01';
      }
    }
  } while (local_6 == 0);
  if (DAT_3360_3b70 == 4) {
    FUN_1b91_00b2();
  }
  if (((char)local_6 != '\0') && ((char)local_6 != -0x20)) {
    return local_6 & 0xff;
  }
  if (local_6 >> 8 == 0x3c) {
    if (DAT_3360_3fa5 != 0) {
      FUN_1bdd_025a();
    }
    DAT_3360_3fa5 = DAT_3360_3fa5 ^ 1;
    FUN_1bdd_00b4();
    if (DAT_3360_3fa5 != 0) {
      FUN_17f5_2828();
    }
  }
  else if (local_6 >> 8 == 0x3d) {
    DAT_3360_3fa6 = DAT_3360_3fa6 ^ 1;
    FUN_1bdd_00b4();
    if (DAT_3360_3fa6 != 0) {
      FUN_1bdd_03e6(0x2e,0x20000);
    }
  }
  return local_6 >> 8;
}

