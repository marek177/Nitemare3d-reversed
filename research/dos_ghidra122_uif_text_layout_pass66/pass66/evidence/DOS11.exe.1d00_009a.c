
void __cdecl16far
FUN_1d00_009a(int param_1,undefined2 param_2,char *param_3,undefined2 param_4,undefined1 param_5,
             undefined2 param_6)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar3 = (uint)DAT_3395_362c * 0x200 + 0x362e;
  if (param_1 == -1) {
    param_1 = FUN_1d00_007c(param_3,param_4);
  }
  cVar1 = *param_3;
  while (cVar1 != '\0') {
    FUN_1155_09c6(param_1,param_2,CONCAT11(*param_3 >> 7,param_5),param_6,
                  *(undefined4 *)(*param_3 * 4 + iVar3));
    uVar2 = *(undefined4 *)(*param_3 * 4 + iVar3);
    param_1 = param_1 + *(byte *)((int)uVar2 + 1) + 1;
    param_3 = param_3 + 1;
    cVar1 = *param_3;
  }
  return;
}

