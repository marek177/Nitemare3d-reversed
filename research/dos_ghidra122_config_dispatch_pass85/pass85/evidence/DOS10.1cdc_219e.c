
void __cdecl16far FUN_1cdc_219e(void)

{
  char cVar1;
  uint uVar2;
  char local_3;
  
  local_3 = '\0';
  do {
    FUN_1cdc_0400(9);
    uVar2 = FUN_1cdc_1936((char *)s__3I_m_sorry__that_is_not_the_cor_3360_1022 + 0x1c,0x2ca8);
    if (uVar2 == 0x23) {
      local_3 = FUN_1cdc_1eb0();
    }
    else if (uVar2 < 0x24) {
      cVar1 = (char)uVar2;
      if (cVar1 == '\x06') {
LAB_1cdc_21d3:
        local_3 = '\x01';
      }
      else if (cVar1 == '\x0e') {
        local_3 = FUN_1cdc_209a();
      }
      else if ((cVar1 == '\x15') || (cVar1 == '\x16')) goto LAB_1cdc_21d3;
    }
    if (local_3 != '\0') {
      FUN_1273_0c4e();
      return;
    }
  } while( true );
}

