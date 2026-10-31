
/* WARNING: Stack frame is not setup normally: Input value of stackpointer is not used */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined2 N3D_rtc_isr_recovered(void)

{
  undefined4 in_EAX;
  undefined4 in_ECX;
  undefined4 in_EDX;
  undefined4 in_EBX;
  int iVar1;
  undefined4 in_ESP;
  undefined4 in_EBP;
  undefined4 in_ESI;
  undefined4 in_EDI;
  undefined2 unaff_ES;
  undefined2 unaff_SS;
  
  iVar1 = (int)in_ESP;
  *(undefined4 *)(iVar1 + -4) = in_EAX;
  *(undefined4 *)(iVar1 + -8) = in_ECX;
  *(undefined4 *)(iVar1 + -0xc) = in_EDX;
  *(undefined4 *)(iVar1 + -0x10) = in_EBX;
  *(undefined4 *)(iVar1 + -0x14) = in_ESP;
  *(undefined4 *)(iVar1 + -0x18) = in_EBP;
  *(undefined4 *)(iVar1 + -0x1c) = in_ESI;
  *(undefined4 *)(iVar1 + -0x20) = in_EDI;
  *(undefined2 *)(iVar1 + -0x22) = (undefined1 *)&DAT_3360_3360;
  *(undefined2 *)(iVar1 + -0x24) = unaff_ES;
  *(undefined2 *)(iVar1 + -0x26) = (undefined1 *)&DAT_3360_3360;
  _DAT_3360_07a2 = _DAT_3360_07a2 + 1;
  out(0x70,0xc);
  in(0x71);
  out(0xa0,0x20);
  out(0x20,0x20);
  return (int)*(undefined4 *)(iVar1 + -4);
}

