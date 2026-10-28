
/* Pass21 original record reader384 mocked cases; pass22 executed in134 original BSF
   command/scanf/object-loader/record/allocator chains using real supplied IMG.1 bytes. Byte0
   width,byte1 height now confirmed against original blitter write traces; +2 dword
   pixel-file-position,+6 far buffer. File I/O/DOS allocation simulated; full VGA/DAC not verified.
    */

void __cdecl16far ReadGraphicRecord(ushort handle,ushort recordOffset)

{
  ushort byteCount;
  undefined2 uVar1;
  ushort uVar2;
  undefined2 uVar3;
  int iVar4;
  undefined2 unaff_DS;
  undefined4 uVar5;
  dword dVar6;
  
  uVar5 = FUN_21bc_1e14(0x1275,handle,recordOffset,10);
  uVar3 = (undefined2)((ulong)uVar5 >> 0x10);
  if ((int)uVar5 != 10) {
    FUN_1f89_0002(0x2c8,0x61e8);
  }
  byteCount = (uint)*(byte *)(recordOffset + 1) * (uint)*(byte *)recordOffset;
  uVar1 = FUN_21bc_2898(handle);
  *(undefined2 *)(recordOffset + 2) = uVar1;
  *(undefined2 *)(recordOffset + 4) = uVar3;
  dVar6 = AllocateFarBytes(byteCount);
  iVar4 = (int)(dVar6 >> 0x10);
  *(undefined2 *)(recordOffset + 6) = (int)dVar6;
  *(int *)(recordOffset + 8) = iVar4;
  if (iVar4 == 0 && *(int *)(recordOffset + 6) == 0) {
    FUN_1f89_0002(0x2eb,0x2de);
  }
  uVar2 = FUN_1f89_0094(handle,(int)*(undefined4 *)(recordOffset + 6),
                        (int)((ulong)*(undefined4 *)(recordOffset + 6) >> 0x10),byteCount);
  if (uVar2 != byteCount) {
    FUN_1f89_0002(0x30e,0x61e8);
  }
  return;
}

