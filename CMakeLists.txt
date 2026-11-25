cmake_minimum_required(VERSION 3.22)
project(TLA)

# ---------------------------------------------------------------------------
# Pre-Stage bootstrap.
# ---------------------------------------------------------------------------

include(Engine/BuildTools/Init.cmake)

# ---------------------------------------------------------------------------
# Engine-level options. Defaults overridable via cache; SetOptionValues only
# sets when the variable is undefined, so a -D flag on the cmake command line
# wins.
# ---------------------------------------------------------------------------

SetOptionValues(
    FO_MAIN_CONFIG TLA.fomain
    FO_DEV_NAME TLA
    FO_NICE_NAME FOnlineTLA
    FO_ENABLE_3D OFF
    FO_DATA_SOURCE_DAT ON
    FO_DATA_SOURCE_ZIP ON
    FO_IMAGE_FRM ON
    FO_IMAGE_RIX ON
    FO_AUDIO_ACM ON
    FO_ANGELSCRIPT_SCRIPTING ON
    FO_NATIVE_SCRIPTING OFF
    FO_MANAGED_SCRIPTING OFF
    FO_GEOMETRY HEXAGONAL
    FO_MAP_HEX_WIDTH 32
    FO_MAP_HEX_HEIGHT 16
    FO_MAP_CAMERA_ANGLE 25.6589
    FO_APP_ICON Resources/TLA.ico
    FO_BUILD_CLIENT ON
    FO_BUILD_SERVER ON
    FO_BUILD_MAPPER ON
    FO_BUILD_ASCOMPILER ON
    FO_BUILD_BAKER ON
    FO_UNIT_TESTS ON
    FO_OUTPUT_PATH ${CMAKE_CURRENT_SOURCE_DIR})

# The Engine AiControl listener (Game.AiControl* script API) is a development tool. Every package
# defined below is a development or test package, so it stays on by default; a release or store
# build must configure with -DTLA_AI_CONTROL=OFF so the binary carries no listening-socket code.
option(TLA_AI_CONTROL "Compile the AiControl listener into development clients" ON)
SetOption(FO_AI_CONTROL ${TLA_AI_CONTROL})

# ---------------------------------------------------------------------------
# Stage 1: Init — options, platform detection, compiler/link flags.
# ---------------------------------------------------------------------------

StartProjectGeneration()

# ---------------------------------------------------------------------------
# Stage 2: ProjectOptions — engine-side option validation.
# ---------------------------------------------------------------------------

RegisterProjectOptions()

# ---------------------------------------------------------------------------
# Stage 3: ThirdParty — bundled engine libs plus project-local extras.
# ---------------------------------------------------------------------------

AddThirdPartyLibraries()

# SHA — small in-tree hash lib used by CommonExtension.cpp.
StatusMessage("Add SHA library")
AddIncludeDirectories("SourceExt/SHA")
SetValue(TLA_SHA_SOURCE
    "SourceExt/SHA/sha1.h"
    "SourceExt/SHA/sha1.c"
    "SourceExt/SHA/sha2.h"
    "SourceExt/SHA/sha2.c")
AddStaticThirdPartyLibrary(SHA
    SOURCE_LIST TLA_SHA_SOURCE
    APPEND_TO FO_COMMON_LIBS)
DisableLibWarnings(SHA)

# ---------------------------------------------------------------------------
# Stage 4: EngineSources — register native extensions before the engine
# aggregates the source lists.
# ---------------------------------------------------------------------------

AddEngineSources(
    COMMON SourceExt/CommonExtension.cpp
    COMMON SourceExt/Dialogs.h
    COMMON SourceExt/Dialogs.cpp
    SERVER SourceExt/ServerExtension.cpp
    CLIENT SourceExt/ClientExtension.cpp
    BAKER SourceExt/BakerExtension.cpp
    BAKER SourceExt/DialogBaker.h
    BAKER SourceExt/DialogBaker.cpp
    TESTS SourceExt/TestDialogs.cpp)

RegisterEngineSources()

# ---------------------------------------------------------------------------
# Packaging definitions go in before the Packages stage processes them.
# ---------------------------------------------------------------------------

DefinePackage(Dev
    CONFIG LocalTest
    BINARY Server Windows win64 NoRes+Root+SingleZip
    BINARY Client Windows win64 NoRes+Root+SingleZip
    BINARY Mapper Windows win64 NoRes+Root+SingleZip
    BINARY Baker Windows win64 Lib+NoRes+Root+SingleZip)

DefinePackage(Test
    CONFIG LocalTest
    BINARY Client Windows win64 TotalProfiling+Raw
    BINARY Server Windows win64 TotalProfiling+Raw)

DefinePackage(LinuxTest
    CONFIG LocalTest
    BINARY Client Linux x64 Raw
    BINARY Server Linux x64 Raw
    BINARY Mapper Linux x64 Raw)

# ---------------------------------------------------------------------------
# Per-target post-build steps need the targets to already exist, so they go
# into a Finalize-Pre hook. The Applications stage copies TLA_BakerLib next to
# the Client, Server, ServerService and ServerHeadless executables; the Mapper
# and ASCompiler are not in its list, so the project copies it for them (the
# engine's PrebakeResources step on startup can then auto-bake on launch).
# ---------------------------------------------------------------------------

function(_tla_post_target_setup)
    # The desktop host prefers the external runtime module when it is present. Build it before the
    # executable so source/config changes cannot leave Build :: TLA_Client with a stale compatibility hash.
    if(TARGET ${FO_DEV_NAME}_Client AND TARGET ${FO_DEV_NAME}_ClientLib)
        add_dependencies(${FO_DEV_NAME}_Client ${FO_DEV_NAME}_ClientLib)
    endif()

    CopyTargetRuntimeToTarget(${FO_DEV_NAME}_Mapper ${FO_DEV_NAME}_BakerLib)
    CopyTargetRuntimeToTarget(${FO_DEV_NAME}_ASCompiler ${FO_DEV_NAME}_BakerLib)
endfunction()

AddStageHook(Finalize Pre _tla_post_target_setup)

# ---------------------------------------------------------------------------
# Stages 5..10 — engine-driven, called explicitly in canonical order.
# ---------------------------------------------------------------------------

SetupCodeGeneration()
BuildCoreLibraries()
BuildApplications()
SetupScriptsAndBaking()
BuildPackages()
FinalizeProjectGeneration()
