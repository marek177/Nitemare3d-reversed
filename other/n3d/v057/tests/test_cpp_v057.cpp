#include "../src/N3DV057GeometryCombat.hpp"
#include <cassert>
using namespace n3d_v057;
int main(){
  auto empty=[](std::uint16_t,std::uint16_t){return Tile{};};
  auto ok=[](std::uint16_t,std::uint16_t){return true;};
  auto r=geometryLine(20,20,3,1,16,true,empty,ok);
  assert(r.accepted() && r.traversed.size()==3 && r.examined.size()==2);
  assert(r.traversed[0].first==21 && r.traversed[0].second==20);
  assert(r.traversed[1].first==22 && r.traversed[1].second==21);
  assert(r.traversed[2].first==23 && r.traversed[2].second==21);
  auto lastWall=[](std::uint16_t x,std::uint16_t y){return Tile{static_cast<std::uint8_t>((x==23 && y==21)?6:0),0};};
  assert(geometryLine(20,20,3,1,16,true,lastWall,ok).accepted());
  auto firstWall=[](std::uint16_t x,std::uint16_t y){return Tile{static_cast<std::uint8_t>((x==21 && y==20)?6:0),0};};
  assert(geometryLine(20,20,3,1,16,true,firstWall,ok).exit==GeometryExit::WallBlocked);
  auto objectBlocking=[](std::uint16_t,std::uint16_t){return Tile{0,2};};
  assert(geometryLine(20,20,3,1,16,true,objectBlocking,ok).exit==GeometryExit::ObjectBlocked);
  assert(geometryLine(20,20,3,1,16,false,objectBlocking,ok).accepted());
  assert(!geometryLine(20,20,0,0,16,false,empty,ok).accepted());
  assert(geometryLine(20,20,16,0,16,false,empty,ok).accepted());
  assert(!geometryLine(20,20,17,0,16,false,empty,ok).accepted());
  assert(s16(sar16(0xFFFFu,8))==-1);
  std::vector<MovingWallRecord> records{{0x1234,0x5678,0},{0x1000,0x2000,2}};
  assert(dosMovingWallPass(records,0x1234,0x5678).value());
  assert(!dosMovingWallPass(records,0x1000,0x2000).value());
  assert(!dosMovingWallPass(records,0x1234,0x1111).has_value());
  assert(guardHitLocal(0,0,1,5).route==HitRoute::Lethal);
  assert(guardHitLocal(8,0,1,5).route==HitRoute::NoDamage);
  assert(guardHitLocal(8,3,4,5).route==HitRoute::Strategy4);
  assert(guardHitLocal(8,3,1,7).preState7Callback);
  for(unsigned c=0;c<256;c++){
    for(unsigned mode=0;mode<4;mode++){
      for(unsigned difficulty=0;difficulty<3;difficulty++){
        const auto s=scalarDamage(static_cast<std::uint8_t>(c),static_cast<std::uint8_t>(mode),
          static_cast<std::uint16_t>(difficulty),100,98,7,3);
        assert(s.directRngDraws==1);
        assert(s.eventCallbackRequired==(c==0x15));
        assert(s.appliedByte==static_cast<std::uint8_t>(s.ax));
      }
    }
  }
  assert(scalarDamage(0x0c,0,1,99,100,0).appliedByte==255);
}
