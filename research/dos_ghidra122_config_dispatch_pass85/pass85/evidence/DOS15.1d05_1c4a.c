
char * __cdecl16far FUN_1d05_1c4a(byte param_1,undefined2 param_2)

{
  char *pcVar1;
  byte bVar2;
  uint uVar3;
  undefined2 uVar4;
  uint uVar5;
  int iVar6;
  char *pcVar7;
  char *local_4;
  
  bVar2 = FUN_10f7_0004(param_2,0);
  uVar3 = FUN_10f7_00ce();
  uVar3 = ((uVar3 & 0xff) - (uint)bVar2) + 1;
  if (10 < uVar3) {
    FUN_1f94_0000();
  }
  iVar6 = 0;
  if (0 < (int)uVar3) {
    local_4 = (char *)s_J7You_recover_to_witness_the_def_374a_1228 + 0xd9;
    pcVar7 = (char *)s_J7You_recover_to_witness_the_def_374a_1228 + 0xd9;
    do {
      if ((DAT_374a_4080 == '\0') &&
         ((1 << ((byte)iVar6 & 0x1f) & (uint)(DAT_374a_40bf ^ DAT_374a_d43d)) != 0)) {
        *pcVar7 = '\x06';
      }
      else {
        *pcVar7 = '\x01';
      }
      pcVar1 = pcVar7 + -1;
      pcVar7 = pcVar7 + 0x12;
      *pcVar1 = (uint)bVar2 + iVar6 == (uint)param_1;
      iVar6 = iVar6 + 1;
    } while (iVar6 < (int)uVar3);
  }
  ((char *)s_J7You_recover_to_witness_the_def_374a_1228 + 0xd4)[iVar6 * 0x12] = '\0';
  uVar4 = FUN_1277_0188(0x10008);
  FUN_1156_097c(100,0x410030,iVar6 * 0xb,uVar4);
  uVar5 = FUN_1d05_191a(&DAT_3092_12fc);
  if (uVar5 == 0x17) {
    iVar6 = 0;
    pcVar7 = (char *)s_J7You_recover_to_witness_the_def_374a_1228 + 0xd4;
    if (0 < (int)uVar3) {
      do {
        if (pcVar7[4] != '\0') {
          local_4 = (char *)(((uint)bVar2 - (uint)param_1) + iVar6);
        }
        pcVar7 = pcVar7 + 0x12;
        iVar6 = iVar6 + 1;
      } while (iVar6 < (int)uVar3);
    }
  }
  else if ((uVar5 < 0x18) && (((char)uVar5 == '\x06' || ((char)uVar5 == '\x16')))) {
    local_4 = (char *)0x0;
  }
  return local_4;
}

