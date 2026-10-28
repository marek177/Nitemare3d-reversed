
/* If segment!=0: OR1 into byte at segment:(offset-2 mod65536); otherwise no write. Original mode4
   consumer192 cases (pass15), heap reuse180 sequences (pass16). No immediate DOS release/coalesce;
   subsequent allocation can merge adjacent free blocks. Return registers unspecified, treated as
   void. */

void __cdecl16far ReleaseFarBlock(dword blockPointer)

{
  byte *pbVar1;
  int iVar2;
  
  iVar2 = (int)(blockPointer >> 0x10);
  if (iVar2 != 0) {
    pbVar1 = (byte *)((int)blockPointer + -2);
    *pbVar1 = *pbVar1 | 1;
  }
  return;
}

