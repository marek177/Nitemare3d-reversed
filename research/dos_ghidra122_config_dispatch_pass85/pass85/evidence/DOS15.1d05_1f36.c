
void __cdecl16far FUN_1d05_1f36(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  char cVar3;
  byte bVar4;
  int iVar5;
  undefined4 *puVar6;
  char *pcVar7;
  undefined4 *puVar8;
  undefined2 unaff_SS;
  undefined2 uVar9;
  undefined4 local_16;
  char local_12;
  char cStack_11;
  char local_10;
  char local_f;
  bool local_e;
  bool local_d;
  bool local_c;
  bool local_b;
  char *local_6;
  undefined2 local_4;
  
  puVar8 = &local_16;
  puVar6 = (undefined4 *)&DAT_374a_4072;
  for (iVar5 = 4; iVar5 != 0; iVar5 = iVar5 + -1) {
    puVar2 = puVar8;
    puVar8 = puVar8 + 1;
    puVar1 = puVar6;
    puVar6 = puVar6 + 1;
    *puVar2 = *puVar1;
  }
  local_6 = (char *)s_J7Unfortunately_the_blast_impact_374a_11a8 + 0x6a;
  local_4 = DAT_374a_252a;
  uVar9 = 0x374a;
  if (((char *)s_J7Unfortunately_the_blast_impact_374a_11a8)[0x6a] != '\0') {
    pcVar7 = (char *)s_J7Unfortunately_the_blast_impact_374a_11a8 + 0x6a;
    do {
      cVar3 = *pcVar7;
      if (cVar3 == '\n') {
        local_e = 0 < *(int *)(pcVar7 + 2);
        bVar4 = (byte)((int)*(undefined2 *)(pcVar7 + 2) >> 0xf);
        local_12 = ((byte)*(undefined2 *)(pcVar7 + 2) ^ bVar4) - bVar4;
      }
      else if (cVar3 == '\v') {
        local_b = 0 < *(int *)(pcVar7 + 2);
        bVar4 = (byte)((int)*(undefined2 *)(pcVar7 + 2) >> 0xf);
        cStack_11 = ((byte)*(undefined2 *)(pcVar7 + 2) ^ bVar4) - bVar4;
      }
      else if (cVar3 == '\f') {
        local_c = 0 < *(int *)(pcVar7 + 2);
        bVar4 = (byte)((int)*(undefined2 *)(pcVar7 + 2) >> 0xf);
        local_f = ((byte)*(undefined2 *)(pcVar7 + 2) ^ bVar4) - bVar4;
      }
      else if (cVar3 == '\r') {
        local_d = 0 < *(int *)(pcVar7 + 2);
        bVar4 = (byte)((int)*(undefined2 *)(pcVar7 + 2) >> 0xf);
        local_10 = ((byte)*(undefined2 *)(pcVar7 + 2) ^ bVar4) - bVar4;
      }
      pcVar7 = pcVar7 + 0x12;
    } while (*pcVar7 != '\0');
    uVar9 = unaff_SS;
  }
  if ((local_d == false) && (*(char *)&DAT_374a_407b != '\0')) {
    FUN_1c07_0286();
  }
  if ((local_d == false) || (*(char *)&DAT_374a_407b != '\0')) {
    local_4 = local_4 & 0xff;
  }
  else {
    local_4 = CONCAT11(1,(undefined1)local_4);
  }
  if (local_f != *(char *)((int)(undefined4 *)&DAT_374a_4076 + 3)) {
    FUN_1c07_03da(0x2e);
  }
  puVar6 = (undefined4 *)&DAT_374a_4072;
  puVar8 = &local_16;
  for (iVar5 = 4; iVar5 != 0; iVar5 = iVar5 + -1) {
    puVar2 = puVar6;
    puVar6 = puVar6 + 1;
    puVar1 = puVar8;
    puVar8 = puVar8 + 1;
    *puVar2 = *puVar1;
  }
  FUN_168f_0192();
  FUN_1c07_00e0();
  if (local_4._1_1_ != '\0') {
    FUN_1c07_029c();
  }
  return;
}

