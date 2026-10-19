#include "formats/Pcx8.hpp"
#include <cassert>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <vector>

int main() {
    const auto path = std::filesystem::temp_directory_path() / "n3d_supplied_palette_test.pal";
    auto save = [&](const std::vector<std::uint8_t>& bytes) {
        std::ofstream out(path, std::ios::binary);
        out.write(reinterpret_cast<const char*>(bytes.data()), bytes.size());
        assert(out.good());
    };
    std::vector<std::uint8_t> bytes(1924);
    bytes[0]=0x3A; bytes[1]=0x3C; bytes[3]=0x1F;
    for (unsigned i=0; i<256; ++i) {
        bytes[1156+i*3]=static_cast<std::uint8_t>(i);
        bytes[1157+i*3]=static_cast<std::uint8_t>(255-i);
        bytes[1158+i*3]=17;
    }
    save(bytes);
    auto palette=n3d::Pcx8::extractPalette(path);
    for (unsigned i=0; i<256; ++i) {
        assert(palette[i].r==i && palette[i].g==255-i && palette[i].b==17);
    }
    bytes.pop_back(); save(bytes);
    bool rejected=false;
    try { (void)n3d::Pcx8::extractPalette(path); } catch(const std::runtime_error&) { rejected=true; }
    assert(rejected);
    bytes.resize(1924); bytes[0]=0; save(bytes); rejected=false;
    try { (void)n3d::Pcx8::extractPalette(path); } catch(const std::runtime_error&) { rejected=true; }
    assert(rejected);
    // Retain the valid PCX route: one 1x1 scanline and a 256-color palette.
    bytes.assign(128+1+769,0); bytes[0]=0x0A; bytes[2]=1; bytes[3]=8;
    bytes[65]=1; bytes[66]=1; bytes[128]=7; bytes[129]=0x0C;
    bytes[130+7*3]=23; save(bytes);
    assert(n3d::Pcx8::extractPalette(path)[7].r==23);
    assert(n3d::Pcx8::load(path).pixels[0]==7);
    std::filesystem::remove(path);
}
