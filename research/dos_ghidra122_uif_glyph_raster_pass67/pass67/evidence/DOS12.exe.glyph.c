
uint __cdecl16far
FUN_1155_09c6(uint param_1,uint param_2,undefined1 param_3,int param_4,undefined2 *param_5)

{
  byte *pbVar1;
  uint uVar2;
  undefined2 uVar3;
  uint uVar4;
  byte bVar5;
  sbyte sVar6;
  uint uVar7;
  undefined1 uVar8;
  char cVar9;
  byte bVar10;
  byte *pbVar11;
  undefined1 *puVar12;
  undefined1 *puVar13;
  
  uVar3 = DAT_339b_012c;
  if (param_4 != 0) {
    uVar3 = DAT_339b_012a;
  }
  puVar12 = (undefined1 *)((param_2 & 0xff) * 0x50 + (param_1 >> 2));
  out(0x3c4,2);
  bVar5 = (byte)param_1 & 3;
  out(0x3c5,'\x11' << bVar5 | 0x11U >> 8 - bVar5);
  uVar7 = CONCAT11(param_3,(byte)param_1) & 0xff03;
  pbVar11 = (byte *)((undefined2 *)param_5 + 1);
  cVar9 = (char)*param_5;
  bVar10 = (byte)((char)((uint)*param_5 >> 8) + 7U) >> 3;
  bVar5 = bVar10;
  puVar13 = puVar12;
  do {
    do {
      pbVar1 = pbVar11;
      pbVar11 = pbVar11 + 1;
      sVar6 = (sbyte)uVar7;
      uVar4 = (uint)*pbVar1 << sVar6 | (uint)(*pbVar1 >> 0x10 - sVar6);
      out(0x3c5,(char)uVar4);
      uVar8 = (undefined1)(uVar7 >> 8);
      *puVar12 = uVar8;
      uVar2 = uVar4 >> 4;
      out(0x3c5,(char)uVar2);
      puVar12[1] = uVar8;
      puVar12 = puVar12 + 2;
      uVar4 = (uVar2 | uVar4 << 0xc) >> 4;
      out(0x3c5,(char)uVar4);
      *puVar12 = uVar8;
      bVar5 = bVar5 - 1;
    } while (bVar5 != 0);
    puVar12 = puVar13 + 0x50;
    cVar9 = cVar9 + -1;
    bVar5 = bVar10;
    puVar13 = puVar12;
  } while (cVar9 != '\0');
  return uVar4 | uVar2 << 0xc;
}

