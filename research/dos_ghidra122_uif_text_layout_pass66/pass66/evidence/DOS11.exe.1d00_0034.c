
int __cdecl16far FUN_1d00_0034(char *param_1,undefined2 param_2)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  undefined2 unaff_SS;
  
  iVar3 = 0;
  cVar1 = *param_1;
  while (cVar1 != '\0') {
    uVar2 = *(undefined4 *)(*param_1 * 4 + (uint)DAT_3395_362c * 0x200 + 0x362e);
    iVar3 = iVar3 + *(byte *)((int)uVar2 + 1) + 1;
    param_1 = param_1 + 1;
    cVar1 = *param_1;
  }
  return iVar3;
}

