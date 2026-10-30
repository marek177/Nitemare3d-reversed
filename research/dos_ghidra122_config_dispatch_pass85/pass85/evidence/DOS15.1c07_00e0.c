
void __cdecl16far FUN_1c07_00e0(int param_1)

{
  char cVar1;
  int iVar2;
  
  if (param_1 == 0) {
    if (DAT_374a_3c36 == '\0') {
      DAT_374a_407d = 0;
      DAT_374a_407b = 0;
      DAT_374a_407c = 0;
      return;
    }
    FUN_1c07_000a();
    DAT_374a_1799 = '\x01';
    iVar2 = FUN_1c07_0024();
    cVar1 = FUN_2099_069e();
    FUN_2099_05d6();
    DAT_374a_35e8 = FUN_2099_063a();
    DAT_374a_35ea = FUN_2099_066c();
    DAT_374a_179b = '\x01';
    if (cVar1 == '\0') {
      DAT_374a_407b = '\0';
    }
    if (iVar2 < 1) {
      DAT_374a_3c37 = '\0';
    }
    if ((DAT_374a_407c == '\0') || (DAT_374a_3c37 == '\0')) {
      DAT_374a_179a = '\0';
    }
    else {
      DAT_374a_179a = '\x01';
    }
    if (DAT_374a_179a == '\0') {
      FUN_2099_0702();
    }
    if (cVar1 != '\0') {
      FUN_1c07_029c(0);
    }
  }
  else {
    if (param_1 == 1) {
      if (DAT_374a_1799 != '\0') {
        FUN_2099_0eb6();
        if (DAT_374a_179a != '\0') {
          FUN_2099_0ee5();
          FUN_2099_0702();
        }
        FUN_2099_0063();
        DAT_374a_1799 = '\0';
        DAT_374a_179a = '\0';
        DAT_374a_179b = '\0';
      }
      DAT_374a_407b = 0;
      DAT_374a_407c = 0;
      DAT_374a_407d = 0;
      return;
    }
    if (param_1 != 2) {
      return;
    }
    if ((((DAT_374a_407d != '\0') || (DAT_374a_407c != '\0')) || (DAT_374a_407b != '\0')) &&
       (DAT_374a_1799 == '\0')) {
      FUN_1c07_000a();
      FUN_1c07_029c(0);
      DAT_374a_1799 = '\x01';
    }
    if ((DAT_374a_407d != '\0') && (DAT_374a_179b == '\0')) {
      FUN_2099_05d6();
      DAT_374a_35e8 = FUN_2099_063a();
      DAT_374a_35ea = FUN_2099_066c();
      DAT_374a_179b = '\x01';
    }
    if (((DAT_374a_407c == '\0') || (DAT_374a_3c37 == '\0')) || (DAT_374a_179a != '\0')) {
      if ((DAT_374a_407c == '\0') && (DAT_374a_179a != '\0')) {
        FUN_2099_0702();
        DAT_374a_179a = '\0';
      }
    }
    else {
      iVar2 = FUN_1c07_0024();
      if (0 < iVar2) {
        DAT_374a_179a = '\x01';
      }
    }
  }
  if (DAT_374a_407b != '\0') {
    FUN_1c07_00ae();
  }
  return;
}

