
void __cdecl16far FUN_1d05_016e(uint param_1)

{
  byte *pbVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  DAT_374a_35fc = (byte)param_1;
  uVar2 = param_1 & 0xff;
  if (*(char *)(uVar2 + 0x1c38) == '\0') {
    *(undefined1 *)(uVar2 + 0x1c38) = 1;
    FUN_1277_1790(param_1,uVar2 * 0x4b0,0x3092);
    iVar3 = (uint)DAT_374a_35fc * 0x200;
    *(int *)(iVar3 + 0x35fe) = (uint)DAT_374a_35fc * 0x4b0;
    *(undefined2 *)(iVar3 + 0x3600) = 0x3092;
    iVar6 = 2;
    iVar3 = 1;
    do {
      iVar4 = ((uint)DAT_374a_35fc * 0x80 + iVar3) * 4;
      pbVar1 = (byte *)((uint)DAT_374a_35fc * 0x4b0 + iVar6);
      *(undefined2 *)(iVar4 + 0x35fe) = pbVar1;
      *(undefined2 *)(iVar4 + 0x3600) = 0x3092;
      iVar4 = (uint)*pbVar1 * ((int)(pbVar1[1] + 7) >> 3);
      if (iVar4 != 0) {
        iVar5 = 0;
        do {
          FUN_1f94_00c6((uint)DAT_374a_35fc * 0x4b0 + iVar6 + iVar5 + 2,0x3092);
          iVar5 = iVar5 + 1;
        } while (iVar5 < iVar4);
      }
      iVar6 = iVar6 + iVar4 + 2;
      iVar3 = iVar3 + 1;
    } while (iVar3 < 0x80);
  }
  return;
}

