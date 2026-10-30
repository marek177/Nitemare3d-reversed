
uint __cdecl16far FUN_168a_03c6(void)

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
  if (DAT_339b_40aa != '\0') {
    puVar3 = (uint *)(DAT_339b_44ae >> 1);
    local_c = DAT_339b_44ac >> 1;
    FUN_180c_006c(local_c,puVar3);
  }
  local_4 = puVar3;
  do {
    local_6 = FUN_168a_0390();
    if (DAT_339b_40aa != '\0') {
      FUN_180c_0038(&local_c,&local_a,local_8);
      iVar1 = FUN_168a_05a2(100);
      if (10 < iVar1) {
        if ((int)puVar3 < local_a) {
          return 0x50;
        }
        return 0x48;
      }
      if (((local_8[0] & 1) == 0) && (DAT_339b_0b24 != 0)) {
        local_6 = CONCAT11(local_6._1_1_,0xd);
      }
      if (((local_8[0] & 2) != 0) && (DAT_339b_0b25 == '\0')) {
        local_6 = CONCAT11(local_6._1_1_,0x1b);
      }
      DAT_339b_0b24 = local_8[0] & 1;
      if (((local_8[0] & 2) == 0) && ((char)local_6 != '\r')) {
        DAT_339b_0b25 = '\0';
      }
      else {
        DAT_339b_0b25 = '\x01';
      }
    }
    if (DAT_339b_40ad != '\0') {
      FUN_1bff_0500();
      uVar2 = (int)local_16 >> 0xf;
      if (0x14 < (int)((local_16 ^ uVar2) - uVar2)) {
        FUN_1bb2_00ac();
        FUN_1bff_0500();
        if (0x14 < (int)((local_16 ^ uVar2) - uVar2)) {
          if ((int)local_16 < 0) {
            return 0x48;
          }
          return 0x50;
        }
      }
      if ((local_14 == 0) && (DAT_339b_0b22 != '\0')) {
        local_6 = CONCAT11(local_6._1_1_,0xd);
      }
      if ((local_12 != 0) && (DAT_339b_0b23 == '\0')) {
        local_6 = CONCAT11(local_6._1_1_,0x1b);
      }
      DAT_339b_0b22 = (char)local_14;
      if ((local_12 == 0) && ((char)local_6 != '\r')) {
        DAT_339b_0b23 = '\0';
      }
      else {
        DAT_339b_0b23 = '\x01';
      }
    }
  } while (local_6 == 0);
  if (DAT_339b_3c76 == 4) {
    FUN_1bb2_00ac();
  }
  if (((char)local_6 != '\0') && ((char)local_6 != -0x20)) {
    return local_6 & 0xff;
  }
  if (local_6 >> 8 == 0x3c) {
    if (DAT_339b_40ab != 0) {
      FUN_1bff_0280();
    }
    DAT_339b_40ab = DAT_339b_40ab ^ 1;
    FUN_1bff_00da();
    if (DAT_339b_40ab != 0) {
      FUN_1818_281a();
    }
  }
  else if (local_6 >> 8 == 0x3d) {
    DAT_339b_40ac = DAT_339b_40ac ^ 1;
    FUN_1bff_00da();
    if (DAT_339b_40ac != 0) {
      FUN_1bff_040c(0x2e,0x20000);
    }
  }
  return local_6 >> 8;
}

