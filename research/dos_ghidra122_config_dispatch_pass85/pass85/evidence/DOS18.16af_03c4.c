
uint __cdecl16far FUN_16af_03c4(void)

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
  if (DAT_376d_414c != '\0') {
    puVar3 = (uint *)(DAT_376d_4550 >> 1);
    local_c = DAT_376d_454e >> 1;
    FUN_1831_006a(local_c,puVar3);
  }
  local_4 = puVar3;
  do {
    local_6 = FUN_16af_038e();
    if (DAT_376d_414c != '\0') {
      FUN_1831_0036(&local_c,&local_a,local_8);
      iVar1 = FUN_16af_05a0(100);
      if (10 < iVar1) {
        if ((int)puVar3 < local_a) {
          return 0x50;
        }
        return 0x48;
      }
      if (((local_8[0] & 1) == 0) && (DAT_376d_0b5a != 0)) {
        local_6 = CONCAT11(local_6._1_1_,0xd);
      }
      if (((local_8[0] & 2) != 0) && (DAT_376d_0b5b == '\0')) {
        local_6 = CONCAT11(local_6._1_1_,0x1b);
      }
      DAT_376d_0b5a = local_8[0] & 1;
      if (((local_8[0] & 2) == 0) && ((char)local_6 != '\r')) {
        DAT_376d_0b5b = '\0';
      }
      else {
        DAT_376d_0b5b = '\x01';
      }
    }
    if (DAT_376d_414f != '\0') {
      FUN_1c27_04ce();
      uVar2 = (int)local_16 >> 0xf;
      if (0x14 < (int)((local_16 ^ uVar2) - uVar2)) {
        FUN_1bda_00b2();
        FUN_1c27_04ce();
        if (0x14 < (int)((local_16 ^ uVar2) - uVar2)) {
          if ((int)local_16 < 0) {
            return 0x48;
          }
          return 0x50;
        }
      }
      if ((local_14 == 0) && (DAT_376d_0b58 != '\0')) {
        local_6 = CONCAT11(local_6._1_1_,0xd);
      }
      if ((local_12 != 0) && (DAT_376d_0b59 == '\0')) {
        local_6 = CONCAT11(local_6._1_1_,0x1b);
      }
      DAT_376d_0b58 = (char)local_14;
      if ((local_12 == 0) && ((char)local_6 != '\r')) {
        DAT_376d_0b59 = '\0';
      }
      else {
        DAT_376d_0b59 = '\x01';
      }
    }
  } while (local_6 == 0);
  if (DAT_376d_3cd6 == 4) {
    FUN_1bda_00b2();
  }
  if (((char)local_6 != '\0') && ((char)local_6 != -0x20)) {
    return local_6 & 0xff;
  }
  if (local_6 >> 8 == 0x3c) {
    if (DAT_376d_414d != 0) {
      FUN_1c27_0286();
    }
    DAT_376d_414d = DAT_376d_414d ^ 1;
    FUN_1c27_00e0();
    if (DAT_376d_414d != 0) {
      FUN_183c_2860();
    }
  }
  else if (local_6 >> 8 == 0x3d) {
    DAT_376d_414e = DAT_376d_414e ^ 1;
    FUN_1c27_00e0();
    if (DAT_376d_414e != 0) {
      FUN_1c27_03da(0x2e,0x20000);
    }
  }
  return local_6 >> 8;
}

