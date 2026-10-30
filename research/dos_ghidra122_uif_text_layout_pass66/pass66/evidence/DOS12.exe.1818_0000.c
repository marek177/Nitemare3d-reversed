
void __cdecl16far FUN_1818_0000(void)

{
  undefined2 uVar1;
  int iVar2;
  int in_DX;
  char *pcVar3;
  undefined2 uVar5;
  undefined4 uVar4;
  
  uVar1 = FUN_1275_0160(0x10001);
  FUN_1155_0a3c(uVar1);
  FUN_1d00_0170();
  uVar1 = FUN_1275_0160(0x1000e);
  FUN_1d00_011c(0x28ffff,(char *)s_3Nitemare_3D_339b_1365 + 1,0x339b,uVar1);
  FUN_1d00_0170();
  uVar1 = FUN_1275_0160(0x1000e);
  FUN_1d00_011c(0x3cffff,0x1372,0x339b,uVar1);
  uVar1 = FUN_1275_0160(0x1000c);
  FUN_1d00_011c(0x64ffff,(char *)s_Distributed_by_339b_1377,0x339b,uVar1);
  uVar1 = FUN_1275_0160(0x1000c);
  uVar1 = FUN_1818_2958(2,uVar1);
  FUN_1d00_011c(0x73ffff,uVar1,in_DX);
  iVar2 = FUN_1818_2958();
  if (in_DX == 0 && iVar2 == 0) {
    uVar5 = 1;
    uVar1 = FUN_1275_0160(0x10004);
    uVar4 = CONCAT22(uVar5,uVar1);
    pcVar3 = (char *)s_Shareware_version_339b_139e;
  }
  else {
    uVar5 = 1;
    uVar1 = FUN_1275_0160(0x10004);
    uVar4 = CONCAT22(uVar5,uVar1);
    pcVar3 = (char *)s_Not_for_re_distribution_339b_1386;
  }
  FUN_1d00_011c(0x8cffff,pcVar3,0x339b,uVar4);
  uVar1 = FUN_1275_0160(0x10006);
  FUN_1d00_011c(0xa0ffff,(char *)s_Copyright_1994__David_P__Gray__339b_13b0,0x339b,uVar1);
  FUN_1d00_0170();
  return;
}

