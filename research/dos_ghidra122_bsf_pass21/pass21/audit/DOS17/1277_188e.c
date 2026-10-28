
/* Original wrapper120 cases across6 builds with mocked IO/final reader: table
   offset=((objectIndex+256)*4)&ffff; read nonzero dword offset, seek there; while signed
   skipFrames>0 read10-byte header and seek width*height relative, then final reader and close.
   Actual asset file not supplied to tests. */

void __cdecl16far LoadIndexedGraphicFrame(ushort objectIndex,short skipFrames,ushort recordOffset)

{
  ushort handle;
  uint uVar1;
  int iVar2;
  undefined2 unaff_DS;
  ulong local_c;
  undefined2 local_8;
  int local_6;
  ushort local_4;
  
  handle = FUN_21d1_1c72(0x61fa,0x8000);
  if (handle == 0xffff) {
    FUN_1f9d_000c(0x709,0x61fa);
  }
  uVar1 = CONCAT11((char)(objectIndex >> 8) + '\x01',(char)objectIndex) << 2;
  local_c = (ulong)uVar1;
  SeekDosHandle(handle,(ulong)uVar1,0);
  iVar2 = FUN_21d1_1e14(0x21d1,handle,&local_c,4);
  if (iVar2 != 4) {
    FUN_1f9d_000c(0x71f,0x61fa);
  }
  if (local_c == 0) {
    FUN_1f9d_000c(0x735,skipFrames);
  }
  SeekDosHandle(handle,local_c,0);
  local_8 = 0;
  if (0 < skipFrames) {
    local_6 = skipFrames;
    local_4 = handle;
    do {
      iVar2 = FUN_21d1_1e14(0x21d1,handle,recordOffset,10);
      if (iVar2 != 10) {
        FUN_1f9d_000c(0x751,0x61fa);
      }
      SeekDosHandle(handle,(ulong)*(byte *)(recordOffset + 1) * (ulong)*(byte *)recordOffset,1);
      local_6 = local_6 + -1;
    } while (local_6 != 0);
  }
  ReadGraphicRecord(handle,recordOffset);
  FUN_21d1_1bb6(0x21d1,handle);
  return;
}

