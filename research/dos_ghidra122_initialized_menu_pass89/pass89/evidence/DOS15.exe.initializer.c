
uint __cdecl16far FUN_1d05_1e94(void)

{
  char cVar1;
  undefined2 uVar2;
  byte bVar3;
  uint uVar4;
  char *pcVar5;
  
  uVar2 = DAT_374a_252a;
  pcVar5 = (char *)s_J7Unfortunately_the_blast_impact_374a_11a8 + 0x6a;
  cVar1 = ((char *)s_J7Unfortunately_the_blast_impact_374a_11a8)[0x6a];
  do {
    if (cVar1 == '\0') {
      FUN_1d05_0404(10);
      uVar4 = FUN_1d05_191a((char *)s_J7Unfortunately_the_blast_impact_374a_11a8 + 0x6a,0x3092);
      if (uVar4 == 0x15) {
        return 1;
      }
      return uVar4 & 0xff00;
    }
    cVar1 = *pcVar5;
    if (cVar1 == '\n') {
      if (DAT_374a_407a != '\0') {
        bVar3 = (byte)DAT_374a_4076;
        goto LAB_1d05_1efa;
      }
      bVar3 = (byte)DAT_374a_4076;
LAB_1d05_1f01:
      uVar4 = -(uint)bVar3;
LAB_1d05_1f05:
      *(uint *)(pcVar5 + 2) = uVar4;
    }
    else {
      if (cVar1 == '\v') {
        if (DAT_374a_407d == '\0') {
          bVar3 = DAT_374a_4076._1_1_;
          goto LAB_1d05_1f01;
        }
        bVar3 = DAT_374a_4076._1_1_;
LAB_1d05_1efa:
        uVar4 = (uint)bVar3;
        goto LAB_1d05_1f05;
      }
      if (cVar1 == '\f') {
        if (DAT_374a_407c == '\0') {
          bVar3 = DAT_374a_4076._3_1_;
          goto LAB_1d05_1f01;
        }
        bVar3 = DAT_374a_4076._3_1_;
        goto LAB_1d05_1efa;
      }
      if (cVar1 == '\r') {
        if (DAT_374a_407b == '\0') {
          bVar3 = DAT_374a_4076._2_1_;
          goto LAB_1d05_1f01;
        }
        bVar3 = DAT_374a_4076._2_1_;
        goto LAB_1d05_1efa;
      }
    }
    pcVar5 = pcVar5 + 0x12;
    cVar1 = *pcVar5;
  } while( true );
}

