
void __cdecl16far FUN_1d00_0a14(void)

{
  char *pcVar1;
  undefined1 local_60 [70];
  int local_1a;
  int local_18;
  undefined2 local_4;
  
  local_4 = 0x3c;
  pcVar1 = (char *)0x0;
  FUN_1bff_0294();
  FUN_1d00_0404();
  FUN_1d00_016e();
  FUN_1817_257a();
  if (local_1a == 0) {
    pcVar1 = (char *)s_Distributed_by_3395_1387 + 1;
  }
  if (local_18 == 0) {
    pcVar1 = (char *)s_Distributed_by_3395_1387 + 1 + (int)pcVar1;
  }
  DAT_3395_40de = DAT_3395_40de + (int)pcVar1;
  FUN_21bc_278c(local_60,0x1cd1,DAT_3395_61c8 + 1);
  FUN_1275_0160(0x1000e);
  FUN_1d00_011a(0x3c00dc,local_60);
  FUN_21bc_278c(local_60,0x1cd4,local_1a);
  FUN_1275_0160(0x1000e);
  FUN_1d00_011a(0xdc,0x50,local_60);
  FUN_21bc_278c(local_60,0x1cd7,local_18);
  FUN_1275_0160(0x1000e);
  FUN_1d00_011a(0xdc,100,local_60);
  FUN_21bc_278c(local_60,0x1cda,pcVar1);
  FUN_1275_0160(0x1000e);
  FUN_1d00_011a(0xdc,0x78,local_60);
  FUN_21bc_278c(local_60,0x1cdd,DAT_3395_40de);
  FUN_1d00_016e();
  FUN_1275_0160(0x1000e);
  FUN_1d00_011a(0xdc,0x8c,local_60);
  FUN_1d00_04fe();
  return;
}

