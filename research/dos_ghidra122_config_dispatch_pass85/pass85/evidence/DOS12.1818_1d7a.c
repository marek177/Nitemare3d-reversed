
void __cdecl16far FUN_1818_1d7a(byte param_1)

{
  char cVar1;
  char cVar2;
  
  cVar2 = DAT_339b_410b;
  cVar1 = DAT_339b_410a;
  if (DAT_339b_40ae == '\0') {
    if ((DAT_339b_40f2 != '\0') && ((param_1 & 0xf) == 0)) {
      DAT_339b_410b = DAT_339b_410b + -1;
    }
    if ((DAT_339b_40f3 != '\0') && ((param_1 & 7) == 0)) {
      DAT_339b_410a = DAT_339b_410a + -1;
    }
    if ((DAT_339b_40f2 != '\0') && (DAT_339b_410b == '\0')) {
      DAT_339b_40f2 = '\0';
      DAT_339b_410b = '\0';
      FUN_1818_1404(3);
    }
    if ((DAT_339b_40f3 != '\0') && (DAT_339b_410a == '\0')) {
      DAT_339b_40f3 = '\0';
      DAT_339b_410a = '\0';
      FUN_1818_1404(3);
    }
    if (cVar1 != DAT_339b_410a) {
      FUN_1818_05c6();
    }
    if (cVar2 != DAT_339b_410b) {
      FUN_1818_05c6();
    }
  }
  return;
}

