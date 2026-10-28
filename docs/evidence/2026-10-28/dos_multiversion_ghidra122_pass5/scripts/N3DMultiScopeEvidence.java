import ghidra.app.script.GhidraScript;
import ghidra.program.model.pcode.*;
import java.nio.file.*;
public class N3DMultiScopeEvidence extends GhidraScript {
 public void run() throws Exception {
  long[] scope=java.util.Arrays.stream(Files.readString(Path.of(getScriptArgs()[1])).trim().split("\\t")).mapToLong(Long::parseLong).toArray();
  StringBuilder rows=new StringBuilder("address\tbytes\tsegment_ops\tSS_ops_kept\tinternal_branches\tmax_original_unique\n");long globalMax=0;int sites=0;
  for(var it=currentProgram.getListing().getInstructions(true);it.hasNext();){var i=it.next();long a=i.getAddress().getOffset();if(!((a>=scope[0]&&a<=scope[1])||(a>=scope[2]&&a<=scope[3])))continue;int count=0,ss=0,branches=0;long max=0;
   for(PcodeOp op:i.getPcode(true)){if((op.getOpcode()==PcodeOp.BRANCH||op.getOpcode()==PcodeOp.CBRANCH)&&op.getInput(0).isConstant())branches++;if(op.getOutput()!=null&&op.getOutput().isUnique())max=Math.max(max,op.getOutput().getOffset());for(Varnode v:op.getInputs())if(v.isUnique())max=Math.max(max,v.getOffset());if(op.getOpcode()==PcodeOp.CALLOTHER&&op.getNumInputs()==3&&"segment".equals(currentProgram.getLanguage().getUserDefinedOpName((int)op.getInput(0).getOffset()))){if(op.getInput(1).getSize()!=2||op.getInput(2).getSize()!=2||op.getOutput().getSize()!=4)throw new IllegalStateException("Unexpected widths");if(op.getInput(1).isRegister()&&op.getInput(1).getAddress().equals(currentProgram.getRegister("SS").getAddress()))ss++;else count++;}}
   if(max>=0x70000000L||count>=16)throw new IllegalStateException("Temporary collision risk");globalMax=Math.max(globalMax,max);if(count>0&&branches==0)sites++;rows.append(i.getAddress()+"\t"+java.util.HexFormat.of().formatHex(i.getBytes())+"\t"+count+"\t"+ss+"\t"+branches+"\t"+Long.toHexString(max)+"\n");
  }
  Path out=Path.of(getScriptArgs()[0]);Files.createDirectories(out);Files.writeString(out.resolve("rewrite_scope.tsv"),rows.toString());Files.writeString(out.resolve("scope_summary.txt"),"rewritable_instruction_sites="+sites+"\nmax_original_unique=0x"+Long.toHexString(globalMax)+"\nnew_unique_base=0x70000000\n");
 }
}
