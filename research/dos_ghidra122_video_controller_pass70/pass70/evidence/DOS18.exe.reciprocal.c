
void __cdecl16far FUN_1156_0000(void)

{
  undefined4 *puVar1;
  long local_6;
  
  local_6 = 1;
  puVar1 = (undefined4 *)&DAT_376d_2654;
  do {
    *puVar1 = (long)(0x400000 / (sqword)local_6);
    puVar1 = puVar1 + 1;
    local_6 = local_6 + 1;
  } while (puVar1 < (undefined4 *)0x2e50);
  return;
}

