import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.nio.file.*;
import java.io.*;
import java.util.*;
public class ExportConfigReferences extends GhidraScript {
 public void run() throws Exception {
  String v=currentProgram.getName().substring(3,5);File out=new File(getScriptArgs()[0]);DecompInterface d=new DecompInterface();d.openProgram(currentProgram);Set<Function> fs=new LinkedHashSet<>();
  try(PrintWriter w=new PrintWriter(new File(out,"DOS"+v+".refs.tsv"))){
   for(String l:Files.readAllLines(new File(out,"seeds.tsv").toPath())){String[] s=l.split("\t");if(!s[0].equals(v))continue;ReferenceIterator it=currentProgram.getReferenceManager().getReferencesTo(toAddr(s[2]));while(it.hasNext()){Reference r=it.next();Instruction i=currentProgram.getListing().getInstructionContaining(r.getFromAddress());Function f=currentProgram.getFunctionManager().getFunctionContaining(r.getFromAddress());w.println(s[1]+"\t"+s[2]+"\t"+r.getFromAddress()+"\t"+r.getReferenceType()+"\t"+(f==null?"":f.getEntryPoint())+"\t"+i);if(f!=null)fs.add(f);}}
   for(Function f:fs){DecompileResults z=d.decompileFunction(f,30,monitor);w.println("decompile\t"+f.getEntryPoint()+"\t"+z.decompileCompleted()+"\t"+z.getErrorMessage());if(z.decompileCompleted())Files.writeString(new File(out,"DOS"+v+"."+f.getEntryPoint().toString().replace(':','_')+".c").toPath(),z.getDecompiledFunction().getC());InstructionIterator it=currentProgram.getListing().getInstructions(f.getBody(),true);while(it.hasNext()){Instruction i=it.next();StringBuilder hex=new StringBuilder();for(byte b:i.getBytes())hex.append(String.format("%02x",b&255));w.println("instruction\t"+f.getEntryPoint()+"\t"+i.getAddress()+"\t"+hex+"\t"+i);}}
  }finally{d.dispose();}
 }
}
