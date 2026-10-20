cmake_minimum_required(VERSION 3.24)
project(Nitemare3D_Reconstructed VERSION 0.77.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(N3D_ENABLE_SDL3 "Build the SDL3 runtime/viewer" ON)
option(N3D_FETCH_SDL3 "Fetch SDL3 automatically when not installed" OFF)

add_library(n3d_core
    src/formats/BinaryIO.cpp
    src/formats/DatArchive.cpp
    src/formats/DefinitionTable.cpp
    src/formats/DemoFile.cpp
    src/formats/FliFile.cpp
    src/formats/ImgArchive.cpp
    src/formats/MapArchive.cpp
    src/formats/Pcx8.cpp
    src/app/GameData.cpp
    src/game/LevelState.cpp
    src/game/CheatSystem.cpp
    src/game/HazardSystem.hpp
    src/ui/MenuModel.cpp
    src/ui/InstructionsData.cpp
    src/renderer/Framebuffer.cpp
    src/renderer/Raycaster.cpp
    src/re/DosV12AnimationRuntime.cpp
    src/re/n3d_v018_facts.c
    src/re/N3DV018Evidence.cpp
    src/re/N3DV019RuntimePrimitives.cpp
    src/re/N3DV020VerificationHarness.cpp
    src/re/N3DV021SubsystemEvidence.cpp
)

target_include_directories(n3d_core PUBLIC src)
target_compile_features(n3d_core PUBLIC cxx_std_20)

if(MSVC)
    target_compile_options(n3d_core PRIVATE /W4 /permissive-)
else()
    target_compile_options(n3d_core PRIVATE -Wall -Wextra -Wpedantic)
endif()

add_executable(n3d_inspect tools/n3d_inspect.cpp)
target_link_libraries(n3d_inspect PRIVATE n3d_core)

add_executable(n3d_pushable_test tests/pushable_test.cpp)
target_link_libraries(n3d_pushable_test PRIVATE n3d_core)

# Synthetic fixture, no original episode data required.
add_executable(n3d_pushable_blocked_test tests/pushable_blocked_test.cpp)
target_link_libraries(n3d_pushable_blocked_test PRIVATE n3d_core)

add_executable(n3d_menu_cheat_test tests/menu_cheat_test.cpp)
target_link_libraries(n3d_menu_cheat_test PRIVATE n3d_core)

add_executable(n3d_hazard_test tests/hazard_test.cpp)
target_link_libraries(n3d_hazard_test PRIVATE n3d_core)

add_executable(n3d_episode3_level_data_test tests/episode3_level_data_test.cpp)
target_link_libraries(n3d_episode3_level_data_test PRIVATE n3d_core)

add_executable(n3d_renderer_facts_test tests/renderer_facts_test.cpp)
target_link_libraries(n3d_renderer_facts_test PRIVATE n3d_core)

add_executable(n3d_win16_wall_raster_core_test tests/win16_wall_raster_core_test.cpp)
target_link_libraries(n3d_win16_wall_raster_core_test PRIVATE n3d_core)

add_executable(n3d_guard_facts_test tests/guard_facts_test.cpp)
target_link_libraries(n3d_guard_facts_test PRIVATE n3d_core)

add_executable(n3d_guard_save_block_test tests/guard_save_block_test.cpp)
target_link_libraries(n3d_guard_save_block_test PRIVATE n3d_core)

add_executable(n3d_object_runtime_facts_test tests/object_runtime_facts_test.cpp)
target_link_libraries(n3d_object_runtime_facts_test PRIVATE n3d_core)

add_executable(n3d_unknown_systems_audit_test tests/unknown_systems_audit_test.cpp)
target_link_libraries(n3d_unknown_systems_audit_test PRIVATE n3d_core)

add_executable(n3d_recovered_runtime_facts_test tests/recovered_runtime_facts_test.cpp)
target_link_libraries(n3d_recovered_runtime_facts_test PRIVATE n3d_core)

add_executable(n3d_projectile_runtime_test tests/projectile_runtime_test.cpp)
target_link_libraries(n3d_projectile_runtime_test PRIVATE n3d_core)

add_executable(n3d_runtime_layout_test tests/runtime_layout_test.cpp)
target_link_libraries(n3d_runtime_layout_test PRIVATE n3d_core)

add_executable(n3d_img_archive_layout_test tests/img_archive_layout_test.cpp)
target_link_libraries(n3d_img_archive_layout_test PRIVATE n3d_core)

add_executable(n3d_demo_file_test tests/demo_file_test.cpp)
target_link_libraries(n3d_demo_file_test PRIVATE n3d_core)

add_executable(n3d_win16_mfc_memory_test tests/win16_mfc_memory_test.cpp)
target_link_libraries(n3d_win16_mfc_memory_test PRIVATE n3d_core)

add_executable(n3d_win16_mfc_addresses_test tests/win16_mfc_addresses_test.cpp)
target_link_libraries(n3d_win16_mfc_addresses_test PRIVATE n3d_core)

add_executable(n3d_win16_mfc_coverage_test tests/win16_mfc_coverage_test.cpp)
target_link_libraries(n3d_win16_mfc_coverage_test PRIVATE n3d_core)

add_executable(n3d_handle_registry_test tests/handle_registry_test.cpp)
target_link_libraries(n3d_handle_registry_test PRIVATE n3d_core)

add_executable(n3d_native_handle_wrapper_test tests/native_handle_wrapper_test.cpp)
target_link_libraries(n3d_native_handle_wrapper_test PRIVATE n3d_core)

add_executable(n3d_window_wrapper_test tests/window_wrapper_test.cpp)
target_link_libraries(n3d_window_wrapper_test PRIVATE n3d_core)

add_executable(n3d_window_registry_test tests/window_registry_test.cpp)
target_link_libraries(n3d_window_registry_test PRIVATE n3d_core)

add_executable(n3d_runtime_safety_test tests/runtime_safety_test.cpp)
target_link_libraries(n3d_runtime_safety_test PRIVATE n3d_core)

add_executable(n3d_player_reconstruction_test tests/player_reconstruction_test.cpp)
target_link_libraries(n3d_player_reconstruction_test PRIVATE n3d_core)

add_executable(n3d_projectile_save_block_test tests/projectile_save_block_test.cpp)
target_link_libraries(n3d_projectile_save_block_test PRIVATE n3d_core)

add_executable(n3d_win16_recovered_facts_20260925_test tests/win16_recovered_facts_2026_09_25_test.cpp)
target_link_libraries(n3d_win16_recovered_facts_20260925_test PRIVATE n3d_core)

add_executable(n3d_v013_recovered_facts_test tests/v013_recovered_facts_test.cpp)
target_link_libraries(n3d_v013_recovered_facts_test PRIVATE n3d_core)

add_executable(n3d_v014_analysis_test tests/v014_analysis_test.cpp)
target_link_libraries(n3d_v014_analysis_test PRIVATE n3d_core)

add_executable(n3d_v015_sprite_facts_test tests/v015_sprite_facts_test.cpp)
target_link_libraries(n3d_v015_sprite_facts_test PRIVATE n3d_core)

add_executable(n3d_v016_coverage_test tests/v016_coverage_test.cpp)
target_link_libraries(n3d_v016_coverage_test PRIVATE n3d_core)

add_executable(n3d_v017_runtime_integration_test tests/v017_runtime_integration_test.cpp)
target_link_libraries(n3d_v017_runtime_integration_test PRIVATE n3d_core)

add_executable(n3d_dos_v12_animation_runtime_test tests/dos_v12_animation_runtime_test.cpp)
target_link_libraries(n3d_dos_v12_animation_runtime_test PRIVATE n3d_core)

add_executable(n3d_v018_evidence_test tests/v018_evidence_test.cpp)
target_link_libraries(n3d_v018_evidence_test PRIVATE n3d_core)

add_executable(n3d_v019_runtime_primitives_test tests/v019_runtime_primitives_test.cpp)
target_link_libraries(n3d_v019_runtime_primitives_test PRIVATE n3d_core)

add_executable(n3d_v020_verification_harness_test tests/v020_verification_harness_test.cpp)
target_link_libraries(n3d_v020_verification_harness_test PRIVATE n3d_core)

add_executable(n3d_v021_subsystem_evidence_test tests/v021_subsystem_evidence_test.cpp)
target_link_libraries(n3d_v021_subsystem_evidence_test PRIVATE n3d_core)

add_executable(n3d_v022_version_evidence_registry_test tests/v022_version_evidence_registry_test.cpp)
target_link_libraries(n3d_v022_version_evidence_registry_test PRIVATE n3d_core)

add_executable(n3d_v023_cross_build_symbol_map_test tests/v023_cross_build_symbol_map_test.cpp)
target_link_libraries(n3d_v023_cross_build_symbol_map_test PRIVATE n3d_core)

add_executable(n3d_v024_guard_state_graph_test tests/v024_guard_state_graph_test.cpp)
target_link_libraries(n3d_v024_guard_state_graph_test PRIVATE n3d_core)

add_executable(n3d_v025_guard_writer_graph_test tests/v025_guard_writer_graph_test.cpp)
target_link_libraries(n3d_v025_guard_writer_graph_test PRIVATE n3d_core)

add_executable(n3d_v026_guard_rng_coupling_test tests/v026_guard_rng_coupling_test.cpp)
target_link_libraries(n3d_v026_guard_rng_coupling_test PRIVATE n3d_core)

add_executable(n3d_v027_projectile_lifecycle_test tests/v027_projectile_lifecycle_test.cpp)
target_link_libraries(n3d_v027_projectile_lifecycle_test PRIVATE n3d_core)

add_executable(n3d_v029_scheduler_evidence_test tests/v029_scheduler_evidence_test.cpp)
target_link_libraries(n3d_v029_scheduler_evidence_test PRIVATE n3d_core)

add_executable(n3d_v030_trace_closure_test tests/v030_trace_closure_test.cpp)
target_link_libraries(n3d_v030_trace_closure_test PRIVATE n3d_core)

add_executable(n3d_v032_static_closure_test tests/v032_static_closure_test.cpp)
target_link_libraries(n3d_v032_static_closure_test PRIVATE n3d_core)

add_executable(n3d_v033_push_scheduler_test tests/v033_push_scheduler_test.cpp)
target_link_libraries(n3d_v033_push_scheduler_test PRIVATE n3d_core)

add_executable(n3d_v034_object_animation_evidence_test tests/v034_object_animation_evidence_test.cpp)
target_link_libraries(n3d_v034_object_animation_evidence_test PRIVATE n3d_core)

add_executable(n3d_v035_rng_census_test tests/v035_rng_census_test.cpp)
target_link_libraries(n3d_v035_rng_census_test PRIVATE n3d_core)

add_executable(n3d_v036_protected_hit_ordering_test tests/v036_protected_hit_ordering_test.cpp)
target_link_libraries(n3d_v036_protected_hit_ordering_test PRIVATE n3d_core)

add_executable(n3d_v037_scheduler_catchup_test tests/v037_scheduler_catchup_test.cpp)
target_link_libraries(n3d_v037_scheduler_catchup_test PRIVATE n3d_core)

add_executable(n3d_v038_three_day_findings_test tests/v038_three_day_findings_test.cpp)
target_link_libraries(n3d_v038_three_day_findings_test PRIVATE n3d_core)

add_executable(n3d_v039_late_static_closures_test tests/v039_late_static_closures_test.cpp)
target_link_libraries(n3d_v039_late_static_closures_test PRIVATE n3d_core)

add_executable(n3d_v040_projectile_reentry_closure_test tests/v040_projectile_reentry_closure_test.cpp)
target_link_libraries(n3d_v040_projectile_reentry_closure_test PRIVATE n3d_core)

add_executable(n3d_v041_latest_static_evidence_test tests/v041_latest_static_evidence_test.cpp)
target_link_libraries(n3d_v041_latest_static_evidence_test PRIVATE n3d_core)

add_executable(n3d_v041_frame_compositor_test tests/v041_frame_compositor_test.cpp)
target_link_libraries(n3d_v041_frame_compositor_test PRIVATE n3d_core)

add_executable(n3d_v042_oct18_closures_test tests/v042_oct18_closures_test.cpp)
target_link_libraries(n3d_v042_oct18_closures_test PRIVATE n3d_core)

add_executable(n3d_dos20_sprite_raster_test tests/dos20_sprite_raster_test.cpp)
target_link_libraries(n3d_dos20_sprite_raster_test PRIVATE n3d_core)

add_executable(n3d_e1m9_radio_lifecycle_test tests/e1m9_radio_lifecycle_test.cpp)
target_link_libraries(n3d_e1m9_radio_lifecycle_test PRIVATE n3d_core)

add_executable(n3d_v043_runtime_closure_test tests/v043_runtime_closure_test.cpp)
target_link_libraries(n3d_v043_runtime_closure_test PRIVATE n3d_core)

add_executable(n3d_v044_weapon_fire_closure_test tests/v044_weapon_fire_closure_test.cpp)
target_link_libraries(n3d_v044_weapon_fire_closure_test PRIVATE n3d_core)

add_executable(n3d_v045_weapon_switch_frame_order_test tests/v045_weapon_switch_frame_order_test.cpp)
target_link_libraries(n3d_v045_weapon_switch_frame_order_test PRIVATE n3d_core)

add_executable(n3d_v046_runtime_acceptance_test tests/v046_runtime_acceptance_test.cpp)
target_link_libraries(n3d_v046_runtime_acceptance_test PRIVATE n3d_core)

add_executable(n3d_v047_worx_dma_runtime_test tests/v047_worx_dma_runtime_test.cpp)
target_link_libraries(n3d_v047_worx_dma_runtime_test PRIVATE n3d_core)

add_executable(n3d_v048_demo_bootstrap_test tests/v048_demo_bootstrap_test.cpp)
target_link_libraries(n3d_v048_demo_bootstrap_test PRIVATE n3d_core)

add_executable(n3d_v049_oct19_evidence_test tests/v049_oct19_evidence_test.cpp)
target_link_libraries(n3d_v049_oct19_evidence_test PRIVATE n3d_core)

add_executable(n3d_v050_guard41_death_test tests/v050_guard41_death_test.cpp)
target_link_libraries(n3d_v050_guard41_death_test PRIVATE n3d_core)

add_executable(n3d_v051_win16_wing_runtime_test tests/v051_win16_wing_runtime_test.cpp)
target_link_libraries(n3d_v051_win16_wing_runtime_test PRIVATE n3d_core)

add_executable(n3d_v052_dos20_rng_timer_test tests/v052_dos20_rng_timer_test.cpp)
target_link_libraries(n3d_v052_dos20_rng_timer_test PRIVATE n3d_core)

add_executable(n3d_v053_hud_weapon_crossbuild_test tests/v053_hud_weapon_crossbuild_test.cpp)
target_link_libraries(n3d_v053_hud_weapon_crossbuild_test PRIVATE n3d_core)

add_executable(n3d_v054_crossbuild_map_palette_test tests/v054_crossbuild_map_palette_test.cpp)
target_link_libraries(n3d_v054_crossbuild_map_palette_test PRIVATE n3d_core)

add_executable(n3d_v055_demo_seed_eof_test tests/v055_demo_seed_eof_test.cpp)
target_link_libraries(n3d_v055_demo_seed_eof_test PRIVATE n3d_core)

add_executable(n3d_v056_frontier_status_test tests/v056_frontier_status_test.cpp)
target_link_libraries(n3d_v056_frontier_status_test PRIVATE n3d_core)

add_executable(n3d_v057_demo_rng_chain_test tests/v057_demo_rng_chain_test.cpp)
target_link_libraries(n3d_v057_demo_rng_chain_test PRIVATE n3d_core)

add_executable(n3d_v058_guard_state09_test tests/v058_guard_state09_test.cpp)
target_link_libraries(n3d_v058_guard_state09_test PRIVATE n3d_core)

add_executable(n3d_v059_win16_save_load_test tests/v059_win16_save_load_test.cpp)
target_link_libraries(n3d_v059_win16_save_load_test PRIVATE n3d_core)

add_executable(n3d_v062_dos20_palette_fade_test tests/v062_dos20_palette_fade_test.cpp)
target_link_libraries(n3d_v062_dos20_palette_fade_test PRIVATE n3d_core)

# Win16 static branch model: synthetic tests only, no original binaries needed.
add_executable(n3d_win16_clock_presentation_contract_test
    tests/win16_clock_presentation_contract_test.cpp)
target_link_libraries(n3d_win16_clock_presentation_contract_test PRIVATE n3d_core)

# Preview renderer regressions; these do not establish original pixel parity.
foreach(preview_test img_texture_sampler wall_marker_visibility wall_pair_texture game_palette)
  add_executable(n3d_${preview_test}_test tests/${preview_test}_test.cpp)
  target_link_libraries(n3d_${preview_test}_test PRIVATE n3d_core)
endforeach()

# DOS v2.0 FEFA owner comparison and CAB8 near-plane cull (bounded research).
# This test does not alter the active diagnostic DDA renderer.
add_executable(n3d_dos20_visibility_opcode_contract_test
    tests/dos20_visibility_opcode_contract_test.cpp)
target_link_libraries(n3d_dos20_visibility_opcode_contract_test PRIVATE n3d_core)

# Bounded original Win16 lifecycle branch contract (synthetic, no old EXEs).
add_executable(n3d_win16_timer_lifecycle_gate_test
    tests/win16_timer_lifecycle_gate_test.cpp)
target_link_libraries(n3d_win16_timer_lifecycle_gate_test PRIVATE n3d_core)

# DOS2 fixed-point wall-column raster. This intentionally does not replace
# the production DDA preview; source/projected column inputs are caller-supplied.
add_executable(n3d_dos20_indexed_wall_column_test
    tests/dos20_indexed_wall_column_test.cpp)
target_link_libraries(n3d_dos20_indexed_wall_column_test PRIVATE n3d_core)

# Experimental DOS2 post-span -> 304 indexed wall-column pipeline.
# No DDA replacement; source IMG/U/shading is passed in explicitly.
add_executable(n3d_dos20_span_wall_pipeline_test
    tests/dos20_span_wall_pipeline_test.cpp)
target_link_libraries(n3d_dos20_span_wall_pipeline_test PRIVATE n3d_core)

# DOS2 static 0x16CE RGB6 shade remap, strict 256-color first-minimum.
add_executable(n3d_dos20_shade_xlat_test
    tests/dos20_shade_xlat_test.cpp)
target_link_libraries(n3d_dos20_shade_xlat_test PRIVATE n3d_core)

# DOS2 IMG sequence/cache/frame + Win16 EBD6-derived perspective-U candidate
# with exact DOS2 RGB6/XLAT as a fail-closed 304-column material resolver.
add_executable(n3d_dos20_wall_material_binding_test
    tests/dos20_wall_material_binding_test.cpp)
target_link_libraries(n3d_dos20_wall_material_binding_test PRIVATE n3d_core)

add_executable(n3d_dos20_shade_remap_test tests/dos20_shade_remap_test.cpp)
target_link_libraries(n3d_dos20_shade_remap_test PRIVATE n3d_core)

include(cmake/RegressionTests.cmake)

if(N3D_ENABLE_SDL3)
    find_package(SDL3 CONFIG QUIET)

    if(NOT SDL3_FOUND AND N3D_FETCH_SDL3)
        include(FetchContent)
        FetchContent_Declare(
            SDL3
            GIT_REPOSITORY https://github.com/libsdl-org/SDL.git
            GIT_TAG release-3.2.22
            GIT_SHALLOW TRUE
        )
        FetchContent_MakeAvailable(SDL3)
    endif()

    if(TARGET SDL3::SDL3)
        add_executable(nitemare3d
            src/main.cpp
            src/platform/sdl/SDLVideo.cpp
        )
        target_link_libraries(nitemare3d PRIVATE n3d_core SDL3::SDL3)
        target_compile_definitions(nitemare3d PRIVATE N3D_USE_SDL3=1)
    else()
        message(WARNING "SDL3 was not found. n3d_inspect will still be built. Install SDL3 or set N3D_FETCH_SDL3=ON to build nitemare3d.")
    endif()
endif()
