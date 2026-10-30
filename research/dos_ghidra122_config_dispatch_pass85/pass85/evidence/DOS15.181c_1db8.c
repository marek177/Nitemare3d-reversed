
void __cdecl16far FUN_181c_1db8(byte param_1)

{
  char cVar1;
  char cVar2;
  
  cVar2 = DAT_374a_40db;
  cVar1 = DAT_374a_40da;
  if (DAT_374a_407e == '\0') {
    if ((DAT_374a_40c2 != '\0') && ((param_1 & 0xf) == 0)) {
      DAT_374a_40db = DAT_374a_40db + -1;
    }
    if ((DAT_374a_40c3 != '\0') && ((param_1 & 7) == 0)) {
      DAT_374a_40da = DAT_374a_40da + -1;
    }
    if ((DAT_374a_40c2 != '\0') && (DAT_374a_40db == '\0')) {
      DAT_374a_40c2 = '\0';
      DAT_374a_40db = '\0';
      FUN_181c_1442(3);
    }
    if ((DAT_374a_40c3 != '\0') && (DAT_374a_40da == '\0')) {
      DAT_374a_40c3 = '\0';
      DAT_374a_40da = '\0';
      FUN_181c_1442(3);
    }
    if (cVar1 != DAT_374a_40da) {
      FUN_181c_05d8();
    }
    if (cVar2 != DAT_374a_40db) {
      FUN_181c_05d8();
    }
  }
  return;
}

