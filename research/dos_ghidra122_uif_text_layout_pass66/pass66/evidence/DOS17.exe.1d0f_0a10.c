
void __cdecl16far FUN_1d0f_0a10(void)

{
  char *pcVar1;
  undefined1 local_60 [70];
  int local_1a;
  int local_18;
  undefined2 local_4;
  
  local_4 = 0x3c;
  pcVar1 = (char *)0x0;
  FUN_1c11_0298();
  FUN_1d0f_0400();
  FUN_1d0f_016a();
  FUN_1826_25ae();
  if (local_1a == 0) {
    pcVar1 = (char *)s_Distributed_by_3754_1381 + 7;
  }
  if (local_18 == 0) {
    pcVar1 = (char *)s_Distributed_by_3754_1381 + 7 + (int)pcVar1;
  }
  DAT_3754_40f0 = DAT_3754_40f0 + (int)pcVar1;
  FUN_21d1_278c(local_60,0x1c99,DAT_3754_61da + 1);
  FUN_1277_0188(0x1000e);
  FUN_1d0f_0116(0x3c00dc,local_60);
  FUN_21d1_278c(local_60,0x1c9c,local_1a);
  FUN_1277_0188(0x1000e);
  FUN_1d0f_0116(0xdc,0x50,local_60);
  FUN_21d1_278c(local_60,0x1c9f,local_18);
  FUN_1277_0188(0x1000e);
  FUN_1d0f_0116(0xdc,100,local_60);
  FUN_21d1_278c(local_60,0x1ca2,pcVar1);
  FUN_1277_0188(0x1000e);
  FUN_1d0f_0116(0xdc,0x78,local_60);
  FUN_21d1_278c(local_60,0x1ca5,DAT_3754_40f0);
  FUN_1d0f_016a();
  FUN_1277_0188(0x1000e);
  FUN_1d0f_0116(0xdc,0x8c,local_60);
  FUN_1d0f_04fa();
  return;
}

