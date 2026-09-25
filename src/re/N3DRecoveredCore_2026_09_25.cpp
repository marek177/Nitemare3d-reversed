#include "N3DRecoveredCore_2026_09_25.hpp"
namespace n3d::re20260925 {
uint16_t Rng::next(){s_=s_*0x343FDu+0x269EC3u;return uint16_t((s_>>16)&0x7FFFu);}
int16_t scoreForClass(uint8_t c){switch(c){
case 8:case 26:return 25; case 9:return 75; case 10:case 32:return 50;
case 11:case 15:case 16:case 23:case 27:case 28:return 100;
case 12:case 29:case 30:return 250; case 13:case 18:case 19:return 150;
case 14:case 20:case 24:case 31:return 200; case 17:case 25:return 0;
case 21:return -1000; case 22:return 1000; default:return 0;}}
DamageResult computeDamage(const DamageInput&i){int s=8*int(int16_t(i.projectedRow-i.viewportCenter))+(i.rng%25),d=s;
switch(i.objectClass){
case 12:case 29:d>>=3;break; case 13:d>>=(i.weapon==1||i.weapon==2)?1:3;break;
case 14:case 17:case 20:d>>=(i.weapon==2)?1:3;break;
case 15:case 16:d=(i.weapon==1)?0:(d>>1);break; case 18:case 19:d=(i.weapon==1)?0:(d>>2);break;
case 21:d=0;break; case 22:d=(i.episode==3)?3:0;break;
case 23:d>>=(i.weapon==1)?8:2;break; case 24:d>>=(i.weapon==1)?8:((i.weapon==2)?4:3);break;
case 25:d=0;break; case 26:d=(i.weapon==1)?(d>>1):0;break; case 27:case 28:d>>=1;break;
case 30:d=(i.weapon==1)?0:(d>>3);break; case 31:d=(i.weapon==1)?0:(d>>2);break;}
int t=d;if(i.difficulty==2)t/=2;else if(i.difficulty==0)t*=2;if(t>255)t=255;
return{s,d,t,uint8_t(t&0xFF)};}
std::optional<uint8_t> fireDamage(uint8_t id){if(id==0x3B)return 100;if(id==0x3C)return 10;if(id==0x3D)return 2;return std::nullopt;}
}
