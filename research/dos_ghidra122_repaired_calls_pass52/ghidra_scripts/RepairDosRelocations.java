import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import java.nio.file.*;
import java.io.*;
import java.util.*;
public class RepairDosRelocations extends GhidraScript {
 int u16(byte[] b,int p){return (b[p]&255)|((b[p+1]&255)<<8);}
 public void run() throws Exception {
  String[] args=getScriptArgs();String n=currentProgram.getName().toLowerCase();String v=null;
  for(String x:new String[]{"10","11","12","15","17","18","19"})if(n.equals("n3d-"+x+".exe"))v=x;
  if(v==null)return;
  byte[] src=Files.readAllBytes(Paths.get(args[0],"DOS"+(v.equals("19")?"18":v)+".exe"));int header=u16(src,8)*16,count=u16(src,6),rt=u16(src,24);boolean repair=args.length>2&&args[2].equals("repair");
  File out=new File(args[1]);out.mkdirs();int functions=currentProgram.getFunctionManager().getFunctionCount();ArrayList<Address> patched=new ArrayList<>();ArrayList<Integer> values=new ArrayList<>();int eligible=0,unmapped=0,different=0,other=0;
  try(PrintWriter w=new PrintWriter(new File(out,currentProgram.getName()+".relocations.tsv"))){
   w.println("mode\t"+(repair?"repair":"audit"));w.println("mz_relocations\t"+count);w.println("functions_before\t"+functions);
   for(int i=0;i<count;i++) {
    int p=rt+4*i,z=u16(src,p+2)*16+u16(src,p);Address a=toAddr(0x10000L+z);int old=u16(src,header+z),value=(old+0x1000)&65535;int actual;
    try{actual=currentProgram.getMemory().getShort(a)&65535;}catch(Exception e){unmapped++;continue;}
    if(actual!=old){different++;continue;}
    Instruction ins=currentProgram.getListing().getInstructionContaining(a);
    if(ins==null||ins.getLength()!=5||!a.equals(ins.getMinAddress().add(3))){other++;continue;}
    byte[] ib=ins.getBytes();if((ib[0]&255)!=0x9a){other++;continue;}
    boolean same=true;for(int j=0;j<5;j++)if(ib[j]!=src[header+z-3+j])same=false;
    if(!same){different++;continue;}eligible++;
    String before=ins.toString();Address start=ins.getMinAddress(),end=ins.getMaxAddress();
    if(repair){currentProgram.getListing().clearCodeUnits(start,end,false);currentProgram.getMemory().setShort(a,(short)value);DisassembleCommand cmd=new DisassembleCommand(start,new AddressSet(start,end),false);cmd.applyTo(currentProgram,monitor);Instruction after=currentProgram.getListing().getInstructionAt(start);if(after==null||after.getLength()!=5)throw new Exception("Redisassembly failed "+start);patched.add(a);values.add(value);w.println("patched\t"+start+"\t"+String.format("%04x",old)+"\t"+String.format("%04x",value)+"\t"+before+"\t"+after);}
    else w.println("eligible\t"+start+"\t"+String.format("%04x",old)+"\t"+String.format("%04x",value)+"\t"+before);
   }
   for(int i=0;i<patched.size();i++)if((currentProgram.getMemory().getShort(patched.get(i))&65535)!=values.get(i))throw new Exception("Postcondition failure");
   if(currentProgram.getFunctionManager().getFunctionCount()!=functions)throw new Exception("Function count changed");
   w.println("eligible_calls\t"+eligible);w.println("unmapped_relocations\t"+unmapped);w.println("different_values\t"+different);w.println("other_relocations\t"+other);w.println("patched_calls\t"+patched.size());w.println("functions_after\t"+currentProgram.getFunctionManager().getFunctionCount());
  }
 }
}
