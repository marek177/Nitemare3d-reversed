
void __cdecl16far FUN_1d00_2184(void)

{
  char cVar1;
  uint uVar2;
  char local_3;
  
  local_3 = '\0';
  do {
    FUN_1d00_0406(9);
    uVar2 = FUN_1d00_191c((char *)s_3You_ve_won__You_ve_won__339b_1033 + 0xb,0x2ce3);
    if (uVar2 == 0x23) {
      local_3 = FUN_1d00_1e96();
    }
    else if (uVar2 < 0x24) {
      cVar1 = (char)uVar2;
      if (cVar1 == '\x06') {
LAB_1d00_21b9:
        local_3 = '\x01';
      }
      else if (cVar1 == '\x0e') {
        local_3 = FUN_1d00_2080();
      }
      else if ((cVar1 == '\x15') || (cVar1 == '\x16')) goto LAB_1d00_21b9;
    }
    if (local_3 != '\0') {
      FUN_1275_0c86();
      return;
    }
  } while( true );
}

