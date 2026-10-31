
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __cdecl16far FUN_1b91_001c(void)

{
  int local_10 [2];
  int local_c;
  undefined4 local_6;
  
  if ((DAT_3360_3b67 != '\0') || (DAT_3360_3b69 == '\0')) {
    FUN_219b_2bae(local_10);
    return local_10[0] * 1000 + local_c;
  }
  local_6 = CONCAT22(_DAT_0000_046e,_DAT_0000_046c);
  if (DAT_3360_1638._2_2_ == 0 && (int)DAT_3360_1638 == 0) {
    DAT_3360_1638 = local_6;
  }
  return (_DAT_0000_046c - (int)DAT_3360_1638) * 0x37;
}

