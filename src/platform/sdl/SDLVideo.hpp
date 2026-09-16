#pragma once

#include "formats/Pcx8.hpp"
#include "renderer/Framebuffer.hpp"

#include <SDL3/SDL.h>
#include <array>

namespace n3d {

struct SDLInputState {
    bool quit{};
    bool forward{};
    bool backward{};
    bool turnLeft{};
    bool turnRight{};
    bool strafeLeft{};
    bool strafeRight{};
    bool actionPressed{};
};

class SDLVideo {
public:
    SDLVideo(int width, int height, int scale = 3);
    ~SDLVideo();
    SDLVideo(const SDLVideo&) = delete;
    SDLVideo& operator=(const SDLVideo&) = delete;
    SDLInputState pollInput();
    void present(const Framebuffer& fb, const std::array<Rgb8, 256>& palette);
private:
    SDL_Window* window_{};
    SDL_Renderer* renderer_{};
    SDL_Texture* texture_{};
};

} // namespace n3d
