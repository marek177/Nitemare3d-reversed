#include "platform/sdl/SDLVideo.hpp"

#include <stdexcept>
#include <string>

namespace n3d {

static std::runtime_error sdlError(const char* prefix) {
    return std::runtime_error(std::string(prefix) + ": " + SDL_GetError());
}

SDLVideo::SDLVideo(int width, int height, int scale) {
    if (!SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS | SDL_INIT_AUDIO)) throw sdlError("SDL_Init failed");
    window_ = SDL_CreateWindow("Nitemare 3D - reconstructed SDL3 runtime", width * scale, height * scale, SDL_WINDOW_RESIZABLE);
    if (!window_) throw sdlError("SDL_CreateWindow failed");
    renderer_ = SDL_CreateRenderer(window_, nullptr);
    if (!renderer_) throw sdlError("SDL_CreateRenderer failed");
    texture_ = SDL_CreateTexture(renderer_, SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_STREAMING, width, height);
    if (!texture_) throw sdlError("SDL_CreateTexture failed");
    SDL_SetTextureScaleMode(texture_, SDL_SCALEMODE_NEAREST);
}

SDLVideo::~SDLVideo() {
    if (texture_) SDL_DestroyTexture(texture_);
    if (renderer_) SDL_DestroyRenderer(renderer_);
    if (window_) SDL_DestroyWindow(window_);
    SDL_Quit();
}

SDLInputState SDLVideo::pollInput() {
    SDLInputState out;
    SDL_Event event;
    while (SDL_PollEvent(&event)) {
        if (event.type == SDL_EVENT_QUIT) out.quit = true;
        if (event.type == SDL_EVENT_KEY_DOWN) {
            if (event.key.key == SDLK_ESCAPE) out.quit = true;
            if (!event.key.repeat && (event.key.key == SDLK_SPACE || event.key.key == SDLK_E)) out.actionPressed = true;
        }
    }
    int count = 0;
    const bool* keys = SDL_GetKeyboardState(&count);
    (void)count;
    out.forward = keys[SDL_SCANCODE_W] || keys[SDL_SCANCODE_UP];
    out.backward = keys[SDL_SCANCODE_S] || keys[SDL_SCANCODE_DOWN];
    out.turnLeft = keys[SDL_SCANCODE_LEFT];
    out.turnRight = keys[SDL_SCANCODE_RIGHT];
    out.strafeLeft = keys[SDL_SCANCODE_A];
    out.strafeRight = keys[SDL_SCANCODE_D];
    return out;
}

void SDLVideo::present(const Framebuffer& fb, const std::array<Rgb8, 256>& palette) {
    const auto argb = fb.toArgb8888(palette);
    if (!SDL_UpdateTexture(texture_, nullptr, argb.data(), fb.width() * static_cast<int>(sizeof(std::uint32_t)))) throw sdlError("SDL_UpdateTexture failed");
    SDL_SetRenderDrawColor(renderer_, 0, 0, 0, 255);
    SDL_RenderClear(renderer_);
    SDL_RenderTexture(renderer_, texture_, nullptr, nullptr);
    SDL_RenderPresent(renderer_);
}

} // namespace n3d
