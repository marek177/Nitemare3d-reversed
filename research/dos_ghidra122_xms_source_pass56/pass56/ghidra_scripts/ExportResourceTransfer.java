import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import java.nio.file.*;
import java.io.*;
public class ExportResourceTransfer extends GhidraScript {
 public void run() throws Exception {
  String v=currentProgram.getName().substring(3,5);File out=new File(getScriptArgs()[0]);DecompInterface d=new DecompInterface();d.openProgram(currentProgram);
  try(PrintWriter w=new PrintWriter(new File(out,currentProgram.getName()+".ghidra.tsv"))){
   for(String l:Files.readAllLines(new File(out,"seeds.tsv").toPath())){String[] s=l.split("\t");if(!s[0].equals(v))continue;Function f=currentProgram.getFunctionManager().getFunctionAt(toAddr(s[2]));if(f==null){w.println("missing\t"+s[1]+"\t"+s[2]);continue;}DecompileResults r=d.decompileFunction(f,30,monitor);w.println("decompile\t"+s[1]+"\t"+s[2]+"\t"+r.decompileCompleted()+"\t"+r.getErrorMessage());if(r.decompileCompleted())Files.writeString(new File(out,currentProgram.getName()+"."+s[1]+".c").toPath(),r.getDecompiledFunction().getC());InstructionIterator it=currentProgram.getListing().getInstructions(f.getBody(),true);while(it.hasNext()){Instruction i=it.next();StringBuilder hex=new StringBuilder();for(byte b:i.getBytes())hex.append(String.format("%02x",b&255));w.println("instruction\t"+s[1]+"\t"+i.getAddress()+"\t"+hex+"\t"+i);}}
  }finally{d.dispose();}
 }
}
