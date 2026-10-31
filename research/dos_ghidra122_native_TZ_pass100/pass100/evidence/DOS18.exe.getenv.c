
int __cdecl16far FUN_21ea_248e(int param_1)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  int *piVar4;
  
  piVar4 = DAT_376d_2140;
  if ((DAT_376d_2140 != (int *)0x0) && (param_1 != 0)) {
    uVar1 = FUN_21ea_239c(param_1);
    for (; *piVar4 != 0; piVar4 = piVar4 + 1) {
      uVar2 = FUN_21ea_239c(*piVar4);
      if (((uVar1 < uVar2) && (*(char *)(*piVar4 + uVar1) == '=')) &&
         (iVar3 = FUN_21ea_23e0(*piVar4,param_1,uVar1), iVar3 == 0)) {
        return *piVar4 + uVar1 + 1;
      }
    }
  }
  return 0;
}

