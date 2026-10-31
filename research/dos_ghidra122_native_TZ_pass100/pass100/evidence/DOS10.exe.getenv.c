
int __cdecl16far FUN_219b_2586(int param_1)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  int *piVar4;
  
  piVar4 = DAT_3360_203c;
  if ((DAT_3360_203c != (int *)0x0) && (param_1 != 0)) {
    uVar1 = FUN_219b_2494(param_1);
    for (; *piVar4 != 0; piVar4 = piVar4 + 1) {
      uVar2 = FUN_219b_2494(*piVar4);
      if (((uVar1 < uVar2) && (*(char *)(*piVar4 + uVar1) == '=')) &&
         (iVar3 = FUN_219b_24d8(*piVar4,param_1,uVar1), iVar3 == 0)) {
        return *piVar4 + uVar1 + 1;
      }
    }
  }
  return 0;
}

