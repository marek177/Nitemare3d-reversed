
/* Verified original routine1008 cases across6 builds with mocked DOS42. Returns position DX:AX
   orffffffff. Success clears low-level handle text EOF bit02. Global guarded negative offset
   branches observed for origins0..2. Loader ignores failure. */

dword __cdecl16far SeekDosHandle(ushort handle,dword signedOffsetBits,ushort origin)

{
  uint uVar1;
  uint uVar2;
  code *pcVar3;
  undefined2 uVar4;
  uint in_DX;
  uint uVar5;
  uint extraout_DX;
  uint extraout_DX_00;
  undefined2 unaff_DS;
  bool bVar6;
  undefined4 uVar7;
  
  if (*(uint *)0x211a <= handle) goto LAB_21bc_1c54;
  bVar6 = false;
  if (*(int *)0x2322 != 0) {
    bVar6 = false;
    if ((signedOffsetBits & 0x80000000) != 0) {
      if (origin == 0) goto LAB_21bc_1c54;
      bVar6 = false;
      pcVar3 = (code *)swi(0x21);
      uVar7 = (*pcVar3)();
      in_DX = (uint)((ulong)uVar7 >> 0x10);
      if (bVar6) goto LAB_21bc_1c54;
      if ((origin & 2) == 0) {
        uVar1 = (uint)CARRY2((uint)uVar7,(uint)signedOffsetBits);
        bVar6 = CARRY2(in_DX,signedOffsetBits._2_2_) || CARRY2(in_DX + signedOffsetBits._2_2_,uVar1)
        ;
        in_DX = in_DX + signedOffsetBits._2_2_ + uVar1;
        if ((int)in_DX < 0) goto LAB_21bc_1c54;
      }
      else {
        pcVar3 = (code *)swi(0x21);
        uVar7 = (*pcVar3)(in_DX);
        uVar5 = (uint)((ulong)uVar7 >> 0x10);
        uVar1 = (uint)CARRY2((uint)uVar7,(uint)signedOffsetBits);
        uVar2 = uVar5 + signedOffsetBits._2_2_;
        bVar6 = CARRY2(uVar5,signedOffsetBits._2_2_) || CARRY2(uVar2,uVar1);
        if ((int)(uVar2 + uVar1) < 0) {
          pcVar3 = (code *)swi(0x21);
          (*pcVar3)();
          in_DX = extraout_DX;
          goto LAB_21bc_1c54;
        }
      }
    }
  }
  pcVar3 = (code *)swi(0x21);
  (*pcVar3)();
  in_DX = extraout_DX_00;
  if (!bVar6) {
    *(byte *)(handle + 0x211c) = *(byte *)(handle + 0x211c) & 0xfd;
  }
LAB_21bc_1c54:
  uVar4 = FUN_21bc_05b7();
  return CONCAT22(in_DX,uVar4);
}

