
void __cdecl16far FUN_1156_00a8(void)

{
  undefined2 uVar1;
  byte bVar2;
  
  uVar1 = DAT_374a_012e;
  LOCK();
  DAT_374a_012e = DAT_374a_012c;
  UNLOCK();
  DAT_374a_012c = uVar1;
  do {
    bVar2 = in(0x3da);
  } while ((bVar2 & 1) != 0);
  out(0x3d4,CONCAT11((char)((uint)uVar1 >> 8) << 4,0xc));
  do {
    bVar2 = in(0x3da);
  } while ((bVar2 & 8) == 0);
  return;
}

