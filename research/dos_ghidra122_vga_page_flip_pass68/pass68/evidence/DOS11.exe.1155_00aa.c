
void __cdecl16far FUN_1155_00aa(void)

{
  undefined2 uVar1;
  byte bVar2;
  
  uVar1 = DAT_3395_012c;
  LOCK();
  DAT_3395_012c = DAT_3395_012a;
  UNLOCK();
  DAT_3395_012a = uVar1;
  do {
    bVar2 = in(0x3da);
  } while ((bVar2 & 1) != 0);
  out(0x3d4,CONCAT11((char)((uint)uVar1 >> 8) << 4,0xc));
  do {
    bVar2 = in(0x3da);
  } while ((bVar2 & 8) == 0);
  return;
}

