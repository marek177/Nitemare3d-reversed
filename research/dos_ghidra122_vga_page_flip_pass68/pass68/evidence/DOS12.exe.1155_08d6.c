
void __cdecl16far
FUN_1155_08d6(uint param_1,uint param_2,int param_3,int param_4,undefined1 param_5,int param_6)

{
  undefined2 uVar1;
  byte bVar2;
  int iVar3;
  undefined1 *puVar4;
  bool bVar5;
  undefined1 *local_4;
  
  if ((param_3 != 0) && (param_4 != 0)) {
    uVar1 = DAT_339b_012c;
    if (param_6 != 0) {
      uVar1 = DAT_339b_012a;
    }
    local_4 = (undefined1 *)((param_2 & 0xff) * 0x50 + (param_1 >> 2));
    out(0x3c4,2);
    bVar2 = (byte)param_1 & 3;
    bVar2 = '\x11' << bVar2 | 0x11U >> 8 - bVar2;
    out(0x3c5,bVar2);
    do {
      iVar3 = param_4;
      puVar4 = local_4;
      do {
        *puVar4 = param_5;
        puVar4 = puVar4 + 0x50;
        iVar3 = iVar3 + -1;
      } while (iVar3 != 0);
      bVar5 = (char)bVar2 < '\0';
      bVar2 = bVar2 << 1 | bVar5;
      out(0x3c5,bVar2);
      if (bVar5) {
        local_4 = local_4 + 1;
      }
      param_3 = param_3 + -1;
    } while (param_3 != 0);
  }
  return;
}

