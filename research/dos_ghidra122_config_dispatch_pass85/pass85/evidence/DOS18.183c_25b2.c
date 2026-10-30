
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl16far FUN_183c_25b2(undefined4 *param_1)

{
  char cVar1;
  int *piVar2;
  uint uVar3;
  undefined1 *puVar4;
  int iVar5;
  bool bVar6;
  
  *param_1 = DAT_376d_151c;
  *(undefined1 *)(param_1 + 1) = DAT_376d_1520;
  *(undefined4 *)((int)param_1 + 10) = DAT_376d_1521;
  *(undefined1 *)((int)param_1 + 0xe) = DAT_376d_1525;
  *(undefined4 *)((int)param_1 + 0x13) = DAT_376d_1526;
  *(undefined1 *)((int)param_1 + 0x17) = DAT_376d_152a;
  *(undefined2 *)((int)param_1 + 6) = 0;
  if (0 < _DAT_376d_6274) {
    puVar4 = (undefined1 *)&DAT_376d_264e;
    iVar5 = 0;
    do {
      if (puVar4[0xb] != '\n') {
        cVar1 = FUN_183c_02ea(*(undefined1 *)(*(int *)(puVar4 + 8) * 0x1c + 0xc));
        if (cVar1 == '\0') {
          *(int *)((int)param_1 + 6) = *(int *)((int)param_1 + 6) + 1;
        }
      }
      puVar4 = puVar4 + 0x1a;
      iVar5 = iVar5 + 1;
    } while (iVar5 < _DAT_376d_6274);
  }
  iVar5 = 0;
  *(undefined2 *)(param_1 + 2) = 0;
  if (0 < *(int *)&DAT_376d_0002) {
    piVar2 = (int *)&DAT_376d_3502;
    do {
      if (*piVar2 == 1) {
        *(int *)(param_1 + 2) = *(int *)(param_1 + 2) + 1;
      }
      piVar2 = piVar2 + 7;
      iVar5 = iVar5 + 1;
    } while (iVar5 < DAT_31f9_0002);
  }
  iVar5 = 0;
  if (((DAT_376d_4190 & 1) == 0) && ((DAT_376d_d50e & 1) != 0)) {
    *(undefined1 *)((int)param_1 + 10) = 0x52;
    iVar5 = 1;
  }
  if (((DAT_376d_4190 & 2) == 0) && ((DAT_376d_d50e & 2) != 0)) {
    *(undefined1 *)((int)param_1 + iVar5 + 10) = 0x47;
    iVar5 = iVar5 + 1;
  }
  if (((DAT_376d_4190 & 4) == 0) && ((DAT_376d_d50e & 4) != 0)) {
    *(undefined1 *)((int)param_1 + iVar5 + 10) = 0x42;
    iVar5 = iVar5 + 1;
  }
  if (((DAT_376d_4190 & 8) == 0) && ((DAT_376d_d50e & 8) != 0)) {
    *(undefined1 *)((int)param_1 + iVar5 + 10) = 0x59;
    iVar5 = iVar5 + 1;
  }
  if (iVar5 != 0) {
    *(undefined1 *)((int)param_1 + iVar5 + 10) = 0;
  }
  iVar5 = 0;
  if (((DAT_376d_4191 & 1) == 0) && ((DAT_376d_d50f & 1) != 0)) {
    *(undefined1 *)((int)param_1 + 0x13) = 0x52;
    iVar5 = 1;
  }
  if (((DAT_376d_4191 & 2) == 0) && ((DAT_376d_d50f & 2) != 0)) {
    *(undefined1 *)((int)param_1 + iVar5 + 0x13) = 0x59;
    iVar5 = iVar5 + 1;
  }
  if (iVar5 != 0) {
    *(undefined1 *)((int)param_1 + iVar5 + 0x13) = 0;
  }
  bVar6 = DAT_376d_4150 != '\0';
  if (bVar6) {
    *(undefined1 *)param_1 = 0x53;
  }
  uVar3 = (uint)bVar6;
  if (DAT_376d_4151 != '\0') {
    *(undefined1 *)(uVar3 + (int)param_1) = 0x50;
    uVar3 = uVar3 + 1;
  }
  if (DAT_376d_4152 != '\0') {
    *(undefined1 *)(uVar3 + (int)param_1) = 0x41;
    uVar3 = uVar3 + 1;
  }
  if (DAT_376d_4153 != '\0') {
    *(undefined1 *)(uVar3 + (int)param_1) = 0x49;
    uVar3 = uVar3 + 1;
  }
  if (uVar3 != 0) {
    *(undefined1 *)(uVar3 + (int)param_1) = 0;
  }
  return;
}

