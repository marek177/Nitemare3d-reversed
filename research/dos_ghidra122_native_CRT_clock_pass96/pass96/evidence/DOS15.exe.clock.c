
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __cdecl16far FUN_1bba_001c(void)

{
  int local_10 [2];
  int local_c;
  undefined4 local_6;
  
  if ((DAT_374a_3c37 != '\0') || (DAT_374a_3c3f == '\0')) {
    FUN_21c7_2aee(local_10);
    return local_10[0] * 1000 + local_c;
  }
  local_6 = CONCAT22(_DAT_0000_046e,_DAT_0000_046c);
  if (DAT_374a_16be._2_2_ == 0 && (int)DAT_374a_16be == 0) {
    DAT_374a_16be = local_6;
  }
  return (_DAT_0000_046c - (int)DAT_374a_16be) * 0x37;
}

