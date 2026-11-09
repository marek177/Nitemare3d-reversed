"""Bounded CPU regression; emulation is not an original-game runtime witness.
Run: python3 -m unittest discover -s tests -p test_rng_unobserved_static.py
Dependencies: iced-x86==1.21.0, unicorn (tested with 2.1.4).
"""
import csv
import json
import sys
import unittest
import tempfile
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UcError
from unicorn.x86_const import UC_X86_REG_AX, UC_X86_REG_DX, UC_X86_REG_CX, UC_X86_REG_EFLAGS
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from audit_unobserved_rng_callers import coordinate_count, SITES, census
from normalize_sign_extension import correction
E=ROOT/'docs/evidence/2026-10-25'

class CPU:
    def __init__(self):
        self.uc=Uc(UC_ARCH_X86,UC_MODE_16);self.uc.mem_map(0,0x10000)
    def run(self,code,ax=0,dx=0,cx=0,flags=0x202):
        self.uc.mem_write(0x1000,code)
        for r,v in [(UC_X86_REG_AX,ax),(UC_X86_REG_DX,dx),(UC_X86_REG_CX,cx),(UC_X86_REG_EFLAGS,flags)]: self.uc.reg_write(r,v)
        self.uc.emu_start(0x1000,0x1000+len(code),count=32)
        return tuple(self.uc.reg_read(r) for r in (UC_X86_REG_AX,UC_X86_REG_DX,UC_X86_REG_CX,UC_X86_REG_EFLAGS))

class RNGStaticTests(unittest.TestCase):
    def test_wrong_source_rejected_before_membership(self):
        with tempfile.TemporaryDirectory() as d:
            bad=Path(d)/'wrong.exe';bad.write_bytes(b'MZ')
            with self.assertRaisesRegex(ValueError,'wrong source EXE SHA256'):
                census(bad,Path(d)/'absent.asm')

    def test_measured_coverage_partition(self):
        census=json.loads((E/'RNG_state_reference_audit.json').read_text())
        direct={r['pc'] for r in census['direct_far_edges'] if r['role']=='RNG_wrapper'}
        with (E/'RNG_DEMO_rng_run_f_calls.csv').open() as f:
            observed={r['literal_wrapper_callsite'] for r in csv.DictReader(f)}
        self.assertEqual(direct-observed,set(SITES))
        self.assertEqual(len(direct),22);self.assertEqual(len(observed),11)

    def test_cwd_division_from_real_postcall_sequences(self):
        audit=json.loads((E/'RNG_unobserved_static_audit.json').read_text())
        cpu=CPU()
        divisors={'04C7:09F6':8,'04C7:0C37':80,'083D:1698':62,'083D:16A7':36,'083D:18F2':4,'083D:1B3C':3}
        for site,d in divisors.items():
            row=next(r for r in audit['sites'] if r['pc']==site)
            prefix=row['post_call_effects'][:3]
            self.assertEqual([r['bytes'] for r in prefix],[f'b9{d:02x}00','99','f7f9'])
            code=b''.join(bytes.fromhex(r['bytes']) for r in prefix)
            for a in [0,1,d-1,d,d+1,127,255,256,32767,32768,65535]:
                q,r,_,_=cpu.run(code,ax=a,dx=0xdead)
                signed=a if a<32768 else a-65536
                quotient=abs(signed)//d * (-1 if signed<0 else 1)
                self.assertEqual(q,quotient&65535)
                self.assertEqual(r,(signed-quotient*d)&65535)

    def test_sign_extension_width_and_flag_preservation(self):
        cpu=CPU()
        for code,reads,writes in [('98',['al'],['ax']),('99',['ax'],['dx']),('6698',['ax'],['eax']),('6699',['eax'],['edx'])]:
            effect=correction(bytes.fromhex(code),0)
            self.assertEqual(effect['register_reads'],reads);self.assertEqual(effect['register_writes'],writes)
            self.assertEqual(effect['eflags_mask'],0)
        for ax in [0,127,128,255,0x7fff,0x8000,0xffff]:
            a,d,c,f=cpu.run(b'\x99',ax=ax,dx=0xbeef,flags=0xad7)
            self.assertEqual(a,ax);self.assertEqual(d,65535 if ax&32768 else 0)
            self.assertEqual(f&0x8d5,0xad7&0x8d5)

    def test_low_word_cube_and_fault_domain(self):
        cpu=CPU()
        # 1684..1690: AX=CX; one-operand IMUL twice; CX=low cube;
        # AX=500; CWD; IDIV CX. No 32-bit cube substitution is valid.
        code=bytes.fromhex('8bc1f7e9f7e98bc8b8f40199f7f9')
        faults=[]
        for n in range(256):
            cpu=CPU()  # isolate architectural exception state between cases
            try: expected=coordinate_count(n)
            except ZeroDivisionError:
                faults.append(n)
                with self.assertRaises(UcError): cpu.run(code,cx=n)
            else:
                a,_,_,_=cpu.run(code,cx=n)
                self.assertEqual(a,expected&65535)
        self.assertEqual(faults,[0,64,128,192])
        self.assertEqual(coordinate_count(1),500)
        self.assertEqual(coordinate_count(8),0)

    def test_jump_table_domains(self):
        tables=json.loads((E/'RNG_unobserved_static_audit.json').read_text())['jump_tables']
        expected=[{'083D:0490':[8],'083D:049C':[9,10],'083D:04AC':[17,18,19,20]},
                  {'083D:18F2':[27,28,29,30,31]}, {'083D:1B3C':[9,10]}, {'083D:1678':[7]}, {'04C7:0E64':[3],'04C7:0F4A':[7]}]
        for table,groups in zip(tables,expected):
            for target,selectors in groups.items():
                self.assertEqual([int(k) for k,v in table['selector_to_target'].items() if v==target],selectors)

    def test_rng_final_flags_are_byte_sized(self):
        cpu=CPU()
        # RNG core's last instruction is AND AH,7Fh, not AND AX,7FFFh.
        a,_,_,flags=cpu.run(bytes.fromhex('80e47f'),ax=0x0001,flags=0xad7)
        self.assertEqual(a,1)
        self.assertTrue(flags&0x40)  # ZF from AH==0 even though AX!=0
        self.assertEqual(flags&(0x800|1|0x80),0) # OF, CF, SF clear

if __name__=='__main__': unittest.main()
