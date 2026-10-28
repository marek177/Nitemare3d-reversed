import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.nio.file.*;
import java.security.MessageDigest;
public class N3DHeapReuseTypes extends GhidraScript {
 String inventory() throws Exception {var md=MessageDigest.getInstance("SHA-256");var listing=currentProgram.getListing();for(var it=listing.getInstructions(true);it.hasNext();){var i=it.next();md.update(i.getAddress().toString().getBytes());md.update(i.getBytes());}for(var it=currentProgram.getFunctionManager().getFunctions(true);it.hasNext();)md.update(it.next().getEntryPoint().toString().getBytes());return java.util.HexFormat.of().formatHex(md.digest());}
 public void run() throws Exception {
  var a=Files.readString(Path.of(getScriptArgs()[1])).trim().split("\\t");var out=Path.of(getScriptArgs()[0]);Files.createDirectories(out);var before=inventory();
  var alloc=getFunctionAt(toAddr(a[0]));alloc.setComment("Far allocator DX:AX or0. Verified empty heap132 cases (pass14) plus180 original alloc/free sequences (pass16): released-block reuse, split, adjacent coalescing during allocation, larger-request growth and failed-growth recovery. Only DOS48 mocked; failure callback null. Not exhaustive arbitrary heap validation.");
  var free=getFunctionAt(toAddr(a[1]));free.setName("ReleaseFarBlock",SourceType.USER_DEFINED);free.setCallingConvention("__cdecl16far");free.setCustomVariableStorage(true);free.replaceParameters(Function.FunctionUpdateType.CUSTOM_STORAGE,true,SourceType.USER_DEFINED,new ParameterImpl("blockPointer",DWordDataType.dataType,4,currentProgram));free.setReturnType(VoidDataType.dataType,SourceType.USER_DEFINED);free.setComment("If segment!=0: OR1 into byte at segment:(offset-2 mod65536); otherwise no write. Original mode4 consumer192 cases (pass15), heap reuse180 sequences (pass16). No immediate DOS release/coalesce; subsequent allocation can merge adjacent free blocks. Return registers unspecified, treated as void.");
  var after=inventory();if(!before.equals(after))throw new IllegalStateException("Instruction/function inventory changed");Files.writeString(out.resolve("inventory.txt"),before+"\n"+after+"\n");var d=new DecompInterface();d.openProgram(currentProgram);var log=new StringBuilder("entry\tname\treturn_storage\tparameters\n");for(var f:new Function[]{alloc,free}){var r=d.decompileFunction(f,60,monitor);if(!r.decompileCompleted())throw new IllegalStateException("Failed "+f.getEntryPoint());Files.writeString(out.resolve(f.getEntryPoint().toString().replace(':','_')+".c"),r.getDecompiledFunction().getC());log.append(f.getEntryPoint()+"\t"+f.getName()+"\t"+f.getReturn().getVariableStorage()+"\t");for(var p:f.getParameters())log.append(p.getName()+":"+p.getVariableStorage()+";");log.append("\n");}d.dispose();Files.writeString(out.resolve("typed_functions.tsv"),log);
 }
}
