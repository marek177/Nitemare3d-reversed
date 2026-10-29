import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.data.DWordDataType;
import ghidra.program.model.symbol.SourceType;
import java.nio.file.*;
import java.io.*;
public class SetSoundReturnAbi extends GhidraScript {
 public void run() throws Exception {
  String v=currentProgram.getName().substring(3,5);try(PrintWriter w=new PrintWriter(new File(getScriptArgs()[0],currentProgram.getName()+".abi.tsv"))){
   for(String l:Files.readAllLines(Paths.get(getScriptArgs()[0],"seeds.tsv"))){String[] s=l.split("\t");if(!s[0].equals(v)||s[1].equals("dispatcher"))continue;Function f=currentProgram.getFunctionManager().getFunctionAt(toAddr(s[2]));if(f==null)throw new Exception("Missing function "+s[2]);String before=f.getReturnType().getDisplayName();VariableStorage storage=new VariableStorage(currentProgram,currentProgram.getRegister("DX"),currentProgram.getRegister("AX"));ReturnParameterImpl ret=new ReturnParameterImpl(DWordDataType.dataType,storage,currentProgram);f.updateFunction(f.getCallingConventionName(),ret,Function.FunctionUpdateType.CUSTOM_STORAGE,true,SourceType.ANALYSIS,new ParameterImpl("resource_id",ghidra.program.model.data.WordDataType.dataType,4,currentProgram));if(f.getReturn().getLength()!=4||!f.hasCustomVariableStorage())throw new Exception("Return ABI not retained");w.println("return_abi\t"+s[1]+"\t"+s[2]+"\t"+before+"\t"+f.getReturnType().getDisplayName()+"\t"+f.getReturn().getVariableStorage());}
  }
 }
}
