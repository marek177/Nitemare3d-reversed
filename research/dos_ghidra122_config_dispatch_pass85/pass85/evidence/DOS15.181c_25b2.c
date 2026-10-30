
void __cdecl16far FUN_181c_25b2(undefined4 *param_1)

{
  char cVar1;
  int *piVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  bool bVar6;
  
  *param_1 = DAT_374a_14ea;
  *(undefined1 *)(param_1 + 1) = DAT_374a_14ee;
  *(undefined4 *)((int)param_1 + 10) = DAT_374a_14ef;
  *(undefined1 *)((int)param_1 + 0xe) = DAT_374a_14f3;
  *(undefined4 *)((int)param_1 + 0x13) = DAT_374a_14f4;
  *(undefined1 *)((int)param_1 + 0x17) = DAT_374a_14f8;
  *(undefined2 *)((int)param_1 + 6) = 0;
  if (0 < DAT_374a_61a2) {
    iVar4 = 0x264e;
    iVar5 = 0;
    do {
      if (*(char *)(iVar4 + 0xb) != '\n') {
        cVar1 = FUN_181c_02ea(*(undefined1 *)(*(int *)(iVar4 + 8) * 0x1c + 0xc));
        if (cVar1 == '\0') {
          *(int *)((int)param_1 + 6) = *(int *)((int)param_1 + 6) + 1;
        }
      }
      iVar4 = iVar4 + 0x1a;
      iVar5 = iVar5 + 1;
    } while (iVar5 < DAT_374a_61a2);
  }
  iVar4 = 0;
  *(undefined2 *)(param_1 + 2) = 0;
  if (0 < *(int *)&DAT_374a_0002) {
    piVar2 = (int *)0x3502;
    do {
      if (*piVar2 == 1) {
        *(int *)(param_1 + 2) = *(int *)(param_1 + 2) + 1;
      }
      piVar2 = piVar2 + 7;
      iVar4 = iVar4 + 1;
    } while (iVar4 < DAT_31d6_0002);
  }
  iVar4 = 0;
  if (((DAT_374a_40be & 1) == 0) && ((DAT_374a_d43c & 1) != 0)) {
    *(undefined1 *)((int)param_1 + 10) = 0x52;
    iVar4 = 1;
  }
  if (((DAT_374a_40be & 2) == 0) && ((DAT_374a_d43c & 2) != 0)) {
    *(undefined1 *)((int)param_1 + iVar4 + 10) = 0x47;
    iVar4 = iVar4 + 1;
  }
  if (((DAT_374a_40be & 4) == 0) && ((DAT_374a_d43c & 4) != 0)) {
    *(undefined1 *)((int)param_1 + iVar4 + 10) = 0x42;
    iVar4 = iVar4 + 1;
  }
  if (((DAT_374a_40be & 8) == 0) && ((DAT_374a_d43c & 8) != 0)) {
    *(undefined1 *)((int)param_1 + iVar4 + 10) = 0x59;
    iVar4 = iVar4 + 1;
  }
  if (iVar4 != 0) {
    *(undefined1 *)((int)param_1 + iVar4 + 10) = 0;
  }
  iVar4 = 0;
  if (((DAT_374a_40bf & 1) == 0) && ((DAT_374a_d43d & 1) != 0)) {
    *(undefined1 *)((int)param_1 + 0x13) = 0x52;
    iVar4 = 1;
  }
  if (((DAT_374a_40bf & 2) == 0) && ((DAT_374a_d43d & 2) != 0)) {
    *(undefined1 *)((int)param_1 + iVar4 + 0x13) = 0x59;
    iVar4 = iVar4 + 1;
  }
  if (iVar4 != 0) {
    *(undefined1 *)((int)param_1 + iVar4 + 0x13) = 0;
  }
  bVar6 = DAT_374a_407e != '\0';
  if (bVar6) {
    *(undefined1 *)param_1 = 0x53;
  }
  uVar3 = (uint)bVar6;
  if (DAT_374a_407f != '\0') {
    *(undefined1 *)(uVar3 + (int)param_1) = 0x50;
    uVar3 = uVar3 + 1;
  }
  if (DAT_374a_4080 != '\0') {
    *(undefined1 *)(uVar3 + (int)param_1) = 0x41;
    uVar3 = uVar3 + 1;
  }
  if (DAT_374a_4081 != '\0') {
    *(undefined1 *)(uVar3 + (int)param_1) = 0x49;
    uVar3 = uVar3 + 1;
  }
  if (uVar3 != 0) {
    *(undefined1 *)(uVar3 + (int)param_1) = 0;
  }
  return;
}

