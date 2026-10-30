
int __cdecl16far FUN_1cdc_000e(char param_1)

{
  undefined4 uVar1;
  
  uVar1 = *(undefined4 *)(((uint)DAT_3360_3532 * 0x80 + (int)param_1) * 4 + 0x3534);
  return *(byte *)((int)uVar1 + 1) + 1;
}

