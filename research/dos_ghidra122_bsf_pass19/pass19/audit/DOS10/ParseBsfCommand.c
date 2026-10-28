
/* Original BSF percent parser612 cases across6 builds. B/C raw byte paths, b/c lookup paths, d
   default8, o/p graphic dependencies. Numeric scanf mocked; formats verified %i for B/C/b/c and %d
   for o/p. Signed upper checks15/255/31 accept negative values. Output record+6 dword cleared at
   entry. Returns delimiter/NUL far pointer DX:AX; scan count>=8 fatal. Effect routines mocked;
   actual graphics/color mapping and scanf implementation not proven. */

dword __cdecl16far
ParseBsfCommand(dword commandText,ushort colorOffset,ushort graphicRecordOffset,ushort columnOffset)

{
  byte bVar1;
  int iVar2;
  undefined1 extraout_AH;
  undefined1 uVar3;
  char *pcVar4;
  undefined2 unaff_SS;
  undefined2 unaff_DS;
  int local_8;
  int local_6;
  int local_4;
  
  *(undefined4 *)(graphicRecordOffset + 6) = 0;
  pcVar4 = (char *)((int)commandText + 1);
  commandText = CONCAT22(commandText._2_2_,pcVar4);
  *(int *)columnOffset = *(int *)columnOffset + 1;
  bVar1 = *(byte *)commandText;
  if (bVar1 == 0x70) {
    iVar2 = FUN_219b_28e0();
    if ((iVar2 != 1) || (0x1f < local_4)) {
      FUN_1f67_000a();
    }
    FUN_1273_18aa();
    goto LAB_1cdc_1239;
  }
  if (0x70 < bVar1) goto LAB_1cdc_1239;
  if (bVar1 == 0x62) {
    iVar2 = FUN_219b_28e0();
    if ((iVar2 != 1) || (uVar3 = 0, 0xf < local_6)) {
      FUN_1f67_000a();
      uVar3 = extraout_AH;
    }
    FUN_1273_016c(CONCAT11(uVar3,(undefined1)local_6));
LAB_1cdc_1100:
    FUN_1155_08d6(0x5000a,0xb4012c);
  }
  else {
    if ((char)bVar1 < 'c') {
      if (bVar1 == 0x42) {
        iVar2 = FUN_219b_28e0();
        if (iVar2 != 1) {
          FUN_1f67_000a();
        }
        goto LAB_1cdc_1100;
      }
      if (bVar1 != 0x43) goto LAB_1cdc_1239;
      iVar2 = FUN_219b_28e0();
      if (iVar2 != 1) {
        FUN_1f67_000a();
      }
    }
    else {
      if (bVar1 == 99) {
        iVar2 = FUN_219b_28e0();
        if ((iVar2 != 1) || (0xf < local_8)) {
          FUN_1f67_000a();
        }
      }
      else if (bVar1 != 100) {
        if (bVar1 == 0x6f) {
          iVar2 = FUN_219b_28e0();
          if ((iVar2 != 1) || (0xff < local_4)) {
            FUN_1f67_000a();
          }
          FUN_1273_17b6();
        }
        goto LAB_1cdc_1239;
      }
      local_8._0_1_ = FUN_1273_016c();
    }
    *(undefined1 *)colorOffset = (undefined1)local_8;
  }
LAB_1cdc_1239:
  local_4 = 0;
  if (*(char *)commandText == '\0') {
    unaff_SS = unaff_DS;
  }
  else {
    do {
      if (*pcVar4 == '%') break;
      local_4 = local_4 + 1;
      *(int *)columnOffset = *(int *)columnOffset + 1;
      pcVar4 = pcVar4 + 1;
    } while (*pcVar4 != '\0');
  }
  if (7 < local_4) {
    FUN_1f67_000a();
  }
  *(int *)columnOffset = *(int *)columnOffset + 1;
  return CONCAT22(commandText._2_2_,pcVar4);
}

