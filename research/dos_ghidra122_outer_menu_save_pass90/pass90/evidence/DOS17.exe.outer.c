
void __cdecl16far FUN_1d0f_217e(void)

{
  char cVar1;
  uint uVar2;
  char local_3;
  
  local_3 = '\0';
  do {
    FUN_1d0f_0400(9);
    uVar2 = FUN_1d0f_1916((char *)s_T7You_ve_won__You_ve_won__3754_103c + 2,0x309c);
    if (uVar2 == 0x23) {
      local_3 = FUN_1d0f_1e90((char *)s_Bad_color_code_in_instr_3754_1d01 + 0xe);
    }
    else if (uVar2 < 0x24) {
      cVar1 = (char)uVar2;
      if (cVar1 == '\x06') {
LAB_1d0f_21b3:
        local_3 = '\x01';
      }
      else if (cVar1 == '\x0e') {
        local_3 = FUN_1d0f_207a();
      }
      else if ((cVar1 == '\x15') || (cVar1 == '\x16')) goto LAB_1d0f_21b3;
    }
    if (local_3 != '\0') {
      FUN_1277_0d06();
      return;
    }
  } while( true );
}

