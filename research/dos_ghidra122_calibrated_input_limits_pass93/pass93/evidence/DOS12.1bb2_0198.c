
void __cdecl16far FUN_1bb2_0198(void)

{
  uint uVar1;
  uint uVar2;
  ulong uVar3;
  int iVar4;
  int iVar5;
  undefined4 in_EDX;
  ulong uVar6;
  int iVar7;
  undefined4 uStack_10;
  undefined4 local_6;
  
  FUN_1bb2_0002();
  FUN_1bb2_0002();
  FUN_1bb2_0154();
  uVar1 = FUN_1bb2_0092();
  iVar4 = (int)in_EDX;
  iVar7 = 10;
  do {
    FUN_1bb2_0154();
    iVar5 = (int)in_EDX;
    iVar7 = iVar7 + -1;
  } while (iVar7 != 0);
  uVar2 = FUN_1bb2_0092();
  uStack_10 = CONCAT22((iVar5 - iVar4) - (uint)(uVar2 < uVar1),uVar2 - uVar1);
  local_6 = uStack_10 / 10;
  DAT_339b_44b2 = (uint)local_6;
  uVar1 = (uint)(local_6 >> 0x10);
  uVar6 = (ulong)uVar1;
  uVar3 = local_6;
  if ((uVar1 == 0) && (DAT_339b_44b2 < 0x41)) {
    uVar1 = FUN_1bb2_0092();
    iVar4 = (int)uVar6;
    iVar7 = 10;
    do {
      FUN_1bb2_0154();
      FUN_1155_0458();
      iVar5 = (int)uVar6;
      iVar7 = iVar7 + -1;
    } while (iVar7 != 0);
    uVar2 = FUN_1bb2_0092();
    uStack_10 = CONCAT22((iVar5 - iVar4) - (uint)(uVar2 < uVar1),uVar2 - uVar1);
    local_6 = uStack_10 / 10;
    uVar3 = CONCAT22((int)(local_6 >> 0x10),DAT_339b_44b2);
  }
  DAT_339b_44b2 = (uint)uVar3;
  DAT_339b_449c = 0;
  DAT_339b_44b4 = (uint)local_6;
  if ((int)(uVar3 >> 0x10) == 0 && (uint)local_6 == 0) {
    FUN_1f8f_0002();
  }
  uVar1 = (uint)(CONCAT12((local_6 & 0x10000) != 0,(uint)local_6) >> 1);
  uStack_10 = CONCAT22((local_6._2_2_ >> 1) + (uint)(0xfc17 < uVar1),uVar1 + 1000);
  DAT_339b_44b6 = (int)(uStack_10 / local_6);
  uVar1 = (uint)(1000 / (long)DAT_339b_3c62);
  uVar2 = (int)uVar1 >> 0xf;
  if ((uVar2 <= local_6._2_2_) && ((uVar2 < local_6._2_2_ || (uVar1 < (uint)local_6)))) {
    uVar2 = local_6._2_2_;
    uVar1 = (uint)local_6;
  }
  local_6 = CONCAT22(uVar2,uVar1);
  uVar2 = uVar2 + (0xfffd < uVar1);
  DAT_339b_44b8._0_2_ =
       (int)(CONCAT12((uVar2 >> 1 & 1) != 0,(int)(CONCAT12((uVar2 & 1) != 0,uVar1 + 2) >> 1)) >> 1);
  if ((uVar2 >> 2 == 0) && ((int)DAT_339b_44b8 == 0)) {
    DAT_339b_44b8._0_2_ = 1;
  }
  uVar3 = (local_6 * 0x168 + 0x578) / 0xaf0;
  if (uVar3 == 0) {
    uVar3 = 1;
  }
  DAT_339b_44b8._2_2_ = (int)uVar3;
  DAT_339b_44bc = (int)DAT_339b_44b8 * 2;
  return;
}

