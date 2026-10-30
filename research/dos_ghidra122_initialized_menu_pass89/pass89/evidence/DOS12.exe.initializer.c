
uint __cdecl16far FUN_1d00_1e96(void)

{
  char cVar1;
  undefined2 uVar2;
  byte bVar3;
  uint uVar4;
  char *pcVar5;
  
  uVar2 = DAT_339b_2558;
  pcVar5 = (char *)s_3Unfortunately_the_blast_impact_o_339b_11a3 + 0x6f;
  cVar1 = ((char *)s_3Unfortunately_the_blast_impact_o_339b_11a3)[0x6f];
  do {
    if (cVar1 == '\0') {
      FUN_1d00_0406(10);
      uVar4 = FUN_1d00_191c((char *)s_3Unfortunately_the_blast_impact_o_339b_11a3 + 0x6f,0x2ce3);
      if (uVar4 == 0x15) {
        return 1;
      }
      return uVar4 & 0xff00;
    }
    cVar1 = *pcVar5;
    if (cVar1 == '\n') {
      if (DAT_339b_40aa != '\0') {
        bVar3 = DAT_339b_40a6;
        goto LAB_1d00_1efc;
      }
      bVar3 = DAT_339b_40a6;
LAB_1d00_1f03:
      uVar4 = -(uint)bVar3;
LAB_1d00_1f07:
      *(uint *)(pcVar5 + 2) = uVar4;
    }
    else {
      if (cVar1 == '\v') {
        if (DAT_339b_40ad == '\0') {
          bVar3 = DAT_339b_40a7;
          goto LAB_1d00_1f03;
        }
        bVar3 = DAT_339b_40a7;
LAB_1d00_1efc:
        uVar4 = (uint)bVar3;
        goto LAB_1d00_1f07;
      }
      if (cVar1 == '\f') {
        if (DAT_339b_40ac == '\0') {
          bVar3 = DAT_339b_40a9;
          goto LAB_1d00_1f03;
        }
        bVar3 = DAT_339b_40a9;
        goto LAB_1d00_1efc;
      }
      if (cVar1 == '\r') {
        if (DAT_339b_40ab == '\0') {
          bVar3 = DAT_339b_40a8;
          goto LAB_1d00_1f03;
        }
        bVar3 = DAT_339b_40a8;
        goto LAB_1d00_1efc;
      }
    }
    pcVar5 = pcVar5 + 0x12;
    cVar1 = *pcVar5;
  } while( true );
}

