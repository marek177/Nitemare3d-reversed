
/* Original near-string sscanf wrapper: input/format near offsets, near destination offsets via
   varargs. Verified204 no-hook cases for %i/%d plus612 original command-parser integrations. 16-bit
   numeric output wraps in tested overflow samples. Initial SPf800 leaves room for original stack
   allocator/bound check. Other formats/float not covered. */

short __cdecl16far SscanfNearString(ushort inputOffset,ushort formatOffset,...)

{
  undefined2 uVar1;
  short sVar2;
  undefined2 unaff_DS;
  undefined1 uStack0008;
  
  *(undefined1 *)0x3c44 = 0x49;
  *(ushort *)0x3c42 = inputOffset;
  *(ushort *)0x3c3e = inputOffset;
  uVar1 = FUN_21bc_2398(inputOffset);
  *(undefined2 *)0x3c40 = uVar1;
  sVar2 = FUN_21bc_0d36(0x3c3e,formatOffset,&uStack0008);
  return sVar2;
}

