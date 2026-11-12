"""Independent byte-level model for cache reset mode2 and level metadata marking.
No allocation,OS calls,coalescing or reclamation is inferred.
"""
import struct

class CacheResetModel:
    def __init__(self, ram, ds):
        self.ram=bytearray(ram);self.ds=ds;self.base=ds*16;self.writes=[];self.marks=[];self.owners=[]
    def word(self,a):
        assert 0<=a<=len(self.ram)-2
        return struct.unpack_from('<H',self.ram,a)[0]
    def far(self,a):
        assert 0<=a<=len(self.ram)-4
        off,seg=struct.unpack_from('<HH',self.ram,a);return seg*16+off
    def put(self,a,n,value,role):
        assert 0<=a and a+n<=len(self.ram)
        value &= (1<<(8*n))-1
        self.ram[a:a+n]=value.to_bytes(n,'little');self.writes.append(dict(address=a,size=n,value=value,role=role))
    def count(self,off):
        w=self.word(self.base+off);return w if w<32768 else w-65536
    def reset(self):
        for i in range(10):
            p=self.far(self.base+0x34cc+4*i);owner=self.word(p+4)
            if owner:self.put(self.base+owner+6,4,0,'wall_record_buffer_clear');self.owners.append(('wall',i,owner))
            self.put(p+4,2,0,'wall_slot_owner_clear');self.put(p,4,0,'wall_slot_stamp_clear')
        count=self.count(0x3504);assert count<=128
        # 0242 loads a code-relocated immediate segment, not mutable DS:[2560].
        table=(self.ds-0x2771+0x1be7)*16
        for i in range(max(0,count)):
            p=self.far(table+4*i);owner=self.word(p)
            if owner:self.put(self.base+owner+6,4,0,'object_record_buffer_clear');self.owners.append(('object',i,owner))
            self.put(p,2,0,'object_slot_owner_clear')
        for i in range(4):
            p=self.far(self.base+0x34f4+4*i)
            self.put(p+4,2,0,'sound_slot_marker_clear');self.put(p,4,0,'sound_slot_stamp_clear')
        self.put(self.base+0x350a,2,0,'XMS_used_cursor_clear')
    def mark(self,ptr,role):
        self.marks.append(dict(pointer=ptr,role=role))
        if self.word(self.base+0x20e8)>=ptr:return
        header=(ptr-2)&65535
        self.put(self.base+header,1,self.ram[self.base+header]|1,'near_block_tag_set')
        if self.word(self.base+0x20ea)>header:self.put(self.base+0x20ea,2,header,'near_heap_minimum_update')
    def cleanup(self):
        self.reset()
        for off,countoff,role in [(0x4316,0x6272,'wall_metadata'),(0x3d24,0x6274,'object_metadata')]:
            for i in range(max(0,self.count(countoff))):self.mark(self.word(self.base+off+8*i),role)
        world=self.word(self.base+0x256c)*16
        for i in range(max(0,self.count(0x6270))):
            at=world+10+28*i;assert at<len(self.ram);cls=self.ram[at];field=self.base+0x3d22+8*cls;ptr=self.word(field)
            if ptr:self.mark(ptr,'class_bank');self.put(field,2,0,'class_bank_pointer_clear')
