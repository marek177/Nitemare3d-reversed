
void __cdecl16far FUN_1bff_00da(int param_1)

{
  char cVar1;
  int iVar2;
  
  if (param_1 == 0) {
    if (DAT_339b_3c66 == '\0') {
      DAT_339b_40ad = 0;
      DAT_339b_40ab = 0;
      DAT_339b_40ac = 0;
      return;
    }
    FUN_1bff_0004();
    DAT_339b_1795 = '\x01';
    iVar2 = FUN_1bff_001e();
    cVar1 = FUN_2093_06aa();
    FUN_2093_05e2();
    DAT_339b_3614 = FUN_2093_0646();
    DAT_339b_3616 = FUN_2093_0678();
    DAT_339b_1797 = '\x01';
    if (cVar1 == '\0') {
      DAT_339b_40ab = '\0';
    }
    if (iVar2 < 1) {
      DAT_339b_3c67 = '\0';
    }
    if ((DAT_339b_40ac == '\0') || (DAT_339b_3c67 == '\0')) {
      DAT_339b_1796 = '\0';
    }
    else {
      DAT_339b_1796 = '\x01';
    }
    if (DAT_339b_1796 == '\0') {
      FUN_2093_070e();
    }
    if (cVar1 != '\0') {
      FUN_1bff_0296(0);
    }
  }
  else {
    if (param_1 == 1) {
      if (DAT_339b_1795 != '\0') {
        FUN_2093_0ec2();
        if (DAT_339b_1796 != '\0') {
          FUN_2093_0ef1();
          FUN_2093_070e();
        }
        FUN_2093_006f();
        DAT_339b_1795 = '\0';
        DAT_339b_1796 = '\0';
        DAT_339b_1797 = '\0';
      }
      DAT_339b_40ab = 0;
      DAT_339b_40ac = 0;
      DAT_339b_40ad = 0;
      return;
    }
    if (param_1 != 2) {
      return;
    }
    if ((((DAT_339b_40ad != '\0') || (DAT_339b_40ac != '\0')) || (DAT_339b_40ab != '\0')) &&
       (DAT_339b_1795 == '\0')) {
      FUN_1bff_0004();
      FUN_1bff_0296(0);
      DAT_339b_1795 = '\x01';
    }
    if ((DAT_339b_40ad != '\0') && (DAT_339b_1797 == '\0')) {
      FUN_2093_05e2();
      DAT_339b_3614 = FUN_2093_0646();
      DAT_339b_3616 = FUN_2093_0678();
      DAT_339b_1797 = '\x01';
    }
    if (((DAT_339b_40ac == '\0') || (DAT_339b_3c67 == '\0')) || (DAT_339b_1796 != '\0')) {
      if ((DAT_339b_40ac == '\0') && (DAT_339b_1796 != '\0')) {
        FUN_2093_070e();
        DAT_339b_1796 = '\0';
      }
    }
    else {
      iVar2 = FUN_1bff_001e();
      if (0 < iVar2) {
        DAT_339b_1796 = '\x01';
      }
    }
  }
  if (DAT_339b_40ab != '\0') {
    FUN_1bff_00a8();
  }
  return;
}

