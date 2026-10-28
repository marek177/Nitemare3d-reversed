
/* Static ABI plus96 wrapper tests: start index uses low8 of second argument, scans class bytes up
   to255 for first equal classValue word. Wrapper tested class3e/start0 with synthetic match0,7,255
   or none; general start/domain not exhaustively tested. */

ushort __cdecl16far FindClassAtOrAfter(ushort classValue,ushort startIndexLowByte)

{
  ushort uVar1;
  undefined2 unaff_DS;
  
  uVar1 = startIndexLowByte & 0xff;
  if (uVar1 < 0x100) {
    do {
      if (*(byte *)(uVar1 + 0xd33a) == classValue) {
        return uVar1;
      }
      uVar1 = uVar1 + 1;
    } while ((int)uVar1 < 0x100);
  }
  uVar1 = FUN_1f94_0000(0xf2,classValue);
  return uVar1;
}

