
int __cdecl16far FUN_1277_158a(int param_1)

{
  int iVar1;
  int iVar2;
  
  if (DAT_374a_064b != '\0') {
    DAT_374a_064b = '\0';
    iVar1 = FUN_21c7_1c76(0x64c,0x8000);
    if (iVar1 == -1) {
      FUN_1f94_0000(0x65c,0x654);
    }
    iVar2 = FUN_1f94_0092(iVar1,0,0x2bb4,0xc0);
    if (iVar2 != 0xc0) {
      FUN_1f94_0000(0x67a,0x672);
    }
    FUN_21c7_1bba((char *)s_About_to__s_game____s__Press_ESC_374a_1f6e + 0x26,iVar1);
  }
  return param_1 * 6;
}

