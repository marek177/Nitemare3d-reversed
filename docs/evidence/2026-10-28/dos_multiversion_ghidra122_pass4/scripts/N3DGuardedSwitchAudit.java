import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.program.model.symbol.*;
import ghidra.program.model.pcode.JumpTable;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import java.io.*;
import java.nio.file.*;
import java.util.*;
public class N3DGuardedSwitchAudit extends GhidraScript {
 public void run() throws Exception {
  File out=new File(getScriptArgs()[1]);out.mkdirs();
  Set<Function> touched=new LinkedHashSet<>();
  try(PrintWriter log=new PrintWriter(new File(out,"guarded_switch_edges.tsv"))) {
   log.println("source\ttable\tguard\tindex\ttarget\tfunction\tstatus");
   for(String line:Files.readAllLines(Path.of(getScriptArgs()[0]))){if(line.startsWith("source")||line.isBlank())continue;String[] s=line.split("\\t");Address source=toAddr(s[0]),table=toAddr(s[1]);int n=Integer.parseInt(s[2]);Function f=getFunctionContaining(source);if(f==null){log.println(s[0]+"\t"+s[1]+"\t"+s[3]+"\t\t\t\tNO_FUNCTION");continue;}
    for(var old:currentProgram.getReferenceManager().getReferencesFrom(source))if(old.getReferenceType().isFlow())currentProgram.getReferenceManager().delete(old);
    ArrayList<Address> targets=new ArrayList<>();
    for(int i=0;i<n;i++){int off=Short.toUnsignedInt(getShort(table.add(2*i)));Address target=toAddr(s[0].substring(0,5)+String.format("%04x",off));if(!currentProgram.getMemory().contains(target))throw new IllegalStateException("Unmapped target "+target);targets.add(target);currentProgram.getReferenceManager().addMemoryReference(source,target,RefType.COMPUTED_JUMP,SourceType.USER_DEFINED,0);disassemble(target);log.println(s[0]+"\t"+table+"\t"+s[3]+"\t"+i+"\t"+target+"\t"+f.getEntryPoint()+"\tOVERRIDE");}
    new JumpTable(source,targets,true,0).writeOverride(f);touched.add(f);
   }
   for(Function f:touched){long before=f.getBody().getNumAddresses();CreateFunctionCmd.fixupFunctionBody(currentProgram,f,monitor);log.println("BODY\t"+f.getEntryPoint()+"\t"+before+"\t"+f.getBody().getNumAddresses());}
  }
 }
}
