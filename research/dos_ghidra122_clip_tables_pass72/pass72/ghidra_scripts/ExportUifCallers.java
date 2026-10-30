import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.nio.file.*;
import java.io.*;
import java.util.*;
public class ExportUifCallers extends GhidraScript {
 public void run() throws Exception {
 String v=currentProgram.getName().substring(3,5);File out=new File(getScriptArgs()[0]);DecompInterface d=new DecompInterface();d.openProgram(currentProgram);Set<Function> fs=new LinkedHashSet<>();
 try(PrintWriter w=new PrintWriter(new File(out,currentProgram.getName()+".xrefs.tsv"))){
 for(String l:Files.readAllLines(new File(out,"seeds.tsv").toPath())){String[] s=l.split("\t");if(!s[0].equals(v))continue;
 if(s[1].equals("at")){Function f=getFunctionContaining(toAddr(s[2]));if(f==null)throw new Exception("Missing containing function");fs.add(f);w.println("at\t"+s[2]+"\tCONTAINING\t"+f.getEntryPoint());continue;}
 ReferenceIterator it=currentProgram.getReferenceManager().getReferencesTo(toAddr(s[2]));while(it.hasNext()){Reference ref=it.next();Function f=getFunctionContaining(ref.getFromAddress());Instruction ins=getInstructionAt(ref.getFromAddress());w.println(s[1]+"\t"+ref.getFromAddress()+"\t"+ref.getReferenceType()+"\t"+(f==null?"":f.getEntryPoint())+"\t"+ins);if(f!=null)fs.add(f);}}
 for(Function f:fs){DecompileResults dr=d.decompileFunction(f,30,monitor);if(dr.decompileCompleted())Files.writeString(new File(out,currentProgram.getName()+"."+f.getEntryPoint().toString().replace(':','_')+".c").toPath(),dr.getDecompiledFunction().getC());InstructionIterator it=currentProgram.getListing().getInstructions(f.getBody(),true);while(it.hasNext()){Instruction ins=it.next();StringBuilder h=new StringBuilder();for(byte b:ins.getBytes())h.append(String.format("%02x",b&255));w.println("instruction\t"+f.getEntryPoint()+"\t"+ins.getAddress()+"\t"+h+"\t"+ins);}}
 }finally{d.dispose();}
 }
}
