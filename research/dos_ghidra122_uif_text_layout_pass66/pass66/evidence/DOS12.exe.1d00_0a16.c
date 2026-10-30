
void __cdecl16far FUN_1d00_0a16(void)

{
  char *pcVar1;
  undefined1 local_60 [70];
  int local_1a;
  int local_18;
  undefined2 local_4;
  
  local_4 = 0x3c;
  pcVar1 = (char *)0x0;
  FUN_1bff_0296();
  FUN_1d00_0406();
  FUN_1d00_0170();
  FUN_1818_256c();
  if (local_1a == 0) {
    pcVar1 = (char *)s_Not_for_re_distribution_339b_1386 + 2;
  }
  if (local_18 == 0) {
    pcVar1 = (char *)s_Not_for_re_distribution_339b_1386 + 2 + (int)pcVar1;
  }
  DAT_339b_40de = DAT_339b_40de + (int)pcVar1;
  FUN_21c2_278c(local_60,0x1cc3,DAT_339b_61c8 + 1);
  FUN_1275_0160(0x1000e);
  FUN_1d00_011c(0x3c00dc,local_60);
  FUN_21c2_278c(local_60,0x1cc6,local_1a);
  FUN_1275_0160(0x1000e);
  FUN_1d00_011c(0xdc,0x50,local_60);
  FUN_21c2_278c(local_60,0x1cc9,local_18);
  FUN_1275_0160(0x1000e);
  FUN_1d00_011c(0xdc,100,local_60);
  FUN_21c2_278c(local_60,0x1ccc,pcVar1);
  FUN_1275_0160(0x1000e);
  FUN_1d00_011c(0xdc,0x78,local_60);
  FUN_21c2_278c(local_60,0x1ccf,DAT_339b_40de);
  FUN_1d00_0170();
  FUN_1275_0160(0x1000e);
  FUN_1d00_011c(0xdc,0x8c,local_60);
  FUN_1d00_0500();
  return;
}

