import ghidra.app.script.GhidraScript;
import java.nio.file.*;
public class N3DFlowExport extends GhidraScript {
 public void run() throws Exception {
  Path out=Path.of(getScriptArgs()[0]);Files.createDirectories(out);
  StringBuilder ins=new StringBuilder("address\tbytes\tdisassembly\tflow\ttargets\n"),calls=new StringBuilder("source\ttarget\ttype\n"),gaps=new StringBuilder("address\tdisassembly\n");
  int count=0;
  for(var it=currentProgram.getListing().getInstructions(true);it.hasNext();){var i=it.next();ins.append(i.getAddress()+"\t"+java.util.HexFormat.of().formatHex(i.getBytes())+"\t"+i+"\t"+i.getFlowType()+"\t"+java.util.Arrays.toString(i.getFlows())+"\n");if(getFunctionContaining(i.getAddress())==null)gaps.append(i.getAddress()+"\t"+i+"\n");for(var r:i.getReferencesFrom())if(r.getReferenceType().isFlow())calls.append(i.getAddress()+"\t"+r.getToAddress()+"\t"+r.getReferenceType()+"\n");count++;}
  Files.writeString(out.resolve("instructions.tsv"),ins);Files.writeString(out.resolve("calls.tsv"),calls);Files.writeString(out.resolve("unowned_instructions.tsv"),gaps);Files.writeString(out.resolve("flow_export_verified.txt"),"instructions="+count+"\n");println("FLOW_EXPORT_COMPLETE "+count);
 }
}
