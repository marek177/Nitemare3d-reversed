
undefined2 __cdecl16far FUN_1155_0090(void)

{
  undefined2 uVar1;
  
  uVar1 = DAT_339b_012c;
  LOCK();
  DAT_339b_012c = DAT_339b_012a;
  UNLOCK();
  DAT_339b_012a = uVar1;
  uVar1 = CONCAT11((char)((uint)uVar1 >> 8) << 4,0xc);
  out(0x3d4,uVar1);
  return uVar1;
}

