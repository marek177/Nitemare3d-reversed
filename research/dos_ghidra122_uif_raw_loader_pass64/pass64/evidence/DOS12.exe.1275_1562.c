
int __cdecl16far FUN_1275_1562(int param_1)

{
  int iVar1;
  int iVar2;
  
  if (DAT_339b_0647 != '\0') {
    DAT_339b_0647 = '\0';
    iVar1 = FUN_21c2_1c72(0x648,0x8000);
    if (iVar1 == -1) {
      FUN_1f8f_0002(0x658,0x650);
    }
    iVar2 = FUN_1f8f_0094(iVar1,0,0x2baf,0xc0);
    if (iVar2 != 0xc0) {
      FUN_1f8f_0002(0x676,0x66e);
    }
    FUN_21c2_1bb6((char *)s_user_sav_339b_1f8e + 1,iVar1);
  }
  return param_1 * 6;
}

