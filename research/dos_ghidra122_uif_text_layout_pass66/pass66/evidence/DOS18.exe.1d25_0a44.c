
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl16far FUN_1d25_0a44(void)

{
  char *pcVar1;
  undefined1 local_60 [70];
  int local_1a;
  int local_18;
  undefined2 local_4;
  
  local_4 = 0x3c;
  pcVar1 = (char *)0x0;
  FUN_1c27_029c();
  FUN_1d25_0404();
  FUN_1d25_016e();
  FUN_183c_25b2();
  if (local_1a == 0) {
    pcVar1 = (char *)s_m7Let_s_find_some_dance_music__376d_137a + 0xe;
  }
  if (local_18 == 0) {
    pcVar1 = (char *)s_m7Let_s_find_some_dance_music__376d_137a + 0xe + (int)pcVar1;
  }
  _DAT_376d_4180 = _DAT_376d_4180 + (int)pcVar1;
  FUN_21ea_2790(local_60,0x1cd3,DAT_376d_626a + 1);
  FUN_1277_0188(0x1000e);
  FUN_1d25_011a(0x3c00dc,local_60);
  FUN_21ea_2790(local_60,0x1cd6,local_1a);
  FUN_1277_0188(0x1000e);
  FUN_1d25_011a(0xdc,0x50,local_60);
  FUN_21ea_2790(local_60,0x1cd9,local_18);
  FUN_1277_0188(0x1000e);
  FUN_1d25_011a(0xdc,100,local_60);
  FUN_21ea_2790(local_60,0x1cdc,pcVar1);
  FUN_1277_0188(0x1000e);
  FUN_1d25_011a(0xdc,0x78,local_60);
  FUN_21ea_2790(local_60,0x1cdf,_DAT_376d_4180);
  FUN_1d25_016e();
  FUN_1277_0188(0x1000e);
  FUN_1d25_011a(0xdc,0x8c,local_60);
  FUN_1d25_04fe();
  return;
}

