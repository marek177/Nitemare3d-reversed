
void __cdecl16far FUN_181c_000e(void)

{
  undefined2 uVar1;
  int iVar2;
  int in_DX;
  char *pcVar3;
  undefined2 uVar5;
  undefined4 uVar4;
  
  uVar1 = FUN_1277_0188(0x10001);
  FUN_1156_0a3a(uVar1);
  FUN_1d05_016e();
  uVar1 = FUN_1277_0188(0x1000e);
  FUN_1d05_011a(0x28ffff,(char *)s_J7Nitemare_3D_374a_136a + 2,0x374a,uVar1);
  FUN_1d05_016e();
  uVar1 = FUN_1277_0188(0x1000e);
  FUN_1d05_011a(0x3cffff,0x1378,0x374a,uVar1);
  uVar1 = FUN_1277_0188(0x1000c);
  FUN_1d05_011a(0x64ffff,(char *)s_Distributed_by_374a_137d,0x374a,uVar1);
  uVar1 = FUN_1277_0188(0x1000c);
  uVar1 = FUN_181c_299e(2,uVar1);
  FUN_1d05_011a(0x73ffff,uVar1,in_DX);
  iVar2 = FUN_181c_299e();
  if (in_DX == 0 && iVar2 == 0) {
    uVar5 = 1;
    uVar1 = FUN_1277_0188(0x10004);
    uVar4 = CONCAT22(uVar5,uVar1);
    pcVar3 = (char *)s_Shareware_version_374a_13a0;
  }
  else {
    uVar5 = 1;
    uVar1 = FUN_1277_0188(0x10004);
    uVar4 = CONCAT22(uVar5,uVar1);
    pcVar3 = (char *)s_Registered_software_374a_138c;
  }
  FUN_1d05_011a(0x8cffff,pcVar3,0x374a,uVar4);
  uVar1 = FUN_1277_0188(0x10006);
  FUN_1d05_011a(0xa0ffff,(char *)s_Copyright_1994__David_P__Gray__374a_13b2,0x374a,uVar1);
  FUN_1d05_016e();
  return;
}

