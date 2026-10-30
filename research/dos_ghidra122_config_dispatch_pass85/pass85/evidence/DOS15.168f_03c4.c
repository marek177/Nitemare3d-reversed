
uint __cdecl16far FUN_168f_03c4(void)

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
  if (DAT_374a_407a != '\0') {
    puVar3 = (uint *)(DAT_374a_447e >> 1);
    local_c = DAT_374a_447c >> 1;
    FUN_1811_006a(local_c,puVar3);
  }
  local_4 = puVar3;
  do {
    local_6 = FUN_168f_038e();
    if (DAT_374a_407a != '\0') {
      FUN_1811_0036(&local_c,&local_a,local_8);
      iVar1 = FUN_168f_05a0(100);
      if (10 < iVar1) {
        if ((int)puVar3 < local_a) {
          return 0x50;
        }
        return 0x48;
      }
      if (((local_8[0] & 1) == 0) && (DAT_374a_0b28 != 0)) {
        local_6 = CONCAT11(local_6._1_1_,0xd);
      }
      if (((local_8[0] & 2) != 0) && (DAT_374a_0b29 == '\0')) {
        local_6 = CONCAT11(local_6._1_1_,0x1b);
      }
      DAT_374a_0b28 = local_8[0] & 1;
      if (((local_8[0] & 2) == 0) && ((char)local_6 != '\r')) {
        DAT_374a_0b29 = '\0';
      }
      else {
        DAT_374a_0b29 = '\x01';
      }
    }
    if (DAT_374a_407d != '\0') {
      FUN_1c07_04ce();
      uVar2 = (int)local_16 >> 0xf;
      if (0x14 < (int)((local_16 ^ uVar2) - uVar2)) {
        FUN_1bba_00b2();
        FUN_1c07_04ce();
        if (0x14 < (int)((local_16 ^ uVar2) - uVar2)) {
          if ((int)local_16 < 0) {
            return 0x48;
          }
          return 0x50;
        }
      }
      if ((local_14 == 0) && (DAT_374a_0b26 != '\0')) {
        local_6 = CONCAT11(local_6._1_1_,0xd);
      }
      if ((local_12 != 0) && (DAT_374a_0b27 == '\0')) {
        local_6 = CONCAT11(local_6._1_1_,0x1b);
      }
      DAT_374a_0b26 = (char)local_14;
      if ((local_12 == 0) && ((char)local_6 != '\r')) {
        DAT_374a_0b27 = '\0';
      }
      else {
        DAT_374a_0b27 = '\x01';
      }
    }
  } while (local_6 == 0);
  if (DAT_374a_3c46 == 4) {
    FUN_1bba_00b2();
  }
  if (((char)local_6 != '\0') && ((char)local_6 != -0x20)) {
    return local_6 & 0xff;
  }
  if (local_6 >> 8 == 0x3c) {
    if (DAT_374a_407b != 0) {
      FUN_1c07_0286();
    }
    DAT_374a_407b = DAT_374a_407b ^ 1;
    FUN_1c07_00e0();
    if (DAT_374a_407b != 0) {
      FUN_181c_2860();
    }
  }
  else if (local_6 >> 8 == 0x3d) {
    DAT_374a_407c = DAT_374a_407c ^ 1;
    FUN_1c07_00e0();
    if (DAT_374a_407c != 0) {
      FUN_1c07_03da(0x2e,0x20000);
    }
  }
  return local_6 >> 8;
}

