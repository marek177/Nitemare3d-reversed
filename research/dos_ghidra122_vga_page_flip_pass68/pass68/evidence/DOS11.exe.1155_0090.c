
undefined2 __cdecl16far FUN_1155_0090(void)

{
  undefined2 uVar1;
  
  uVar1 = DAT_3395_012c;
  LOCK();
  DAT_3395_012c = DAT_3395_012a;
  UNLOCK();
  DAT_3395_012a = uVar1;
  uVar1 = CONCAT11((char)((uint)uVar1 >> 8) << 4,0xc);
  out(0x3d4,uVar1);
  return uVar1;
}

