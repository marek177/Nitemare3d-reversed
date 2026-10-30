
void __cdecl16far FUN_183c_1db8(byte param_1)

{
  char cVar1;
  char cVar2;
  
  cVar2 = DAT_376d_41ad;
  cVar1 = DAT_376d_41ac;
  if (DAT_376d_4150 == '\0') {
    if ((DAT_376d_4194 != '\0') && ((param_1 & 0xf) == 0)) {
      DAT_376d_41ad = DAT_376d_41ad + -1;
    }
    if ((DAT_376d_4195 != '\0') && ((param_1 & 7) == 0)) {
      DAT_376d_41ac = DAT_376d_41ac + -1;
    }
    if ((DAT_376d_4194 != '\0') && (DAT_376d_41ad == '\0')) {
      DAT_376d_4194 = '\0';
      DAT_376d_41ad = '\0';
      FUN_183c_1442(3);
    }
    if ((DAT_376d_4195 != '\0') && (DAT_376d_41ac == '\0')) {
      DAT_376d_4195 = '\0';
      DAT_376d_41ac = '\0';
      FUN_183c_1442(3);
    }
    if (cVar1 != DAT_376d_41ac) {
      FUN_183c_05d8();
    }
    if (cVar2 != DAT_376d_41ad) {
      FUN_183c_05d8();
    }
  }
  return;
}

