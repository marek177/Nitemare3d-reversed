
void __cdecl16far FUN_1155_0a3c(undefined1 param_1,int param_2)

{
  undefined2 *puVar1;
  undefined2 uVar2;
  char *pcVar3;
  undefined2 *puVar4;
  
  out(0x3c4,0xf02);
  uVar2 = DAT_3360_012c;
  if (param_2 != 0) {
    uVar2 = DAT_3360_012a;
  }
  puVar4 = (undefined2 *)0x0;
  for (pcVar3 = (char *)s_Copyright_1992__David_P_Gray__Gr_3360_1f3f + 1; pcVar3 != (char *)0x0;
      pcVar3 = pcVar3 + -1) {
    puVar1 = puVar4;
    puVar4 = puVar4 + 1;
    *puVar1 = CONCAT11(param_1,param_1);
  }
  return;
}

