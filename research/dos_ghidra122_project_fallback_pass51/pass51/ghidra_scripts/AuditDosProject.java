import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.*;
import java.io.*;
public class AuditDosProject extends GhidraScript {
 public void run() throws Exception {
  File dir=new File(getScriptArgs()[0]);dir.mkdirs();
  try(PrintWriter w=new PrintWriter(new File(dir,currentProgram.getName()+".tsv"))){
   w.println("name\t"+currentProgram.getName());w.println("language\t"+currentProgram.getLanguageID());w.println("compiler\t"+currentProgram.getCompilerSpec().getCompilerSpecID());w.println("sha256\t"+currentProgram.getExecutableSHA256());w.println("functions\t"+currentProgram.getFunctionManager().getFunctionCount());w.println("instructions\t"+currentProgram.getListing().getNumInstructions());
   for(MemoryBlock b:currentProgram.getMemory().getBlocks())w.println("block\t"+b.getName()+"\t"+b.getStart()+"\t"+b.getSize()+"\t"+b.isInitialized());
   String name=currentProgram.getName().toLowerCase();String addr=null;
   if(name.equals("n3d-10.exe"))addr="1bdd:0376";
   if(name.equals("n3d-11.exe"))addr="1bff:039a";
   if(name.equals("n3d-12.exe"))addr="1bff:039c";
   if(name.equals("n3d-15.exe"))addr="1c07:03a2";
   if(name.equals("n3d-17.exe"))addr="1c11:039e";
   if(name.equals("n3d-18.exe")||name.equals("n3d-19.exe"))addr="1c27:03a2";
   if(addr!=null){byte[] raw=new byte[112];currentProgram.getMemory().getBytes(toAddr(addr),raw);StringBuilder hex=new StringBuilder();for(byte b:raw)hex.append(String.format("%02x",b&255));w.println("fallback_bytes\t"+addr+"\t"+hex);}
   FunctionIterator fs=currentProgram.getFunctionManager().getFunctions(true);while(fs.hasNext()){Function f=fs.next();w.println("function\t"+f.getEntryPoint()+"\t"+f.getName()+"\t"+f.getBody().getNumAddresses());}
  }
 }
}
