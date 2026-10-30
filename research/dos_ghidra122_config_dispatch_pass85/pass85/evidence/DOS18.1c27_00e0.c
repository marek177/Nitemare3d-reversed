
void __cdecl16far FUN_1c27_00e0(int param_1)

{
  char cVar1;
  int iVar2;
  
  if (param_1 == 0) {
    if (DAT_376d_3cc6 == '\0') {
      DAT_376d_414f = 0;
      DAT_376d_414d = 0;
      DAT_376d_414e = 0;
      return;
    }
    FUN_1c27_000a();
    DAT_376d_17cb = '\x01';
    iVar2 = FUN_1c27_0024();
    cVar1 = FUN_20bc_069e();
    FUN_20bc_05d6();
    DAT_376d_3678 = FUN_20bc_063a();
    DAT_376d_367a = FUN_20bc_066c();
    DAT_376d_17cd = '\x01';
    if (cVar1 == '\0') {
      DAT_376d_414d = '\0';
    }
    if (iVar2 < 1) {
      DAT_376d_3cc7 = '\0';
    }
    if ((DAT_376d_414e == '\0') || (DAT_376d_3cc7 == '\0')) {
      DAT_376d_17cc = '\0';
    }
    else {
      DAT_376d_17cc = '\x01';
    }
    if (DAT_376d_17cc == '\0') {
      FUN_20bc_0702();
    }
    if (cVar1 != '\0') {
      FUN_1c27_029c(0);
    }
  }
  else {
    if (param_1 == 1) {
      if (DAT_376d_17cb != '\0') {
        FUN_20bc_0eb6();
        if (DAT_376d_17cc != '\0') {
          FUN_20bc_0ee5();
          FUN_20bc_0702();
        }
        FUN_20bc_0063();
        DAT_376d_17cb = '\0';
        DAT_376d_17cc = '\0';
        DAT_376d_17cd = '\0';
      }
      DAT_376d_414d = 0;
      DAT_376d_414e = 0;
      DAT_376d_414f = 0;
      return;
    }
    if (param_1 != 2) {
      return;
    }
    if ((((DAT_376d_414f != '\0') || (DAT_376d_414e != '\0')) || (DAT_376d_414d != '\0')) &&
       (DAT_376d_17cb == '\0')) {
      FUN_1c27_000a();
      FUN_1c27_029c(0);
      DAT_376d_17cb = '\x01';
    }
    if ((DAT_376d_414f != '\0') && (DAT_376d_17cd == '\0')) {
      FUN_20bc_05d6();
      DAT_376d_3678 = FUN_20bc_063a();
      DAT_376d_367a = FUN_20bc_066c();
      DAT_376d_17cd = '\x01';
    }
    if (((DAT_376d_414e == '\0') || (DAT_376d_3cc7 == '\0')) || (DAT_376d_17cc != '\0')) {
      if ((DAT_376d_414e == '\0') && (DAT_376d_17cc != '\0')) {
        FUN_20bc_0702();
        DAT_376d_17cc = '\0';
      }
    }
    else {
      iVar2 = FUN_1c27_0024();
      if (0 < iVar2) {
        DAT_376d_17cc = '\x01';
      }
    }
  }
  if (DAT_376d_414d != '\0') {
    FUN_1c27_00ae();
  }
  return;
}

