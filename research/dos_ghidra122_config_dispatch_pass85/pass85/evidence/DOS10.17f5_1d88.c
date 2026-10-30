
void __cdecl16far FUN_17f5_1d88(byte param_1)

{
  char cVar1;
  char cVar2;
  
  cVar2 = DAT_3360_4005;
  cVar1 = DAT_3360_4004;
  if (DAT_3360_3fa8 == '\0') {
    if ((DAT_3360_3fec != '\0') && ((param_1 & 0xf) == 0)) {
      DAT_3360_4005 = DAT_3360_4005 + -1;
    }
    if ((DAT_3360_3fed != '\0') && ((param_1 & 7) == 0)) {
      DAT_3360_4004 = DAT_3360_4004 + -1;
    }
    if ((DAT_3360_3fec != '\0') && (DAT_3360_4005 == '\0')) {
      DAT_3360_3fec = '\0';
      DAT_3360_4005 = '\0';
      FUN_17f5_1412(3);
    }
    if ((DAT_3360_3fed != '\0') && (DAT_3360_4004 == '\0')) {
      DAT_3360_3fed = '\0';
      DAT_3360_4004 = '\0';
      FUN_17f5_1412(3);
    }
    if (cVar1 != DAT_3360_4004) {
      FUN_17f5_05ca();
    }
    if (cVar2 != DAT_3360_4005) {
      FUN_17f5_05ca();
    }
  }
  return;
}

