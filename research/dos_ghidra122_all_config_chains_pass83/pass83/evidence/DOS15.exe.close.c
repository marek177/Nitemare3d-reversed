
void FUN_21c7_1bba(undefined2 param_1,uint param_2)

{
  code *pcVar1;
  bool bVar2;
  
  bVar2 = param_2 < DAT_374a_20e8;
  if (bVar2) {
    pcVar1 = (code *)swi(0x21);
    (*pcVar1)();
    if (!bVar2) {
      ((undefined1 *)&DAT_374a_20ea)[param_2] = 0;
    }
  }
  FUN_21c7_05a6();
  return;
}

