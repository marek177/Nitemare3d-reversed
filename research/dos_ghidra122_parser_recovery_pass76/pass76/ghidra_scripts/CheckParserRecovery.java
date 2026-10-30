import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import java.nio.file.*;
import java.io.*;
public class CheckParserRecovery extends GhidraScript {
 public void run() throws Exception {String v=currentProgram.getName().substring(3,5);File out=new File(getScriptArgs()[0]);for(String l:Files.readAllLines(new File(out,"seeds.tsv").toPath())){String[] s=l.split("\t");if(!s[0].equals(v))continue;Function f=getFunctionAt(toAddr(s[1]));int good=0,bad=0;for(String line:Files.readAllLines(new File(out,"DOS"+v+".instructions.tsv").toPath())){String[] p=line.split("\t");Instruction ins=getInstructionAt(toAddr(p[0]));String h="";if(ins!=null)for(byte b:ins.getBytes())h+=String.format("%02x",b&255);if(h.equals(p[1])&&f.getBody().contains(toAddr(p[0])))good++;else bad++;}DecompInterface d=new DecompInterface();d.openProgram(currentProgram);DecompileResults dr=d.decompileFunction(f,60,monitor);Files.writeString(new File(out,currentProgram.getName()+".readback.tsv").toPath(),"matched="+good+"\tmismatch="+bad+"\tdecompile="+dr.decompileCompleted()+"\t"+dr.getErrorMessage()+"\n");d.dispose();}}
}
