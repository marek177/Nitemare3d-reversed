import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.data.*;
import ghidra.program.model.symbol.SourceType;
import java.nio.file.*;
import java.io.*;
public class CorrectXmsStoreAbi extends GhidraScript {
 public void run() throws Exception {
  String[] args=getScriptArgs();String v=currentProgram.getName().substring(3,5);File out=new File(args[0]);boolean write=args[1].equals("write");DecompInterface d=new DecompInterface();
  try(PrintWriter w=new PrintWriter(new File(out,currentProgram.getName()+"."+args[1]+".tsv"))){
   for(String l:Files.readAllLines(new File(out,"seeds.tsv").toPath())){String[] s=l.split("\t");if(!s[0].equals(v)||!s[1].equals("xmsstore"))continue;Function f=currentProgram.getFunctionManager().getFunctionAt(toAddr(s[2]));if(f==null)throw new Exception("Missing function "+s[2]);
    if(write){VariableStorage st=new VariableStorage(currentProgram,currentProgram.getRegister("DX"),currentProgram.getRegister("AX"));f.updateFunction(f.getCallingConventionName(),new ReturnParameterImpl(DWordDataType.dataType,st,currentProgram),Function.FunctionUpdateType.CUSTOM_STORAGE,true,SourceType.ANALYSIS,new ParameterImpl("source_far",DWordDataType.dataType,4,currentProgram),new ParameterImpl("length",WordDataType.dataType,8,currentProgram));}
    if(!f.getReturn().getVariableStorage().toString().equals("DX:2,AX:2")||f.getParameters().length!=2||f.getParameters()[0].getLength()!=4||f.getParameters()[0].getStackOffset()!=4||f.getParameters()[1].getLength()!=2||f.getParameters()[1].getStackOffset()!=8)throw new Exception("ABI mismatch");w.println("verified_ABI\t"+s[2]+"\t"+f.getReturn().getVariableStorage()+"\tsource_far:stack4:4,length:stack8:2");
   }
   if(!write){String source="N3D-"+v+(v.equals("17")||v.equals("18")?".EXE":".exe")+".file0.bin.unpacked.bin";byte[] expected=Files.readAllBytes(Paths.get(args[2],source));for(int i=0;i<expected.length;i++)if(currentProgram.getMemory().getByte(toAddr(0x10000L+i))!=expected[i])throw new Exception("Memory mismatch "+i);w.println("runtime_bytes_verified\t"+expected.length);}
   d.openProgram(currentProgram);
   for(String l:Files.readAllLines(new File(out,"seeds.tsv").toPath())){String[] s=l.split("\t");if(!s[0].equals(v))continue;Function f=currentProgram.getFunctionManager().getFunctionAt(toAddr(s[2]));DecompileResults r=d.decompileFunction(f,30,monitor);w.println("decompile\t"+s[1]+"\t"+r.decompileCompleted()+"\t"+r.getErrorMessage());if(r.decompileCompleted())Files.writeString(new File(out,currentProgram.getName()+"."+args[1]+"."+s[1]+".c").toPath(),r.getDecompiledFunction().getC());}
  w.flush();}finally{d.dispose();}
 }
}
