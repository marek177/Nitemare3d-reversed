Open project/N3D_Runtime54.gpr next to project/N3D_Runtime54.rep. This copy retains the pass54 runtime-byte/DS model, pass57 XMS status interfaces, and additionally six explicit XMS-store interfaces from pass58. Six programs are under /inputs; DOS18.exe also represents the identical supplied DOS1.9 image.

Store interface: packed32 return DX:AX; packed source far pointer at entry stack+4 and length16 at stack+8. This is resource placement into an existing XMS handle, not the XMS manager's allocation function. See REPORT_PASS58.md for tested behavior and remaining limitations.
