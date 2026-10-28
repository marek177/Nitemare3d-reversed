
/* Verified complete loader control flow with mocked OS/allocator dependencies and original decoder:
   reserves length+1, seeks, reads length bytes, writes trailing NUL, closes, decodes and returns
   saved DX:AX buffer. Short/error read results are not checked by this wrapper. OS and allocator
   implementations remain separate scope. */

dword __cdecl16far ReadAndDecodeBsfBlock(ushort filenameOffset,dword fileOffset,ushort byteLength)

{
  ushort handle;
  ushort bufferSegment;
  dword dVar1;
  
  handle = FUN_219b_1d6e();
  if (handle == 0xffff) {
    FUN_1f67_000a();
  }
  dVar1 = AllocateFarBytes(byteLength + 1);
  bufferSegment = (ushort)(dVar1 >> 0x10);
  if (dVar1 == 0) {
    FUN_1f67_000a();
  }
  SeekDosHandle(handle,fileOffset,0);
  FUN_1f67_009c(handle,dVar1,byteLength);
  *(undefined1 *)((ushort)dVar1 + byteLength) = 0;
  FUN_219b_1cb2();
  XorDecodeAndFoldOriginalBytes((ushort)dVar1,bufferSegment,byteLength);
  return dVar1;
}

