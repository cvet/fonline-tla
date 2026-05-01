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
    FO_ANGELSCRIPT_SCRIPTING ON
    FO_NATIVE_SCRIPTING OFF
    FO_MONO_SCRIPTING OFF
    FO_GEOMETRY HEXAGONAL
    FO_MAP_HEX_WIDTH 32
    FO_MAP_HEX_HEIGHT 16
    FO_MAP_CAMERA_ANGLE 25.6589
    FO_APP_ICON Resources/TLA.ico
    FO_BUILD_CLIENT ON
    FO_BUILD_SERVER ON
    FO_BUILD_MAPPER ON
    FO_BUILD_EDITOR ON
    FO_BUILD_ASCOMPILER ON
    FO_BUILD_BAKER ON
    FO_UNIT_TESTS ON
    FO_OUTPUT_PATH ${CMAKE_CURRENT_SOURCE_DIR})

# ---------------------------------------------------------------------------
# Stage 1: Init — options, platform detection, compiler/link flags.
# ---------------------------------------------------------------------------

StartProjectGeneration()

# ---------------------------------------------------------------------------
# Stage 2: ProjectOptions — engine-side option validation.
# ---------------------------------------------------------------------------

RegisterProjectOptions()

# Engine 89a83316b regression workaround: ThirdParty stage gates LibreSSL on
# FO_BUILD_OPENSSL_LIB, but the option is never declared or auto-derived
# (pre-refactor it was FO_BUILD_SERVER_LIB). Mirror the previous behaviour so
# Asio/websocketpp's TLS headers can find OpenSSL. Drop once upstream fixes it.
SetValue(FO_BUILD_OPENSSL_LIB ${FO_BUILD_SERVER_LIB})

# ---------------------------------------------------------------------------
# Stage 3: ThirdParty — bundled engine libs plus project-local extras.
# ---------------------------------------------------------------------------

AddThirdPartyLibraries()

# SHA — small in-tree hash lib used by CommonExtension.cpp.
StatusMessage("Add SHA library")
AddIncludeDirectories("SourceExt/SHA")
SetValue(FO_SHA_SOURCE
    "SourceExt/SHA/sha1.h"
    "SourceExt/SHA/sha1.c"
    "SourceExt/SHA/sha2.h"
    "SourceExt/SHA/sha2.c")
AddStaticThirdPartyLibrary(SHA
    SOURCE_LIST FO_SHA_SOURCE
    APPEND_TO FO_COMMON_LIBS)
DisableLibWarnings(SHA)

# ---------------------------------------------------------------------------
# Stage 4: EngineSources — register native extensions before the engine
# aggregates the source lists.
# ---------------------------------------------------------------------------

AddEngineSources(
    COMMON SourceExt/CommonExtension.cpp
    COMMON SourceExt/ContentMigration.cpp
    COMMON SourceExt/Dialogs.h
    COMMON SourceExt/Dialogs.cpp
    SERVER SourceExt/ServerExtension.cpp
    CLIENT SourceExt/ClientExtension.cpp
    BAKER SourceExt/BakerExtension.cpp
    BAKER SourceExt/DialogBaker.h
    BAKER SourceExt/DialogBaker.cpp)

RegisterEngineSources()

# ---------------------------------------------------------------------------
# Packaging definitions go in before the Packages stage processes them.
# ---------------------------------------------------------------------------

DefinePackage(Dev
    CONFIG LocalTest
    BINARY Server Windows win64 NoRes+Root+SingleZip
    BINARY Client Windows win64 NoRes+Root+SingleZip
    BINARY Mapper Windows win64 NoRes+Root+SingleZip
    BINARY Editor Windows win64 NoRes+Root+SingleZip
    BINARY Baker Windows win64 Lib+NoRes+Root+SingleZip)

DefinePackage(Test
    CONFIG LocalTest
    BINARY Client Windows win64 TotalProfiling+OGL+Raw
    BINARY Server Windows win64 TotalProfiling+Raw)

DefinePackage(LinuxTest
    CONFIG LocalTest
    BINARY Client Linux x64 Raw
    BINARY Server Linux x64 Raw
    BINARY Editor Linux x64 Raw
    BINARY Mapper Linux x64 Raw)

# ---------------------------------------------------------------------------
# Stages 5..10 — engine-driven, called explicitly in canonical order.
# ---------------------------------------------------------------------------

SetupCodeGeneration()
BuildCoreLibraries()
BuildApplications()
SetupScriptsAndBaking()
BuildPackages()
FinalizeProjectGeneration()
