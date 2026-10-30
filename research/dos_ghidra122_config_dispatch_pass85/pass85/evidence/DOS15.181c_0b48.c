
char __cdecl16far FUN_181c_0b48(void)

{
  undefined2 uVar1;
  char local_3;
  
  if (DAT_374a_407f != '\0') {
    return '\x01';
  }
  if (DAT_374a_40bb != '\0') {
    if (DAT_374a_40bb == '\x01') {
      local_3 = DAT_374a_40dc;
      if (DAT_374a_40dc != '\0') {
        DAT_374a_40dc = DAT_374a_40dc + -1;
      }
      uVar1 = 9;
      goto LAB_181c_0ba2;
    }
    if (DAT_374a_40bb == '\x02') {
      local_3 = DAT_374a_40b7;
      if (DAT_374a_40b7 != '\0') {
        DAT_374a_40b7 = DAT_374a_40b7 + -1;
      }
      uVar1 = 7;
      goto LAB_181c_0ba2;
    }
    if (DAT_374a_40bb != '\x03') {
      return '\0';
    }
  }
  local_3 = DAT_374a_40b8;
  if (DAT_374a_40b8 != '\0') {
    DAT_374a_40b8 = DAT_374a_40b8 + -1;
  }
  uVar1 = 8;
LAB_181c_0ba2:
  FUN_181c_05d8(uVar1);
  return local_3;
}

