
void __cdecl16far FUN_1d05_0a14(void)

{
  char *pcVar1;
  undefined1 local_60 [70];
  int local_1a;
  int local_18;
  undefined2 local_4;
  
  local_4 = 0x3c;
  pcVar1 = (char *)0x0;
  FUN_1c07_029c();
  FUN_1d05_0404();
  FUN_1d05_016e();
  FUN_181c_25b2();
  if (local_1a == 0) {
    pcVar1 = (char *)s_Distributed_by_374a_137d + 0xb;
  }
  if (local_18 == 0) {
    pcVar1 = (char *)s_Distributed_by_374a_137d + 0xb + (int)pcVar1;
  }
  DAT_374a_40ae = DAT_374a_40ae + (int)pcVar1;
  FUN_21c7_2790(local_60,0x1c95,DAT_374a_6198 + 1);
  FUN_1277_0188(0x1000e);
  FUN_1d05_011a(0x3c00dc,local_60);
  FUN_21c7_2790(local_60,0x1c98,local_1a);
  FUN_1277_0188(0x1000e);
  FUN_1d05_011a(0xdc,0x50,local_60);
  FUN_21c7_2790(local_60,0x1c9b,local_18);
  FUN_1277_0188(0x1000e);
  FUN_1d05_011a(0xdc,100,local_60);
  FUN_21c7_2790(local_60,0x1c9e,pcVar1);
  FUN_1277_0188(0x1000e);
  FUN_1d05_011a(0xdc,0x78,local_60);
  FUN_21c7_2790(local_60,0x1ca1,DAT_374a_40ae);
  FUN_1d05_016e();
  FUN_1277_0188(0x1000e);
  FUN_1d05_011a(0xdc,0x8c,local_60);
  FUN_1d05_04fe();
  return;
}

