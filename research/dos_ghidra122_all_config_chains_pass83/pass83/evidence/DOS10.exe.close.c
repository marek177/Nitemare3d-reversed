
void FUN_219b_1cb2(undefined2 param_1,uint param_2)

{
  code *pcVar1;
  bool bVar2;
  
  bVar2 = param_2 < DAT_3360_2022;
  if (bVar2) {
    pcVar1 = (code *)swi(0x21);
    (*pcVar1)();
    if (!bVar2) {
      ((undefined1 *)&DAT_3360_2024)[param_2] = 0;
    }
  }
  FUN_219b_059a();
  return;
}

