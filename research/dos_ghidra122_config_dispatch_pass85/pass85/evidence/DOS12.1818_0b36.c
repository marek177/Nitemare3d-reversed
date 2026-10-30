
char __cdecl16far FUN_1818_0b36(void)

{
  undefined2 uVar1;
  char local_3;
  
  if (DAT_339b_40af != '\0') {
    return '\x01';
  }
  if (DAT_339b_40eb != '\0') {
    if (DAT_339b_40eb == '\x01') {
      local_3 = DAT_339b_410c;
      if (DAT_339b_410c != '\0') {
        DAT_339b_410c = DAT_339b_410c + -1;
      }
      uVar1 = 9;
      goto LAB_1818_0b90;
    }
    if (DAT_339b_40eb == '\x02') {
      local_3 = DAT_339b_40e7;
      if (DAT_339b_40e7 != '\0') {
        DAT_339b_40e7 = DAT_339b_40e7 + -1;
      }
      uVar1 = 7;
      goto LAB_1818_0b90;
    }
    if (DAT_339b_40eb != '\x03') {
      return '\0';
    }
  }
  local_3 = DAT_339b_40e8;
  if (DAT_339b_40e8 != '\0') {
    DAT_339b_40e8 = DAT_339b_40e8 + -1;
  }
  uVar1 = 8;
LAB_1818_0b90:
  FUN_1818_05c6(uVar1);
  return local_3;
}

