
uint __cdecl16far FUN_1d25_1ec4(void)

{
  char cVar1;
  undefined2 uVar2;
  byte bVar3;
  uint uVar4;
  char *pcVar5;
  
  uVar2 = DAT_376d_2568;
  pcVar5 = (char *)s_m7Unfortunately_the_blast_impact_376d_11da + 0x38;
  cVar1 = ((char *)s_m7Unfortunately_the_blast_impact_376d_11da)[0x38];
  do {
    if (cVar1 == '\0') {
      FUN_1d25_0404(10);
      uVar4 = FUN_1d25_194a((char *)s_m7Unfortunately_the_blast_impact_376d_11da + 0x38,0x30b5);
      if (uVar4 == 0x15) {
        return 1;
      }
      return uVar4 & 0xff00;
    }
    cVar1 = *pcVar5;
    if (cVar1 == '\n') {
      if (DAT_376d_414c != '\0') {
        bVar3 = DAT_376d_4148;
        goto LAB_1d25_1f2a;
      }
      bVar3 = DAT_376d_4148;
LAB_1d25_1f31:
      uVar4 = -(uint)bVar3;
LAB_1d25_1f35:
      *(uint *)(pcVar5 + 2) = uVar4;
    }
    else {
      if (cVar1 == '\v') {
        if (DAT_376d_414f == '\0') {
          bVar3 = DAT_376d_4149;
          goto LAB_1d25_1f31;
        }
        bVar3 = DAT_376d_4149;
LAB_1d25_1f2a:
        uVar4 = (uint)bVar3;
        goto LAB_1d25_1f35;
      }
      if (cVar1 == '\f') {
        if (DAT_376d_414e == '\0') {
          bVar3 = DAT_376d_414b;
          goto LAB_1d25_1f31;
        }
        bVar3 = DAT_376d_414b;
        goto LAB_1d25_1f2a;
      }
      if (cVar1 == '\r') {
        if (DAT_376d_414d == '\0') {
          bVar3 = DAT_376d_414a;
          goto LAB_1d25_1f31;
        }
        bVar3 = DAT_376d_414a;
        goto LAB_1d25_1f2a;
      }
    }
    pcVar5 = pcVar5 + 0x12;
    cVar1 = *pcVar5;
  } while( true );
}

