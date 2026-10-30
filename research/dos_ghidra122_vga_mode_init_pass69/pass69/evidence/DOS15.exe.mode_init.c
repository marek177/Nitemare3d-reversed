
uint __cdecl16far FUN_1156_0a66(void)

{
  code *pcVar1;
  byte bVar2;
  undefined1 uVar3;
  undefined1 extraout_AH;
  uint uVar4;
  
  pcVar1 = (code *)swi(0x10);
  (*pcVar1)();
  out(0x3c4,4);
  bVar2 = in(0x3c5);
  out(0x3c5,bVar2 & 0xf7 | 4);
  out(0x3ce,5);
  bVar2 = in(0x3cf);
  out(0x3cf,bVar2 & 0xef);
  out(0x3ce,6);
  bVar2 = in(0x3cf);
  out(0x3cf,bVar2 & 0xfd);
  FUN_1156_0a3a(0);
  FUN_1156_0a3a(0);
  out(0x3d4,0x14);
  uVar3 = in(0x3d5);
  uVar4 = CONCAT11(extraout_AH,uVar3) & 0xffbf;
  out(0x3d5,(char)uVar4);
  out(0x3d4,0x17);
  uVar3 = in(0x3d5);
  uVar4 = CONCAT11((char)(uVar4 >> 8),uVar3) | 0x40;
  out(0x3d5,(char)uVar4);
  return uVar4;
}

