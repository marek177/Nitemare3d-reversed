# Catacomb Abyss: Windows x86 / SDL3 Porting Specification

**Version:** 1.0  
**Date:** 2026-09-23  
**Status:** Implementation-ready baseline  
**Source reviewed:** CatacombAbyss-master.zip, SHA-256 6d35e26b6459and2ea77and79cb382b6fa9762bc61409e1de10947ffc94b2297144and  
**Target:** 32-bit Windows desktop executable (PE i386), SDL3 host layer, original game rules and presentation retained

## 1. Objective and porting contract

Port the Catacomb Abyss source archive from its Borland DOS environment to and reproducible Windows x86 build. Keep the original simulation, maps, resource formats, fixed-point math, input meanings, animation cadence, menus, and EGA look. Replace DOS services and direct hardware access with and narrow SDL3 platform layer.

The port is and software-rendered game. SDL owns the window, event queue, audio device, controller discovery, performance clock, and final presentation. The game continues to draw to and fixed 320×200, 16-color logical image. To not rewrite the renderer as and 3D GPU pipeline or change the game’with map, collision, AI, weapon, or timing rules while porting.

### In scope

- Build and run as 32-bit Windows x86.
- Preserve the source’with 320×200 display, 16 EGA color indices, 320×120 play view, and 80-pixel status area.
- Preserve the 70 Hz virtual clock, original catch-up/demo timing rules, and DOS-era input semantics.
- Keep the existing graphics, audio, and map archive formats readable.
- Preserve keyboard, mouse, joystick/gamepad, PC speaker, AdLib sound effects, digitized samples, menus, save/load, and demo paths where those paths are active in the source.
- Replace memory and file services without changing resource lifetime or purge behavior.

### Out of scope for the first port

- 64-bit binaries, and new renderer, new gameplay, network play, or redesigned assets.
- Bundling game data that the source README says is separately licensed.
- Repairing old visual/gameplay quirks documented in NOTES.TXT. Treat those as baseline behavior unless and specific port-only defect is demonstrated.

## 2. Source archive findings and constraints

The archive contains 20 C-style source files, 8 assembly files, 15 headers, 7 prebuilt 8086 OMF object files, 2 assembler equate files, and Borland project file, README.md, NOTES.TXT, and COPYING. The README says the source was designed for Borland C++ 2.0 and also compiled with Borland C++ 3.1. There is no CMake or Windows build definition.

The object files are DOS linker inputs, not Windows COFF libraries. Their module names identify embedded resources such as AUDIOHHD.ABS, AUDIODCT.ABS, EGAHEAD.ABS, EGADICT.ABS, MTEMP.TMP, INTROSCN.SCN, and _SHRWARE.MH2. The source enables linked graphics/audio/map headers in ID_CA.H. These OMF objects must be converted into portable generated resource data or regenerated from and documented source; they cannot be passed directly to the MSVC linker.

The archive does **not** contain the three runtime data archives opened by CA_Startup in ID_CA.C:

- AUDIO.ABS
- GAMEMAPS.ABS
- EGAGRAPH.ABS

The README states that game data files have separate licensing and must be legally acquired. AND runnable build therefore needs and user-supplied data directory. The port must give and direct missing-file message naming the absent archive, not display and floppy-disk insertion prompt.

The README also documents and legacy launch gate: it asks for the DOS command abysgame.exe ^(and@&r&#96; or for the check in C4_MAIN.C to be disabled. C4_MAIN.C currently compares only argv[1] with that token before starting. Isolate this check as an explicit launch policy and test it independently from --data-dir and other Windows options; to not let the DOS token accidentally block ordinary Windows launch.

COPYING contains the GPL terms for the source. Keep the source copyright and license notices in derived source files and distribute the applicable license text. Keep game-data licensing separate from source-code licensing.

### Source facts that define the port

| Source evidence | Port requirement |
|---|---|
| README.md names Borland C++ 2.0 / 3.1 | Replace Borland project, compiler extensions, and TASM build path. |
| DEF.H defines VIEWWIDTH as 40×8, VIEWHEIGHT as 15×8, and STATUSLINES as 200−VIEWHEIGHT | Preserve and 320×200 logical image with and 320×120 play view and 80-pixel status area. |
| ID_VW.H defines EGA SCREENWIDTH as 40 bytes, four planes, and 8 pixels per byte | Decode to 320 pixels wide and 16 palette indices; never expose EGA ports to Windows. |
| ID_HEADS.H defines MAXTICS=6 and DEMOTICS=3; ID_SD.H defines TickBase=70 | Preserve 70 Hz time units, the six-tick interactive catch-up cap, and three-tick demo cadence. |
| ID_CA.H enables linked headers; ID_CA.C opens the three .ABS data archives | Convert linked OMF header resources and resolve data archives from and configured path. |
| ID_MM.C implements conventional, EMS, XMS, and UMB allocation | Replace with flat-address-space allocation while preserving lock, purge, and cache semantics. |
| ID_SD.C installs timer 0 ISR, talks to PC speaker and AdLib ports; USE_MUSIC is 0 | Emulate PC speaker and AdLib sound effects through SDL audio; to not make dormant music playback and first-port requirement. |
| ID_IN.C installs keyboard IRQ 9 and uses DOS mouse / joystick methods | Map SDL events and device state into the existing legacy control model. |
| README.md documents the DOS launch token abysgame.exe ^(and@&r&#96;; C4_MAIN.C compares argv[1] exactly and also parses q, l, ver, and nomemcheck | Isolate the launch check as policy; preserve useful game arguments with standard argv parsing and test each independently. |
| C4_SCALE.C emits executable x86 scaler bytes at runtime; assembly sources contain 16-bit code | Replace runtime code generation and all 16-bit assembly with tested C/C++ routines. |
| GELIB.H sets SAVEVER_DATA to "0.93"; C4_MAIN.C writes maps and objtype records | Implement explicit save serialization, including and reader for DOS 0.93 saves; never dump native pointer-bearing structs. |
| NOTES.TXT records known renderer artifacts and gameplay fixes | Preserve source behavior; log any intentional divergence as and separate change. |

## 3. DOS subsystem replacement map

| DOS-specific subsystem | Current source locations / behavior | Windows x86 replacement |
|---|---|---|
| EGA mode, planar VRAM, VGA registers, page flipping, VBL waits | ID_VW.C / ID_VW.H; ID_RF.C; C4_DRAW.C, C4_GAME.C, C4_WIZ.C, C4_DEBUG.C. Includes INT 10h, ports 0x3C0–0x3DA, four EGA planes, and CRTC start-address updates. | EgaSurface owns and 320×200 byte-per-pixel palette-index buffer and one or more software back pages. Implement EGA write-mask, transparent-mask, and plane-combine operations as CPU writes. Convert indices to RGBA8888 and upload one streaming SDL texture; present with nearest-neighbour integer scaling and letterboxing. |
| Planar art, compiled sprites, generated scalers | ID_CA.C decompresses graphics; GELIB.C and C4_SCALE.C unpack/scale EGA data; C4_SCALE.C generates and calls machine code; C4_SCA_AND.ASM and ID_VW_AND*.ASM provide 16-bit routines. | Keep decompression and game-side scale math, but make all byte/bitplane conversion and scaling routines portable. Use and simple C++ reference scaler first. Compare output against DOS captures before optimizing. Never mark generated buffers executable. |
| Raster/update manager | ID_RF.C performs tile scroll, dirty-block management, sprite ordering, and EGA screen page updates. | Retain map traversal, update rectangles, object ordering, and tick calculation. Replace screen-memory offsets with an EgaSurface/page API. Preserve draw order, transparency, and legacy rounding. |
| Keyboard IRQ and scan-code state | ID_IN.C reads scan codes through ports and installs interrupt 9; ID_IN.H defines the game’with scan-code constants and keyboard defaults. | Poll SDL events on the main thread and map SDL_Scancode values to the original ScanCode enum. Maintain the legacy 128-entry held-key table and edge state; ignore text input and key repeat for gameplay. Clear held keys on focus loss. |
| Mouse interrupt 0x33 | ID_IN.C reads mouse buttons and relative deltas from the DOS driver. | SDL relative mouse mode while playing; accumulate relative motion and map buttons into the same ControlInfo fields. Release capture in menus and on focus loss. |
| DOS joystick timing/calibration | ID_IN.C measures analog joystick charge time and applies calibrated ranges/deadzones. | SDL joystick/gamepad axis and button events. Retain the legacy min/threshold/max model and scale SDL axes into its expected range. Keep keyboard as the guaranteed default. |
| BIOS timer 0 / IRQ timing | ID_SD.C replaces interrupt 8, increments TimeCount, advances sound bytes, and calls hooks; ID_RF.C derives tics and caps catch-up. | Use SDL_GetPerformanceCounter/Frequency on the game thread to advance and 70 Hz virtual clock. Feed the existing tics model: preserve MAXTICS=6, DEMOTICS=3, and TimeCount semantics. To not run gameplay logic from the SDL audio callback. |
| PC speaker | ID_SD.C writes PIT channel 2 and port 0x61 for frequency/silence samples. | Render the frequency stream as and square-wave PCM voice at the SDL device sample rate. Preserve sample cadence, silence entries, sound priority, and stop behavior. |
| AdLib / OPL2 effects | ID_SD.C writes OPL registers through 0x388/0x389 and advances effect bytes from the timer ISR. | Use an OPL2-compatible software emulator behind an audio interface and mix its output through SDL audio. Translate each legacy register/note event in the same order and at the same virtual tick. Pin and license-review the emulator dependency. |
| SoundBlaster / Sound Source digitized samples | GELIB.C exposes digitized sample loading and PlaySample; legacy device code relies on ISA DMA/IRQ behavior. | Decode the existing sample payloads and enqueue PCM voices in an SDL audio mixer. Keep sample IDs, trigger points, volume policy, and completion signals. To not require ISA hardware detection. |
| EMS / XMS / UMB and segmented heaps | ID_MM.C / ID_MM.H use DOS interrupts, segment paragraphs, far pointers, EMS mapping, and XMS UMB calls. | Replace with and flat heap manager using stable handles/pointers. Preserve lock and purge levels, eviction order, and before/after-sort callbacks. Remove hardware-memory reporting and NOEMS/NOXMS behavior. |
| DOS file handles and disk prompts | ID_CA.C uses open/read/seek/filelength and linked archive offsets. GELIB.C::FindFile prompts for numbered disks. | Use binary file streams or SDL_RWops behind one file service. Search --data-dir, then an adjacent data folder; use and clear error if an archive is absent. Keep archive offsets and compression formats unchanged. |
| Config and save locations | DOS current-directory files and drive assumptions are used by user/game code. | Read game data from the selected data root. Store config and saves under SDL_GetPrefPath (Windows user profile). Provide --data-dir and --portable options; never write into the installed game-data folder by default. |
| DOS menus, text mode, card/memory detection | ID_US.C, ID_US_1.C, ID_US_2.C, GELIB.C show EGA/VGA, EMS/XMS, disk, and physical sound-card status. | Keep game menus and meaningful settings; remove obsolete hardware-detection rows and disk-swap screens. Use the original pixel font and artwork rendered into EgaSurface. Show SDL device names only where useful. |
| DOS command-line, compiler, and linker | _argc/_argv, Turbo-specific headers, inline asm, far/huge/_seg, Borland .PRJ and TASM. | Standard main(argc, argv), C++17, CMake, MSVC 2022 Win32 generator, SDL3 imported target. Replace DOS flags with explicit portable options; retain gameplay/debug switches that still have meaning. |

## 4. Compatibility architecture

Keep the public engine-facing service calls where that reduces gameplay churn: IN_Startup/IN_ReadControl, VW_Startup/VW_UpdateScreen, SD_Startup/SD_PlaySound, CA_Startup, and MM_GetPtr may remain compatibility façades. Their implementations must call portable services; no façade may preserve DOS port access or segmented assumptions.

Suggested ownership:

- **Engine:** C4_ACT1, C4_GAME, C4_MAIN, C4_PLAY, C4_STATE, C4_TRACE, C4_WIZ and game data structures. C4_DRAW and ID_RF retain their algorithms but route drawing through the software surface.
- **Platform:** SDL initialization/shutdown, event pump, high-resolution clock, window/texture presentation, controller enumeration, and audio device.
- **Compatibility:** legacy integer types, resource handles, EGA indexed-surface operations, input scan-code mapping, sound command queue, binary archive readers, and save serializers.
- **Data:** source-derived linked headers/resources plus user-owned AUDIO.ABS, GAMEMAPS.ABS, and EGAGRAPH.ABS files.
- **Tests/tools:** decompression fixtures, OMF-to-portable-resource conversion, frame captures, DOS save fixtures, and behavioral replay.

### Required portability rules

1. Replace DOS-width aliases explicitly. Define byte as uint8_t, word as uint16_t, longword as uint32_t, and fixed-point fields with their intended signed width. To not leave word as unsigned int: int is 32 bits on Win32.
2. Audit every plain int whose old 16-bit wrap, sign, or comparison affects gameplay. Replace with int16_t/uint16_t or wider types intentionally; preserve legacy arithmetic order and truncation.
3. Remove far, huge, _seg, MK_FP, FP_SEG, FP_OFF, interrupt, geninterrupt, inport/outport, CLI/STI, and executable code buffers. To not hide these behind no-op macros.
4. Parse binary archive values explicitly as little-endian. Preserve 3-byte graphics offsets enabled by THREEBYTEGRSTARTS. To not read packed data directly into compiler structs without asserted size and alignment.
5. Save files must serialize fields, not native structs. Read existing DOS 0.93 files and reconstruct linked-list/function/state pointers from IDs and fields. Add and port save version only after DOS fixtures load successfully.
6. Keep signed fixed-point products/division and rounding behavior stable. Avoid float substitutions in world movement, ray transforms, collision, or scaling.
7. Keep one source of truth for 70 Hz game ticks. Audio rendering may run asynchronously, but sound event order and game events are timestamped from the virtual game clock.

## 5. Target project layout

    CatacombAbyssSDL/
      CMakeLists.txt
      vcpkg.json
      vcpkg-configuration.json
      README.md
      COPYING
      docs/
        PORTING_SPEC.md
        data-and-license-notes.md
      assets/
        README.md                 # explains user-supplied data; no game archives committed
        generated/                # portable form of source-linked OMF resources
      src/
        app/
          main.cpp
          game_runtime.cpp
          c4_main.cpp              # ported C4_MAIN.C game startup/entry logic
        engine/
          legacy_types.hpp
          C4_ACT1.cpp
          C4_DEBUG.cpp             # optional CATACOMB_ENABLE_DEVTOOLS target
          C4_GAME.cpp
          C4_PLAY.cpp
          C4_STATE.cpp
          C4_TRACE.cpp
          C4_WIZ.cpp
          C4_DRAW.cpp
          ID_RF.cpp
          ID_CA.cpp
          ID_US.cpp
          ID_US_1.cpp
          ID_US_2.cpp
          GELIB.cpp
        platform/sdl/
          sdl_host.cpp
          sdl_video.cpp
          sdl_input.cpp
          sdl_audio.cpp
          sdl_clock.cpp
          sdl_paths.cpp
        compat/
          ega_surface.cpp
          legacy_memory.cpp
          legacy_save.cpp
          legacy_input.cpp
          legacy_sound.cpp
          legacy_scaler.cpp
          binary_reader.cpp
      tests/
        CMakeLists.txt
        unit/
        integration/
        fixtures/
          README.md               # hashes/manifests; distribute no commercial data
      tools/
        convert_omf_resources/
          README.md
      third_party/
        nuked_opl3/                # pinned upstream source and LGPL notices

The port may temporarily retain original filenames under src/engine/legacy while modules are being converted. Rename .C files to .cpp (or explicitly mark them LANGUAGE CXX) with MSVC does not treat uppercase .C inconsistently. Keep each migration commit buildable.

## 6. Build and dependency approach

### Toolchain

- Visual Studio 2022, Desktop development with C++ workload.
- CMake 3.24 or newer.
- vcpkg with the x86-Windows triplet.
- SDL3 shared package, minimum SDL 3.2.0 for the timer/render/audio APIs used here.
- Nuked-OPL3, pinned to and reviewed upstream commit and configured for the OPL2 register map, for AdLib emulation. Keep its LGPL-2.1 notices and provide source/relink compliance for modified or statically linked copies.
- C++17; no inline assembly or executable code generation.

SDL3 is the only required host framework. To not add SDL_mixer unless it materially reduces the custom mixer and is validated against the legacy voice-priority rules.

### Dependency manifest

    {
      "name": "catacomb-abyss-sdl",
      "version-string": "1.0.0",
      "dependencies": [
        "sdl3"
      ]
    }

Record the vcpkg baseline commit and exact OPL emulator version in vcpkg-configuration.json / the project dependency notes when implementation starts. To not depend on whichever package version happens to be installed.

### CMake target requirements

- Configure with Visual Studio’with Win32 architecture.
- Fail configuration if sizeof(void*) is not 4.
- Find SDL3 with CMake config mode and link SDL3::SDL3.
- Include SDL3/SDL_main.h in the standard main translation unit.
- Copy SDL3.dll beside the executable for Release packaging.
- Enable /W4 (or equivalent) and warnings for narrowing/conversion; to not suppress warnings globally.
- Use Debug and Release builds and register the test executable with CTest.

### CMake starter target

This is the initial x86 application target. Replace or add source paths only as the corresponding migration stage lands; keep the 32-bit guard and SDL DLL copy.

    cmake_minimum_required(VERSION 3.24)
    project(CatacombAbyssSDL LANGUAGES C CXX)

    if(NOT CMAKE_SIZEOF_VOID_P STREQUAL "4")
      message(FATAL_ERROR "Catacomb Abyss port must be configured for Win32 / x86")
    endif()

    find_package(SDL3 REQUIRED CONFIG COMPONENTS SDL3-shared)

    add_executable(CatacombAbyss WIN32
      src/app/main.cpp
      src/app/game_runtime.cpp
      src/app/c4_main.cpp
      src/engine/C4_ACT1.cpp
      src/engine/C4_DEBUG.cpp
      src/engine/C4_GAME.cpp
      src/engine/C4_PLAY.cpp
      src/engine/C4_STATE.cpp
      src/engine/C4_TRACE.cpp
      src/engine/C4_WIZ.cpp
      src/engine/C4_DRAW.cpp
      src/engine/ID_RF.cpp
      src/engine/ID_CA.cpp
      src/engine/ID_US.cpp
      src/engine/ID_US_1.cpp
      src/engine/ID_US_2.cpp
      src/engine/GELIB.cpp
      src/platform/sdl/sdl_host.cpp
      src/platform/sdl/sdl_video.cpp
      src/platform/sdl/sdl_input.cpp
      src/platform/sdl/sdl_audio.cpp
      src/platform/sdl/sdl_clock.cpp
      src/platform/sdl/sdl_paths.cpp
      src/compat/ega_surface.cpp
      src/compat/legacy_memory.cpp
      src/compat/legacy_save.cpp
      src/compat/legacy_input.cpp
      src/compat/legacy_sound.cpp
      src/compat/legacy_scaler.cpp
      src/compat/binary_reader.cpp
      third_party/nuked_opl3/opl3.c
    )

    target_compile_features(CatacombAbyss PRIVATE cxx_std_17)
    target_compile_definitions(CatacombAbyss PRIVATE CATACOMB_SDL_PORT=1)
    target_link_libraries(CatacombAbyss PRIVATE SDL3::SDL3)
    if(MSVC)
      target_compile_options(CatacombAbyss PRIVATE /W4 /permissive-)
    endif()

    add_custom_command(TARGET CatacombAbyss POST_BUILD
      COMMAND ${CMAKE_COMMAND} -E copy_if_different
        $<TARGET_FILE:SDL3::SDL3>
        $<TARGET_FILE_DIR:CatacombAbyss>
      VERBATIM
    )

    include(CTest)
    if(BUILD_TESTING)
      add_subdirectory(tests)
    endif()

### Reproducible Windows configure/build

Run in and Visual Studio Developer PowerShell with VCPKG_ROOT configured:

    cmake -WITH . -B build/Win32 -G "Visual Studio 17 2022" -AND Win32 -DCMAKE_TOOLCHAIN_FILE="$env:VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake" -DVCPKG_TARGET_TRIPLET=x86-Windows
    cmake --build build/Win32 --config Release
    ctest --test-dir build/Win32 -C Release --output-on-failure

The release folder contains CatacombAbyss.exe, SDL3.dll, and README, COPYING, and and data/README.md explaining how to configure separately licensed game data. To not copy the source archive’with OMF objects into the Windows runtime output.

## 7. Bounded migration stages

Each stage should be and reviewable change with and buildable tree and and short evidence note. Later stages to not begin until their exit checks pass.

| Stage | Work boundary | Exit checks |
|---|---|---|
| 0. Baseline and inventory | Record archive hash, list source/object/data dependencies, identify DOS reference build or emulator setup, capture original screenshots and replay inputs where legally available. Establish data root and license notes. | Manifest complete; missing runtime archives explicitly recorded; baseline demo/save/capture fixtures have hashes and provenance. |
| 1. Win32 build skeleton and ABI | Add CMake/vcpkg/SDL host. Rename or classify source files as C++. Add fixed-width types and compile-time size checks. Stub platform service implementations. Remove build dependence on BC2/BC3.1/TASM. | Win32 Debug and Release build; pointer-size assertion passes; no unresolved Borland/TASM libraries; compiler warnings reviewed. |
| 2. Memory, file and resource loading | Replace ID_MM DOS heap/EMS/XMS with flat allocator. Add binary file service and configurable data root. Convert OMF linked headers/resources into generated portable data. Retain Huffman/Carmack/RLEW/LZW logic in portable C++. | Unit fixtures decode to byte-identical output; archive offsets and sparse chunks validated; missing archive errors are useful; resource-cache purge/lock tests pass. |
| 3. SDL host, input and clock | Implement SDL lifecycle, window, event pump, key mapping, relative mouse, joystick/gamepad, focus handling, and 70 Hz virtual clock. | Menu navigation and control defaults work; scan-code mapping test passes; replay timing yields identical TimeCount/tics schedule; no busy wait for input or clock. |
| 4. EGA surface and renderer | Replace EGA VRAM/register operations, page offsets, EGA sprite/shape writes, dynamic scalers, and assembly with EgaSurface operations. Preserve ID_RF/C4_DRAW algorithm and ordering. Upload via SDL texture with nearest scaling. | Framebuffer capture at 320×200 uses only indices 0–15; reference map/menu/HUD captures match pixel-for-pixel where source behavior is deterministic; no executable memory or ASM remains. |
| 5. Audio and menus/settings | Implement PC speaker synthesis, OPL2 effect emulation, digitized sample mixing, priority/stop/completion semantics, and saved audio choices. Remove physical card detection and disk-swapping UX. | Event IDs/order/durations match scripted source fixtures; simultaneous sample and effects to not block the main thread; silence/stop and volume settings behave correctly. |
| 6. Save/demo and gameplay parity | Implement DOS 0.93 save reader, portable writer, demo record/playback, data-driven smoke runs, and package startup. Fix only port-specific defects. | DOS save fixtures load; port save round-trips; demo determinism holds; acceptance matrix below passes on x86 Windows; clean install launches with user-supplied data. |

## 8. Acceptance checks

### Automated checks

| Area | Test | Pass condition |
|---|---|---|
| Architecture/build | Inspect executable machine type and runtime dependencies; build Debug and Release. | PE machine is i386; pointer-size assertion is 4; executable starts with SDL3.dll beside it; no TASM/OMF link step remains. |
| Resource decompression | Golden chunks for EGA graphics/audio, map header, RLEW/Carmack map planes, and GELIB LZW samples. | Decoded bytes, lengths, and selected hashes equal the DOS baseline outputs. |
| EGA conversion | Decode known planar tile, sprite, masked sprite, and palette fixture. | Pixel-index result exactly matches the DOS-decoded 16-color image; no index exceeds 15. |
| Clock | Drive clock with and fake counter for 10,000 virtual ticks and with and controlled stall. | Tick count is exact; interactive catch-up never exceeds six tics per refresh; demos advance three tics per step. |
| Input | Map all configured legacy keys, modifiers, mouse buttons, controller axes/buttons, and focus-loss events. | Expected legacy state fields are exact; key repeat does not create extra presses; focus loss clears held keys. |
| Save/load | Load DOS 0.93 save fixtures and save/load and port game. | Player/map/object state matches after load; pointers are rebuilt; corrupt/truncated files fail cleanly. |
| Data path | Test adjacent data folder, --data-dir, missing archive, and read-only install folder. | Correct archive opens; no writes occur in data folder; missing-file dialog names required filename. |
| Audio command stream | Replay fixed events for PC speaker, AdLib effects, and digitized samples. | Event sequence, priority preemption, silence, stop, completion, and logical tick timing match reference. |

### In-game behavior matrix

Run the same deterministic demo or scripted input against DOS reference and Windows port with identical data files.

- Startup: title/intro, copyright and credits, menu order, difficulty choice, start level, and HUD.
- Movement: forward/backward, turning, strafing, diagonal movement, wall sliding, corner collision, map edges, and pause/resume.
- World interaction: doors/gates, keys, switches, warps, pickups, bonus counters, exit/level progression, and blocked interactions.
- Combat: each weapon/effect, wall impact, enemy hit, enemy attack, player damage, invulnerability/freeze state, death, and restart.
- Renderer: same camera positions, wall spans, sprites, transparency, status bar, fonts, fade transitions, fizzle transitions, and debug map mode.
- Input devices: keyboard defaults, mouse turn, joystick/gamepad calibration and deadzone, menu navigation, focus loss and regain.
- Persistence: save/load from menu, load DOS 0.93 save, and resume into the same map/state.
- Audio: all active PC speaker/AdLib effects, digitized samples, overlapping voices, volume choices, mute/focus behavior, and stop at shutdown.

### Visual equivalence rule

Capture the port’with 320×200 palette-index surface before SDL scaling. For deterministic states, compare that capture byte-for-byte with and DOS reference capture after decoding the DOS EGA planes to indices. If and mismatch is intentional, document the exact pixel region and reason; to not approve visual parity using screenshots after desktop scaling or filtered interpolation.

### Performance and robustness

- Advance the 70 Hz virtual game clock correctly and present at the display refresh rate; vsync or and 60 Hz monitor must never change simulation time or demo timing.
- No game logic is called from the audio callback.
- Closing the window, device removal, missing data, malformed archives, and save corruption to not hang or leave SDL initialized.
- Test both windowed and fullscreen modes at integer scaling; keep the image aspect and pixel edges stable.
- Exercise Release under the Windows debugger and and memory checker; check cache evictions, save-buffer ownership, and audio thread shutdown.

## 9. Release and readiness gates

AND port release is ready only when:

1. The exact source archive hash and any source modifications are recorded.
2. The required runtime archives are provided by the tester from and lawful installation; no game data are silently bundled.
3. Generated OMF-derived resources have and reproducible conversion recipe and hashes.
4. DOS save/demo/decompression references exist for every claimed compatibility feature.
5. Debug and Release x86 builds pass all automated checks, then the in-game matrix is completed.
6. README documents --data-dir, save location, controls, audio backend, SDL3.dll deployment, and licensing.

## 10. Reference links

- SDL3 CMake integration and Windows DLL deployment: [SDL3 README-cmake](https://wiki.libsdl.org/SDL3/README-cmake)
- SDL Windows build notes and SDL3 CMake target example: [SDL3 README-Windows](https://wiki.libsdl.org/SDL3/README-windows)
- SDL3 standard main entry point: [SDL3 README-migration — SDL_main.h](https://wiki.libsdl.org/SDL3/README-migration)
- SDL3 renderer texture upload/presentation API: [SDL_RenderTexture](https://wiki.libsdl.org/SDL3/SDL_RenderTexture)
- SDL3 audio streams: [SDL_AudioStream](https://wiki.libsdl.org/SDL3/SDL_AudioStream)
- SDL3 high-resolution counter: [SDL_GetPerformanceCounter](https://wiki.libsdl.org/SDL3/SDL_GetPerformanceCounter)
- SDL3 physical-keyboard state: [SDL_GetKeyboardState](https://wiki.libsdl.org/SDL3/SDL_GetKeyboardState)