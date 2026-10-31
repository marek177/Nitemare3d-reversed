
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __cdecl16far FUN_1bb2_0016(void)

{
  int local_10 [2];
  int local_c;
  undefined4 local_6;
  
  if ((DAT_339b_3c67 != '\0') || (DAT_339b_3c6f == '\0')) {
    FUN_21c2_2aea(local_10);
    return local_10[0] * 1000 + local_c;
  }
  local_6 = CONCAT22(_DAT_0000_046e,_DAT_0000_046c);
  if (DAT_339b_16ba._2_2_ == 0 && (int)DAT_339b_16ba == 0) {
    DAT_339b_16ba = local_6;
  }
  return (_DAT_0000_046c - (int)DAT_339b_16ba) * 0x37;
}

