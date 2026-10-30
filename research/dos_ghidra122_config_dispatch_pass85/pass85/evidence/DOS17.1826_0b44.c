
char __cdecl16far FUN_1826_0b44(void)

{
  undefined2 uVar1;
  char local_3;
  
  if (DAT_3754_40c1 != '\0') {
    return '\x01';
  }
  if (DAT_3754_40fd != '\0') {
    if (DAT_3754_40fd == '\x01') {
      local_3 = DAT_3754_411e;
      if (DAT_3754_411e != '\0') {
        DAT_3754_411e = DAT_3754_411e + -1;
      }
      uVar1 = 9;
      goto LAB_1826_0b9e;
    }
    if (DAT_3754_40fd == '\x02') {
      local_3 = DAT_3754_40f9;
      if (DAT_3754_40f9 != '\0') {
        DAT_3754_40f9 = DAT_3754_40f9 + -1;
      }
      uVar1 = 7;
      goto LAB_1826_0b9e;
    }
    if (DAT_3754_40fd != '\x03') {
      return '\0';
    }
  }
  local_3 = DAT_3754_40fa;
  if (DAT_3754_40fa != '\0') {
    DAT_3754_40fa = DAT_3754_40fa + -1;
  }
  uVar1 = 8;
LAB_1826_0b9e:
  FUN_1826_05d4(uVar1);
  return local_3;
}

