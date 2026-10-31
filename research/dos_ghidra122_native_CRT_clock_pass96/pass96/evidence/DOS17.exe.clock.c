
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __cdecl16far FUN_1bc4_0018(void)

{
  int local_10 [2];
  int local_c;
  undefined4 local_6;
  
  if ((DAT_3754_3c37 != '\0') || (DAT_3754_3c3f == '\0')) {
    FUN_21d1_2aea(local_10);
    return local_10[0] * 1000 + local_c;
  }
  local_6 = CONCAT22(_DAT_0000_046e,_DAT_0000_046c);
  if (DAT_3754_16c2._2_2_ == 0 && (int)DAT_3754_16c2 == 0) {
    DAT_3754_16c2 = local_6;
  }
  return (_DAT_0000_046c - (int)DAT_3754_16c2) * 0x37;
}

