import ghidra.app.script.GhidraScript;
import ghidra.program.database.mem.FileBytes;
import ghidra.program.model.mem.*;
import java.nio.file.*;
import java.io.*;
public class ExportDosSources extends GhidraScript {
 public void run() throws Exception {
  String n=currentProgram.getName().toLowerCase();if(!n.matches("n3d-(10|11|12|15|17|18|19)\\.exe"))return;
  File out=new File(getScriptArgs()[0]);out.mkdirs();
  try(PrintWriter w=new PrintWriter(new File(out,currentProgram.getName()+".source.tsv"))){
   int index=0;for(FileBytes fb:currentProgram.getMemory().getAllFileBytes()){
    byte[] b=new byte[(int)fb.getSize()];fb.getOriginalBytes(0,b);String file=currentProgram.getName()+".file"+(index++)+".bin";Files.write(new File(out,file).toPath(),b);w.println("source\t"+file+"\t"+fb.getFilename()+"\t"+b.length);
   }
   for(MemoryBlock mb:currentProgram.getMemory().getBlocks())w.println("block\t"+mb.getName()+"\t"+mb.getStart()+"\t"+mb.getSize()+"\t"+mb.isInitialized());
  }
 }
}
