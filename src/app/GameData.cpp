#include "app/GameData.hpp"

#include <stdexcept>
#include <string>

namespace n3d {

GameData GameData::loadEpisode(const std::filesystem::path& root, int episode) {
    if (episode < 1 || episode > 3) {
        throw std::runtime_error("Episode must be 1, 2, or 3");
    }

    const std::string suffix = "." + std::to_string(episode);
    GameData data;
    data.episode_.maps = MapArchive::load(root / ("MAP" + suffix));
    data.episode_.images = ImgArchive::load(root / ("IMG" + suffix));
    data.episode_.objects = DefinitionTable::load(root / ("OBJECTS" + suffix));
    data.episode_.walls = DefinitionTable::load(root / ("WALLS" + suffix));
    data.palette_ = Pcx8::extractPalette(root / "GAME.PAL");
    return data;
}

} // namespace n3d
