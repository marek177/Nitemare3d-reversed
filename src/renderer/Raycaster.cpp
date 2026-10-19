#include "renderer/Raycaster.hpp"
#include "renderer/ImgTextureSampler.hpp"

#include <algorithm>
#include <cmath>
#include <limits>

namespace n3d {

void Raycaster::render(Framebuffer& fb, const LevelState& level) {
    const int w = fb.width();
    const int h = fb.height();
    depthBuffer_.assign(static_cast<std::size_t>(w), std::numeric_limits<double>::infinity());

    // Video-reference preview palette only: original gameplay clips show a
    // nearly-neutral charcoal ceiling (~54 RGB) and a near-black floor
    // (~13 RGB). In the supplied GAME.PAL these are closest to indices 7/2.
    // This is NOT a proven DOS DS:627B/627A fill-value reconstruction.
    fb.fillRect(0, 0, w, h / 2, 7);
    fb.fillRect(0, h / 2, w, h - h / 2, 2);

    const auto& player = level.player();
    const double dirX = std::cos(player.angleRadians);
    const double dirY = std::sin(player.angleRadians);
    constexpr double planeScale = 0.66; // ~66 degree horizontal field of view
    const double planeX = -dirY * planeScale;
    const double planeY = dirX * planeScale;

    for (int sx = 0; sx < w; ++sx) {
        const double cameraX = 2.0 * sx / static_cast<double>(w) - 1.0;
        const double rayDirX = dirX + planeX * cameraX;
        const double rayDirY = dirY + planeY * cameraX;

        int mapX = static_cast<int>(std::floor(player.x));
        int mapY = static_cast<int>(std::floor(player.y));

        const double deltaDistX = rayDirX == 0.0 ? 1e30 : std::abs(1.0 / rayDirX);
        const double deltaDistY = rayDirY == 0.0 ? 1e30 : std::abs(1.0 / rayDirY);
        double sideDistX{};
        double sideDistY{};
        int stepX{};
        int stepY{};

        if (rayDirX < 0.0) {
            stepX = -1;
            sideDistX = (player.x - mapX) * deltaDistX;
        } else {
            stepX = 1;
            sideDistX = (mapX + 1.0 - player.x) * deltaDistX;
        }
        if (rayDirY < 0.0) {
            stepY = -1;
            sideDistY = (player.y - mapY) * deltaDistY;
        } else {
            stepY = 1;
            sideDistY = (mapY + 1.0 - player.y) * deltaDistY;
        }

        int side = 0;
        std::uint8_t wallId = 0;
        bool hit = false;
        for (int guard = 0; guard < 128 && !hit; ++guard) {
            if (sideDistX < sideDistY) {
                sideDistX += deltaDistX;
                mapX += stepX;
                side = 0;
            } else {
                sideDistY += deltaDistY;
                mapY += stepY;
                side = 1;
            }

            if (!level.inBounds(mapX, mapY)) {
                break;
            }
            wallId = level.at(mapX, mapY).wall;
            if (level.wallObscuresView(wallId)) {
                hit = true;
            }
        }
        if (!hit) {
            continue;
        }

        double perpWallDist = side == 0
            ? (mapX - player.x + (1 - stepX) / 2.0) / rayDirX
            : (mapY - player.y + (1 - stepY) / 2.0) / rayDirY;
        if (perpWallDist < 0.001) {
            perpWallDist = 0.001;
        }
        depthBuffer_[static_cast<std::size_t>(sx)] = perpWallDist;

        const int lineHeight = static_cast<int>(h / perpWallDist);
        const int drawStart = std::max(0, -lineHeight / 2 + h / 2);
        const int drawEnd = std::min(h - 1, lineHeight / 2 + h / 2);

        const ImgFrame* wallImage = imageBank_
            ? img::imageForSlot(*imageBank_, img::RenderSlot::Wall, wallId) : nullptr;
        if (wallImage) {
            // Hit position on the wall along its horizontal texture axis.
            // The IMG plane is column-major; its complete 64/128-pixel width
            // is sampled over this one grid cell in the playable DDA preview.
            double u = side == 0
                ? player.y + perpWallDist * rayDirY
                : player.x + perpWallDist * rayDirX;
            u -= std::floor(u);
            if ((side == 0 && rayDirX > 0) || (side == 1 && rayDirY < 0)) {
                u = 1.0 - u;
            }
            const double top = static_cast<double>(h - lineHeight) * 0.5;
            for (int y = drawStart; y <= drawEnd; ++y) {
                const double v = (static_cast<double>(y) - top) / lineHeight;
                fb.setPixel(sx, y, img::samplePreviewWallFace(*wallImage, u, v,
                    img::previewWallFaceHalf(side, stepX, stepY)));
            }
        } else {
            // Keep the old solid-color fallback for synthetic fixtures and
            // invalid IMG slots instead of dereferencing a missing frame.
            std::uint8_t color = static_cast<std::uint8_t>(32 + (wallId % 176));
            if (side != 0) {
                color = static_cast<std::uint8_t>(color > 8 ? color - 8 : color);
            }
            for (int y = drawStart; y <= drawEnd; ++y) {
                fb.setPixel(sx, y, color);
            }
        }
    }

    renderPushables(fb, level, dirX, dirY, planeX, planeY);
}

void Raycaster::renderPushables(Framebuffer& fb, const LevelState& level,
                                double dirX, double dirY, double planeX, double planeY) {
    struct SpriteRef {
        const PushableObject* p{};
        double distance2{};
    };
    std::vector<SpriteRef> sprites;
    for (const auto& p : level.pushables()) {
        const double px = static_cast<double>(p.fixedX) / LevelState::FixedUnitsPerTile;
        const double py = static_cast<double>(p.fixedY) / LevelState::FixedUnitsPerTile;
        const double dx = px - level.player().x;
        const double dy = py - level.player().y;
        sprites.push_back({&p, dx * dx + dy * dy});
    }
    std::sort(sprites.begin(), sprites.end(), [](const auto& a, const auto& b) {
        return a.distance2 > b.distance2;
    });

    const double invDet = 1.0 / (planeX * dirY - dirX * planeY);
    for (const auto& s : sprites) {
        const double px = static_cast<double>(s.p->fixedX) / LevelState::FixedUnitsPerTile;
        const double py = static_cast<double>(s.p->fixedY) / LevelState::FixedUnitsPerTile;
        const double relX = px - level.player().x;
        const double relY = py - level.player().y;
        const double transformX = invDet * (dirY * relX - dirX * relY);
        const double transformY = invDet * (-planeY * relX + planeX * relY);
        if (transformY <= 0.05) {
            continue;
        }

        const int screenX = static_cast<int>((fb.width() / 2.0) * (1.0 + transformX / transformY));
        const ImgFrame* sprite = imageBank_
            ? img::imageForSlot(*imageBank_, img::RenderSlot::Object, s.p->objectId) : nullptr;
        const double fullTileHeight = fb.height() / transformY;
        const int spriteH = sprite
            ? std::max(1, static_cast<int>(fullTileHeight * sprite->height / 64.0))
            : std::abs(static_cast<int>(fullTileHeight));
        const int spriteW = sprite
            ? std::max(1, static_cast<int>(fullTileHeight * sprite->width / 64.0))
            : std::max(1, spriteH / 2);
        // IMG sprite baseline follows the floor (rather than centering the
        // smaller source images at eye height). Still only an approximation.
        const int fullBottom = fb.height() / 2 + static_cast<int>(fullTileHeight / 2.0);
        const int fullTop = sprite ? fullBottom - spriteH : fb.height() / 2 - spriteH / 2;
        const int left = screenX - spriteW / 2;
        const int x0 = std::max(0, left);
        const int x1 = std::min(fb.width(), left + spriteW); // exclusive
        const int y0 = std::max(0, fullTop);
        const int y1 = std::min(fb.height(), fullTop + spriteH); // exclusive
        const std::uint8_t color = static_cast<std::uint8_t>(208 + (s.p->objectId % 32));

        for (int stripe = x0; stripe < x1; ++stripe) {
            if (transformY >= depthBuffer_[static_cast<std::size_t>(stripe)]) {
                continue;
            }
            for (int y = y0; y < y1; ++y) {
                if (sprite) {
                    const double u = (stripe - left) / static_cast<double>(spriteW);
                    const double v = (y - fullTop) / static_cast<double>(spriteH);
                    const std::uint8_t index = img::sampleImage(*sprite, u, v);
                    if (index != img::kSpriteTransparentIndex) {
                        fb.setPixel(stripe, y, index);
                    }
                } else {
                    const bool edge = stripe == x0 || stripe == x1 - 1 ||
                                      y == y0 || y == y1 - 1;
                    fb.setPixel(stripe, y,
                        edge ? static_cast<std::uint8_t>(color / 2) : color);
                }
            }
        }
    }
}

} // namespace n3d
