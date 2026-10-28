
/* Recovered direct caller from existing unowned instructions and call refs. Original full
   routine480 cases across6 builds: mode3/5 forwarded, total=1+count('#'), key50 down/key48 up
   (hex), ESC exit, original far-free once. Dispatch pointer, key input, page renderer and other UI
   calls mocked. Leading/repeated marker behavior follows pointer scan, not naive split. Print/D
   branch and actual renderer not verified. displayStyle analytical name, callers pass16. */

void __cdecl16far BrowseBsfPages(ushort displayStyle,ushort bsfMode)

{
  char *pcVar1;
  char cVar2;
  int iVar3;
  undefined2 uVar4;
  char *pcVar5;
  char *pcVar6;
  undefined2 unaff_SS;
  undefined2 unaff_DS;
  char *pcVar7;
  undefined4 uVar8;
  undefined1 auStack_9c [136];
  int iStack_14;
  char *pcStack_12;
  int iStack_10;
  undefined4 uStack_e;
  char cStack_9;
  int iStack_8;
  char *pcStack_6;
  int iStack_4;
  
  cStack_9 = '\0';
  FUN_1d00_0170();
  iStack_8 = 1;
  iStack_14 = 1;
  pcVar7 = (char *)BsfDispatchMode(bsfMode);
  uVar4 = (undefined2)((ulong)pcVar7 >> 0x10);
  pcVar6 = (char *)pcVar7;
  uStack_e = (char *)CONCAT22(uVar4,(char *)uStack_e);
  cVar2 = *pcVar7;
  pcVar5 = pcVar6;
  pcVar1 = uStack_e;
  while (cVar2 != '\0') {
    if (*pcVar5 == '#') {
      iStack_8 = iStack_8 + 1;
    }
    pcVar5 = pcVar5 + 1;
    pcVar1 = pcVar7;
    cVar2 = *pcVar5;
  }
  uStack_e._2_2_ = (int)((ulong)pcVar1 >> 0x10);
  iStack_4 = uStack_e._2_2_;
  uStack_e = pcVar1;
  pcStack_6 = pcVar6;
  FUN_1155_0256();
  FUN_1275_15d8();
  FUN_1d00_1266(pcVar6,uStack_e._2_2_,1,iStack_8);
  FUN_1155_0256();
  FUN_1275_15d8();
  uStack_e = (char *)CONCAT22(uStack_e._2_2_,pcVar6);
  pcVar5 = pcStack_6;
  do {
    cVar2 = FUN_168a_03c6();
    iVar3 = (int)cVar2;
    if (iVar3 == 0x44) {
      FUN_1d00_0534(0x1dcf,unaff_DS);
      FUN_1bb2_00ac();
      FUN_21c2_278c(auStack_9c,0x1e0f);
      FUN_21c2_38e6();
LAB_1d00_152b:
      uVar8 = CONCAT22(iStack_8,iStack_14);
LAB_1d00_152e:
      FUN_1d00_1266(pcVar5,iStack_4,uVar8);
    }
    else if (iVar3 < 0x45) {
      if (iVar3 == 0x1b) {
        cStack_9 = '\x01';
      }
    }
    else if (0x47 < iVar3) {
      if (iVar3 == 0x49 || iVar3 + -0x48 < 1) {
        if ((pcVar5 != (char *)uStack_e) || (iStack_4 != uStack_e._2_2_)) {
          pcVar5 = pcVar5 + -2;
          if ((pcVar5 != (char *)uStack_e) || (iStack_4 != uStack_e._2_2_)) {
            do {
              if (*pcVar5 == '#') break;
              pcVar5 = pcVar5 + -1;
            } while (((char *)uStack_e != pcVar5) || (uStack_e._2_2_ != iStack_4));
            unaff_DS = unaff_SS;
          }
          if ((pcVar5 != (char *)uStack_e) || (iStack_4 != uStack_e._2_2_)) {
            pcVar5 = pcVar5 + 1;
          }
          iStack_14 = iStack_14 + -1;
          goto LAB_1d00_152b;
        }
      }
      else if ((6 < iVar3 + -0x49) && (iVar3 + -0x50 < 2)) {
        pcVar6 = pcVar5 + 1;
        iStack_10 = iStack_4;
        if (*pcVar6 != '\0') {
          do {
            if (*pcVar6 == '#') break;
            pcVar6 = pcVar6 + 1;
          } while (*pcVar6 != '\0');
          unaff_DS = unaff_SS;
          pcStack_12 = pcVar5;
        }
        if (*pcVar6 != '\0') {
          iStack_14 = iStack_14 + 1;
          uVar8 = CONCAT22(iStack_8,iStack_14);
          pcVar5 = pcVar6 + 1;
          goto LAB_1d00_152e;
        }
      }
    }
    if (cStack_9 != '\0') {
      uVar4 = FUN_1f8f_004e();
      FUN_1453_0082(0x1e1b,uVar4);
      ReleaseFarBlock((dword)uStack_e);
      FUN_1d00_0170();
      return;
    }
  } while( true );
}

