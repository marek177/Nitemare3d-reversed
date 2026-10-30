
void __cdecl16far FUN_1817_0004(void)

{
  undefined2 uVar1;
  int iVar2;
  int in_DX;
  char *pcVar3;
  undefined2 uVar5;
  undefined4 uVar4;
  
  uVar1 = FUN_1275_0160(0x10001);
  FUN_1155_0a3c(uVar1);
  FUN_1d00_016e();
  uVar1 = FUN_1275_0160(0x1000e);
  FUN_1d00_011a(0x28ffff,(char *)s_3Nitemare_3D_3395_1375 + 1,0x3395,uVar1);
  FUN_1d00_016e();
  uVar1 = FUN_1275_0160(0x1000e);
  FUN_1d00_011a(0x3cffff,0x1382,0x3395,uVar1);
  uVar1 = FUN_1275_0160(0x1000c);
  FUN_1d00_011a(0x64ffff,(char *)s_Distributed_by_3395_1387,0x3395,uVar1);
  uVar1 = FUN_1275_0160(0x1000c);
  uVar1 = FUN_1817_2966(2,uVar1);
  FUN_1d00_011a(0x73ffff,uVar1,in_DX);
  iVar2 = FUN_1817_2966();
  if (in_DX == 0 && iVar2 == 0) {
    uVar5 = 1;
    uVar1 = FUN_1275_0160(0x10004);
    uVar4 = CONCAT22(uVar5,uVar1);
    pcVar3 = (char *)s_Shareware_version_3395_13ae;
  }
  else {
    uVar5 = 1;
    uVar1 = FUN_1275_0160(0x10004);
    uVar4 = CONCAT22(uVar5,uVar1);
    pcVar3 = (char *)s_Not_for_re_distribution_3395_1396;
  }
  FUN_1d00_011a(0x8cffff,pcVar3,0x3395,uVar4);
  uVar1 = FUN_1275_0160(0x10006);
  FUN_1d00_011a(0xa0ffff,(char *)s_Copyright_1994__David_P__Gray__3395_13c0,0x3395,uVar1);
  FUN_1d00_016e();
  return;
}

