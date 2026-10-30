
void FUN_21ea_1bba(undefined2 param_1,uint param_2)

{
  code *pcVar1;
  bool bVar2;
  
  bVar2 = param_2 < DAT_376d_2126;
  if (bVar2) {
    pcVar1 = (code *)swi(0x21);
    (*pcVar1)();
    if (!bVar2) {
      ((undefined1 *)&DAT_376d_2128)[param_2] = 0;
    }
  }
  FUN_21ea_05a6();
  return;
}

