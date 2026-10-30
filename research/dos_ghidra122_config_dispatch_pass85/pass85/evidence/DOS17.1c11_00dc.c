
void __cdecl16far FUN_1c11_00dc(int param_1)

{
  char cVar1;
  int iVar2;
  
  if (param_1 == 0) {
    if (DAT_3754_3c36 == '\0') {
      DAT_3754_40bf = 0;
      DAT_3754_40bd = 0;
      DAT_3754_40be = 0;
      return;
    }
    FUN_1c11_0006();
    DAT_3754_179d = '\x01';
    iVar2 = FUN_1c11_0020();
    cVar1 = FUN_20a2_06aa();
    FUN_20a2_05e2();
    DAT_3754_35ec = FUN_20a2_0646();
    DAT_3754_35ee = FUN_20a2_0678();
    DAT_3754_179f = '\x01';
    if (cVar1 == '\0') {
      DAT_3754_40bd = '\0';
    }
    if (iVar2 < 1) {
      DAT_3754_3c37 = '\0';
    }
    if ((DAT_3754_40be == '\0') || (DAT_3754_3c37 == '\0')) {
      DAT_3754_179e = '\0';
    }
    else {
      DAT_3754_179e = '\x01';
    }
    if (DAT_3754_179e == '\0') {
      FUN_20a2_070e();
    }
    if (cVar1 != '\0') {
      FUN_1c11_0298(0);
    }
  }
  else {
    if (param_1 == 1) {
      if (DAT_3754_179d != '\0') {
        FUN_20a2_0ec2();
        if (DAT_3754_179e != '\0') {
          FUN_20a2_0ef1();
          FUN_20a2_070e();
        }
        FUN_20a2_006f();
        DAT_3754_179d = '\0';
        DAT_3754_179e = '\0';
        DAT_3754_179f = '\0';
      }
      DAT_3754_40bd = 0;
      DAT_3754_40be = 0;
      DAT_3754_40bf = 0;
      return;
    }
    if (param_1 != 2) {
      return;
    }
    if ((((DAT_3754_40bf != '\0') || (DAT_3754_40be != '\0')) || (DAT_3754_40bd != '\0')) &&
       (DAT_3754_179d == '\0')) {
      FUN_1c11_0006();
      FUN_1c11_0298(0);
      DAT_3754_179d = '\x01';
    }
    if ((DAT_3754_40bf != '\0') && (DAT_3754_179f == '\0')) {
      FUN_20a2_05e2();
      DAT_3754_35ec = FUN_20a2_0646();
      DAT_3754_35ee = FUN_20a2_0678();
      DAT_3754_179f = '\x01';
    }
    if (((DAT_3754_40be == '\0') || (DAT_3754_3c37 == '\0')) || (DAT_3754_179e != '\0')) {
      if ((DAT_3754_40be == '\0') && (DAT_3754_179e != '\0')) {
        FUN_20a2_070e();
        DAT_3754_179e = '\0';
      }
    }
    else {
      iVar2 = FUN_1c11_0020();
      if (0 < iVar2) {
        DAT_3754_179e = '\x01';
      }
    }
  }
  if (DAT_3754_40bd != '\0') {
    FUN_1c11_00aa();
  }
  return;
}

