
void __cdecl16far FUN_1bdd_00b4(int param_1)

{
  char cVar1;
  int iVar2;
  
  if (param_1 == 0) {
    if (DAT_3360_3b66 == '\0') {
      DAT_3360_3fa7 = 0;
      DAT_3360_3fa5 = 0;
      DAT_3360_3fa6 = 0;
      return;
    }
    FUN_1bdd_0008();
    DAT_3360_16c1 = '\x01';
    iVar2 = FUN_1bdd_0022();
    cVar1 = FUN_206c_06a2();
    FUN_206c_05da();
    DAT_3360_351e = FUN_206c_063e();
    DAT_3360_3520 = FUN_206c_0670();
    DAT_3360_16c3 = '\x01';
    if (cVar1 == '\0') {
      DAT_3360_3fa5 = '\0';
    }
    if (iVar2 < 1) {
      DAT_3360_3b67 = '\0';
    }
    if ((DAT_3360_3fa6 == '\0') || (DAT_3360_3b67 == '\0')) {
      DAT_3360_16c2 = '\0';
    }
    else {
      DAT_3360_16c2 = '\x01';
    }
    if (DAT_3360_16c2 == '\0') {
      FUN_206c_0706();
    }
    if (cVar1 != '\0') {
      FUN_1bdd_0270(0);
    }
  }
  else {
    if (param_1 == 1) {
      if (DAT_3360_16c1 != '\0') {
        FUN_206c_0eba();
        if (DAT_3360_16c2 != '\0') {
          FUN_206c_0ee9();
          FUN_206c_0706();
        }
        FUN_206c_0067();
        DAT_3360_16c1 = '\0';
        DAT_3360_16c2 = '\0';
        DAT_3360_16c3 = '\0';
      }
      DAT_3360_3fa5 = 0;
      DAT_3360_3fa6 = 0;
      DAT_3360_3fa7 = 0;
      return;
    }
    if (param_1 != 2) {
      return;
    }
    if ((((DAT_3360_3fa7 != '\0') || (DAT_3360_3fa6 != '\0')) || (DAT_3360_3fa5 != '\0')) &&
       (DAT_3360_16c1 == '\0')) {
      FUN_1bdd_0008();
      FUN_1bdd_0270(0);
      DAT_3360_16c1 = '\x01';
    }
    if ((DAT_3360_3fa7 != '\0') && (DAT_3360_16c3 == '\0')) {
      FUN_206c_05da();
      DAT_3360_351e = FUN_206c_063e();
      DAT_3360_3520 = FUN_206c_0670();
      DAT_3360_16c3 = '\x01';
    }
    if (((DAT_3360_3fa6 == '\0') || (DAT_3360_3b67 == '\0')) || (DAT_3360_16c2 != '\0')) {
      if ((DAT_3360_3fa6 == '\0') && (DAT_3360_16c2 != '\0')) {
        FUN_206c_0706();
        DAT_3360_16c2 = '\0';
      }
    }
    else {
      iVar2 = FUN_1bdd_0022();
      if (0 < iVar2) {
        DAT_3360_16c2 = '\x01';
      }
    }
  }
  if (DAT_3360_3fa5 != '\0') {
    FUN_1bdd_0082();
  }
  return;
}

