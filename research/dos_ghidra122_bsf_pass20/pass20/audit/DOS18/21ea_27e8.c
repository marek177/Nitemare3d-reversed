
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
  
  *(undefined1 *)0x3ca4 = 0x49;
  *(ushort *)0x3ca2 = inputOffset;
  *(ushort *)0x3c9e = inputOffset;
  uVar1 = FUN_21ea_239c(inputOffset);
  *(undefined2 *)0x3ca0 = uVar1;
  sVar2 = FUN_21ea_0d3a(0x3c9e,formatOffset,&uStack0008);
  return sVar2;
}

