import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.nio.file.*;
import java.io.*;
import java.util.*;
public class ExportLifecycleCallers extends GhidraScript {
 public void run() throws Exception {
  String v=currentProgram.getName().substring(3,5);File out=new File(getScriptArgs()[0]);
  try(PrintWriter w=new PrintWriter(new File(out,currentProgram.getName()+".callers.tsv"))){
   for(String l:Files.readAllLines(new File(out,"seeds.tsv").toPath())){String[] s=l.split("\t");if(!s[0].equals(v))continue;ReferenceIterator refs=currentProgram.getReferenceManager().getReferencesTo(toAddr(s[1]));while(refs.hasNext()){Reference r=refs.next();Instruction call=currentProgram.getListing().getInstructionAt(r.getFromAddress());if(call==null||!call.getFlowType().isCall())continue;Function f=currentProgram.getFunctionManager().getFunctionContaining(call.getAddress());w.println("caller\t"+call.getAddress()+"\t"+(f==null?"":f.getEntryPoint())+"\t"+call);ArrayList<Instruction> prior=new ArrayList<>();Instruction i=call;for(int n=0;n<8&&i!=null;n++){prior.add(i);i=currentProgram.getListing().getInstructionBefore(i.getAddress());}Collections.reverse(prior);for(Instruction q:prior){StringBuilder hex=new StringBuilder();for(byte b:q.getBytes())hex.append(String.format("%02x",b&255));w.println("context\t"+q.getAddress()+"\t"+hex+"\t"+q);}}
   }w.flush();
  }
 }
}
