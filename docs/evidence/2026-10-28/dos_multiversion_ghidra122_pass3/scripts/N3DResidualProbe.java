import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import java.nio.file.*;
import java.io.*;
public class N3DResidualProbe extends GhidraScript {
 public void run() throws Exception {
  Path out=Path.of(getScriptArgs()[0]);Files.createDirectories(out);StringBuilder refs=new StringBuilder("entry\tfrom\ttype\n"),stats=new StringBuilder("entry\tstyle\tcompleted\tC_available\tpcode_ops\terror\n");
  for(String entry:getScriptArgs()[1].split(",")){
   var a=toAddr(entry);for(var it=currentProgram.getReferenceManager().getReferencesTo(a);it.hasNext();){var r=it.next();refs.append(entry+"\t"+r.getFromAddress()+"\t"+r.getReferenceType()+"\n");}
   var f=getFunctionAt(a);if(f==null)continue;
   for(String mode:new String[]{"normalize"}){
    var d=new DecompInterface();d.openProgram(currentProgram);d.setSimplificationStyle(mode);var r=d.decompileFunction(f,15,monitor);StringBuilder ops=new StringBuilder();int n=0;if(r.getHighFunction()!=null)for(var it=r.getHighFunction().getPcodeOps();it.hasNext();){var op=it.next();ops.append(op.getSeqnum()+"\t"+op+"\n");n++;}
    stats.append(entry+"\t"+mode+"\t"+r.decompileCompleted()+"\t"+(r.getDecompiledFunction()!=null)+"\t"+n+"\t"+r.getErrorMessage().replace('\n',' ')+"\n");Files.writeString(out.resolve(entry.replace(':','_')+"_pcode.tsv"),ops);d.dispose();
   }
  }
  Files.writeString(out.resolve("incoming_references.tsv"),refs);Files.writeString(out.resolve("normalized_results.tsv"),stats);
 }
}
