
void __cdecl16far FUN_1826_1db4(byte param_1)

{
  char cVar1;
  char cVar2;
  
  cVar2 = DAT_3754_411d;
  cVar1 = DAT_3754_411c;
  if (DAT_3754_40c0 == '\0') {
    if ((DAT_3754_4104 != '\0') && ((param_1 & 0xf) == 0)) {
      DAT_3754_411d = DAT_3754_411d + -1;
    }
    if ((DAT_3754_4105 != '\0') && ((param_1 & 7) == 0)) {
      DAT_3754_411c = DAT_3754_411c + -1;
    }
    if ((DAT_3754_4104 != '\0') && (DAT_3754_411d == '\0')) {
      DAT_3754_4104 = '\0';
      DAT_3754_411d = '\0';
      FUN_1826_143e(3);
    }
    if ((DAT_3754_4105 != '\0') && (DAT_3754_411c == '\0')) {
      DAT_3754_4105 = '\0';
      DAT_3754_411c = '\0';
      FUN_1826_143e(3);
    }
    if (cVar1 != DAT_3754_411c) {
      FUN_1826_05d4();
    }
    if (cVar2 != DAT_3754_411d) {
      FUN_1826_05d4();
    }
  }
  return;
}

