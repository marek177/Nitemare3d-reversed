import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.app.plugin.processors.sleigh.*;
import ghidra.program.model.pcode.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.lang.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;
public class N3DMultiRealModeProbe extends GhidraScript {
 static long[] scope;
 static class ExplicitCallback extends DecompileCallback {
  final Program p;final StringBuilder events;
  ExplicitCallback(Program p,Language l,CompilerSpec c,PcodeDataTypeManager dt,StringBuilder e){super(p,l,c,dt);this.p=p;events=e;}
  public void getPcode(Address address,PatchEncoder encoder){
   Instruction ins=p.getListing().getInstructionAt(address);long physical=address.getOffset();boolean farScope=(physical>=scope[0]&&physical<=scope[1])||(physical>=scope[2]&&physical<=scope[3]),nearScope=physical>=scope[4]&&physical<=scope[5];
   if(ins==null||(!farScope&&!nearScope)){super.getPcode(address,encoder);return;}
   try{PcodeOp[] original=ins.getPcode(true);boolean internal=false;for(PcodeOp op:original)if((op.getOpcode()==PcodeOp.BRANCH||op.getOpcode()==PcodeOp.CBRANCH)&&op.getInput(0).isConstant())internal=true;
    ArrayList<PcodeOp> ops=new ArrayList<>();boolean changed=false;int slot=0;
    for(PcodeOp op:original){
     if(farScope&&!internal&&!(op.getNumInputs()>1&&op.getInput(1).isRegister()&&op.getInput(1).getAddress().equals(p.getRegister("SS").getAddress()))&&op.getOpcode()==PcodeOp.CALLOTHER&&op.getNumInputs()==3&&"segment".equals(p.getLanguage().getUserDefinedOpName((int)op.getInput(0).getOffset()))){
      if(op.getOutput()==null||op.getOutput().getSize()!=4||op.getInput(1).getSize()!=2||op.getInput(2).getSize()!=2)throw new IllegalStateException("Unsupported segment widths");
      AddressSpace unique=p.getAddressFactory().getAddressSpace("unique"),constant=p.getAddressFactory().getConstantSpace();long temp=0x70000000L+physical*0x100+slot++*0x10;Varnode base=new Varnode(unique.getAddress(temp),4),shifted=new Varnode(unique.getAddress(temp+4),4),offset=new Varnode(unique.getAddress(temp+8),4);
      ops.add(new PcodeOp(address,ops.size(),PcodeOp.INT_ZEXT,new Varnode[]{op.getInput(1)},base));ops.add(new PcodeOp(address,ops.size(),PcodeOp.INT_LEFT,new Varnode[]{base,new Varnode(constant.getAddress(4),4)},shifted));ops.add(new PcodeOp(address,ops.size(),PcodeOp.INT_ZEXT,new Varnode[]{op.getInput(2)},offset));ops.add(new PcodeOp(address,ops.size(),PcodeOp.INT_ADD,new Varnode[]{shifted,offset},op.getOutput()));events.append(address+"\tSEGMENT_LINEARIZE\t"+op.getInput(1)+"\t"+op.getInput(2)+"\n");changed=true;
     }else ops.add(op);
    }
    if(nearScope){byte[] b=ins.getBytes();Integer disp=null;if(b.length==3&&((b[0]&255)==0xe8||(b[0]&255)==0xe9))disp=(int)(short)((b[1]&255)|((b[2]&255)<<8));else if(b.length==4&&(b[0]&255)==15&&(b[1]&255)>=0x80&&(b[1]&255)<=0x8f)disp=(int)(short)((b[2]&255)|((b[3]&255)<<8));
     if(disp!=null){long correct=scope[4]+(((int)(physical-scope[4])+b.length+disp)&65535);for(PcodeOp op:ops)if((op.getOpcode()==PcodeOp.BRANCH||op.getOpcode()==PcodeOp.CBRANCH||op.getOpcode()==PcodeOp.CALL)&&op.getNumInputs()>0&&!op.getInput(0).isConstant()&&op.getInput(0).getAddress().getAddressSpace().equals(p.getAddressFactory().getDefaultAddressSpace())&&op.getInput(0).getOffset()!=correct){events.append(address+"\t"+op.getMnemonic()+"\t"+op.getInput(0).getAddress()+"\t"+Long.toHexString(correct)+"\n");op.setInput(new Varnode(p.getAddressFactory().getDefaultAddressSpace().getAddress(correct),op.getInput(0).getSize()),0);changed=true;}}
    }
    if(changed)DecompileCallback.encodeInstruction(encoder,address,ops.toArray(PcodeOp[]::new),ins.getLength(),0,p.getAddressFactory());else super.getPcode(address,encoder);
   }catch(Exception e){throw new RuntimeException(e);}
  }
 }
 static class ExplicitDecompiler extends DecompInterface {
  final StringBuilder events;ExplicitDecompiler(StringBuilder e){events=e;}
  protected void initializeProcess() throws IOException,DecompileException {
   super.initializeProcess();SleighLanguage lang=(SleighLanguage)getLanguage();XmlEncode enc=new XmlEncode(false);lang.encodeTranslator(enc,program.getAddressFactory(),UniqueLayout.SLEIGH_BASE.getOffset(lang));String tspec=enc.toString();enc.clear();getDataTypeManager().encodeCoreTypes(enc);String core=enc.toString();enc.clear();compilerSpec.encode(enc);String cspec=enc.toString();String pspec=Files.readString(Path.of(lang.getLanguageDescription().getSpecFile().getAbsolutePath()));decompProcess.deregisterProgram();decompCallback=new ExplicitCallback(program,getLanguage(),compilerSpec,getDataTypeManager(),events);decompProcess.registerProgram(decompCallback,pspec,cspec,tspec,core,program);
  }
 }
 public void run() throws Exception {
  scope=java.util.Arrays.stream(Files.readString(Path.of(getScriptArgs()[1])).trim().split("\\t")).mapToLong(Long::parseLong).toArray();if(scope.length!=7)throw new IllegalStateException("Bad scope");File out=new File(getScriptArgs()[0]);out.mkdirs();StringBuilder events=new StringBuilder("source\tkind\tinput_or_old_target\tinput_or_new_target\n"),rows=new StringBuilder("entry\tmodel\tcompleted\tC_available\terror\n");
  boolean all=true;java.util.ArrayList<String> addresses=new java.util.ArrayList<>();if(all){for(var it=currentProgram.getFunctionManager().getFunctions(true);it.hasNext();)addresses.add(it.next().getEntryPoint().toString());}else addresses.addAll(java.util.List.of("1000:01e0","1000:0aea","1d29:20aa","183d:143c","1fd9:016a","1fd9:048e"));
  for(String model:new String[]{"stock","explicit_real_mode_pcode_view"}){DecompInterface d=model.equals("stock")?new DecompInterface():new ExplicitDecompiler(events);if(!d.openProgram(currentProgram))throw new IOException(d.getLastMessage());for(String address:addresses){var r=d.decompileFunction(getFunctionAt(toAddr(address)),30,monitor);rows.append(address+"\t"+model+"\t"+r.decompileCompleted()+"\t"+(r.getDecompiledFunction()!=null)+"\t"+r.getErrorMessage().replace('\n',' ')+"\n");if(r.getDecompiledFunction()!=null)Files.writeString(new File(out,address.replace(':','_')+"_"+model+".c").toPath(),r.getDecompiledFunction().getC());}d.dispose();}
  Files.writeString(new File(out,"explicit_model_results.tsv").toPath(),rows.toString());Files.writeString(new File(out,"explicit_pcode_changes.tsv").toPath(),events.toString());println(rows.toString());
 }
}
