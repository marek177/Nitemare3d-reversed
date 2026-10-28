import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.*;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.listing.*;
import java.nio.file.*;
public class N3DMultiABIFix extends GhidraScript {
 public void run() throws Exception {
  var s=Files.readString(Path.of(getScriptArgs()[1])).replace("\n","").replace("\r","").split("\\t",-1);Path out=Path.of(getScriptArgs()[0]);Files.createDirectories(out);StringBuilder rows=new StringBuilder("entry\tbefore_type\tbefore_storage\tafter_type\tafter_storage\n");
  for(int n=0;n<2;n++){
   var f=getFunctionAt(toAddr(s[n]));var before=f.getReturnType()+"\t"+f.getReturn().getVariableStorage();f.setCallingConvention("__cdecl16far");f.setCustomVariableStorage(true);f.replaceParameters(Function.FunctionUpdateType.CUSTOM_STORAGE,true,SourceType.USER_DEFINED,new ParameterImpl(n==0?"vectorOffset":"mode",UnsignedShortDataType.dataType,4,currentProgram));
   if(n==0){f.setReturn(ByteDataType.dataType,new VariableStorage(currentProgram,currentProgram.getRegister("AL")),SourceType.USER_DEFINED);f.setComment("Verified byte return in AL, not boolean AX. 1371 original post-projection executions in this build; two explicit return paths assign AL only. One word stack argument at SPentry+4. Projection/prologue runtime parity not claimed.");}
   else{f.setReturn(DWordDataType.dataType,new VariableStorage(currentProgram,currentProgram.getRegister("DX"),currentProgram.getRegister("AX")),SourceType.USER_DEFINED);if(f.getReturn().getVariableStorage().isForcedIndirect())throw new IllegalStateException("Hidden return pointer");f.setComment("Verified mode1 return storage DX:AX. Original mode1 executions test zero flag ->0, nonzero ->DS:flagOffset. One word mode at SPentry+4; no hidden return pointer. Return meaning of other modes remains separately unresolved.");}
   rows.append(f.getEntryPoint()+"\t"+before+"\t"+f.getReturnType()+"\t"+f.getReturn().getVariableStorage()+"\n");
  }
  StringBuilder refs=new StringBuilder("candidate\tfrom\ttype\n");if(s.length>2&&!s[2].isBlank())for(String e:s[2].split(",")){var f=getFunctionAt(toAddr(e));if(f==null)throw new IllegalStateException("Candidate missing");f.setComment("Unsubstantiated analysis entry seed. Its documented original near CALL source(s) resolve in another CS-preserving target, not here. No claim of global runtime unreachability. Label and bytes retained pending full dynamic-pointer analysis.");for(var it=currentProgram.getReferenceManager().getReferencesTo(f.getEntryPoint());it.hasNext();){var r=it.next();refs.append(e+"\t"+r.getFromAddress()+"\t"+r.getReferenceType()+"\n");}}
  Files.writeString(out.resolve("abi_fixes.tsv"),rows);Files.writeString(out.resolve("candidate_incoming.tsv"),refs);
 }
}
