
uint __cdecl16far FUN_1cdc_1eb0(void)

{
  char cVar1;
  undefined2 uVar2;
  byte bVar3;
  uint uVar4;
  char *pcVar5;
  
  uVar2 = DAT_3360_2464;
  pcVar5 = (char *)s__3You_recover_to_witness_the_def_3360_1164 + 0xae;
  cVar1 = ((char *)s__3You_recover_to_witness_the_def_3360_1164)[0xae];
  do {
    if (cVar1 == '\0') {
      FUN_1cdc_0400(10);
      uVar4 = FUN_1cdc_1936((char *)s__3You_recover_to_witness_the_def_3360_1164 + 0xae,0x2ca8);
      if (uVar4 == 0x15) {
        return 1;
      }
      return uVar4 & 0xff00;
    }
    cVar1 = *pcVar5;
    if (cVar1 == '\n') {
      if (DAT_3360_3fa4 != '\0') {
        bVar3 = DAT_3360_3fa0;
        goto LAB_1cdc_1f16;
      }
      bVar3 = DAT_3360_3fa0;
LAB_1cdc_1f1d:
      uVar4 = -(uint)bVar3;
LAB_1cdc_1f21:
      *(uint *)(pcVar5 + 2) = uVar4;
    }
    else {
      if (cVar1 == '\v') {
        if (DAT_3360_3fa7 == '\0') {
          bVar3 = DAT_3360_3fa1;
          goto LAB_1cdc_1f1d;
        }
        bVar3 = DAT_3360_3fa1;
LAB_1cdc_1f16:
        uVar4 = (uint)bVar3;
        goto LAB_1cdc_1f21;
      }
      if (cVar1 == '\f') {
        if (DAT_3360_3fa6 == '\0') {
          bVar3 = DAT_3360_3fa3;
          goto LAB_1cdc_1f1d;
        }
        bVar3 = DAT_3360_3fa3;
        goto LAB_1cdc_1f16;
      }
      if (cVar1 == '\r') {
        if (DAT_3360_3fa5 == '\0') {
          bVar3 = DAT_3360_3fa2;
          goto LAB_1cdc_1f1d;
        }
        bVar3 = DAT_3360_3fa2;
        goto LAB_1cdc_1f16;
      }
    }
    pcVar5 = pcVar5 + 0x12;
    cVar1 = *pcVar5;
  } while( true );
}

