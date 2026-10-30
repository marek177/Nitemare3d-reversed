
void __cdecl16far FUN_1d05_0532(char *param_1,int *param_2)

{
  int iVar1;
  undefined2 uVar2;
  int in_DX;
  char *pcVar3;
  int iVar4;
  int local_12;
  int local_10;
  undefined4 local_c;
  
  FUN_1d05_016e();
  iVar1 = FUN_21c7_3c3a();
  if (in_DX == 0 && iVar1 == 0) {
    local_12 = FUN_1d05_0034((char *)param_1,param_1._2_2_);
  }
  else {
    local_12 = 0;
  }
  local_10 = 0xb;
  local_c = param_1;
  if (*param_1 != '\0') {
    pcVar3 = (char *)param_1;
    do {
      if (*pcVar3 == '\n') {
        *pcVar3 = '\0';
        iVar1 = FUN_1d05_0034(local_c);
        if (local_12 < iVar1) {
          local_12 = iVar1;
        }
        local_10 = local_10 + 0xb;
        *pcVar3 = '\n';
        local_c = (char *)CONCAT22(param_1._2_2_,pcVar3 + 1);
      }
      pcVar3 = pcVar3 + 1;
    } while (*pcVar3 != '\0');
  }
  iVar1 = FUN_1d05_0034(local_c);
  if (local_12 < iVar1) {
    local_12 = iVar1;
  }
  iVar1 = -(local_12 / 2 - DAT_374a_447c);
  iVar4 = DAT_374a_447e - local_10 / 2;
  uVar2 = FUN_1277_0188(0x10008);
  FUN_1156_097c(iVar1 + -8,iVar4 + -8,local_12 + 0x10,local_10 + 0x10,uVar2);
  local_c = param_1;
  if (*param_1 != '\0') {
    do {
      if (*(char *)param_1 == '\n') {
        *(char *)param_1 = '\0';
        uVar2 = FUN_1277_0188(0x1000e);
        FUN_1d05_011a(iVar1,iVar4,local_c,uVar2);
        iVar4 = iVar4 + 0xb;
        *(char *)param_1 = '\n';
        local_c = (char *)CONCAT22(param_1._2_2_,(char *)param_1 + 1);
      }
      param_1._0_2_ = (char *)param_1 + 1;
    } while (*(char *)param_1 != '\0');
  }
  uVar2 = FUN_1277_0188(0x1000e);
  FUN_1d05_011a(iVar1,iVar4,local_c,uVar2);
  *param_2 = iVar1;
  param_2[1] = iVar4;
  param_2[2] = local_12;
  param_2[3] = local_10;
  return;
}

