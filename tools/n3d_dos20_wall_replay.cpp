// Runnable DOS2 snapshot -> material binder -> fixed-point wall pipeline.
// Input geometry is borrowed from the checkpoint, not regenerated from MAP.
#include "formats/BinaryIO.hpp"
#include "re/N3DDos20WallMaterialBinding.hpp"

#include <array>
#include <charconv>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace fs = std::filesystem;
namespace sw = n3d::re::dos20::spanwall;
namespace wm = n3d::re::dos20::wallmaterial;
namespace shade = n3d::re::dos20::shade;

struct Options {
    fs::path ds, img, background, reference, output;
    unsigned vecCount{}, page{};
};
static unsigned number(std::string_view text) {
    unsigned value{};
    const auto [end, error] = std::from_chars(text.data(), text.data()+text.size(), value);
    if (error != std::errc{} || end != text.data()+text.size())
        throw std::runtime_error("Expected an unsigned decimal integer");
    return value;
}
static Options options(int argc, char** argv) {
    Options out{};
    for (int i=1; i<argc; ++i) {
        const std::string_view arg = argv[i];
        if (i+1>=argc) throw std::runtime_error("Missing option value");
        const std::string_view value = argv[++i];
        if (arg=="--ds") out.ds=value;
        else if (arg=="--img") out.img=value;
        else if (arg=="--background-frame") out.background=value;
        else if (arg=="--reference-frame") out.reference=value;
        else if (arg=="--output-dir") out.output=value;
        else if (arg=="--vec-count") out.vecCount=number(value);
        else if (arg=="--page") out.page=number(value);
        else throw std::runtime_error("Unknown option: "+std::string(arg));
    }
    if (out.ds.empty() || out.img.empty() || out.background.empty() || out.output.empty() ||
        out.vecCount==0 || out.vecCount>sw::kMaxVecs || out.page>1)
        throw std::runtime_error("Require --ds, --img, --background-frame, --vec-count 1..1000, --output-dir; --page 0|1 is optional");
    if (fs::exists(out.output)) throw std::runtime_error("Output directory must not already exist");
    return out;
}
static void writeBytes(const fs::path& path, std::span<const std::uint8_t> bytes) {
    std::ofstream out(path, std::ios::binary);
    out.write(reinterpret_cast<const char*>(bytes.data()), static_cast<std::streamsize>(bytes.size()));
    out.close();
    if (!out) throw std::runtime_error("Unable to write replay output");
}
static void writeText(const fs::path& path, const std::string& text) {
    std::ofstream out(path, std::ios::binary);
    out << text;
    out.close();
    if (!out) throw std::runtime_error("Unable to write replay metadata");
}
struct Binding {
    unsigned physicalU{}, width{}, frameIndex{}, shadeIndex{};
    std::uint32_t frameOffset{};
    bool clamped{};
};

int main(int argc, char** argv) {
    if (argc==2 && std::string_view(argv[1])=="--help") {
        std::cout << "n3d_dos20_wall_replay --ds DS.bin --img IMG.1 --vec-count N "
                     "--background-frame background.idx --output-dir NEW_DIR "
                     "[--reference-frame original.idx] [--page 0|1]\n"
                     "Research wall-only replay: copied checkpoint geometry/background; "
                     "no full-scene or authenticated original-versus-port verdict.\n";
        return 0;
    }
    try {
        const auto opts=options(argc, argv);
        const auto ds=n3d::io::readFile(opts.ds);
        const auto img=n3d::io::readFile(opts.img);
        auto frame=n3d::io::readFile(opts.background);
        if (ds.size()!=sw::kSegmentBytes || frame.size()!=64000)
            throw std::runtime_error("Require exactly 65536 DS bytes and 64000 background indices");
        const auto reference=opts.reference.empty() ? std::vector<std::uint8_t>{}
                                                    : n3d::io::readFile(opts.reference);
        if (!opts.reference.empty() && reference.size()!=64000)
            throw std::runtime_error("Reference frame must contain exactly 64000 indices");
        shade::Prepared active{}, zero{};
        if (!shade::prepareFromDosSegment(ds, active) ||
            !shade::prepare(active.baseRgb6, 0, zero))
            throw std::runtime_error("Invalid checkpoint base RGB6 palette or shade selector");
        wm::ImgWallCatalog catalog{};
        if (!catalog.build(img, ds, opts.vecCount))
            throw std::runtime_error("IMG cache/frame catalog does not match checkpoint VEC selectors");
        wm::MaterialBinder binder{};
        binder.ds=ds; binder.catalog=&catalog;
        binder.shading=&active; binder.shadingZero=&zero;
        // No Win16 trig, guessed camera/FOV, or fallback material.
        std::array<Binding, sw::kColumns> bindings{};
        auto resolve=[&](unsigned x, std::uint16_t owner, std::uint8_t wall,
                         const sw::Span& span, int bottom, unsigned height,
                         std::uint16_t yq4) -> std::optional<sw::Material> {
            const auto material=binder(x,owner,wall,span,bottom,height,yq4);
            if (!material) return std::nullopt;
            const auto vec=wm::vecFromDosDS(ds,owner);
            const auto selected=catalog.select(vec);
            if (!selected) return std::nullopt;
            bindings[x-sw::kLeft]={material->physicalU, material->imageWidth,
                selected->selectedFrameIndex,
                wm::useZeroShadeForWall(ds,vec,active.shadeIndex) ? 0u : active.shadeIndex,
                selected->frame.fileOffset, selected->clampedAnimationFrame};
            return material;
        };
        sw::Plan plan{};
        const auto status=sw::prepare(ds,opts.vecCount,opts.page,resolve,plan);
        if (status!=sw::Status::Ok)
            throw std::runtime_error("Wall plan rejected; status="+std::to_string(static_cast<unsigned>(status)));
        if (sw::render(plan,frame,{})!=sw::Status::Ok)
            throw std::runtime_error("Prepared wall raster rejected");
        std::vector<std::uint8_t> mask(64000);
        std::array<std::uint8_t,sw::kColumns> u{}, valid{};
        unsigned generated=0, mismatches=0, clamped=0;
        std::optional<unsigned> firstMismatch{};
        std::ostringstream columns;
        columns << "screen_x,draw,span_index,owner,wall_id,span_y_q4,physical_u,image_width,frame_index,frame_offset,shade_index,clamped_animation,first_y,pixel_count\n";
        for (unsigned j=0; j<sw::kColumns; ++j) {
            const auto& c=plan.columns[j];
            const auto& b=bindings[j];
            columns << j+sw::kLeft << ',' << c.draw << ',' << c.spanIndex << ','
                    << c.nearOwner << ',' << unsigned(c.wallId) << ',' << c.spanYQ4 << ',';
            if (c.draw) {
                u[j]=static_cast<std::uint8_t>(b.physicalU); valid[j]=1;
                clamped+=b.clamped ? 1u : 0u;
                columns << b.physicalU << ',' << b.width << ',' << b.frameIndex << ','
                        << b.frameOffset << ',' << b.shadeIndex << ',' << b.clamped << ','
                        << c.drawArgs.firstY << ',' << c.drawArgs.pixelCount;
                for (unsigned y=c.drawArgs.firstY; y<c.drawArgs.firstY+c.drawArgs.pixelCount; ++y) {
                    const unsigned at=y*320+c.drawArgs.x;
                    mask[at]=1; ++generated;
                    if (!reference.empty() && frame[at]!=reference[at]) {
                        ++mismatches;
                        if (!firstMismatch) firstMismatch=at;
                    }
                }
            } else {
                columns << ",,,,,,,"; // No invented material/U for culled columns.
            }
            columns << '\n';
        }
        const bool compared=!reference.empty() && generated>0;
        std::ostringstream report;
        report << "{\n  \"scope\": \"supplied_post_span_snapshot_wall_replay\",\n"
               << "  \"geometry_from_checkpoint\": true,\n"
               << "  \"background_from_caller\": true,\n"
               << "  \"base_palette_from_ds_4a64\": true,\n"
               << "  \"full_frame_parity_proven\": false,\n"
               << "  \"original_recording_authenticated\": false,\n"
               << "  \"input_state_synchronization_verified\": false,\n"
               << "  \"active_vec_count\": " << opts.vecCount << ",\n"
               << "  \"span_count\": " << plan.spanCount << ",\n"
               << "  \"drawn_columns\": " << plan.drawnColumns << ",\n"
               << "  \"culled_columns\": " << plan.culledColumns << ",\n"
               << "  \"clamped_animation_columns\": " << clamped << ",\n"
               << "  \"generated_wall_pixels\": " << generated << ",\n"
               << "  \"wall_pixels_compared\": " << (compared ? generated : 0) << ",\n"
               << "  \"wall_pixel_mismatches\": ";
        if (compared) report << mismatches; else report << "null";
        report << ",\n  \"first_wall_mismatch_pixel\": ";
        if (firstMismatch) report << *firstMismatch; else report << "null";
        report << ",\n  \"wall_pixels_equal\": ";
        if (compared) report << (mismatches==0 ? "true" : "false"); else report << "null";
        report << "\n}\n";
        // Validate every input/plan before creating output; never replace files.
        if (!fs::create_directory(opts.output)) throw std::runtime_error("Cannot create new output directory");
        try {
            writeBytes(opts.output/"candidate.idx",frame);
            writeBytes(opts.output/"generated.mask",mask);
            writeBytes(opts.output/"candidate.u",u);
            writeBytes(opts.output/"candidate.u-valid",valid);
            writeText(opts.output/"columns.csv",columns.str());
            writeText(opts.output/"report.json",report.str());
        } catch (...) {
            std::error_code ignored;
            fs::remove_all(opts.output, ignored); // Only the directory just created by this invocation.
            throw;
        }
        std::cout << report.str();
        return compared && mismatches ? 1 : 0;
    } catch (const std::exception& error) {
        std::cerr << "INCOMPARABLE: " << error.what() << '\n';
        return 2;
    }
}
