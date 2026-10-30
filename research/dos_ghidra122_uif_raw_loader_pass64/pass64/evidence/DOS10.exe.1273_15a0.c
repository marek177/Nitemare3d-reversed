
uint __cdecl16far FUN_1273_15a0(undefined2 param_1)

{
  int *piVar1;
  undefined2 uVar2;
  undefined1 extraout_AH;
  undefined2 in_DX;
  int iVar3;
  int iVar4;
  byte local_1d0 [320];
  byte local_90 [4];
  int local_8c;
  int local_8a;
  int local_88;
  int local_86;
  undefined2 local_10;
  int local_e;
  byte *local_c;
  undefined2 local_8;
  byte local_6;
  byte local_5;
  int local_4;
  
  local_e = 0;
  local_c = local_1d0;
  piVar1 = (int *)FUN_1273_152a(param_1);
  if (*piVar1 == 0) {
    return (uint)piVar1 & 0xff00;
  }
  local_8 = in_DX;
  uVar2 = FUN_219b_06de(0x645,0x642);
  FUN_219b_268c(uVar2,(int)*(undefined4 *)(piVar1 + 1),
                (int)((ulong)*(undefined4 *)(piVar1 + 1) >> 0x10),0);
  FUN_219b_06f4(local_90,0x80,1,uVar2);
  local_10 = uVar2;
  if (local_90[0] != 10) {
    FUN_1f67_000a(0x64d);
  }
  if ((local_86 - local_8a != 199) && (local_88 - local_8c != 0x13f)) {
    FUN_1f67_000a(0x662);
  }
  do {
    FUN_219b_06f4(&local_5,1,1,local_10);
    iVar3 = local_e;
    if ((local_5 & 0xc0) == 0xc0) {
      FUN_219b_06f4(&local_6,1,1,local_10);
      local_4 = 0;
      if ((local_5 & 0x3f) != 0) {
        iVar3 = local_e;
        do {
          *local_c = local_6;
          local_c = local_c + 1;
          iVar4 = iVar3;
          if (local_c == local_90) {
            iVar4 = iVar3 + 1;
            local_c = local_1d0;
            FUN_1155_07e0(local_c,(undefined1 *)&DAT_3360_3360,0,iVar3,0x10140,0x140,1,0,0xffff);
          }
          local_4 = local_4 + 1;
          iVar3 = iVar4;
        } while (local_4 < (int)(local_5 & 0x3f));
        local_e = iVar4;
      }
    }
    else {
      *local_c = local_5;
      local_c = local_c + 1;
      if (local_c == local_90) {
        local_e = local_e + 1;
        local_c = local_1d0;
        FUN_1155_07e0(local_c,(undefined1 *)&DAT_3360_3360,0,iVar3,0x10140,0x140,1,0,0xffff);
      }
    }
  } while (local_e < 200);
  FUN_219b_05f2(local_10);
  return CONCAT11(extraout_AH,1);
}

