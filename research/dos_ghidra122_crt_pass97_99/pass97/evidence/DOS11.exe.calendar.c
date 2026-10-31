
int __cdecl16far
FUN_21bc_2dc0(uint param_1,int param_2,int param_3,uint param_4,uint param_5,int param_6)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined2 uVar4;
  undefined2 uVar5;
  undefined2 uVar6;
  undefined2 uVar7;
  int local_18;
  undefined1 local_14 [4];
  uint local_10;
  int local_c;
  int local_a;
  int local_6;
  
  iVar2 = *(int *)(param_2 * 2 + 0x2478);
  if (((param_1 & 3) == 0) && (2 < param_2)) {
    iVar2 = iVar2 + 1;
  }
  FUN_21bc_2bf4();
  uVar7 = 0;
  uVar6 = 0x3c;
  uVar5 = 0;
  uVar4 = 0x3c;
  uVar3 = FUN_21bc_3ad8((long)(int)param_1 * 0x16d +
                        CONCAT22((int)(param_1 + 3) >> 0xf,(int)(param_1 + 3) >> 2) + (long)param_3
                        + (long)iVar2 + 0xe44,0x18,0);
  uVar3 = FUN_21bc_3ad8((uint)uVar3 + param_4,
                        (int)((ulong)uVar3 >> 0x10) + ((int)param_4 >> 0xf) +
                        (uint)CARRY2((uint)uVar3,param_4),uVar4,uVar5);
  iVar1 = FUN_21bc_3ad8((uint)uVar3 + param_5,
                        (int)((ulong)uVar3 >> 0x10) + ((int)param_5 >> 0xf) +
                        (uint)CARRY2((uint)uVar3,param_5),uVar6,uVar7);
  local_18 = iVar1 + param_6 + DAT_3395_2498;
  local_6 = param_3 + iVar2;
  local_a = param_1 + 0x50;
  local_c = param_2 + -1;
  local_10 = param_4;
  if (DAT_3395_249c != 0) {
    iVar2 = FUN_21bc_2d00(local_14);
    if (iVar2 != 0) {
      local_18 = local_18 + -0xe10;
    }
  }
  return local_18;
}

