"""Read-only semantics model for RE MAX v0.58 evidence-scoped local branches.

Implements numeric dispatch and descriptor slot rejection, not full original game.
May not be used as proof of runtime 1:1 parity or rare-branch reachability.
"""
from dataclasses import dataclass
from typing import Callable

SCORE_08_20=(25,75,50,100,250,150,200,100,100,0,150,150,200,-1000,1000,
             100,200,0,25,100,100,250,250,200,50)
DEATH_08_1F=(35,8,7,36,4,19,14,'rng%3+11','rng%3+11',0,7,7,35,0,0,
             70,70,0,74,2,2,9,70,70)
STATE7_08_1F=(34,'rng%3+56','rng%3+56',59,20,21,16,'rng%2+54','rng%2+54',
              6,63,60,0,0,18,72,71,0,73,13,13,56,61,61)

def class_score(class_id:int)->int:
    return SCORE_08_20[class_id-8] if 8<=class_id<=0x20 else 0

def lethal_if_hp_le_damage(hp_byte:int,damage_byte:int)->bool:
    """Local hit-wrapper comparison after zero-extending 8-bit values."""
    if not 0<=hp_byte<=255 or not 0<=damage_byte<=255:
        raise ValueError('HP/damage here are byte-domain only')
    return hp_byte<=damage_byte

def sfx_backend_initial_gate(sound_enabled_byte:int,selected_slot_first_word:int)->bool:
    """DOS 2.0 C686 entry-only guards. True does NOT establish sound playback."""
    return sound_enabled_byte!=0 and selected_slot_first_word!=0

def apply_score32(original_uint32:int,class_id:int)->int:
    """Exact 32-bit low-word add + high-word ADC for signed16 score."""
    return (original_uint32 + class_score(class_id))&0xFFFFFFFF

def sound_rule(table:tuple,class_id:int)->int|str:
    return table[class_id-8] if 8<=class_id<=0x1F else 0

def select_sound(rule:int|str,next_rng:Callable[[],int])->tuple[int,int]:
    if isinstance(rule,int):return rule,0
    a,b=rule.removeprefix('rng%').split('+');mod,base=int(a),int(b)
    return next_rng()%mod+base,1

@dataclass
class LCG:
    state:int=1
    draws:int=0
    def rand15(self)->int:
        self.state=(self.state*214013+2531011)&0xFFFFFFFF
        self.draws+=1
        return (self.state>>16)&0x7FFF

def variant_select(*,guard_plus12:int,high_flag:int,seven_low_bytes:tuple[int,...],
                   next_rng:Callable[[],int],max_model_draws:int=1000)->tuple[int,int]:
    """Local original branch semantics; bounded only in this diagnostic model.

    With no nonzero selector bytes, original rejection loop has no local exit;
    this diagnostic model raises instead of hanging forever.
    """
    if len(seven_low_bytes)!=7:raise ValueError('exactly 7 descriptor low bytes required')
    if guard_plus12==0 and high_flag!=0:return 7,0
    if not any(seven_low_bytes):
        raise ValueError('model identified all-zero seven-slot rejection (original has no local exit)')
    for attempt in range(1,max_model_draws+1):
        selected=next_rng()%7
        if seven_low_bytes[selected]!=0:return selected,attempt
    raise ValueError('model draw cap exhausted; original remains in rejection loop')

def after_nonfatal_hit(*,strategy:int,seven_low_bytes:tuple[int,...],high_flag:int,
                       next_rng:Callable[[],int])->tuple[int|None,int]:
    """Call path only. GUARD+12 already written to 8 before selector.

    Note: strategy4 exits without this variant selector; state7 SFX call and
    unconditional damage scalar RNG may already have occurred.
    """
    if strategy==4:return None,0
    return variant_select(guard_plus12=8,high_flag=high_flag,
                          seven_low_bytes=seven_low_bytes,next_rng=next_rng)
