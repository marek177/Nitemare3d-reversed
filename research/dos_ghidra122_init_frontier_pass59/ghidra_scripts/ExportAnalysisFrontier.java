import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import java.io.*;
public class ExportAnalysisFrontier extends GhidraScript {
 public void run() throws Exception {
  File out=new File(getScriptArgs()[0]);
  try(PrintWriter f=new PrintWriter(new File(out,currentProgram.getName()+".functions.tsv"));PrintWriter c=new PrintWriter(new File(out,currentProgram.getName()+".computed_flows.tsv"))){
   f.println("entry\tname\tbody_bytes\tparameters\tcalling_convention");for(Function q:currentProgram.getFunctionManager().getFunctions(true))f.println(q.getEntryPoint()+"\t"+q.getName()+"\t"+q.getBody().getNumAddresses()+"\t"+q.getParameterCount()+"\t"+q.getCallingConventionName());
   c.println("address\tfunction\tflow\tknown_targets\tinstruction");InstructionIterator it=currentProgram.getListing().getInstructions(true);while(it.hasNext()){Instruction i=it.next();if(i.getFlowType().isComputed()&&(i.getFlowType().isCall()||i.getFlowType().isJump())){Function q=currentProgram.getFunctionManager().getFunctionContaining(i.getAddress());c.println(i.getAddress()+"\t"+(q==null?"":q.getEntryPoint())+"\t"+i.getFlowType()+"\t"+i.getFlows().length+"\t"+i);}}f.flush();c.flush();
  }
 }
}
