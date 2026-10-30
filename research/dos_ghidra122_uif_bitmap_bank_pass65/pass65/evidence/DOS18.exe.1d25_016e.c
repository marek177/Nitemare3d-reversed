
void __cdecl16far FUN_1d25_016e(uint param_1)

{
  byte *pbVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  DAT_376d_368c = (byte)param_1;
  uVar2 = param_1 & 0xff;
  if (*(char *)(uVar2 + 0x1c6a) == '\0') {
    *(undefined1 *)(uVar2 + 0x1c6a) = 1;
    FUN_1277_196c(param_1,uVar2 * 0x4b0,0x30b5);
    iVar3 = (uint)DAT_376d_368c * 0x200;
    *(int *)(iVar3 + 0x368e) = (uint)DAT_376d_368c * 0x4b0;
    *(undefined2 *)(iVar3 + 0x3690) = 0x30b5;
    iVar6 = 2;
    iVar3 = 1;
    do {
      iVar4 = ((uint)DAT_376d_368c * 0x80 + iVar3) * 4;
      pbVar1 = (byte *)((uint)DAT_376d_368c * 0x4b0 + iVar6);
      *(undefined2 *)(iVar4 + 0x368e) = pbVar1;
      *(undefined2 *)(iVar4 + 0x3690) = 0x30b5;
      iVar4 = (uint)*pbVar1 * ((int)(pbVar1[1] + 7) >> 3);
      if (iVar4 != 0) {
        iVar5 = 0;
        do {
          FUN_1fb7_00c6((uint)DAT_376d_368c * 0x4b0 + iVar6 + iVar5 + 2,0x30b5);
          iVar5 = iVar5 + 1;
        } while (iVar5 < iVar4);
      }
      iVar6 = iVar6 + iVar4 + 2;
      iVar3 = iVar3 + 1;
    } while (iVar3 < 0x80);
  }
  return;
}

