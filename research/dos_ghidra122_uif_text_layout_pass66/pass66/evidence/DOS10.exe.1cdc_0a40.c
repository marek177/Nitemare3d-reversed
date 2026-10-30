
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl16far FUN_1cdc_0a40(void)

{
  char *pcVar1;
  undefined1 local_60 [70];
  int local_1a;
  int local_18;
  undefined2 local_4;
  
  local_4 = 0x3c;
  pcVar1 = (char *)0x0;
  FUN_1bdd_0270();
  FUN_1cdc_0400();
  FUN_1cdc_016a();
  FUN_17f5_257a();
  if (local_1a == 0) {
    pcVar1 = (char *)s_class__d__strength__d__strategy___3360_134d + 0x3b;
  }
  if (local_18 == 0) {
    pcVar1 = (char *)s_class__d__strength__d__strategy___3360_134d + 0x3b + (int)pcVar1;
  }
  _DAT_3360_3fd8 = _DAT_3360_3fd8 + (int)pcVar1;
  FUN_219b_2888(local_60,0x1bef,DAT_3360_60c2 + 1);
  FUN_1273_016c(0x1000e);
  FUN_1cdc_0116(0x3c00dc,local_60);
  FUN_219b_2888(local_60,0x1bf2,local_1a);
  FUN_1273_016c(0x1000e);
  FUN_1cdc_0116(0xdc,0x50,local_60);
  FUN_219b_2888(local_60,0x1bf5,local_18);
  FUN_1273_016c(0x1000e);
  FUN_1cdc_0116(0xdc,100,local_60);
  FUN_219b_2888(local_60,0x1bf8,pcVar1);
  FUN_1273_016c(0x1000e);
  FUN_1cdc_0116(0xdc,0x78,local_60);
  FUN_219b_2888(local_60,0x1bfb,_DAT_3360_3fd8);
  FUN_1cdc_016a();
  FUN_1273_016c(0x1000e);
  FUN_1cdc_0116(0xdc,0x8c,local_60);
  FUN_1cdc_04fa();
  return;
}

