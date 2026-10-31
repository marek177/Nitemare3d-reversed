
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl16far FUN_17d7_0352(void)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  undefined4 *puVar4;
  int local_4;
  
  puVar4 = (undefined4 *)&DAT_3754_4124;
  local_4 = 8;
  do {
    uVar1 = (uint)*(byte *)((int)puVar4 + 0x12);
    if (*(char *)(puVar4 + 3) == '\x01') {
      if (*(ulong *)((int)puVar4 + 0x16) <= _DAT_3754_07f0) {
        *(char *)((int)puVar4 + 0x11) = *(char *)((int)puVar4 + 0x11) + '\x01';
        if ((int)((undefined2 *)&DAT_3754_3c8e)[uVar1 * 4] <=
            (int)(uint)*(byte *)((int)puVar4 + 0x11)) {
          *(undefined1 *)((int)puVar4 + 0x11) = 0;
        }
        iVar3 = DAT_3754_07f2 +
                (uint)CARRY2(DAT_3754_07f0,((undefined2 *)&DAT_3754_3c90)[uVar1 * 4]);
        *(int *)((int)puVar4 + 0x16) = DAT_3754_07f0 + ((undefined2 *)&DAT_3754_3c90)[uVar1 * 4];
        *(int *)(puVar4 + 6) = iVar3;
      }
      FUN_17d7_0264(puVar4);
      uVar1 = *(int *)((int)puVar4 + 0x1e) - (int)DAT_3754_40d2;
      uVar2 = (int)uVar1 >> 0xf;
      if ((0x14 < (int)((uVar1 ^ uVar2) - uVar2)) ||
         (uVar1 = *(int *)(puVar4 + 8) - DAT_3754_40d2._2_2_ >> 0xf,
         0x14 < (int)((*(int *)(puVar4 + 8) - DAT_3754_40d2._2_2_ ^ uVar1) - uVar1))) {
LAB_17d7_0427:
        FUN_1ad0_0434((int)puVar4 + 0xe,0x3754);
      }
    }
    else if (*(char *)(puVar4 + 3) == '\x02') {
      if (*(ulong *)((int)puVar4 + 0x16) <= _DAT_3754_07f0) {
        *(char *)((int)puVar4 + 0x11) = *(char *)((int)puVar4 + 0x11) + '\x01';
        iVar3 = DAT_3754_07f2 +
                (uint)CARRY2(DAT_3754_07f0,((undefined2 *)&DAT_3754_3c90)[uVar1 * 4]);
        *(int *)((int)puVar4 + 0x16) = DAT_3754_07f0 + ((undefined2 *)&DAT_3754_3c90)[uVar1 * 4];
        *(int *)(puVar4 + 6) = iVar3;
      }
      if ((int)(uint)*(byte *)((int)puVar4 + 0x11) < (int)((undefined2 *)&DAT_3754_3c8e)[uVar1 * 4])
      goto LAB_17d7_0427;
      *(undefined1 *)(puVar4 + 3) = 0;
    }
    puVar4 = (undefined4 *)((int)puVar4 + 0x2a);
    local_4 = local_4 + -1;
    if (local_4 == 0) {
      return;
    }
  } while( true );
}

