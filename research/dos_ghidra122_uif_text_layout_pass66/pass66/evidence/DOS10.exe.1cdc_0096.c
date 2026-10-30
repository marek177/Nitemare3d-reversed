
void __cdecl16far
FUN_1cdc_0096(int param_1,undefined2 param_2,char *param_3,undefined2 param_4,undefined1 param_5,
             undefined2 param_6)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar3 = (uint)DAT_3360_3532 * 0x200 + 0x3534;
  if (param_1 == -1) {
    param_1 = FUN_1cdc_0078(param_3,param_4);
  }
  cVar1 = *param_3;
  while (cVar1 != '\0') {
    switchD_1000:8d17::caseD_6
              (param_1,param_2,CONCAT11(*param_3 >> 7,param_5),param_6,
               *(undefined4 *)(*param_3 * 4 + iVar3));
    uVar2 = *(undefined4 *)(*param_3 * 4 + iVar3);
    param_1 = param_1 + *(byte *)((int)uVar2 + 1) + 1;
    param_3 = param_3 + 1;
    cVar1 = *param_3;
  }
  return;
}

