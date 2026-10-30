import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.nio.file.*;
import java.io.*;
public class ExportXmsLifecycle extends GhidraScript {
 public void run() throws Exception {
  String v=currentProgram.getName().substring(3,5);File out=new File(getScriptArgs()[0]);DecompInterface d=new DecompInterface();boolean opened=d.openProgram(currentProgram);println("DECOMP_OPEN="+opened+" MESSAGE="+d.getLastMessage());
  try(PrintWriter w=new PrintWriter(new File(out,currentProgram.getName()+".ghidra.tsv"))){
   for(String l:Files.readAllLines(new File(out,"seeds.tsv").toPath())){String[] s=l.split("\t");if(!s[0].equals(v))continue;
    if(s[1].equals("used_global")){ReferenceIterator it=currentProgram.getReferenceManager().getReferencesTo(toAddr(s[2]));while(it.hasNext()){Reference r=it.next();Instruction i=currentProgram.getListing().getInstructionContaining(r.getFromAddress());w.println("used_xref\t"+r.getFromAddress()+"\t"+r.getReferenceType()+"\t"+(i==null?"":i));}continue;}
    Function f=currentProgram.getFunctionManager().getFunctionAt(toAddr(s[2]));if(f==null)throw new Exception("Missing function "+s[2]);DecompileResults r=d.decompileFunction(f,30,monitor);w.println("decompile\t"+s[1]+"\t"+s[2]+"\t"+r.decompileCompleted()+"\t"+r.getErrorMessage()+"\t"+d.getLastMessage());if(r.decompileCompleted())Files.writeString(new File(out,currentProgram.getName()+"."+s[1]+".c").toPath(),r.getDecompiledFunction().getC());
    InstructionIterator it=currentProgram.getListing().getInstructions(f.getBody(),true);while(it.hasNext()){Instruction i=it.next();StringBuilder hex=new StringBuilder();for(byte b:i.getBytes())hex.append(String.format("%02x",b&255));w.println("instruction\t"+s[1]+"\t"+i.getAddress()+"\t"+hex+"\t"+i);}
   }w.flush();
  }finally{d.dispose();}
 }
}
