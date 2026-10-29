import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.lang.*;
import java.math.BigInteger;
import java.nio.file.*;
import java.io.*;
public class VerifyAndDecompileRuntime extends GhidraScript {
 public void run() throws Exception {
  String[] args=getScriptArgs();String v=currentProgram.getName().substring(3,5);String source="N3D-"+v+(v.equals("17")||v.equals("18")?".EXE":".exe")+".file0.bin.unpacked.bin";byte[] raw=Files.readAllBytes(Paths.get(args[0],source));
  for(int i=0;i<raw.length;i++)if(currentProgram.getMemory().getByte(toAddr(0x10000L+i))!=raw[i])throw new Exception("Memory mismatch "+i);
  int ds=0;switch(v){case "10":ds=0x3360;break;case "11":ds=0x3395;break;case "12":ds=0x339b;break;case "15":ds=0x374a;break;case "17":ds=0x3754;break;case "18":ds=0x376d;break;}
  File out=new File(args[1]);out.mkdirs();Register reg=currentProgram.getRegister("DS");
  DecompInterface decomp=new DecompInterface();decomp.openProgram(currentProgram);
  try(PrintWriter w=new PrintWriter(new File(out,currentProgram.getName()+".verified.tsv"))){
   w.println("verified_runtime_bytes\t"+raw.length);w.println("functions\t"+currentProgram.getFunctionManager().getFunctionCount());w.println("instructions\t"+currentProgram.getListing().getNumInstructions());
   for(String l:Files.readAllLines(Paths.get(args[1],"seeds.tsv"))){String[] s=l.split("\t");if(!s[0].equals(v))continue;java.math.BigInteger context=currentProgram.getProgramContext().getValue(reg,toAddr(s[2]),false);w.println("DS_context\t"+s[1]+"\t"+s[2]+"\t"+context);if(context==null||context.intValue()!=ds)throw new Exception("Incorrect DS context "+s[2]);Function f=currentProgram.getFunctionManager().getFunctionAt(toAddr(s[2]));if(f==null){w.println("decompile\t"+s[1]+"\tmissing_function");continue;}if(!s[1].equals("dispatcher")){String storage=f.getReturn().getVariableStorage().toString();if(!storage.equals("DX:2,AX:2")||f.getParameters().length!=1||f.getParameters()[0].getStackOffset()!=4||f.getParameters()[0].getLength()!=2)throw new Exception("ABI mismatch "+s[2]);w.println("ABI_verified\t"+s[1]+"\t"+storage+"\tresource_id:stack4:2");}DecompileResults r=decomp.decompileFunction(f,30,monitor);w.println("decompile\t"+s[1]+"\t"+r.decompileCompleted()+"\t"+r.getErrorMessage());if(r.decompileCompleted())Files.writeString(new File(out,currentProgram.getName()+"."+s[1]+".c").toPath(),r.getDecompiledFunction().getC());}
  }finally{decomp.dispose();}
 }
}
