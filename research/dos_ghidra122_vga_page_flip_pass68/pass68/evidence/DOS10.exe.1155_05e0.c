
/* WARNING: Restarted to delay deadcode elimination for space: stack */

uint __cdecl16far FUN_1155_05e0(int param_1)

{
  byte bVar1;
  char cVar2;
  byte *pbVar3;
  undefined2 uVar4;
  uint uVar5;
  ulong uVar6;
  undefined2 uVar7;
  uint uVar8;
  int iVar9;
  ulong uVar10;
  long lVar11;
  byte bVar12;
  uint uVar13;
  uint uVar14;
  int iVar15;
  char *pcVar16;
  undefined2 unaff_SS;
  bool bVar17;
  ulong uStack_34;
  undefined4 local_2a;
  byte local_1e;
  uint *local_1c;
  uint local_1a;
  uint local_16;
  int local_10;
  uint local_e;
  uint local_c;
  char *local_8;
  int local_4;
  
  uVar7 = DAT_3360_012c;
  pbVar3 = (byte *)*(undefined2 *)(param_1 + 6);
  local_4 = *(int *)(pbVar3 + 6);
  uVar4 = *(undefined2 *)(pbVar3 + 8);
  local_e = *(uint *)(param_1 + 0xc);
  local_c = *(uint *)(param_1 + 8);
  uVar8 = (uint)pbVar3[1];
  local_16 = (uint)*pbVar3;
  local_10 = 2 - (local_c - *(int *)(param_1 + 10));
  uVar13 = 1 - (local_e - *(int *)(param_1 + 0xe));
  uStack_34 = (ulong)uVar13;
  uVar10 = ((ulong)uVar8 << 0x10) / uStack_34;
  local_1a = 0;
  local_2a = 0;
  if (DAT_3360_43a4 < *(int *)(param_1 + 0xe)) {
    uVar13 = uVar13 + (DAT_3360_43a4 - *(int *)(param_1 + 0xe));
  }
  if (*(int *)(param_1 + 0xc) < (int)DAT_3360_43a2) {
    local_e = DAT_3360_43a2;
    uVar13 = uVar13 - (DAT_3360_43a2 - *(int *)(param_1 + 0xc));
    uVar6 = (long)(int)(DAT_3360_43a2 - *(int *)(param_1 + 0xc)) * uVar10;
    local_2a = uVar6 & 0xffff;
    local_4 = local_4 + (int)(uVar6 >> 0x10);
  }
  if (*(int *)(param_1 + 10) < DAT_3360_43a0) {
    if (*(int *)(param_1 + 8) < (int)DAT_3360_439e) {
      local_c = DAT_3360_439e;
      local_10 = 2 - (DAT_3360_439e - *(int *)(param_1 + 10));
      uStack_34 = (ulong)(int)(DAT_3360_439e - *(int *)(param_1 + 8));
      lVar11 = (((ulong)uVar8 << 0x10) / (ulong)uVar13) * uStack_34;
      iVar15 = (int)((ulong)lVar11 >> 0x10);
      local_2a = CONCAT22((int)lVar11,(undefined2)local_2a);
      local_4 = local_4 + (uint)pbVar3[1] * iVar15;
      local_16 = local_16 - iVar15;
    }
  }
  else {
    local_10 = (DAT_3360_43a0 - local_c) + 1;
  }
  uVar5 = *(uint *)(param_1 + 0x10);
  local_1c = (uint *)(local_c * 2 + 0x463a);
  bVar1 = *(byte *)((int)*(undefined4 *)(param_1 + 2) + 5);
  local_8 = (char *)((local_e & 0xff) * 0x50 + (local_c >> 2));
  out(0x3c4,2);
  bVar12 = (byte)local_c & 3;
  local_1e = '\x11' << bVar12 | 0x11U >> 8 - bVar12;
  out(0x3c5,local_1e);
  iVar15 = local_4;
  while( true ) {
    lVar11 = CONCAT22(iVar15,(undefined2)local_2a);
    if (((bVar1 & 0x10) != 0) || (*local_1c <= uVar5)) {
      pcVar16 = local_8;
      uVar14 = uVar13;
      do {
        cVar2 = *(char *)((ulong)lVar11 >> 0x10);
        if (cVar2 != '\x1f') {
          *pcVar16 = cVar2;
        }
        pcVar16 = pcVar16 + 0x50;
        lVar11 = uVar10 + lVar11;
        uVar14 = uVar14 - 1;
      } while (uVar14 != 0);
    }
    lVar11 = uVar10 + CONCAT22(local_1a,local_2a._2_2_);
    local_2a = CONCAT22((int)lVar11,(undefined2)local_2a);
    local_1a = (uint)((ulong)lVar11 >> 0x10);
    if ((int)local_16 <= (int)local_1a) break;
    iVar9 = (local_1a & 0xff) * uVar8;
    iVar15 = local_4 + iVar9;
    local_1c = local_1c + 1;
    bVar17 = (char)local_1e < '\0';
    local_1e = local_1e << 1 | bVar17;
    out(0x3c5,local_1e);
    if (bVar17) {
      local_8 = local_8 + 1;
    }
    local_10 = local_10 + -1;
    if (local_10 == 0) {
      return CONCAT11((char)((uint)iVar9 >> 8),local_1e);
    }
  }
  return local_1a;
}

