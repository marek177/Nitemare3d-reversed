import ghidra.app.script.GhidraScript;
import ghidra.program.model.mem.*;
import ghidra.program.model.lang.*;
import java.nio.file.*;
import java.math.BigInteger;
import java.io.*;
public class PrepareRuntimeImage extends GhidraScript {
 public void run() throws Exception {
  String[] args=getScriptArgs();String v=currentProgram.getName().substring(3,5);String original="N3D-"+v+(v.equals("17")||v.equals("18")?".EXE":".exe")+".file0.bin.unpacked.bin";
  byte[] expected=Files.readAllBytes(Paths.get(args[0],original));
  for(int i=0;i<expected.length;i++)if(currentProgram.getMemory().getByte(toAddr(0x10000L+i))!=expected[i])throw new Exception("Runtime memory mismatch "+i);
  int ds=0;switch(v){case "10":ds=0x3360;break;case "11":ds=0x3395;break;case "12":ds=0x339b;break;case "15":ds=0x374a;break;case "17":ds=0x3754;break;case "18":ds=0x376d;break;}
  Register reg=currentProgram.getRegister("DS");for(MemoryBlock mb:currentProgram.getMemory().getBlocks())if(mb.getStart().getAddressSpace().equals(currentProgram.getAddressFactory().getDefaultAddressSpace()))currentProgram.getProgramContext().setValue(reg,mb.getStart(),mb.getEnd(),BigInteger.valueOf(ds));
  File out=new File(args[1]);out.mkdirs();try(PrintWriter w=new PrintWriter(new File(out,currentProgram.getName()+".prepared.tsv"))){w.println("runtime_bytes_verified\t"+expected.length);w.println("analysis_DS_assumption\t"+Integer.toHexString(ds));w.println("language\t"+currentProgram.getLanguageID());}
 }
}
