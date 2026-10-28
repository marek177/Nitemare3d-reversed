
/* Pass22:268 original blits on134 real IMG.1 graphics selected by actual BSF %o references across6
   builds. Every observed plane-mask/address/value write matches column-major oracle; opaqueffff and
   transparent31. File loading134 original parser/scanf/loader/record/allocator chains with real
   bytes but mocked IO/DOS48. Writes observed in ordinary mapped memory with port-mask model, not
   full VGA/DAC. Record byte0=width,byte1=height confirmed by layout argument flow and blit
   loop/write observations. */

void __cdecl16far
BlitColumnMajorGraphic
          (dword pixelPointer,ushort x,ushort y,ushort sourceWidthArgument,ushort columnStride,
          ushort drawWidth,ushort drawHeight,ushort pageSelect,ushort transparentIndexBits)

{
  char *pcVar1;
  undefined2 uVar2;
  byte bVar3;
  ushort uVar4;
  char *pcVar5;
  char *pcVar6;
  undefined2 unaff_DS;
  undefined2 uVar7;
  bool bVar8;
  char *local_6;
  char *local_4;
  
  uVar2 = *(undefined2 *)0x12e;
  if (pageSelect != 0) {
    uVar2 = *(undefined2 *)0x12c;
  }
  local_4 = (char *)((y & 0xff) * 0x50 + (x >> 2));
  out(0x3c4,2);
  bVar3 = (byte)x & 3;
  bVar3 = '\x11' << bVar3 | 0x11U >> 8 - bVar3;
  out(0x3c5,bVar3);
  uVar7 = (undefined2)(pixelPointer >> 0x10);
  local_6 = (char *)pixelPointer;
  if ((int)transparentIndexBits < 0) {
    do {
      uVar4 = drawHeight;
      pcVar5 = local_6;
      pcVar6 = local_4;
      do {
        pcVar1 = pcVar5;
        pcVar5 = pcVar5 + 1;
        *pcVar6 = *pcVar1;
        pcVar6 = pcVar6 + 0x50;
        uVar4 = uVar4 - 1;
      } while (uVar4 != 0);
      bVar8 = (char)bVar3 < '\0';
      bVar3 = bVar3 << 1 | bVar8;
      out(0x3c5,bVar3);
      if (bVar8) {
        local_4 = local_4 + 1;
      }
      local_6 = local_6 + columnStride;
      drawWidth = drawWidth - 1;
    } while (drawWidth != 0);
  }
  else {
    do {
      uVar4 = drawHeight;
      pcVar5 = local_6;
      pcVar6 = local_4;
      do {
        pcVar1 = pcVar5;
        pcVar5 = pcVar5 + 1;
        if (*pcVar1 != (char)transparentIndexBits) {
          *pcVar6 = *pcVar1;
        }
        pcVar6 = pcVar6 + 0x50;
        uVar4 = uVar4 - 1;
      } while (uVar4 != 0);
      bVar8 = (char)bVar3 < '\0';
      bVar3 = bVar3 << 1 | bVar8;
      out(0x3c5,bVar3);
      if (bVar8) {
        local_4 = local_4 + 1;
      }
      local_6 = local_6 + columnStride;
      drawWidth = drawWidth - 1;
    } while (drawWidth != 0);
  }
  return;
}

