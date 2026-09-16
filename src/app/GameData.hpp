#pragma once

#include "formats/DefinitionTable.hpp"
#include "formats/ImgArchive.hpp"
#include "formats/MapArchive.hpp"
#include "formats/Pcx8.hpp"

#include <array>
#include <filesystem>

namespace n3d {

struct EpisodeData {
    MapArchive maps;
    ImgArchive images;
    DefinitionTable objects;
    DefinitionTable walls;
};

class GameData {
public:
    static GameData loadEpisode(const std::filesystem::path& root, int episode);

    const EpisodeData& episode() const { return episode_; }
    const std::array<Rgb8, 256>& palette() const { return palette_; }

private:
    EpisodeData episode_;
    std::array<Rgb8, 256> palette_{};
};

} // namespace n3d
