
void __cdecl16far FUN_1817_1d88(byte param_1)

{
  char cVar1;
  char cVar2;
  
  cVar2 = DAT_3395_410b;
  cVar1 = DAT_3395_410a;
  if (DAT_3395_40ae == '\0') {
    if ((DAT_3395_40f2 != '\0') && ((param_1 & 0xf) == 0)) {
      DAT_3395_410b = DAT_3395_410b + -1;
    }
    if ((DAT_3395_40f3 != '\0') && ((param_1 & 7) == 0)) {
      DAT_3395_410a = DAT_3395_410a + -1;
    }
    if ((DAT_3395_40f2 != '\0') && (DAT_3395_410b == '\0')) {
      DAT_3395_40f2 = '\0';
      DAT_3395_410b = '\0';
      FUN_1817_1412(3);
    }
    if ((DAT_3395_40f3 != '\0') && (DAT_3395_410a == '\0')) {
      DAT_3395_40f3 = '\0';
      DAT_3395_410a = '\0';
      FUN_1817_1412(3);
    }
    if (cVar1 != DAT_3395_410a) {
      FUN_1817_05ca();
    }
    if (cVar2 != DAT_3395_410b) {
      FUN_1817_05ca();
    }
  }
  return;
}

