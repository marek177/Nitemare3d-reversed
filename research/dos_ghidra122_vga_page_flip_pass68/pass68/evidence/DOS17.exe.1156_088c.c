
void __cdecl16far FUN_1156_088c(uint param_1,uint param_2,undefined1 param_3,int param_4)

{
  undefined2 uVar1;
  byte bVar2;
  
  if ((int)param_2 < 200) {
    uVar1 = DAT_3754_012e;
    if (param_4 != 0) {
      uVar1 = DAT_3754_012c;
    }
    out(0x3c4,2);
    bVar2 = (byte)param_1 & 3;
    out(0x3c5,'\x11' << bVar2 | 0x11U >> 8 - bVar2);
    *(undefined1 *)((param_2 & 0xff) * 0x50 + (param_1 >> 2)) = param_3;
  }
  return;
}

