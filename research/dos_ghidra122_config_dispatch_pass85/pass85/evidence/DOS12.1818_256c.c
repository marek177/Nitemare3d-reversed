
void __cdecl16far FUN_1818_256c(undefined4 *param_1)

{
  char cVar1;
  int *piVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  bool bVar6;
  
  *param_1 = DAT_339b_14e6;
  *(undefined1 *)(param_1 + 1) = DAT_339b_14ea;
  *(undefined4 *)((int)param_1 + 10) = DAT_339b_14eb;
  *(undefined1 *)((int)param_1 + 0xe) = DAT_339b_14ef;
  *(undefined4 *)((int)param_1 + 0x13) = DAT_339b_14f0;
  *(undefined1 *)((int)param_1 + 0x17) = DAT_339b_14f4;
  *(undefined2 *)((int)param_1 + 6) = 0;
  if (0 < DAT_339b_61d2) {
    iVar4 = 0x264e;
    iVar5 = 0;
    do {
      if (*(char *)(iVar4 + 0xb) != '\n') {
        cVar1 = FUN_1818_02dc(*(undefined1 *)(*(int *)(iVar4 + 8) * 0x1c + 0xc));
        if (cVar1 == '\0') {
          *(int *)((int)param_1 + 6) = *(int *)((int)param_1 + 6) + 1;
        }
      }
      iVar4 = iVar4 + 0x1a;
      iVar5 = iVar5 + 1;
    } while (iVar5 < DAT_339b_61d2);
  }
  iVar4 = 0;
  *(undefined2 *)(param_1 + 2) = 0;
  if (0 < *(int *)&DAT_339b_0002) {
    piVar2 = (int *)0x3502;
    do {
      if (*piVar2 == 1) {
        *(int *)(param_1 + 2) = *(int *)(param_1 + 2) + 1;
      }
      piVar2 = piVar2 + 7;
      iVar4 = iVar4 + 1;
    } while (iVar4 < DAT_2e27_0002);
  }
  iVar4 = 0;
  if (((DAT_339b_40ee & 1) == 0) && ((DAT_339b_d46c & 1) != 0)) {
    *(undefined1 *)((int)param_1 + 10) = 0x52;
    iVar4 = 1;
  }
  if (((DAT_339b_40ee & 2) == 0) && ((DAT_339b_d46c & 2) != 0)) {
    *(undefined1 *)((int)param_1 + iVar4 + 10) = 0x47;
    iVar4 = iVar4 + 1;
  }
  if (((DAT_339b_40ee & 4) == 0) && ((DAT_339b_d46c & 4) != 0)) {
    *(undefined1 *)((int)param_1 + iVar4 + 10) = 0x42;
    iVar4 = iVar4 + 1;
  }
  if (((DAT_339b_40ee & 8) == 0) && ((DAT_339b_d46c & 8) != 0)) {
    *(undefined1 *)((int)param_1 + iVar4 + 10) = 0x59;
    iVar4 = iVar4 + 1;
  }
  if (iVar4 != 0) {
    *(undefined1 *)((int)param_1 + iVar4 + 10) = 0;
  }
  iVar4 = 0;
  if (((DAT_339b_40ef & 1) == 0) && ((DAT_339b_d46d & 1) != 0)) {
    *(undefined1 *)((int)param_1 + 0x13) = 0x52;
    iVar4 = 1;
  }
  if (((DAT_339b_40ef & 2) == 0) && ((DAT_339b_d46d & 2) != 0)) {
    *(undefined1 *)((int)param_1 + iVar4 + 0x13) = 0x59;
    iVar4 = iVar4 + 1;
  }
  if (iVar4 != 0) {
    *(undefined1 *)((int)param_1 + iVar4 + 0x13) = 0;
  }
  bVar6 = DAT_339b_40ae != '\0';
  if (bVar6) {
    *(undefined1 *)param_1 = 0x53;
  }
  uVar3 = (uint)bVar6;
  if (DAT_339b_40af != '\0') {
    *(undefined1 *)(uVar3 + (int)param_1) = 0x50;
    uVar3 = uVar3 + 1;
  }
  if (DAT_339b_40b0 != '\0') {
    *(undefined1 *)(uVar3 + (int)param_1) = 0x41;
    uVar3 = uVar3 + 1;
  }
  if (DAT_339b_40b1 != '\0') {
    *(undefined1 *)(uVar3 + (int)param_1) = 0x49;
    uVar3 = uVar3 + 1;
  }
  if (uVar3 != 0) {
    *(undefined1 *)(uVar3 + (int)param_1) = 0;
  }
  return;
}

