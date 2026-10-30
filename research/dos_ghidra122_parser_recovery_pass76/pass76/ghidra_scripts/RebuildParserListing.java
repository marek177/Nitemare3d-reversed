import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import java.nio.file.*;
import java.io.*;
import java.util.*;
import java.math.BigInteger;
import ghidra.program.model.pcode.JumpTable;
public class RebuildParserListing extends GhidraScript {
 public void run() throws Exception {
 String v=currentProgram.getName().substring(3,5);File out=new File(getScriptArgs()[0]);
 for(String l:Files.readAllLines(new File(out,"seeds.tsv").toPath())){String[] s=l.split("\t");if(!s[0].equals(v))continue;Address entry=toAddr(s[1]),end=toAddr(s[2]);Function f=getFunctionAt(entry);List<String> lines=Files.readAllLines(new File(out,"DOS"+v+".instructions.tsv").toPath());AddressSet body=new AddressSet();
 for(String line:lines){String[] p=line.split("\t");Address a=toAddr(p[0]);body.add(a,a.add(p[1].length()/2-1));}
 clearListing(entry,end);int cs=Integer.parseInt(s[1].split(":")[0],16);currentProgram.getProgramContext().setValue(currentProgram.getRegister("CS"),entry,end,BigInteger.valueOf(cs));for(String line:lines){String[] p=line.split("\t");Address a=toAddr(p[0]);new DisassembleCommand(a,body,false).applyTo(currentProgram,monitor);}
 if(f==null)f=createFunction(entry,"RecoveredCommandParser");f.setBody(body);List<String> sw=Files.readAllLines(new File(out,"DOS"+v+".switch.tsv").toPath());ArrayList<Address> targets=new ArrayList<>();for(int i=1;i<sw.size();i++)targets.add(toAddr(sw.get(i)));new JumpTable(toAddr(sw.get(0)),targets,true,0).writeOverride(f);
 try(PrintWriter w=new PrintWriter(new File(out,currentProgram.getName()+".rebuild.tsv"))){int good=0,bad=0;for(String line:lines){String[] p=line.split("\t");Instruction ins=getInstructionAt(toAddr(p[0]));String h="";if(ins!=null)for(byte b:ins.getBytes())h+=String.format("%02x",b&255);boolean same=h.equals(p[1]);if(same)good++;else bad++;w.println("instruction\t"+p[0]+"\t"+p[1]+"\t"+h+"\t"+same+"\t"+ins);}
 DecompInterface d=new DecompInterface();d.openProgram(currentProgram);DecompileResults dr=d.decompileFunction(f,60,monitor);w.println("result\tmatched="+good+"\tmismatch="+bad+"\tdecompile="+dr.decompileCompleted()+"\t"+dr.getErrorMessage());if(dr.decompileCompleted())Files.writeString(new File(out,currentProgram.getName()+".parser.c").toPath(),dr.getDecompiledFunction().getC());d.dispose();}
 }
 }
}
