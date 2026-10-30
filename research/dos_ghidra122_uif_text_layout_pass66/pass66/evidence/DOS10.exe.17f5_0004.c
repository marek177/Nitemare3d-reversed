
void __cdecl16far FUN_17f5_0004(void)

{
  undefined2 uVar1;
  int iVar2;
  int in_DX;
  char *pcVar3;
  undefined2 uVar5;
  undefined4 uVar4;
  
  uVar1 = FUN_1273_016c(0x10001);
  FUN_1155_0a3c(uVar1);
  FUN_1cdc_016a();
  uVar1 = FUN_1273_016c(0x1000e);
  FUN_1cdc_0116(0x28ffff,(char *)s__3Nitemare_3D_3360_12a6 + 2,(undefined1 *)&DAT_3360_3360,uVar1);
  FUN_1cdc_016a();
  uVar1 = FUN_1273_016c(0x1000e);
  FUN_1cdc_0116(0x3cffff,0x12b4,(undefined1 *)&DAT_3360_3360,uVar1);
  uVar1 = FUN_1273_016c(0x1000c);
  FUN_1cdc_0116(0x64ffff,(char *)s_Distributed_by_3360_12b9,(undefined1 *)&DAT_3360_3360,uVar1);
  uVar1 = FUN_1273_016c(0x1000c);
  uVar1 = FUN_17f5_2966(2,uVar1);
  FUN_1cdc_0116(0x73ffff,uVar1,in_DX);
  iVar2 = FUN_17f5_2966();
  if (in_DX == 0 && iVar2 == 0) {
    uVar5 = 1;
    uVar1 = FUN_1273_016c(0x10004);
    uVar4 = CONCAT22(uVar5,uVar1);
    pcVar3 = (char *)s_Shareware_version_3360_12e0;
  }
  else {
    uVar5 = 1;
    uVar1 = FUN_1273_016c(0x10004);
    uVar4 = CONCAT22(uVar5,uVar1);
    pcVar3 = (char *)s_Not_for_re_distribution_3360_12c8;
  }
  FUN_1cdc_0116(0x8cffff,pcVar3,(undefined1 *)&DAT_3360_3360,uVar4);
  uVar1 = FUN_1273_016c(0x10006);
  FUN_1cdc_0116(0xa0ffff,(char *)s_Copyright_1994__David_P__Gray__3360_12f2,
                (undefined1 *)&DAT_3360_3360,uVar1);
  FUN_1cdc_016a();
  return;
}

