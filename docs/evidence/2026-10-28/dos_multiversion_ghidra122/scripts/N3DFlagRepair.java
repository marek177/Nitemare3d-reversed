import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.program.model.symbol.SourceType;
import java.io.*;
public class N3DFlagRepair extends GhidraScript {
 public void run() throws Exception {
  File out=new File(getScriptArgs()[0]);out.mkdirs();
  try(PrintWriter log=new PrintWriter(new File(out,"flag_repairs.tsv"))) {
   log.println("start\tend\tremoved_interior_function\tresult");
   for(String spec:getScriptArgs()[1].split(",")) {
    String[] z=spec.split("-");var a=toAddr(z[0]);var end=toAddr(z[1]);
    if((getByte(a)&255)!=0xc8||(getByte(end)&255)!=0xcb)throw new IllegalStateException("Invalid flag boundaries");
    for(var it=currentProgram.getFunctionManager().getFunctions(a,true);it.hasNext();) {var f=it.next();if(f.getEntryPoint().compareTo(end)>0)break;if(!f.getEntryPoint().equals(a)){log.println(a+"\t"+end+"\t"+f.getEntryPoint()+"\tremoved");removeFunction(f);}}
    disassemble(a);var f=getFunctionAt(a);if(f==null)f=createFunction(a,null);if(f==null)throw new IllegalStateException("No function "+a);
    CreateFunctionCmd.fixupFunctionBody(currentProgram,f,monitor);
    f.setName("BuildClassFlagsLayer"+(z[0].equals(getScriptArgs()[1].split("-")[0])?"A":"B"),SourceType.USER_DEFINED);
    f.setComment("Verified original opcodes with Unicorn for all 256 class values and stack seeds 00,7f,80,ff. Bit 7 preserves incoming stack byte; bits 0..6 assigned deterministically. See class_flags_emulation.json. No whole-game runtime claim.");
    log.println(a+"\t"+end+"\t-\t"+f.getBody().getNumAddresses());
   }
  }
 }
}
