
void __cdecl16far FUN_1817_257a(undefined4 *param_1)

{
  char cVar1;
  int *piVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  bool bVar6;
  
  *param_1 = DAT_3395_14f4;
  *(undefined1 *)(param_1 + 1) = DAT_3395_14f8;
  *(undefined4 *)((int)param_1 + 10) = DAT_3395_14f9;
  *(undefined1 *)((int)param_1 + 0xe) = DAT_3395_14fd;
  *(undefined4 *)((int)param_1 + 0x13) = DAT_3395_14fe;
  *(undefined1 *)((int)param_1 + 0x17) = DAT_3395_1502;
  *(undefined2 *)((int)param_1 + 6) = 0;
  if (0 < DAT_3395_61d2) {
    iVar4 = 0x264e;
    iVar5 = 0;
    do {
      if (*(char *)(iVar4 + 0xb) != '\n') {
        cVar1 = FUN_1817_02e0(*(undefined1 *)(*(int *)(iVar4 + 8) * 0x1c + 0xc));
        if (cVar1 == '\0') {
          *(int *)((int)param_1 + 6) = *(int *)((int)param_1 + 6) + 1;
        }
      }
      iVar4 = iVar4 + 0x1a;
      iVar5 = iVar5 + 1;
    } while (iVar5 < DAT_3395_61d2);
  }
  iVar4 = 0;
  *(undefined2 *)(param_1 + 2) = 0;
  if (0 < *(int *)&DAT_3395_0002) {
    piVar2 = (int *)0x3502;
    do {
      if (*piVar2 == 1) {
        *(int *)(param_1 + 2) = *(int *)(param_1 + 2) + 1;
      }
      piVar2 = piVar2 + 7;
      iVar4 = iVar4 + 1;
    } while (iVar4 < DAT_2e21_0002);
  }
  iVar4 = 0;
  if (((DAT_3395_40ee & 1) == 0) && ((DAT_3395_d45c & 1) != 0)) {
    *(undefined1 *)((int)param_1 + 10) = 0x52;
    iVar4 = 1;
  }
  if (((DAT_3395_40ee & 2) == 0) && ((DAT_3395_d45c & 2) != 0)) {
    *(undefined1 *)((int)param_1 + iVar4 + 10) = 0x47;
    iVar4 = iVar4 + 1;
  }
  if (((DAT_3395_40ee & 4) == 0) && ((DAT_3395_d45c & 4) != 0)) {
    *(undefined1 *)((int)param_1 + iVar4 + 10) = 0x42;
    iVar4 = iVar4 + 1;
  }
  if (((DAT_3395_40ee & 8) == 0) && ((DAT_3395_d45c & 8) != 0)) {
    *(undefined1 *)((int)param_1 + iVar4 + 10) = 0x59;
    iVar4 = iVar4 + 1;
  }
  if (iVar4 != 0) {
    *(undefined1 *)((int)param_1 + iVar4 + 10) = 0;
  }
  iVar4 = 0;
  if (((DAT_3395_40ef & 1) == 0) && ((DAT_3395_d45d & 1) != 0)) {
    *(undefined1 *)((int)param_1 + 0x13) = 0x52;
    iVar4 = 1;
  }
  if (((DAT_3395_40ef & 2) == 0) && ((DAT_3395_d45d & 2) != 0)) {
    *(undefined1 *)((int)param_1 + iVar4 + 0x13) = 0x59;
    iVar4 = iVar4 + 1;
  }
  if (iVar4 != 0) {
    *(undefined1 *)((int)param_1 + iVar4 + 0x13) = 0;
  }
  bVar6 = DAT_3395_40ae != '\0';
  if (bVar6) {
    *(undefined1 *)param_1 = 0x53;
  }
  uVar3 = (uint)bVar6;
  if (DAT_3395_40af != '\0') {
    *(undefined1 *)(uVar3 + (int)param_1) = 0x50;
    uVar3 = uVar3 + 1;
  }
  if (DAT_3395_40b0 != '\0') {
    *(undefined1 *)(uVar3 + (int)param_1) = 0x41;
    uVar3 = uVar3 + 1;
  }
  if (DAT_3395_40b1 != '\0') {
    *(undefined1 *)(uVar3 + (int)param_1) = 0x49;
    uVar3 = uVar3 + 1;
  }
  if (uVar3 != 0) {
    *(undefined1 *)(uVar3 + (int)param_1) = 0;
  }
  return;
}

