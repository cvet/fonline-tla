# Project info
SetupGame( DEV_NAME "TLA"
    NICE_NAME "FOnlineTLA"
    AUTHOR_NAME "FODev"
    GAME_VERSION "0.0.4"
    SINGLEPLAYER NO
    ENABLE_3D NO
    ANGELSCRIPT_SCRIPTING YES
    NATIVE_SCRIPTING NO
    MONO_SCRIPTING NO
    DEBUGGING_CONFIG Debugging
    MAPPER_CONFIG Mapper
    GENERATE_ANGELSCRIPT_CONTENT Scripts
    GEOMETRY HEXAGONAL )

# Native code
AddEngineSource( SERVER Scripts/Extension/ServerExtension.cpp )
AddEngineSource( CLIENT Scripts/Extension/ClientExtension.cpp )

# Content
AddContent( Configs )
AddContent( Scripts Scripts/Json )
AddContent( Maps )
AddContent( Critters Critters/Types )
AddContent( Items Items/Static Items/Custom )
AddContent( Dialogs )
AddContent( Texts )

# Resources
AddResources( FOnline Resources/FOnline )
AddResources( FOArt Resources/DataPacks/fo_art.zip Resources/DataPacks/fo_art_critters_h.zip )
AddResources( FOArt Resources/DataPacks/fo_art_critters_m.zip Resources/DataPacks/fo_art_critters_n.zip )
AddResources( BlackCombatArmor Resources/DataPacks/cablack.dat )
AddResources( Lieutenant Resources/DataPacks/lieutenant.dat )
AddResources( LongHairDude Resources/DataPacks/longhairdude.dat )
#AddResources( FTRobots Resources/DataPacks/ftrobots.bos )
AddResources( FOSound Resources/DataPacks/fo_sound.zip )
AddResources( Music Resources/FOnlineMusic )
AddResources( Video Resources/FOnlineVideo )
AddResources( CommonData Resources/CommonData )
AddResources( ServerData Resources/ServerData )
AddResources( Mapper Resources/Mapper )
# AddResources( VanBuren Resources/VanBuren )
# AddRawResources( Resources/Mapper )

# Test builds
CreatePackage( Dev LocalTest )
AddToPackage( Dev Client Windows win64 Raw )
AddToPackage( Dev Server Windows win64 Raw )
AddToPackage( Dev Editor Windows win64 Raw )
AddToPackage( Dev Mapper Windows win64 Raw Mapper )

# Production builds
#CreatePackage( Production PublicGame )
#AddToPackage( Production Client Windows win64 Raw+Zip )
#AddToPackage( Production Server Windows win64 Raw+Zip )
#AddToPackage( Production Client Windows win32+win64 Raw )
#AddToPackage( Production Client Windows win32+win64 Wix )
#AddToPackage( Production Client Windows win32 Zip )
#AddToPackage( Production Client Android arm+arm64+x86 Apk )
#AddToPackage( Production Client Web wasm Raw )
#AddToPackage( Production Client macOS x64 Bundle )
#AddToPackage( Production Client iOS arm64 Bundle )
#AddToPackage( Production Client Linux x64 AppImage )
#AddToPackage( Production Server Windows win64 Raw )
#AddToPackage( Production Server Windows win64 Zip )
#AddToPackage( Production Server Linux x64 Raw )
#AddToPackage( Production Server Linux x64 Tar )
#AddToPackage( Production Server Linux x64 AppImage )
