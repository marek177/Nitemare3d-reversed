
char __cdecl16far FUN_1817_0b44(void)

{
  undefined2 uVar1;
  char local_3;
  
  if (DAT_3395_40af != '\0') {
    return '\x01';
  }
  if (DAT_3395_40eb != '\0') {
    if (DAT_3395_40eb == '\x01') {
      local_3 = DAT_3395_410c;
      if (DAT_3395_410c != '\0') {
        DAT_3395_410c = DAT_3395_410c + -1;
      }
      uVar1 = 10;
      goto LAB_1817_0b9e;
    }
    if (DAT_3395_40eb == '\x02') {
      local_3 = DAT_3395_40e7;
      if (DAT_3395_40e7 != '\0') {
        DAT_3395_40e7 = DAT_3395_40e7 + -1;
      }
      uVar1 = 8;
      goto LAB_1817_0b9e;
    }
    if (DAT_3395_40eb != '\x03') {
      return '\0';
    }
  }
  local_3 = DAT_3395_40e8;
  if (DAT_3395_40e8 != '\0') {
    DAT_3395_40e8 = DAT_3395_40e8 + -1;
  }
  uVar1 = 9;
LAB_1817_0b9e:
  FUN_1817_05ca(uVar1);
  return local_3;
}

