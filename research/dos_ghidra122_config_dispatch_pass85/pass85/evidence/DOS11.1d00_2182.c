
void __cdecl16far FUN_1d00_2182(void)

{
  char cVar1;
  uint uVar2;
  char local_3;
  
  local_3 = '\0';
  do {
    FUN_1d00_0404(9);
    uVar2 = FUN_1d00_191a((char *)s_3Watch_out_you_clod__You_almost_h_3395_1017 + 0x27,0x2cdd);
    if (uVar2 == 0x23) {
      local_3 = FUN_1d00_1e94();
    }
    else if (uVar2 < 0x24) {
      cVar1 = (char)uVar2;
      if (cVar1 == '\x06') {
LAB_1d00_21b7:
        local_3 = '\x01';
      }
      else if (cVar1 == '\x0e') {
        local_3 = FUN_1d00_207e();
      }
      else if ((cVar1 == '\x15') || (cVar1 == '\x16')) goto LAB_1d00_21b7;
    }
    if (local_3 != '\0') {
      FUN_1275_0c74();
      return;
    }
  } while( true );
}

