
int __cdecl16far FUN_1277_1766(int param_1)

{
  int iVar1;
  int iVar2;
  
  if (DAT_376d_0678 != '\0') {
    DAT_376d_0678 = '\0';
    iVar1 = FUN_21ea_1c76(0x679,0x8000);
    if (iVar1 == -1) {
      FUN_1fb7_0000(0x689,0x681);
    }
    iVar2 = FUN_1fb7_0092(iVar1,0,0x2bd7,0xc0);
    if (iVar2 != 0xc0) {
      FUN_1fb7_0000(0x6a7,0x69f);
    }
    FUN_21ea_1bba((char *)s_About_to__s_game____s__Press_ESC_376d_1fac + 0xb,iVar1);
  }
  return param_1 * 6;
}

