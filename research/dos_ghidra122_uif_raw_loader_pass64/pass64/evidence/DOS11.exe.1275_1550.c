
int __cdecl16far FUN_1275_1550(int param_1)

{
  int iVar1;
  int iVar2;
  
  if (DAT_3395_063c != '\0') {
    DAT_3395_063c = '\0';
    iVar1 = FUN_21bc_1c72(0x63d,0x8000);
    if (iVar1 == -1) {
      FUN_1f89_0002(0x64d,0x645);
    }
    iVar2 = FUN_1f89_0094(iVar1,0,0x2ba9,0xc0);
    if (iVar2 != 0xc0) {
      FUN_1f89_0002(0x66b,0x663);
    }
    FUN_21bc_1bb6((char *)s_About_to__s_game____s__Press_ESC_3395_1f66 + 0x23,iVar1);
  }
  return param_1 * 6;
}

