
/* WARNING: Removing unreachable block (ram,0x00023c0c) */

uint __cdecl16far FUN_21ea_1c76(undefined2 param_1,uint param_2,uint param_3)

{
  code *pcVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  byte bVar5;
  uint uVar6;
  uint extraout_DX;
  bool bVar7;
  undefined1 uVar8;
  bool bVar9;
  byte local_6;
  char local_4;
  
  uVar4 = (uint)_local_4 >> 8;
  local_4 = '\0';
  local_6 = 0;
  if (((param_2 & 0x8000) == 0) && (((param_2 & 0x4000) != 0 || ((DAT_376d_232b & 0x80) == 0)))) {
    local_6 = 0x80;
  }
  bVar7 = false;
  pcVar1 = (code *)swi(0x21);
  uVar6 = param_2;
  uVar2 = (*pcVar1)();
  if (bVar7) {
    if ((uVar2 != 2) || ((uVar6 & 0x100) == 0)) goto LAB_21ea_1cba;
    bVar7 = false;
    local_4 = '\x03';
    FUN_21ea_1e07();
    uVar8 = 0;
    uVar6 = 0;
LAB_21ea_1d76:
    pcVar1 = (code *)swi(0x21);
    uVar2 = (*pcVar1)();
    if ((bool)uVar8) {
LAB_21ea_1d7f:
      uVar4 = FUN_21ea_05bb();
      return uVar4;
    }
    if ((local_4 != '\0') || ((param_2 & 2) == 0)) {
      pcVar1 = (code *)swi(0x21);
      (*pcVar1)();
      bVar9 = false;
      pcVar1 = (code *)swi(0x21);
      uVar2 = (*pcVar1)();
      if (bVar9) goto LAB_21ea_1d7f;
      if ((!bVar7) && ((param_3 & 1) != 0)) {
        bVar7 = false;
        uVar6 = (uint)(byte)((byte)uVar6 | 1);
        pcVar1 = (code *)swi(0x21);
        (*pcVar1)();
        if (bVar7) goto LAB_21ea_1d7f;
      }
    }
  }
  else {
    if ((uVar6 & 0x500) == 0x500) {
      pcVar1 = (code *)swi(0x21);
      (*pcVar1)();
      goto LAB_21ea_1cba;
    }
    bVar7 = true;
    pcVar1 = (code *)swi(0x21);
    (*pcVar1)();
    if ((extraout_DX & 0x80) != 0) {
      local_6 = local_6 | 0x40;
    }
    if ((local_6 & 0x40) == 0) {
      if ((param_2 & 0x200) == 0) {
        if (((local_6 & 0x80) != 0) && ((param_2 & 2) != 0)) {
          pcVar1 = (code *)swi(0x21);
          (*pcVar1)();
          pcVar1 = (code *)swi(0x21);
          iVar3 = (*pcVar1)();
          if ((iVar3 != 0) && ((char)uVar4 == '\x1a')) {
            pcVar1 = (code *)swi(0x21);
            (*pcVar1)();
            pcVar1 = (code *)swi(0x21);
            (*pcVar1)();
          }
          uVar6 = 0;
          pcVar1 = (code *)swi(0x21);
          (*pcVar1)();
        }
      }
      else {
        uVar8 = 0;
        if ((param_2 & 3) == 0) {
          pcVar1 = (code *)swi(0x21);
          (*pcVar1)();
          pcVar1 = (code *)swi(0x21);
          (*pcVar1)();
          goto LAB_21ea_1d76;
        }
        uVar6 = 0;
        pcVar1 = (code *)swi(0x21);
        (*pcVar1)();
      }
    }
  }
  if ((local_6 & 0x40) == 0) {
    pcVar1 = (code *)swi(0x21);
    (*pcVar1)();
    bVar5 = 0;
    if ((uVar6 & 1) != 0) {
      bVar5 = 0x10;
    }
    if ((param_2 & 8) != 0) {
      bVar5 = bVar5 | 0x20;
    }
  }
  else {
    bVar5 = 0;
  }
  if (uVar2 < DAT_376d_2126) {
    ((undefined1 *)&DAT_376d_2128)[uVar2] = bVar5 | local_6 | 1;
    return uVar2;
  }
  pcVar1 = (code *)swi(0x21);
  (*pcVar1)();
LAB_21ea_1cba:
  uVar4 = FUN_21ea_05bb();
  return uVar4;
}

