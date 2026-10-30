
int __cdecl16far FUN_1277_1602(int param_1)

{
  int iVar1;
  int iVar2;
  
  if (DAT_3754_064b != '\0') {
    DAT_3754_064b = '\0';
    iVar1 = FUN_21d1_1c72(0x64c,0x8000);
    if (iVar1 == -1) {
      FUN_1f9d_000c(0x65c,0x654);
    }
    iVar2 = FUN_1f9d_009e(iVar1,0,0x2bbe,0xc0);
    if (iVar2 != 0xc0) {
      FUN_1f9d_000c(0x67a,0x672);
    }
    FUN_21d1_1bb6((char *)s_About_to__s_game____s__Press_ESC_3754_1f72 + 0x2b,iVar1);
  }
  return param_1 * 6;
}

