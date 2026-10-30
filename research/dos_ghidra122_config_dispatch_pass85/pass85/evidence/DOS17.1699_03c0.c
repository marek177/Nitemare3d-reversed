
uint __cdecl16far FUN_1699_03c0(void)

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
  if (DAT_3754_40bc != '\0') {
    puVar3 = (uint *)(DAT_3754_44c0 >> 1);
    local_c = DAT_3754_44be >> 1;
    FUN_181b_0066(local_c,puVar3);
  }
  local_4 = puVar3;
  do {
    local_6 = FUN_1699_038a();
    if (DAT_3754_40bc != '\0') {
      FUN_181b_0032(&local_c,&local_a,local_8);
      iVar1 = FUN_1699_059c(100);
      if (10 < iVar1) {
        if ((int)puVar3 < local_a) {
          return 0x50;
        }
        return 0x48;
      }
      if (((local_8[0] & 1) == 0) && (DAT_3754_0b2c != 0)) {
        local_6 = CONCAT11(local_6._1_1_,0xd);
      }
      if (((local_8[0] & 2) != 0) && (DAT_3754_0b2d == '\0')) {
        local_6 = CONCAT11(local_6._1_1_,0x1b);
      }
      DAT_3754_0b2c = local_8[0] & 1;
      if (((local_8[0] & 2) == 0) && ((char)local_6 != '\r')) {
        DAT_3754_0b2d = '\0';
      }
      else {
        DAT_3754_0b2d = '\x01';
      }
    }
    if (DAT_3754_40bf != '\0') {
      FUN_1c11_04ca();
      uVar2 = (int)local_16 >> 0xf;
      if (0x14 < (int)((local_16 ^ uVar2) - uVar2)) {
        FUN_1bc4_00ae();
        FUN_1c11_04ca();
        if (0x14 < (int)((local_16 ^ uVar2) - uVar2)) {
          if ((int)local_16 < 0) {
            return 0x48;
          }
          return 0x50;
        }
      }
      if ((local_14 == 0) && (DAT_3754_0b2a != '\0')) {
        local_6 = CONCAT11(local_6._1_1_,0xd);
      }
      if ((local_12 != 0) && (DAT_3754_0b2b == '\0')) {
        local_6 = CONCAT11(local_6._1_1_,0x1b);
      }
      DAT_3754_0b2a = (char)local_14;
      if ((local_12 == 0) && ((char)local_6 != '\r')) {
        DAT_3754_0b2b = '\0';
      }
      else {
        DAT_3754_0b2b = '\x01';
      }
    }
  } while (local_6 == 0);
  if (DAT_3754_3c46 == 4) {
    FUN_1bc4_00ae();
  }
  if (((char)local_6 != '\0') && ((char)local_6 != -0x20)) {
    return local_6 & 0xff;
  }
  if (local_6 >> 8 == 0x3c) {
    if (DAT_3754_40bd != 0) {
      FUN_1c11_0282();
    }
    DAT_3754_40bd = DAT_3754_40bd ^ 1;
    FUN_1c11_00dc();
    if (DAT_3754_40bd != 0) {
      FUN_1826_285c();
    }
  }
  else if (local_6 >> 8 == 0x3d) {
    DAT_3754_40be = DAT_3754_40be ^ 1;
    FUN_1c11_00dc();
    if (DAT_3754_40be != 0) {
      FUN_1c11_03d6(0x2e,0x20000);
    }
  }
  return local_6 >> 8;
}

