import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import java.io.*;
import java.security.MessageDigest;
public class N3DPass2FullAudit extends GhidraScript {
 public void run() throws Exception {
  File out=new File(getScriptArgs()[0]); out.mkdirs();
  DecompInterface d=new DecompInterface(); d.openProgram(currentProgram);
  try(PrintWriter meta=new PrintWriter(new File(out,"manifest.txt"));PrintWriter fs=new PrintWriter(new File(out,"functions.tsv"));PrintWriter ins=new PrintWriter(new File(out,"instructions.tsv"));PrintWriter calls=new PrintWriter(new File(out,"calls.tsv"));PrintWriter gaps=new PrintWriter(new File(out,"unowned_instructions.tsv"))) {
   meta.println("name="+currentProgram.getName()+"\nmd5="+currentProgram.getExecutableMD5()+"\nlanguage="+currentProgram.getLanguageID()+"\nbase="+currentProgram.getImageBase());
   for(var b:currentProgram.getMemory().getBlocks())meta.println("block="+b.getName()+" "+b.getStart()+" "+b.getEnd()+" initialized="+b.isInitialized());
   fs.println("entry\tname\tbody_bytes\tinstructions\tcomputed_flows\tcompleted\terror\tsha256");
   ins.println("address\tbytes\tdisassembly\tflow\ttargets"); calls.println("source\ttarget\ttype");gaps.println("address\tdisassembly");
   for(var it=currentProgram.getListing().getInstructions(true);it.hasNext();) {var i=it.next();String hex=java.util.HexFormat.of().formatHex(i.getBytes());ins.println(i.getAddress()+"\t"+hex+"\t"+i+"\t"+i.getFlowType()+"\t"+java.util.Arrays.toString(i.getFlows()));if(getFunctionContaining(i.getAddress())==null)gaps.println(i.getAddress()+"\t"+i);for(var ref:i.getReferencesFrom())if(ref.getReferenceType().isFlow())calls.println(i.getAddress()+"\t"+ref.getToAddress()+"\t"+ref.getReferenceType());}
   int n=0;for(var it=currentProgram.getFunctionManager().getFunctions(true);it.hasNext()&&!monitor.isCancelled();) {var f=it.next();int count=0,computed=0;MessageDigest sha=MessageDigest.getInstance("SHA-256");for(var ii=currentProgram.getListing().getInstructions(f.getBody(),true);ii.hasNext();){var i=ii.next();count++;if(i.getFlowType().isComputed())computed++;sha.update(i.getBytes());}DecompileResults r; try {r=d.decompileFunction(f,10,monitor);} catch(Exception ex) {fs.println(f.getEntryPoint()+"\t"+f.getName()+"\t"+f.getBody().getNumAddresses()+"\t"+count+"\t"+computed+"\tfalse\tEXCEPTION:"+ex.getClass().getName()+"\t"+java.util.HexFormat.of().formatHex(sha.digest()));fs.flush();d.dispose();d=new DecompInterface();d.openProgram(currentProgram);continue;}String error=r.getErrorMessage().replace('\n',' ').replace('\t',' ');fs.println(f.getEntryPoint()+"\t"+f.getName()+"\t"+f.getBody().getNumAddresses()+"\t"+count+"\t"+computed+"\t"+r.decompileCompleted()+"\t"+error+"\t"+java.util.HexFormat.of().formatHex(sha.digest()));fs.flush();try(PrintWriter c=new PrintWriter(new File(out,f.getEntryPoint().toString().replace(':','_')+".c"))){if(r.decompileCompleted())c.print(r.getDecompiledFunction().getC());else c.println("/* FAILED: "+error+" */");}if(++n%50==0)println("AUDIT_PROGRESS "+n);}
  } finally {d.dispose();}
 }
}
