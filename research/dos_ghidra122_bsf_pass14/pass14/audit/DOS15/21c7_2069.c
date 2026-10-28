
/* Original allocator returns far pointer DX:AX or0. Empty-heap tests132 across6 builds:
   sizes0..ffe8 accepted under mocked DOS allocation, >ffe8 rejected; size0 may return nonnull. Null
   failure handler, original heap init/split, DOS48 mocked. Existing-heap/retry-handler behavior
   remains unverified. */

dword __cdecl16far AllocateFarBytes(ushort byteCount)

{
  undefined4 *puVar1;
  int iVar2;
  int in_BX;
  uint uVar3;
  code *pcVar4;
  undefined2 uVar5;
  undefined2 unaff_DS;
  uint uVar6;
  bool bVar7;
  bool bVar8;
  dword dVar9;
  uint uVar10;
  
  uVar5 = 0x21c7;
  do {
    if (byteCount < 0xffe9) {
      bVar7 = false;
      if (*(int *)0x22f8 != 0) {
        pcVar4 = (code *)0x216c;
        while( true ) {
          uVar3 = *(uint *)0x2300;
          uVar6 = (uint)((ulong)*(undefined4 *)0x22fa >> 0x10);
          in_BX = (int)*(undefined4 *)0x22fa;
          do {
            uVar10 = uVar6;
            do {
              uVar5 = 0x2000;
              dVar9 = (*pcVar4)();
              if (!bVar7) {
                if (pcVar4 != (code *)0x216c) goto LAB_21c7_20d0;
                goto LAB_21c7_20d3;
              }
              puVar1 = (undefined4 *)(in_BX + 0xc);
              in_BX = (int)*puVar1;
              bVar7 = uVar6 < uVar3;
              bVar8 = uVar6 != uVar3;
              uVar6 = (uint)((ulong)*puVar1 >> 0x10);
            } while (bVar8);
            uVar3 = *(uint *)((int)*(undefined4 *)0x22fa + 0x12);
            uVar6 = (uint)((ulong)*(undefined4 *)0x22f6 >> 0x10);
            in_BX = (int)*(undefined4 *)0x22f6;
            bVar7 = uVar6 < uVar10;
          } while (uVar6 != uVar10);
          bVar7 = pcVar4 < (code *)0x21e8;
          if (pcVar4 == (code *)0x21e8) break;
          pcVar4 = (code *)0x21e8;
        }
      }
      FUN_21c7_22e6();
      if (!bVar7) {
LAB_21c7_20d0:
        dVar9 = FUN_21c7_216c();
LAB_21c7_20d3:
        *(undefined2 *)0x22fc = (int)(dVar9 >> 0x10);
        *(int *)0x22fa = in_BX;
        return dVar9;
      }
    }
    if (*(int *)0x22f4 == 0 && *(int *)0x22f2 == 0) {
      return 0;
    }
    iVar2 = (*(code *)*(undefined2 *)0x22f2)(uVar5,byteCount);
    if (iVar2 == 0) {
      return 0;
    }
  } while( true );
}

