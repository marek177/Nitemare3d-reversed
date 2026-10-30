
undefined2 __cdecl16far FUN_1156_008e(void)

{
  undefined2 uVar1;
  
  uVar1 = DAT_3754_012e;
  LOCK();
  DAT_3754_012e = DAT_3754_012c;
  UNLOCK();
  DAT_3754_012c = uVar1;
  uVar1 = CONCAT11((char)((uint)uVar1 >> 8) << 4,0xc);
  out(0x3d4,uVar1);
  return uVar1;
}

