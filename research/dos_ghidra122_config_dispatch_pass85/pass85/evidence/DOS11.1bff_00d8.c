
void __cdecl16far FUN_1bff_00d8(int param_1)

{
  char cVar1;
  int iVar2;
  
  if (param_1 == 0) {
    if (DAT_3395_3c66 == '\0') {
      DAT_3395_40ad = 0;
      DAT_3395_40ab = 0;
      DAT_3395_40ac = 0;
      return;
    }
    FUN_1bff_0002();
    DAT_3395_17a3 = '\x01';
    iVar2 = FUN_1bff_001c();
    cVar1 = FUN_208d_06aa();
    FUN_208d_05e2();
    DAT_3395_3618 = FUN_208d_0646();
    DAT_3395_361a = FUN_208d_0678();
    DAT_3395_17a5 = '\x01';
    if (cVar1 == '\0') {
      DAT_3395_40ab = '\0';
    }
    if (iVar2 < 1) {
      DAT_3395_3c67 = '\0';
    }
    if ((DAT_3395_40ac == '\0') || (DAT_3395_3c67 == '\0')) {
      DAT_3395_17a4 = '\0';
    }
    else {
      DAT_3395_17a4 = '\x01';
    }
    if (DAT_3395_17a4 == '\0') {
      FUN_208d_070e();
    }
    if (cVar1 != '\0') {
      FUN_1bff_0294(0);
    }
  }
  else {
    if (param_1 == 1) {
      if (DAT_3395_17a3 != '\0') {
        FUN_208d_0ec2();
        if (DAT_3395_17a4 != '\0') {
          FUN_208d_0ef1();
          FUN_208d_070e();
        }
        FUN_208d_006f();
        DAT_3395_17a3 = '\0';
        DAT_3395_17a4 = '\0';
        DAT_3395_17a5 = '\0';
      }
      DAT_3395_40ab = 0;
      DAT_3395_40ac = 0;
      DAT_3395_40ad = 0;
      return;
    }
    if (param_1 != 2) {
      return;
    }
    if ((((DAT_3395_40ad != '\0') || (DAT_3395_40ac != '\0')) || (DAT_3395_40ab != '\0')) &&
       (DAT_3395_17a3 == '\0')) {
      FUN_1bff_0002();
      FUN_1bff_0294(0);
      DAT_3395_17a3 = '\x01';
    }
    if ((DAT_3395_40ad != '\0') && (DAT_3395_17a5 == '\0')) {
      FUN_208d_05e2();
      DAT_3395_3618 = FUN_208d_0646();
      DAT_3395_361a = FUN_208d_0678();
      DAT_3395_17a5 = '\x01';
    }
    if (((DAT_3395_40ac == '\0') || (DAT_3395_3c67 == '\0')) || (DAT_3395_17a4 != '\0')) {
      if ((DAT_3395_40ac == '\0') && (DAT_3395_17a4 != '\0')) {
        FUN_208d_070e();
        DAT_3395_17a4 = '\0';
      }
    }
    else {
      iVar2 = FUN_1bff_001c();
      if (0 < iVar2) {
        DAT_3395_17a4 = '\x01';
      }
    }
  }
  if (DAT_3395_40ab != '\0') {
    FUN_1bff_00a6();
  }
  return;
}

