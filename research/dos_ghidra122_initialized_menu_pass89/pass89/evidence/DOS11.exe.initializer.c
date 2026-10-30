
uint __cdecl16far FUN_1d00_1e94(void)

{
  char cVar1;
  undefined2 uVar2;
  byte bVar3;
  uint uVar4;
  char *pcVar5;
  
  uVar2 = DAT_3395_255c;
  pcVar5 = (char *)s_3Unfortunately_the_blast_impact_o_3395_11b3 + 0x5f;
  cVar1 = ((char *)s_3Unfortunately_the_blast_impact_o_3395_11b3)[0x5f];
  do {
    if (cVar1 == '\0') {
      FUN_1d00_0404(10);
      uVar4 = FUN_1d00_191a((char *)s_3Unfortunately_the_blast_impact_o_3395_11b3 + 0x5f,0x2cdd);
      if (uVar4 == 0x15) {
        return 1;
      }
      return uVar4 & 0xff00;
    }
    cVar1 = *pcVar5;
    if (cVar1 == '\n') {
      if (DAT_3395_40aa != '\0') {
        bVar3 = (byte)DAT_3395_40a6;
        goto LAB_1d00_1efa;
      }
      bVar3 = (byte)DAT_3395_40a6;
LAB_1d00_1f01:
      uVar4 = -(uint)bVar3;
LAB_1d00_1f05:
      *(uint *)(pcVar5 + 2) = uVar4;
    }
    else {
      if (cVar1 == '\v') {
        if (DAT_3395_40ad == '\0') {
          bVar3 = DAT_3395_40a6._1_1_;
          goto LAB_1d00_1f01;
        }
        bVar3 = DAT_3395_40a6._1_1_;
LAB_1d00_1efa:
        uVar4 = (uint)bVar3;
        goto LAB_1d00_1f05;
      }
      if (cVar1 == '\f') {
        if (DAT_3395_40ac == '\0') {
          bVar3 = DAT_3395_40a6._3_1_;
          goto LAB_1d00_1f01;
        }
        bVar3 = DAT_3395_40a6._3_1_;
        goto LAB_1d00_1efa;
      }
      if (cVar1 == '\r') {
        if (DAT_3395_40ab == '\0') {
          bVar3 = DAT_3395_40a6._2_1_;
          goto LAB_1d00_1f01;
        }
        bVar3 = DAT_3395_40a6._2_1_;
        goto LAB_1d00_1efa;
      }
    }
    pcVar5 = pcVar5 + 0x12;
    cVar1 = *pcVar5;
  } while( true );
}

