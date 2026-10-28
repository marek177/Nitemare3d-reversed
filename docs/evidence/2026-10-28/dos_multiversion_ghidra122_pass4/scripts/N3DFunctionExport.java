import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import java.nio.file.*;
import java.security.MessageDigest;
public class N3DFunctionExport extends GhidraScript {
 public void run() throws Exception {
  Path out=Path.of(getScriptArgs()[0]);Files.createDirectories(out);StringBuilder s=new StringBuilder("entry\tname\tbody_bytes\tinstructions\tcomputed_flows\tcompleted\terror\tsha256\n");DecompInterface d=new DecompInterface();d.openProgram(currentProgram);int n=0;
  try{for(var it=currentProgram.getFunctionManager().getFunctions(true);it.hasNext();){var f=it.next();int count=0,computed=0;var sha=MessageDigest.getInstance("SHA-256");for(var ii=currentProgram.getListing().getInstructions(f.getBody(),true);ii.hasNext();){var i=ii.next();count++;if(i.getFlowType().isComputed())computed++;sha.update(i.getBytes());}boolean done=false;String error="",c="";
   try{var r=d.decompileFunction(f,10,monitor);done=r.decompileCompleted();error=r.getErrorMessage();if(done&&r.getDecompiledFunction()!=null)c=r.getDecompiledFunction().getC();else c="/* FAILED: "+error+" */\n";}catch(Exception ex){error=ex.toString();d.dispose();d=new DecompInterface();d.openProgram(currentProgram);}
   s.append(f.getEntryPoint()+"\t"+f.getName()+"\t"+f.getBody().getNumAddresses()+"\t"+count+"\t"+computed+"\t"+done+"\t"+error.replace('\n',' ').replace('\t',' ')+"\t"+java.util.HexFormat.of().formatHex(sha.digest())+"\n");Files.writeString(out.resolve(f.getEntryPoint().toString().replace(':','_')+".c"),c);n++;
  }}finally{d.dispose();}Files.writeString(out.resolve("functions.tsv"),s);Files.writeString(out.resolve("function_export_verified.txt"),"functions="+n+"\n");println("FUNCTION_EXPORT_COMPLETE "+n);
 }
}
