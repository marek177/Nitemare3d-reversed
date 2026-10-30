
void FUN_21d1_1bb6(undefined2 param_1,uint param_2)

{
  code *pcVar1;
  bool bVar2;
  
  bVar2 = param_2 < DAT_3754_20ec;
  if (bVar2) {
    pcVar1 = (code *)swi(0x21);
    (*pcVar1)();
    if (!bVar2) {
      ((undefined1 *)&DAT_3754_20ee)[param_2] = 0;
    }
  }
  FUN_21d1_05a2();
  return;
}

