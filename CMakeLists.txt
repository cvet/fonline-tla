cmake_minimum_required(VERSION 3.22)
project(TLA)

include(Engine/BuildTools/Init.cmake)

SetOption(FO_MAIN_CONFIG "TLA.fomain")
SetOption(FO_DEV_NAME "TLA")
SetOption(FO_NICE_NAME "FOnlineTLA")
SetOption(FO_ENABLE_3D OFF)
SetOption(FO_ANGELSCRIPT_SCRIPTING ON)
SetOption(FO_NATIVE_SCRIPTING OFF)
SetOption(FO_MONO_SCRIPTING OFF)
SetOption(FO_GEOMETRY HEXAGONAL)
SetOption(FO_APP_ICON Resources/TLA.ico)

SetOption(FO_BUILD_CLIENT ON)
SetOption(FO_BUILD_SERVER ON)
SetOption(FO_BUILD_MAPPER ON)
SetOption(FO_BUILD_EDITOR ON)
SetOption(FO_BUILD_ASCOMPILER ON)
SetOption(FO_BUILD_BAKER ON)
SetOption(FO_UNIT_TESTS ON)
SetOption(FO_OUTPUT_PATH ${CMAKE_CURRENT_SOURCE_DIR})

include(Engine/BuildTools/StartGeneration.cmake)

# SHA
include_directories("Scripts/Extension/SHA")
add_library(SHA STATIC EXCLUDE_FROM_ALL
    "Scripts/Extension/SHA/sha1.h"
    "Scripts/Extension/SHA/sha1.c"
    "Scripts/Extension/SHA/sha2.h"
    "Scripts/Extension/SHA/sha2.c")
DisableLibWarnings(SHA)
list(APPEND FO_COMMON_LIBS SHA)

# Native code
AddEngineSource(COMMON Scripts/Extension/CommonExtension.cpp)
AddEngineSource(COMMON Scripts/Extension/ContentMigration.cpp)
AddEngineSource(SERVER Scripts/Extension/ServerExtension.cpp)
AddEngineSource(CLIENT Scripts/Extension/ClientExtension.cpp)
AddEngineSource(COMMON Scripts/Extension/Dialogs.h)
AddEngineSource(COMMON Scripts/Extension/Dialogs.cpp)
AddEngineSource(BAKER Scripts/Extension/BakerExtension.cpp)
AddEngineSource(BAKER Scripts/Extension/DialogBaker.h)
AddEngineSource(BAKER Scripts/Extension/DialogBaker.cpp)

# Test builds
CreatePackage(Dev LocalTest)
AddToPackage(Dev Server Windows win64 NoRes+Root+SingleZip)
AddToPackage(Dev Client Windows win64 NoRes+Root+SingleZip)
AddToPackage(Dev Mapper Windows win64 NoRes+Root+SingleZip)
AddToPackage(Dev Editor Windows win64 NoRes+Root+SingleZip)
AddToPackage(Dev Baker Windows win64 Lib+NoRes+Root+SingleZip)

CreatePackage(Test LocalTest)
AddToPackage(Test Client Windows win64 TotalProfiling+OGL+Raw)
AddToPackage(Test Server Windows win64 TotalProfiling+Raw)

CreatePackage(LinuxTest LocalTest)
AddToPackage(LinuxTest Client Linux x64 Raw)
AddToPackage(LinuxTest Server Linux x64 Raw)
AddToPackage(LinuxTest Editor Linux x64 Raw)
AddToPackage(LinuxTest Mapper Linux x64 Raw)

#
include(Engine/BuildTools/FinalizeGeneration.cmake)
