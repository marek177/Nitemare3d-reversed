
/* Original wrapper/class lookup96 cases across6 builds. Finds first class3e from start0, then
   forwards(objectIndex,skipFrames,recordOffset) to indexed loader. Numeric p argument is frame skip
   count, not ordinal class match. Missing class reaches fatal. Synthetic class table, indexed
   loader mocked. */

void __cdecl16far LoadClass3eGraphicFrame(short skipFrames,ushort recordOffset)

{
  ushort uVar1;
  
  uVar1 = FindClassAtOrAfter(0x3e,0);
  LoadIndexedGraphicFrame(uVar1 & 0xff,skipFrames,recordOffset);
  return;
}

