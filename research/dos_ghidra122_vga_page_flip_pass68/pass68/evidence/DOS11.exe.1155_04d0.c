
/* WARNING: Restarted to delay deadcode elimination for space: stack */

int __cdecl16far
FUN_1155_04d0(int param_1,undefined2 param_2,int param_3,uint param_4,uint param_5,int param_6,
             int param_7)

{
  uint uVar1;
  int iVar2;
  undefined2 uVar3;
  int iVar4;
  uint uVar5;
  byte bVar6;
  int iVar7;
  int iVar8;
  byte bVar9;
  byte *pbVar10;
  byte *pbVar11;
  undefined2 unaff_SS;
  bool bVar12;
  undefined2 local_a;
  int local_8;
  
  uVar3 = DAT_3395_012c;
  uVar1 = local_a >> 8;
  local_a = local_a & 0xff00;
  iVar7 = (param_5 - DAT_3395_44ae) * 2;
  iVar4 = iVar7 + 1;
  if ((int)param_5 < DAT_3395_44aa) {
    param_5 = param_5 - iVar4;
    iVar8 = iVar7 + 2;
  }
  else {
    local_a = CONCAT11((char)uVar1,1);
    param_5 = DAT_3395_44a8;
    iVar8 = DAT_3395_44a2;
  }
  uVar1 = *(uint *)(iVar4 * 4 + 0x2644);
  iVar2 = *(int *)(iVar4 * 4 + 0x2646);
  pbVar10 = (byte *)(param_1 + param_3 * 0x40);
  uVar5 = 0;
  if (local_a != 0) {
    pbVar10 = pbVar10 + (byte)((undefined1 *)&DAT_3395_2e45)[iVar7];
    uVar5 = *(uint *)(iVar4 * 2 + 0x3044);
  }
  pbVar11 = (byte *)((param_5 & 0xff) * 0x50 + (param_4 >> 2));
  out(0x3c4,2);
  bVar6 = (byte)param_4 & 3;
  bVar6 = '\x11' << bVar6 | 0x11U >> 8 - bVar6;
  local_8 = 1;
  if ((0x40 < iVar4) && ((int)param_4 <= param_7)) {
    iVar7 = 1;
    bVar9 = bVar6;
    if ((char)local_a != '\0') {
      iVar7 = 3;
    }
    do {
      bVar12 = (char)bVar9 < '\0';
      bVar9 = bVar9 << 1 | bVar12;
      if (bVar12) break;
      bVar6 = bVar6 | bVar9;
      local_8 = local_8 + 1;
      iVar7 = iVar7 + -1;
    } while (iVar7 != 0);
  }
  out(0x3c5,bVar6);
  if (param_6 == 0) {
    do {
      *pbVar11 = *pbVar10;
      pbVar11 = pbVar11 + 0x50;
      bVar12 = CARRY2(uVar5,uVar1);
      uVar5 = uVar5 + uVar1;
      pbVar10 = pbVar10 + (uint)bVar12 + iVar2;
      iVar8 = iVar8 + -1;
    } while (iVar8 != 0);
  }
  else {
    *(int *)0x3446 = iVar2;
    do {
      *pbVar11 = *(byte *)(ulong)(*pbVar10 + 0xd158);
      pbVar11 = pbVar11 + 0x50;
      bVar12 = CARRY2(uVar5,uVar1);
      uVar5 = uVar5 + uVar1;
      pbVar10 = pbVar10 + (uint)bVar12 + *(int *)0x3446;
      iVar8 = iVar8 + -1;
    } while (iVar8 != 0);
  }
  return local_8;
}

