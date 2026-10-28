
/* Call-backed BSF page layout, recovered or newly typed according to per-build inventory. Original
   routine156 cases across6 builds with mocked UI/glyph renderer/width: x12,y7, line step11; space
   advance6; tab column next multiple4 and x=6*(column+2); other advance from width helper. Hash
   stops only at line start; LF ends line; y>=205 fatal branch. Percent parser/bitmap and actual
   framebuffer not verified. Header formatting/UI dependencies mocked. */

void __cdecl16far LayoutBsfPage(dword pageText,ushort pageNumber,ushort totalPages)

{
  char *pcVar1;
  char *pcVar2;
  int iVar3;
  uint in_DX;
  int iVar4;
  undefined2 uVar5;
  undefined1 local_2a [16];
  undefined1 local_1a;
  undefined1 local_19;
  undefined4 local_14;
  char local_10 [2];
  int local_e;
  undefined2 local_c;
  int local_a;
  undefined1 local_7;
  int local_6;
  undefined2 local_4;
  
  local_10[0] = '\0';
  local_10[1] = 0;
  local_7 = FUN_1275_0160();
  FUN_1155_08d6(0x5000a,0xb4012c,0xbf);
  FUN_21c2_278c(local_2a,0x1dac,_pageNumber);
  FUN_1155_08d6(0xbc00ff,0xa0037,0xbf);
  FUN_1275_0160(8);
  FUN_1d00_009c(0xbe0101,local_2a);
  local_c = 0;
  if (*(char *)pageText != '\0') {
    local_a = 7;
    pcVar1 = (char *)pageText;
    do {
      pcVar2 = (char *)pcVar1;
      if (*pcVar1 == '#') break;
      if (0xcc < local_a) {
        FUN_1f8f_0002();
      }
      local_6 = local_a;
      local_e = 0;
      uVar5 = pageText._2_2_;
      if (*pcVar2 != '\0') {
        local_4 = 0xc;
        iVar4 = 0xc;
        do {
          uVar5 = pageText._2_2_;
          if (*pcVar2 == '\n') break;
          if (*pcVar2 == '%') {
            pcVar2 = (char *)FUN_1d00_1042();
            pageText = (ulong)in_DX << 0x10;
            if (local_14._2_2_ != 0 || (int)local_14 != 0) {
              FUN_1155_07e0(local_14,iVar4,local_6,local_1a,local_19,local_1a,local_19,0x1f0000);
              ReleaseFarBlock(local_14);
            }
          }
          else {
            local_10[0] = *pcVar2;
            FUN_1d00_009c(iVar4,local_6,local_10);
            if (*pcVar2 == '\t') {
              in_DX = local_e % 4;
              local_e = local_e + (4 - in_DX);
              iVar4 = (local_e + 2) * 6;
            }
            else {
              if (*pcVar2 == ' ') {
                iVar4 = iVar4 + 6;
              }
              else {
                iVar3 = FUN_1d00_0036(local_10);
                iVar4 = iVar4 + iVar3;
              }
              local_e = local_e + 1;
            }
          }
          pcVar2 = pcVar2 + 1;
          uVar5 = pageText._2_2_;
        } while (*pcVar2 != '\0');
      }
      local_a = local_a + 0xb;
      pcVar1 = (char *)CONCAT22(uVar5,pcVar2 + 1);
    } while (pcVar2[1] != '\0');
  }
  FUN_1155_0090();
  return;
}

