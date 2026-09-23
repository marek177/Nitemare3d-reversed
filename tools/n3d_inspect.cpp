#include "formats/DatArchive.hpp"
#include "formats/DefinitionTable.hpp"
#include "formats/DemoFile.hpp"
#include "formats/FliFile.hpp"
#include "formats/ImgArchive.hpp"
#include "formats/MapArchive.hpp"
#include "formats/Pcx8.hpp"

#include <filesystem>
#include <iomanip>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>

namespace fs = std::filesystem;

static void inspectMap(const fs::path& p) {
    const auto map = n3d::MapArchive::load(p);
    std::cout << p.filename().string() << ": levels=" << map.levels().size() << ", headerCount=" << map.declaredLevelCount() << "\n";
}
static void inspectImg(const fs::path& p) {
    const auto img = n3d::ImgArchive::load(p);
    std::size_t nonZeroWallSlots = 0, exactWallFrameRefs = 0;
    std::size_t nonZeroObjectSlots = 0, exactObjectFrameRefs = 0;
    for (auto off : img.wallSlotOffsets()) {
        if (off != 0) {
            ++nonZeroWallSlots;
            if (img.frameAtExactOffset(off)) ++exactWallFrameRefs;
        }
    }
    for (auto off : img.objectSlotOffsets()) {
        if (off != 0) {
            ++nonZeroObjectSlots;
            if (img.frameAtExactOffset(off)) ++exactObjectFrameRefs;
        }
    }
    std::cout << p.filename().string()
              << ": wallSlots=" << img.wallSlotOffsets().size()
              << ", wallRefs=" << nonZeroWallSlots << "/" << exactWallFrameRefs
              << ", objectSlots=" << img.objectSlotOffsets().size()
              << ", objectRefs=" << nonZeroObjectSlots << "/" << exactObjectFrameRefs
              << ", frames=" << img.frames().size()
              << ", seqdefBanks=" << (img.hasSequenceDefinitions() ? 2 : 0)
              << ", firstData=0x" << std::hex << img.firstDataOffset() << std::dec << "\n";
}
static void inspectDat(const fs::path& p) {
    const auto dat = n3d::DatArchive::load(p);
    std::map<std::string, std::size_t> types;
    for (const auto& e : dat.entries()) ++types[e.typeGuess()];
    std::cout << p.filename().string() << ": entries=" << dat.entries().size() << ", descriptorBytes=" << dat.headerBytesUsed() << ", firstPayload=" << dat.firstPayloadOffset() << "\n";
    for (const auto& [type, count] : types) std::cout << "  " << std::setw(22) << std::left << type << " " << count << "\n";
}
static void inspectDefs(const fs::path& p) {
    const auto defs = n3d::DefinitionTable::load(p);
    std::map<std::string, std::size_t> classes;
    for (const auto& r : defs.records()) ++classes[r.className];
    std::cout << p.filename().string() << ": records=" << defs.records().size() << ", classes=" << classes.size() << "\n";
}
static void inspectDemo(const fs::path& p) {
    const auto d = n3d::DemoFile::load(p);
    std::cout << p.filename().string() << ": header={" << d.rawHeaderWords()[0] << "," << d.rawHeaderWords()[1] << "," << d.rawHeaderWords()[2] << "}, records=" << d.records().size() << ", ticksMonotonic=" << (d.ticksAreMonotonic() ? "yes" : "no");
    if (!d.records().empty()) std::cout << ", lastTick=" << d.records().back().tick;
    std::cout << "\n";
}
static void inspectPcx(const fs::path& p) { const auto pcx = n3d::Pcx8::load(p); std::cout << p.filename().string() << ": " << pcx.width << "x" << pcx.height << " 8-bit PCX\n"; }
static void inspectFli(const fs::path& p) { const auto f = n3d::FliFile::readHeader(p); std::cout << p.filename().string() << ": magic=0x" << std::hex << f.magic << std::dec << ", frames=" << f.frames << ", " << f.width << "x" << f.height << "x" << f.depth << ", speedRaw=" << f.speedRaw << "\n"; }

int main(int argc, char** argv) {
    try {
        fs::path root = argc >= 2 ? fs::path(argv[1]) : fs::path("data/original");
        for (int ep = 1; ep <= 3; ++ep) {
            inspectMap(root / ("MAP." + std::to_string(ep)));
            inspectImg(root / ("IMG." + std::to_string(ep)));
            inspectDefs(root / ("OBJECTS." + std::to_string(ep)));
            inspectDefs(root / ("WALLS." + std::to_string(ep)));
            inspectDemo(root / ("DEMO." + std::to_string(ep)));
        }
        inspectDat(root / "SND.DAT");
        inspectDat(root / "UIF.DAT");
        inspectPcx(root / "GAME.PAL");
        inspectFli(root / "ENDING.FLI");
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "n3d_inspect: " << e.what() << '\n';
        return 1;
    }
}
