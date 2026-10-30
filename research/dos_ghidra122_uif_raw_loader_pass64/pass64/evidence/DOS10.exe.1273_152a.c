
int __cdecl16far FUN_1273_152a(int param_1)

{
  int iVar1;
  int iVar2;
  
  if (DAT_3360_05fd != '\0') {
    DAT_3360_05fd = '\0';
    iVar1 = FUN_219b_1d6e(0x5fe,0x8000);
    if (iVar1 == -1) {
      FUN_1f67_000a(0x60e,0x606);
    }
    iVar2 = FUN_1f67_009c(iVar1,0,0x2b94,0xc0);
    if (iVar2 != 0xc0) {
      FUN_1f67_000a(0x62c,0x624);
    }
    FUN_219b_1cb2((char *)s_Copyright_1992__David_P_Gray__Gr_3360_1f3f + 0x28,iVar1);
  }
  return param_1 * 6;
}

