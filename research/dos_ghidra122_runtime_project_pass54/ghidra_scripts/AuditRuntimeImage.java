import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.*;
import java.io.*;
public class AuditRuntimeImage extends GhidraScript {
 public void run() throws Exception {
  File out=new File(getScriptArgs()[0]);out.mkdirs();try(PrintWriter w=new PrintWriter(new File(out,currentProgram.getName()+".analyzed.tsv"))){
   w.println("functions\t"+currentProgram.getFunctionManager().getFunctionCount());w.println("instructions\t"+currentProgram.getListing().getNumInstructions());
   for(MemoryBlock b:currentProgram.getMemory().getBlocks())w.println("block\t"+b.getName()+"\t"+b.getStart()+"\t"+b.getSize()+"\t"+b.isInitialized());
   for(Function f:currentProgram.getFunctionManager().getFunctions(true))w.println("function\t"+f.getEntryPoint()+"\t"+f.getName()+"\t"+f.getBody().getNumAddresses());
  }
 }
}
