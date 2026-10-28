
/* Far allocator DX:AX or0. Verified empty heap132 cases (pass14) plus180 original alloc/free
   sequences (pass16): released-block reuse, split, adjacent coalescing during allocation,
   larger-request growth and failed-growth recovery. Only DOS48 mocked; failure callback null. Not
   exhaustive arbitrary heap validation. */

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
  
  uVar5 = 0x21ea;
  do {
    if (byteCount < 0xffe9) {
      bVar7 = false;
      if (*(int *)0x2336 != 0) {
        pcVar4 = (code *)0x216c;
        while( true ) {
          uVar3 = *(uint *)0x233e;
          uVar6 = (uint)((ulong)*(undefined4 *)0x2338 >> 0x10);
          in_BX = (int)*(undefined4 *)0x2338;
          do {
            uVar10 = uVar6;
            do {
              uVar5 = 0x2000;
              dVar9 = (*pcVar4)();
              if (!bVar7) {
                if (pcVar4 != (code *)0x216c) goto LAB_21ea_20d0;
                goto LAB_21ea_20d3;
              }
              puVar1 = (undefined4 *)(in_BX + 0xc);
              in_BX = (int)*puVar1;
              bVar7 = uVar6 < uVar3;
              bVar8 = uVar6 != uVar3;
              uVar6 = (uint)((ulong)*puVar1 >> 0x10);
            } while (bVar8);
            uVar3 = *(uint *)((int)*(undefined4 *)0x2338 + 0x12);
            uVar6 = (uint)((ulong)*(undefined4 *)0x2334 >> 0x10);
            in_BX = (int)*(undefined4 *)0x2334;
            bVar7 = uVar6 < uVar10;
          } while (uVar6 != uVar10);
          bVar7 = pcVar4 < (code *)0x21e8;
          if (pcVar4 == (code *)0x21e8) break;
          pcVar4 = (code *)0x21e8;
        }
      }
      FUN_21ea_22e6();
      if (!bVar7) {
LAB_21ea_20d0:
        dVar9 = FUN_21ea_216c();
LAB_21ea_20d3:
        *(undefined2 *)0x233a = (int)(dVar9 >> 0x10);
        *(int *)0x2338 = in_BX;
        return dVar9;
      }
    }
    if (*(int *)0x2332 == 0 && *(int *)0x2330 == 0) {
      return 0;
    }
    iVar2 = (*(code *)*(undefined2 *)0x2330)(uVar5,byteCount);
    if (iVar2 == 0) {
      return 0;
    }
  } while( true );
}

