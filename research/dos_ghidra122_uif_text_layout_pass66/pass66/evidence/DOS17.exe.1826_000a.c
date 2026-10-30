
void __cdecl16far FUN_1826_000a(void)

{
  undefined2 uVar1;
  int iVar2;
  int in_DX;
  char *pcVar3;
  undefined2 uVar5;
  undefined4 uVar4;
  
  uVar1 = FUN_1277_0188(0x10001);
  FUN_1156_0a3a(uVar1);
  FUN_1d0f_016a();
  uVar1 = FUN_1277_0188(0x1000e);
  FUN_1d0f_0116(0x28ffff,(char *)s_T7Nitemare_3D_3754_136e + 2,0x3754,uVar1);
  FUN_1d0f_016a();
  uVar1 = FUN_1277_0188(0x1000e);
  FUN_1d0f_0116(0x3cffff,0x137c,0x3754,uVar1);
  uVar1 = FUN_1277_0188(0x1000c);
  FUN_1d0f_0116(0x64ffff,(char *)s_Distributed_by_3754_1381,0x3754,uVar1);
  uVar1 = FUN_1277_0188(0x1000c);
  uVar1 = FUN_1826_299a(2,uVar1);
  FUN_1d0f_0116(0x73ffff,uVar1,in_DX);
  iVar2 = FUN_1826_299a();
  if (in_DX == 0 && iVar2 == 0) {
    uVar5 = 1;
    uVar1 = FUN_1277_0188(0x10004);
    uVar4 = CONCAT22(uVar5,uVar1);
    pcVar3 = (char *)s_Shareware_version_3754_13a4;
  }
  else {
    uVar5 = 1;
    uVar1 = FUN_1277_0188(0x10004);
    uVar4 = CONCAT22(uVar5,uVar1);
    pcVar3 = (char *)s_Registered_software_3754_1390;
  }
  FUN_1d0f_0116(0x8cffff,pcVar3,0x3754,uVar4);
  uVar1 = FUN_1277_0188(0x10006);
  FUN_1d0f_0116(0xa0ffff,(char *)s_Copyright_1994__David_P__Gray__3754_13b6,0x3754,uVar1);
  FUN_1d0f_016a();
  return;
}

