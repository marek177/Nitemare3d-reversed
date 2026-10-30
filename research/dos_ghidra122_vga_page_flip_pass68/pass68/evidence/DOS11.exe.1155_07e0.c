
void __cdecl16far
FUN_1155_07e0(char *param_1,uint param_2,uint param_3,undefined2 param_4,int param_5,int param_6,
             int param_7,int param_8,int param_9)

{
  char *pcVar1;
  undefined2 uVar2;
  byte bVar3;
  int iVar4;
  char *pcVar5;
  char *pcVar6;
  undefined2 uVar7;
  bool bVar8;
  char *local_6;
  char *local_4;
  
  uVar2 = DAT_3395_012c;
  if (param_8 != 0) {
    uVar2 = DAT_3395_012a;
  }
  local_4 = (char *)((param_3 & 0xff) * 0x50 + (param_2 >> 2));
  out(0x3c4,2);
  bVar3 = (byte)param_2 & 3;
  bVar3 = '\x11' << bVar3 | 0x11U >> 8 - bVar3;
  out(0x3c5,bVar3);
  uVar7 = (undefined2)((ulong)param_1 >> 0x10);
  local_6 = (char *)param_1;
  if (param_9 < 0) {
    do {
      iVar4 = param_7;
      pcVar5 = local_6;
      pcVar6 = local_4;
      do {
        pcVar1 = pcVar5;
        pcVar5 = pcVar5 + 1;
        *pcVar6 = *pcVar1;
        pcVar6 = pcVar6 + 0x50;
        iVar4 = iVar4 + -1;
      } while (iVar4 != 0);
      bVar8 = (char)bVar3 < '\0';
      bVar3 = bVar3 << 1 | bVar8;
      out(0x3c5,bVar3);
      if (bVar8) {
        local_4 = local_4 + 1;
      }
      local_6 = local_6 + param_5;
      param_6 = param_6 + -1;
    } while (param_6 != 0);
  }
  else {
    do {
      iVar4 = param_7;
      pcVar5 = local_6;
      pcVar6 = local_4;
      do {
        pcVar1 = pcVar5;
        pcVar5 = pcVar5 + 1;
        if (*pcVar1 != (char)param_9) {
          *pcVar6 = *pcVar1;
        }
        pcVar6 = pcVar6 + 0x50;
        iVar4 = iVar4 + -1;
      } while (iVar4 != 0);
      bVar8 = (char)bVar3 < '\0';
      bVar3 = bVar3 << 1 | bVar8;
      out(0x3c5,bVar3);
      if (bVar8) {
        local_4 = local_4 + 1;
      }
      local_6 = local_6 + param_5;
      param_6 = param_6 + -1;
    } while (param_6 != 0);
  }
  return;
}

