
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
  char *pcVar4;
  char *pcVar5;
  undefined2 uVar6;
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
  FUN_1d05_016e();
  iStack_8 = 1;
  iStack_14 = 1;
  pcVar7 = (char *)BsfDispatchMode(bsfMode);
  uVar6 = (undefined2)((ulong)pcVar7 >> 0x10);
  pcVar5 = (char *)pcVar7;
  uStack_e = (char *)CONCAT22(uVar6,(char *)uStack_e);
  cVar2 = *pcVar7;
  pcVar4 = pcVar5;
  pcVar1 = uStack_e;
  while (cVar2 != '\0') {
    if (*pcVar4 == '#') {
      iStack_8 = iStack_8 + 1;
    }
    pcVar4 = pcVar4 + 1;
    pcVar1 = pcVar7;
    cVar2 = *pcVar4;
  }
  uStack_e._2_2_ = (int)((ulong)pcVar1 >> 0x10);
  iStack_4 = uStack_e._2_2_;
  uStack_e = pcVar1;
  pcStack_6 = pcVar5;
  FUN_1156_0254();
  FUN_1277_1600();
  func_0x0001e2b4(0x1277,pcVar5,uStack_e._2_2_,1,iStack_8);
  FUN_1156_0254();
  FUN_1277_1600();
  uStack_e = (char *)CONCAT22(uStack_e._2_2_,pcVar5);
  pcVar4 = pcStack_6;
  do {
    uVar6 = 0x168f;
    cVar2 = FUN_168f_03c4();
    iVar3 = (int)cVar2;
    if (iVar3 == 0x44) {
      FUN_1d05_0532(0x1da1,unaff_DS);
      FUN_1bba_00b2();
      FUN_21c7_2790(auStack_9c,0x1de1);
      uVar6 = 0x21c7;
      FUN_21c7_38ea();
LAB_1d05_1529:
      uVar8 = CONCAT22(iStack_8,iStack_14);
LAB_1d05_152c:
      func_0x0001e2b4(uVar6,pcVar4,iStack_4,uVar8);
    }
    else if (iVar3 < 0x45) {
      if (iVar3 == 0x1b) {
        cStack_9 = '\x01';
      }
    }
    else if (0x47 < iVar3) {
      if (iVar3 == 0x49 || iVar3 + -0x48 < 1) {
        if ((pcVar4 != (char *)uStack_e) || (iStack_4 != uStack_e._2_2_)) {
          pcVar4 = pcVar4 + -2;
          if ((pcVar4 != (char *)uStack_e) || (iStack_4 != uStack_e._2_2_)) {
            do {
              if (*pcVar4 == '#') break;
              pcVar4 = pcVar4 + -1;
            } while (((char *)uStack_e != pcVar4) || (uStack_e._2_2_ != iStack_4));
            unaff_DS = unaff_SS;
          }
          if ((pcVar4 != (char *)uStack_e) || (iStack_4 != uStack_e._2_2_)) {
            pcVar4 = pcVar4 + 1;
          }
          iStack_14 = iStack_14 + -1;
          goto LAB_1d05_1529;
        }
      }
      else if ((6 < iVar3 + -0x49) && (iVar3 + -0x50 < 2)) {
        pcVar5 = pcVar4 + 1;
        iStack_10 = iStack_4;
        if (*pcVar5 != '\0') {
          do {
            if (*pcVar5 == '#') break;
            pcVar5 = pcVar5 + 1;
          } while (*pcVar5 != '\0');
          unaff_DS = unaff_SS;
          pcStack_12 = pcVar4;
        }
        if (*pcVar5 != '\0') {
          iStack_14 = iStack_14 + 1;
          uVar8 = CONCAT22(iStack_8,iStack_14);
          pcVar4 = pcVar5 + 1;
          goto LAB_1d05_152c;
        }
      }
    }
    if (cStack_9 != '\0') {
      uVar6 = FUN_1f94_004c();
      FUN_1458_007a(0x1ded,uVar6);
      ReleaseFarBlock((dword)uStack_e);
      FUN_1d05_016e();
      return;
    }
  } while( true );
}

