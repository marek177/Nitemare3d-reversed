
void __cdecl16far FUN_1d25_21b2(void)

{
  char cVar1;
  uint uVar2;
  char local_3;
  
  local_3 = '\0';
  do {
    FUN_1d25_0404(9);
    uVar2 = FUN_1d25_194a((char *)s_m7Watch_out_you_clod__You_almost_376d_103e,0x30b5);
    if (uVar2 == 0x23) {
      local_3 = FUN_1d25_1ec4();
    }
    else if (uVar2 < 0x24) {
      cVar1 = (char)uVar2;
      if (cVar1 == '\x06') {
LAB_1d25_21e7:
        local_3 = '\x01';
      }
      else if (cVar1 == '\x0e') {
        local_3 = FUN_1d25_20ae();
      }
      else if ((cVar1 == '\x15') || (cVar1 == '\x16')) goto LAB_1d25_21e7;
    }
    if (local_3 != '\0') {
      FUN_1277_0d04();
      return;
    }
  } while( true );
}

