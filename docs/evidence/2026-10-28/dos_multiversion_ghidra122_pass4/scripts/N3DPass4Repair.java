import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.program.model.symbol.*;
import java.nio.file.*;
public class N3DPass4Repair extends GhidraScript {
 public void run() throws Exception {
  Path out=Path.of(getScriptArgs()[0]);Files.createDirectories(out);StringBuilder log=new StringBuilder("source\ttarget\tstatus\n");
  for(String line:Files.readAllLines(Path.of(getScriptArgs()[1]))){if(line.startsWith("source")||line.isBlank())continue;var s=line.split("\\t");var a=toAddr(s[0]);var t=toAddr(s[1]);var i=getInstructionAt(a);if(!java.util.HexFormat.of().formatHex(i.getBytes()).equals(s[2]))throw new IllegalStateException("Wrong bytes");for(var r:i.getReferencesFrom())if(r.getReferenceType().isJump())currentProgram.getReferenceManager().delete(r);var r=currentProgram.getReferenceManager().addMemoryReference(a,t,RefType.CONDITIONAL_JUMP,SourceType.USER_DEFINED,0);currentProgram.getReferenceManager().setPrimary(r,true);var f=getFunctionContaining(a);if(f!=null)CreateFunctionCmd.fixupFunctionBody(currentProgram,f,monitor);log.append(a+"\t"+t+"\tCORRECTED\n");}
  Files.writeString(out.resolve("flow_repairs.tsv"),log);
  var start=toAddr(getScriptArgs()[2]);var end=toAddr(getScriptArgs()[3]);var f=getFunctionAt(toAddr(getScriptArgs()[4]));String before=f.getBody().toString();var bytes=getBytes(start,10);if(!java.util.HexFormat.of().formatHex(bytes).equals("895ee88c46ea26833f00"))throw new IllegalStateException("Wrong boundary");
  clearListing(f.getEntryPoint(),end);disassemble(f.getEntryPoint());CreateFunctionCmd.fixupFunctionBody(currentProgram,f,monitor);Files.writeString(out.resolve("boundary_repair.txt"),"before="+before+"\nafter="+f.getBody()+"\nstart="+getInstructionAt(start)+"\nnext="+getInstructionAt(start.add(3))+"\nend="+getInstructionAt(end)+"\n");
 }
}
