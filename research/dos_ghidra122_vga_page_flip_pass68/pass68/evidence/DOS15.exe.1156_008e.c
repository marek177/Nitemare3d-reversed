
undefined2 __cdecl16far FUN_1156_008e(void)

{
  undefined2 uVar1;
  
  uVar1 = DAT_374a_012e;
  LOCK();
  DAT_374a_012e = DAT_374a_012c;
  UNLOCK();
  DAT_374a_012c = uVar1;
  uVar1 = CONCAT11((char)((uint)uVar1 >> 8) << 4,0xc);
  out(0x3d4,uVar1);
  return uVar1;
}

