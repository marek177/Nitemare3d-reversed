
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __cdecl16far FUN_1bda_001c(void)

{
  int local_10 [2];
  int local_c;
  undefined4 local_6;
  
  if ((DAT_376d_3cc7 != '\0') || (DAT_376d_3ccf == '\0')) {
    FUN_21ea_2aee(local_10);
    return local_10[0] * 1000 + local_c;
  }
  local_6 = CONCAT22(_DAT_0000_046e,_DAT_0000_046c);
  if (DAT_376d_16f0._2_2_ == 0 && (int)DAT_376d_16f0 == 0) {
    DAT_376d_16f0 = local_6;
  }
  return (_DAT_0000_046c - (int)DAT_376d_16f0) * 0x37;
}

