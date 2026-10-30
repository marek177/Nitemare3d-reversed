
void __cdecl16far FUN_1155_0032(void)

{
  long lVar1;
  int iVar2;
  int iVar3;
  undefined2 *puVar4;
  long lStack_12;
  undefined4 local_6;
  
  local_6 = 1;
  puVar4 = (undefined2 *)&DAT_339b_3042;
  do {
    iVar2 = (uint)local_6 - DAT_339b_44a2;
    iVar3 = (local_6._2_2_ - ((int)DAT_339b_44a2 >> 0xf)) - (uint)((uint)local_6 < DAT_339b_44a2);
    if ((iVar3 < 1) && (iVar3 < 0)) {
      iVar2 = 0;
    }
    lStack_12 = (ulong)(uint)(iVar2 << 6) << 0x10;
    lVar1 = lStack_12 / local_6 >> 1;
    *(undefined1 *)((uint)local_6 + 0x2e40) = (char)((ulong)lVar1 >> 0x10);
    *puVar4 = (int)lVar1;
    puVar4 = puVar4 + 1;
    local_6 = local_6 + 1;
  } while (puVar4 < (undefined2 *)&DAT_339b_3440);
  return;
}

