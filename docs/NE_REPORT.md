# NITE3W.EXE NE report

- File size: 230400 bytes
- NE header: `0x80`
- Target OS code: `2` (Windows)
- Expected Windows version word: `0x030A`
- Segments: 10
- Imported modules: `KERNEL`, `WING`, `DISPDIB`, `GDI`, `USER`, `KEYBOARD`, `COMMDLG`, `MMSYSTEM`, `SHELL`

The original Windows 3.1 display path uses WinG and DISPDIB. The reconstructed runtime replaces that presentation path with SDL3 while retaining an 8-bit indexed framebuffer model.
