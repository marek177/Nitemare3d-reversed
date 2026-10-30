
char * __cdecl16far FUN_1cdc_1c66(byte param_1,undefined2 param_2)

{
  char *pcVar1;
  byte bVar2;
  uint uVar3;
  undefined2 uVar4;
  uint uVar5;
  int iVar6;
  char *pcVar7;
  char *local_4;
  
  bVar2 = FUN_10f6_000a(param_2,0);
  uVar3 = FUN_10f6_00d4((char *)s__3Unfortunately_the_blast_impact_3360_10e4 + 0x12,param_2);
  uVar3 = ((uVar3 & 0xff) - (uint)bVar2) + 1;
  if (10 < uVar3) {
    FUN_1f67_000a();
  }
  iVar6 = 0;
  if (0 < (int)uVar3) {
    local_4 = (char *)s_Copyright_1994__David_P__Gray__3360_12f2 + 0xf;
    pcVar7 = (char *)s_Copyright_1994__David_P__Gray__3360_12f2 + 0xf;
    do {
      if ((DAT_3360_3faa == '\0') &&
         ((1 << ((byte)iVar6 & 0x1f) & (uint)(DAT_3360_3fe9 ^ DAT_3360_d357)) != 0)) {
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
  ((char *)s_Copyright_1994__David_P__Gray__3360_12f2 + 10)[iVar6 * 0x12] = '\0';
  uVar4 = FUN_1273_016c(0x10008);
  FUN_1155_097e(100,0x410030,iVar6 * 0xb,uVar4);
  uVar5 = FUN_1cdc_1936(&DAT_2ca8_12fc);
  if (uVar5 == 0x17) {
    iVar6 = 0;
    pcVar7 = (char *)s_Copyright_1994__David_P__Gray__3360_12f2 + 10;
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

