
void __cdecl16far FUN_1bda_019e(void)

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
  
  FUN_1bda_0008();
  FUN_1bda_0008();
  FUN_1bda_015a();
  uVar1 = FUN_1bda_0098();
  iVar4 = (int)in_EDX;
  iVar7 = 10;
  do {
    FUN_1bda_015a();
    iVar5 = (int)in_EDX;
    iVar7 = iVar7 + -1;
  } while (iVar7 != 0);
  uVar2 = FUN_1bda_0098();
  uStack_10 = CONCAT22((iVar5 - iVar4) - (uint)(uVar2 < uVar1),uVar2 - uVar1);
  local_6 = uStack_10 / 10;
  DAT_376d_4554 = (uint)local_6;
  uVar1 = (uint)(local_6 >> 0x10);
  uVar6 = (ulong)uVar1;
  uVar3 = local_6;
  if ((uVar1 == 0) && (DAT_376d_4554 < 0x41)) {
    uVar1 = FUN_1bda_0098();
    iVar4 = (int)uVar6;
    iVar7 = 10;
    do {
      FUN_1bda_015a();
      FUN_1156_0456();
      iVar5 = (int)uVar6;
      iVar7 = iVar7 + -1;
    } while (iVar7 != 0);
    uVar2 = FUN_1bda_0098();
    uStack_10 = CONCAT22((iVar5 - iVar4) - (uint)(uVar2 < uVar1),uVar2 - uVar1);
    local_6 = uStack_10 / 10;
    uVar3 = CONCAT22((int)(local_6 >> 0x10),DAT_376d_4554);
  }
  DAT_376d_4554 = (uint)uVar3;
  DAT_376d_453e = 0;
  DAT_376d_4556 = (uint)local_6;
  if ((int)(uVar3 >> 0x10) == 0 && (uint)local_6 == 0) {
    FUN_1fb7_0000();
  }
  uVar1 = (uint)(CONCAT12((local_6 & 0x10000) != 0,(uint)local_6) >> 1);
  uStack_10 = CONCAT22((local_6._2_2_ >> 1) + (uint)(0xfc17 < uVar1),uVar1 + 1000);
  DAT_376d_4558 = (int)(uStack_10 / local_6);
  uVar1 = (uint)(1000 / (long)DAT_376d_3cc2);
  uVar2 = (int)uVar1 >> 0xf;
  if ((uVar2 <= local_6._2_2_) && ((uVar2 < local_6._2_2_ || (uVar1 < (uint)local_6)))) {
    uVar2 = local_6._2_2_;
    uVar1 = (uint)local_6;
  }
  local_6 = CONCAT22(uVar2,uVar1);
  uVar2 = uVar2 + (0xfffd < uVar1);
  DAT_376d_455a =
       (int)(CONCAT12((uVar2 >> 1 & 1) != 0,(int)(CONCAT12((uVar2 & 1) != 0,uVar1 + 2) >> 1)) >> 1);
  if ((uVar2 >> 2 == 0) && (DAT_376d_455a == 0)) {
    DAT_376d_455a = 1;
  }
  uVar3 = (local_6 * 0x168 + 0x578) / 0xaf0;
  if (uVar3 == 0) {
    uVar3 = 1;
  }
  DAT_376d_455c = (int)uVar3;
  DAT_376d_455e = DAT_376d_455a * 2;
  return;
}

