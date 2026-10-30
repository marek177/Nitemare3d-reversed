
char __cdecl16far FUN_183c_0b48(void)

{
  undefined2 uVar1;
  char local_3;
  
  if (DAT_376d_4151 != '\0') {
    return '\x01';
  }
  if (DAT_376d_418d != '\0') {
    if (DAT_376d_418d == '\x01') {
      local_3 = DAT_376d_41ae;
      if (DAT_376d_41ae != '\0') {
        DAT_376d_41ae = DAT_376d_41ae + -1;
      }
      uVar1 = 9;
      goto LAB_183c_0ba2;
    }
    if (DAT_376d_418d == '\x02') {
      local_3 = DAT_376d_4189;
      if (DAT_376d_4189 != '\0') {
        DAT_376d_4189 = DAT_376d_4189 + -1;
      }
      uVar1 = 7;
      goto LAB_183c_0ba2;
    }
    if (DAT_376d_418d != '\x03') {
      return '\0';
    }
  }
  local_3 = DAT_376d_418a;
  if (DAT_376d_418a != '\0') {
    DAT_376d_418a = DAT_376d_418a + -1;
  }
  uVar1 = 8;
LAB_183c_0ba2:
  FUN_183c_05d8(uVar1);
  return local_3;
}

