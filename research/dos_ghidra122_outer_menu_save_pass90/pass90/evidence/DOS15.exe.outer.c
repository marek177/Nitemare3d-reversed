
void __cdecl16far FUN_1d05_2182(void)

{
  char cVar1;
  uint uVar2;
  char local_3;
  
  local_3 = '\0';
  do {
    FUN_1d05_0404(9);
    uVar2 = FUN_1d05_191a((char *)s_J7You_ve_won__You_ve_won__374a_1038 + 6,0x3092);
    if (uVar2 == 0x23) {
      local_3 = FUN_1d05_1e94();
    }
    else if (uVar2 < 0x24) {
      cVar1 = (char)uVar2;
      if (cVar1 == '\x06') {
LAB_1d05_21b7:
        local_3 = '\x01';
      }
      else if (cVar1 == '\x0e') {
        local_3 = FUN_1d05_207e();
      }
      else if ((cVar1 == '\x15') || (cVar1 == '\x16')) goto LAB_1d05_21b7;
    }
    if (local_3 != '\0') {
      FUN_1277_0cae();
      return;
    }
  } while( true );
}

