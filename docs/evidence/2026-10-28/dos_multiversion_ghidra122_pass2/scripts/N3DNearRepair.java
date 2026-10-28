import ghidra.app.script.GhidraScript;
import ghidra.program.model.symbol.*;
import java.nio.file.*;
import java.io.*;
public class N3DNearRepair extends GhidraScript {
 public void run() throws Exception {
  try(PrintWriter log=new PrintWriter(getScriptArgs()[1])){
   log.println("source\ttarget\tstatus");
   for(String line:Files.readAllLines(Path.of(getScriptArgs()[0]))){if(line.startsWith("source")||line.isBlank())continue;var s=line.split("\\t");var a=toAddr(s[0]);var t=toAddr(s[1]);var i=getInstructionAt(a);var b=i.getBytes();if(!java.util.HexFormat.of().formatHex(b).equals(s[2])||b.length!=3||(b[0]&255)!=0xe8)throw new IllegalStateException("Bad source "+a);
    int off=Integer.parseInt(s[0].split(":")[1],16);int want=(off+3+(short)((b[1]&255)|((b[2]&255)<<8)))&65535;if(want!=Integer.parseInt(s[1].split(":")[1],16))throw new IllegalStateException("Bad target");
    for(var r:i.getReferencesFrom())if(r.getReferenceType().isCall())currentProgram.getReferenceManager().delete(r);
    var r=currentProgram.getReferenceManager().addMemoryReference(a,t,RefType.UNCONDITIONAL_CALL,SourceType.USER_DEFINED,0);currentProgram.getReferenceManager().setPrimary(r,true);log.println(a+"\t"+t+"\tCORRECTED");
   }
  }
 }
}
