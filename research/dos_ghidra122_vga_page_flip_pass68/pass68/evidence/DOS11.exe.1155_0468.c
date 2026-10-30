
void __cdecl16far FUN_1155_0468(uint param_1,uint param_2,uint param_3,uint param_4)

{
  undefined2 *puVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  uint uVar4;
  uint uVar5;
  undefined2 *puVar6;
  undefined2 *puVar7;
  
  uVar2 = DAT_3395_012c;
  puVar6 = (undefined2 *)((param_2 & 0xff) * 0x50 + (param_1 >> 2));
  out(0x3c4,2);
  out(0x3c5,0xf);
  param_4 = param_4 >> 1;
  uVar3 = CONCAT11(DAT_3395_61d7,DAT_3395_61d7);
  uVar5 = param_4;
  do {
    puVar7 = puVar6;
    for (uVar4 = param_3 >> 3; uVar4 != 0; uVar4 = uVar4 - 1) {
      puVar1 = puVar7;
      puVar7 = puVar7 + 1;
      *puVar1 = uVar3;
    }
    puVar6 = puVar6 + 0x28;
    uVar5 = uVar5 - 1;
  } while (uVar5 != 0);
  uVar3 = CONCAT11(DAT_3395_61d6,DAT_3395_61d6);
  do {
    puVar7 = puVar6;
    for (uVar5 = param_3 >> 3; uVar5 != 0; uVar5 = uVar5 - 1) {
      puVar1 = puVar7;
      puVar7 = puVar7 + 1;
      *puVar1 = uVar3;
    }
    puVar6 = puVar6 + 0x28;
    param_4 = param_4 - 1;
  } while (param_4 != 0);
  return;
}

