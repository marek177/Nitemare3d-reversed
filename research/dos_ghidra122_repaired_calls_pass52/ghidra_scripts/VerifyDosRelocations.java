import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import java.nio.file.*;
import java.io.*;
public class VerifyDosRelocations extends GhidraScript {
 public void run() throws Exception {
  String[] args=getScriptArgs();File f=new File(args[0],currentProgram.getName()+".relocations.tsv");if(!f.exists())return;int verified=0,flows=0;
  for(String line:Files.readAllLines(f.toPath())){String[] s=line.split("\t");if(!s[0].equals("patched"))continue;Address a=toAddr(s[1]);Instruction ins=currentProgram.getListing().getInstructionAt(a);if(ins==null)throw new Exception("No instruction "+a);byte[] b=ins.getBytes();int seg=(b[3]&255)|((b[4]&255)<<8),off=(b[1]&255)|((b[2]&255)<<8);if(seg!=Integer.parseInt(s[3],16))throw new Exception("Segment mismatch "+a);Address[] targets=ins.getFlows();boolean ok=false;for(Address t:targets)if(t.getOffset()==seg*16L+off)ok=true;if(!ok)throw new Exception("Flow mismatch "+a+" "+ins);verified++;flows++;}
  try(PrintWriter w=new PrintWriter(new File(args[0],currentProgram.getName()+".verified.tsv"))){w.println("persisted_patches_verified\t"+verified);w.println("corrected_direct_flows_verified\t"+flows);w.println("functions\t"+currentProgram.getFunctionManager().getFunctionCount());}
 }
}
