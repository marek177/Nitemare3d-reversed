
char __cdecl16far FUN_17f5_0b44(void)

{
  undefined2 uVar1;
  char local_3;
  
  if (DAT_3360_3fa9 != '\0') {
    return '\x01';
  }
  if (DAT_3360_3fe5 != '\0') {
    if (DAT_3360_3fe5 == '\x01') {
      local_3 = DAT_3360_4006;
      if (DAT_3360_4006 != '\0') {
        DAT_3360_4006 = DAT_3360_4006 + -1;
      }
      uVar1 = 10;
      goto LAB_17f5_0b9e;
    }
    if (DAT_3360_3fe5 == '\x02') {
      local_3 = DAT_3360_3fe1;
      if (DAT_3360_3fe1 != '\0') {
        DAT_3360_3fe1 = DAT_3360_3fe1 + -1;
      }
      uVar1 = 8;
      goto LAB_17f5_0b9e;
    }
    if (DAT_3360_3fe5 != '\x03') {
      return '\0';
    }
  }
  local_3 = DAT_3360_3fe2;
  if (DAT_3360_3fe2 != '\0') {
    DAT_3360_3fe2 = DAT_3360_3fe2 + -1;
  }
  uVar1 = 9;
LAB_17f5_0b9e:
  FUN_17f5_05ca(uVar1);
  return local_3;
}

