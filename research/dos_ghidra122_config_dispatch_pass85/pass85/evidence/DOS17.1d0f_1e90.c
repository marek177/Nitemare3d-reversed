
uint FUN_1d0f_1e90(void)

{
  char cVar1;
  undefined2 uVar2;
  byte bVar3;
  uint uVar4;
  char *pcVar5;
  
  uVar2 = DAT_3754_252e;
  pcVar5 = (char *)s_T7Unfortunately_the_blast_impact_3754_11ac + 0x66;
  cVar1 = ((char *)s_T7Unfortunately_the_blast_impact_3754_11ac)[0x66];
  do {
    if (cVar1 == '\0') {
      FUN_1d0f_0400(10);
      uVar4 = FUN_1d0f_1916((char *)s_T7Unfortunately_the_blast_impact_3754_11ac + 0x66,0x309c);
      if (uVar4 == 0x15) {
        return 1;
      }
      return uVar4 & 0xff00;
    }
    cVar1 = *pcVar5;
    if (cVar1 == '\n') {
      if (DAT_3754_40bc != '\0') {
        bVar3 = DAT_3754_40b8;
        goto LAB_1d0f_1ef6;
      }
      bVar3 = DAT_3754_40b8;
LAB_1d0f_1efd:
      uVar4 = -(uint)bVar3;
LAB_1d0f_1f01:
      *(uint *)(pcVar5 + 2) = uVar4;
    }
    else {
      if (cVar1 == '\v') {
        if (DAT_3754_40bf == '\0') {
          bVar3 = DAT_3754_40b9;
          goto LAB_1d0f_1efd;
        }
        bVar3 = DAT_3754_40b9;
LAB_1d0f_1ef6:
        uVar4 = (uint)bVar3;
        goto LAB_1d0f_1f01;
      }
      if (cVar1 == '\f') {
        if (DAT_3754_40be == '\0') {
          bVar3 = DAT_3754_40bb;
          goto LAB_1d0f_1efd;
        }
        bVar3 = DAT_3754_40bb;
        goto LAB_1d0f_1ef6;
      }
      if (cVar1 == '\r') {
        if (DAT_3754_40bd == '\0') {
          bVar3 = DAT_3754_40ba;
          goto LAB_1d0f_1efd;
        }
        bVar3 = DAT_3754_40ba;
        goto LAB_1d0f_1ef6;
      }
    }
    pcVar5 = pcVar5 + 0x12;
    cVar1 = *pcVar5;
  } while( true );
}

