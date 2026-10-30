
void __cdecl16far FUN_1156_0a3a(undefined1 param_1,int param_2)

{
  undefined2 *puVar1;
  undefined2 uVar2;
  char *pcVar3;
  undefined2 *puVar4;
  
  out(0x3c4,0xf02);
  uVar2 = DAT_3754_012e;
  if (param_2 != 0) {
    uVar2 = DAT_3754_012c;
  }
  puVar4 = (undefined2 *)0x0;
  for (pcVar3 = (char *)s_About_to__s_game____s__Press_ESC_3754_1f2e + 0x12; pcVar3 != (char *)0x0;
      pcVar3 = pcVar3 + -1) {
    puVar1 = puVar4;
    puVar4 = puVar4 + 1;
    *puVar1 = CONCAT11(param_1,param_1);
  }
  return;
}

