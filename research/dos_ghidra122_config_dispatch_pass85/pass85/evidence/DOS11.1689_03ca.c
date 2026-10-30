
uint __cdecl16far FUN_1689_03ca(void)

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
  if (DAT_3395_40aa != '\0') {
    puVar3 = (uint *)(DAT_3395_44ae >> 1);
    local_c = DAT_3395_44ac >> 1;
    FUN_180b_0070(local_c,puVar3);
  }
  local_4 = puVar3;
  do {
    local_6 = FUN_1689_0394();
    if (DAT_3395_40aa != '\0') {
      FUN_180b_003c(&local_c,&local_a,local_8);
      iVar1 = FUN_1689_05a6(100);
      if (10 < iVar1) {
        if ((int)puVar3 < local_a) {
          return 0x50;
        }
        return 0x48;
      }
      if (((local_8[0] & 1) == 0) && (DAT_3395_0b35 != 0)) {
        local_6 = CONCAT11(local_6._1_1_,0xd);
      }
      if (((local_8[0] & 2) != 0) && (DAT_3395_0b36 == '\0')) {
        local_6 = CONCAT11(local_6._1_1_,0x1b);
      }
      DAT_3395_0b35 = local_8[0] & 1;
      if (((local_8[0] & 2) == 0) && ((char)local_6 != '\r')) {
        DAT_3395_0b36 = '\0';
      }
      else {
        DAT_3395_0b36 = '\x01';
      }
    }
    if (DAT_3395_40ad != '\0') {
      FUN_1bff_04fe();
      uVar2 = (int)local_16 >> 0xf;
      if (0x14 < (int)((local_16 ^ uVar2) - uVar2)) {
        FUN_1bb2_00aa();
        FUN_1bff_04fe();
        if (0x14 < (int)((local_16 ^ uVar2) - uVar2)) {
          if ((int)local_16 < 0) {
            return 0x48;
          }
          return 0x50;
        }
      }
      if ((local_14 == 0) && (DAT_3395_0b33 != '\0')) {
        local_6 = CONCAT11(local_6._1_1_,0xd);
      }
      if ((local_12 != 0) && (DAT_3395_0b34 == '\0')) {
        local_6 = CONCAT11(local_6._1_1_,0x1b);
      }
      DAT_3395_0b33 = (char)local_14;
      if ((local_12 == 0) && ((char)local_6 != '\r')) {
        DAT_3395_0b34 = '\0';
      }
      else {
        DAT_3395_0b34 = '\x01';
      }
    }
  } while (local_6 == 0);
  if (DAT_3395_3c76 == 4) {
    FUN_1bb2_00aa();
  }
  if (((char)local_6 != '\0') && ((char)local_6 != -0x20)) {
    return local_6 & 0xff;
  }
  if (local_6 >> 8 == 0x3c) {
    if (DAT_3395_40ab != 0) {
      FUN_1bff_027e();
    }
    DAT_3395_40ab = DAT_3395_40ab ^ 1;
    FUN_1bff_00d8();
    if (DAT_3395_40ab != 0) {
      FUN_1817_2828();
    }
  }
  else if (local_6 >> 8 == 0x3d) {
    DAT_3395_40ac = DAT_3395_40ac ^ 1;
    FUN_1bff_00d8();
    if (DAT_3395_40ac != 0) {
      FUN_1bff_040a(0x2e,0x20000);
    }
  }
  return local_6 >> 8;
}

