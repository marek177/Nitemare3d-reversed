
/* Recovered call-backed unowned page layout. Original routine156 cases across6 builds with mocked
   UI/glyph renderer/width: x12,y7, line step11; space advance6; tab column next multiple4 and
   x=6*(column+2); other advance from width helper. Hash stops only at line start; LF ends line;
   y>=205 fatal branch. Percent parser/bitmap and actual framebuffer not verified. Header
   formatting/UI dependencies mocked. */

void __cdecl16far LayoutBsfPage(dword pageText,ushort pageNumber,ushort totalPages)

{
  char *pcVar1;
  char *pcVar2;
  int iVar3;
  uint in_DX;
  int iVar4;
  undefined2 uVar5;
  undefined1 auStack_2a [16];
  undefined1 uStack_1a;
  undefined1 uStack_19;
  undefined4 uStack_14;
  char acStack_10 [2];
  int iStack_e;
  undefined2 uStack_c;
  int iStack_a;
  undefined1 uStack_7;
  int iStack_6;
  undefined2 uStack_4;
  
  acStack_10[0] = '\0';
  acStack_10[1] = 0;
  uStack_7 = FUN_1273_016c();
  FUN_1155_08d6(0x5000a,0xb4012c,0xbf);
  FUN_219b_2888(auStack_2a,0x1cd8,_pageNumber);
  FUN_1155_08d6(0xbc00ff,0xa0037,0xbf);
  FUN_1273_016c(8);
  FUN_1cdc_0096(0xbe0101,auStack_2a);
  uStack_c = 0;
  if (*(char *)pageText != '\0') {
    iStack_a = 7;
    pcVar1 = (char *)pageText;
    do {
      pcVar2 = (char *)pcVar1;
      if (*pcVar1 == '#') break;
      if (0xcc < iStack_a) {
        FUN_1f67_000a();
      }
      iStack_6 = iStack_a;
      iStack_e = 0;
      uVar5 = pageText._2_2_;
      if (*pcVar2 != '\0') {
        uStack_4 = 0xc;
        iVar4 = 0xc;
        do {
          uVar5 = pageText._2_2_;
          if (*pcVar2 == '\n') break;
          if (*pcVar2 == '%') {
            pcVar2 = (char *)FUN_1cdc_106c();
            pageText = (ulong)in_DX << 0x10;
            if (uStack_14._2_2_ != 0 || (int)uStack_14 != 0) {
              FUN_1155_07e0(uStack_14,iVar4,iStack_6,uStack_1a,uStack_19,uStack_1a,uStack_19,
                            0x1f0000);
              ReleaseFarBlock(uStack_14);
            }
          }
          else {
            acStack_10[0] = *pcVar2;
            FUN_1cdc_0096(iVar4,iStack_6,acStack_10);
            if (*pcVar2 == '\t') {
              in_DX = iStack_e % 4;
              iStack_e = iStack_e + (4 - in_DX);
              iVar4 = (iStack_e + 2) * 6;
            }
            else {
              if (*pcVar2 == ' ') {
                iVar4 = iVar4 + 6;
              }
              else {
                iVar3 = FUN_1cdc_0030(acStack_10);
                iVar4 = iVar4 + iVar3;
              }
              iStack_e = iStack_e + 1;
            }
          }
          pcVar2 = pcVar2 + 1;
          uVar5 = pageText._2_2_;
        } while (*pcVar2 != '\0');
      }
      iStack_a = iStack_a + 0xb;
      pcVar1 = (char *)CONCAT22(uVar5,pcVar2 + 1);
    } while (pcVar2[1] != '\0');
  }
  FUN_1155_0090();
  return;
}

