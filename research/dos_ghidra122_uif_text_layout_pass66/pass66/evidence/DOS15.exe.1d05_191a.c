
char __cdecl16far FUN_1d05_191a(char *param_1)

{
  int *piVar1;
  char cVar2;
  byte bVar3;
  int iVar4;
  uint uVar5;
  uint extraout_DX;
  char *pcVar6;
  char *pcVar7;
  undefined2 uVar8;
  undefined2 uVar9;
  uint local_a;
  char *local_8;
  uint uStack_6;
  char local_4;
  
  local_4 = '\0';
  FUN_1d05_016e();
  pcVar7 = (char *)param_1;
  if (*param_1 != '\0') {
    do {
      pcVar6 = pcVar7;
      FUN_1d05_009a();
      FUN_1d05_1720(pcVar6,param_1._2_2_);
      pcVar7 = pcVar6 + 0x12;
    } while (pcVar6[0x12] != '\0');
    _local_8 = (char *)CONCAT22(param_1._2_2_,pcVar6);
  }
  local_a = param_1._2_2_;
  cVar2 = *param_1;
  pcVar7 = (char *)param_1;
  while ((cVar2 != '\0' && (pcVar7[4] == '\0'))) {
    pcVar7 = pcVar7 + 0x12;
    cVar2 = *pcVar7;
  }
  uVar5 = param_1._2_2_;
  if (*pcVar7 == '\0') {
    FUN_1f94_0000();
  }
  uVar8 = (undefined2)((ulong)_local_8 >> 0x10);
  if (pcVar7[5] == '\x06') {
    pcVar7 = (char *)FUN_1d05_1888(param_1,(char *)_local_8,uVar8,pcVar7,param_1._2_2_,1);
    local_a = uVar5;
  }
  do {
    bVar3 = FUN_168f_03c4();
    if (bVar3 == 0x50) {
      uVar9 = 1;
LAB_1d05_1aa0:
      pcVar7 = (char *)FUN_1d05_1888(param_1,(char *)_local_8,uVar8,pcVar7,local_a,uVar9);
      local_a = uVar5;
    }
    else if (bVar3 < 0x51) {
      if (bVar3 == 0x20) {
LAB_1d05_1a14:
        cVar2 = pcVar7[5];
        if (cVar2 == '\x01') {
          local_4 = '\x01';
        }
        else if (cVar2 == '\x02') {
          pcVar7[2] = pcVar7[2] ^ 1;
        }
        else if (cVar2 == '\x03') {
          *(int *)(pcVar7 + 2) = -*(int *)(pcVar7 + 2);
        }
        else if (cVar2 == '\x04') {
          local_4 = FUN_1d05_0f22(pcVar7);
        }
      }
      else {
        if ((char)bVar3 < '!') {
          if (bVar3 != 0xd) {
            if (bVar3 == 0x1b) {
              return '\x06';
            }
            goto LAB_1d05_1ab8;
          }
          goto LAB_1d05_1a14;
        }
        if (bVar3 == 0x48) {
          uVar9 = 0xffff;
          goto LAB_1d05_1aa0;
        }
        if (((bVar3 != 0x4b) && (bVar3 != 0x4d)) || (pcVar7[5] != '\x03')) goto LAB_1d05_1ab8;
        uVar5 = (int)*(uint *)(pcVar7 + 2) >> 0xf;
        *(uint *)(pcVar7 + 2) = (*(uint *)(pcVar7 + 2) ^ uVar5) - uVar5;
        if (bVar3 == 0x4b) {
          iVar4 = -5;
        }
        else {
          iVar4 = 5;
        }
        piVar1 = (int *)(pcVar7 + 2);
        *piVar1 = *piVar1 + iVar4;
        if (*piVar1 < 0) {
          (pcVar7 + 2)[0] = '\0';
          (pcVar7 + 2)[1] = '\0';
        }
        if (100 < *(int *)(pcVar7 + 2)) {
          (pcVar7 + 2)[0] = 'd';
          (pcVar7 + 2)[1] = '\0';
        }
      }
      FUN_1d05_1720(pcVar7);
    }
LAB_1d05_1ab8:
    if (*(long *)(pcVar7 + 6) != 0) {
      (**(code **)(pcVar7 + 6))();
      uVar5 = extraout_DX;
    }
    if (local_4 != '\0') {
      return *pcVar7;
    }
  } while( true );
}

