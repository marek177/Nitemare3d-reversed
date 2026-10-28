
/* Original percent parser with original sscanf/CRT executed612 command cases (pass20); only effects
   mocked and fatal stopped. %i accepts hex/octal, %d decimal; 65536 ->0,32768 ->8000, -32769 ->7fff
   in tested16-bit conversion. Signed upper-only checks allow negative converted values. Return
   DX:AX points to closing percent or NUL. Graphics/palette effects remain separate. */

dword __cdecl16far
ParseBsfCommand(dword commandText,ushort colorOffset,ushort graphicRecordOffset,ushort columnOffset)

{
  byte bVar1;
  int iVar2;
  short sVar3;
  undefined1 extraout_AH;
  undefined1 uVar4;
  char *pcVar5;
  undefined2 unaff_SS;
  undefined2 unaff_DS;
  undefined4 local_10;
  undefined4 uStack_c;
  int local_8;
  int local_6;
  int local_4;
  
  *(undefined4 *)(graphicRecordOffset + 6) = 0;
  iVar2 = (int)commandText;
  pcVar5 = (char *)((int)commandText + 1);
  commandText = CONCAT22(commandText._2_2_,pcVar5);
  *(int *)columnOffset = *(int *)columnOffset + 1;
  local_10 = *(undefined4 *)(iVar2 + 2);
  uStack_c = *(undefined4 *)(iVar2 + 6);
  bVar1 = *(byte *)commandText;
  if (bVar1 == 0x70) {
    sVar3 = SscanfNearString((ushort)&local_10,0x1d5e);
    if ((sVar3 != 1) || (0x1f < local_4)) {
      FUN_1f8f_0002();
    }
    FUN_1275_18e2();
    goto LAB_1d00_120f;
  }
  if (0x70 < bVar1) goto LAB_1d00_120f;
  if (bVar1 == 0x62) {
    sVar3 = SscanfNearString((ushort)&local_10,0x1d28);
    if ((sVar3 != 1) || (uVar4 = 0, 0xf < local_6)) {
      FUN_1f8f_0002();
      uVar4 = extraout_AH;
    }
    FUN_1275_0160(CONCAT11(uVar4,(undefined1)local_6));
LAB_1d00_10d6:
    FUN_1155_08d6(0x5000a,0xb4012c);
  }
  else {
    if ((char)bVar1 < 'c') {
      if (bVar1 == 0x42) {
        sVar3 = SscanfNearString((ushort)&local_10,0x1d43);
        if (sVar3 != 1) {
          FUN_1f8f_0002();
        }
        goto LAB_1d00_10d6;
      }
      if (bVar1 != 0x43) goto LAB_1d00_120f;
      sVar3 = SscanfNearString((ushort)&local_10,0x1d0d);
      if (sVar3 != 1) {
        FUN_1f8f_0002();
      }
    }
    else {
      if (bVar1 == 99) {
        sVar3 = SscanfNearString((ushort)&local_10,0x1cf2);
        if ((sVar3 != 1) || (0xf < local_8)) {
          FUN_1f8f_0002();
        }
      }
      else if (bVar1 != 100) {
        if (bVar1 == 0x6f) {
          sVar3 = SscanfNearString((ushort)&local_10,0x1d79);
          if ((sVar3 != 1) || (0xff < local_4)) {
            FUN_1f8f_0002();
          }
          FUN_1275_17ee();
        }
        goto LAB_1d00_120f;
      }
      local_8._0_1_ = FUN_1275_0160();
    }
    *(undefined1 *)colorOffset = (undefined1)local_8;
  }
LAB_1d00_120f:
  local_4 = 0;
  if (*(char *)commandText == '\0') {
    unaff_SS = unaff_DS;
  }
  else {
    do {
      if (*pcVar5 == '%') break;
      local_4 = local_4 + 1;
      *(int *)columnOffset = *(int *)columnOffset + 1;
      pcVar5 = pcVar5 + 1;
    } while (*pcVar5 != '\0');
  }
  if (7 < local_4) {
    FUN_1f8f_0002();
  }
  *(int *)columnOffset = *(int *)columnOffset + 1;
  return CONCAT22(commandText._2_2_,pcVar5);
}

