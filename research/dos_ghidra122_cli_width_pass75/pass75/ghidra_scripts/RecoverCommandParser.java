import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import java.nio.file.*;
import java.io.*;
public class RecoverCommandParser extends GhidraScript {
 public void run() throws Exception {
 String v=currentProgram.getName().substring(3,5);File out=new File(getScriptArgs()[0]);
 for(String l:Files.readAllLines(new File(out,"seeds.tsv").toPath())){String[] s=l.split("\t");if(!s[0].equals(v))continue;Address a=toAddr(s[1]),end=toAddr(s[2]);Function f=getFunctionAt(a);boolean recovered=f==null;if(f==null)f=createFunction(a,"RecoveredCommandParser");if(f==null)throw new Exception("create failed");f.setBody(new AddressSet(a,end));DecompInterface d=new DecompInterface();d.openProgram(currentProgram);DecompileResults dr=d.decompileFunction(f,60,monitor);
 try(PrintWriter w=new PrintWriter(new File(out,currentProgram.getName()+".ghidra.tsv"))){w.println("function\t"+a+"\t"+end+"\trecovered="+recovered+"\tdecompile="+dr.decompileCompleted());if(dr.decompileCompleted())Files.writeString(new File(out,currentProgram.getName()+".parser.c").toPath(),dr.getDecompiledFunction().getC());InstructionIterator it=currentProgram.getListing().getInstructions(f.getBody(),true);while(it.hasNext()){Instruction ins=it.next();StringBuilder h=new StringBuilder();for(byte b:ins.getBytes())h.append(String.format("%02x",b&255));w.println("instruction\t"+ins.getAddress()+"\t"+h+"\t"+ins);}}finally{d.dispose();}}
 }
}
