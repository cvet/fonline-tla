# Project info
SetupGame( DEV_NAME "TLA"
    NICE_NAME "FOnline: The Life After"
    AUTHOR_NAME "MyCorpLtd"
    GAME_VERSION "0.1.0"
    SINGLEPLAYER NO
    ENABLE_3D NO
    ANGELSCRIPT_SCRIPTING YES
	NATIVE_SCRIPTING NO
	MONO_SCRIPTING NO )

# Content
AddContent( Maps )
AddContent( Critters Critters/Types )
AddContent( Items Items/Static Items/Custom )
AddContent( Dialogs )
AddContent( Texts )

# Scripts
AddEngineSource( SERVER Scripts/Extension/ServerExtension.cpp )
AddEngineSource( SERVER Scripts/Extension/CritterTimeEvents.cpp )
AddEngineSource( CLIENT Scripts/Extension/ClientExtension.cpp )
# AddAngelScriptExtensionSource( Scripts/AngelScriptExtension.cpp )
# AddAngelScriptExtensionEntry( InitAngelScriptExtension )
AddAngelScriptSource( Scripts/*.fos )
AddAngelScriptSource( Scripts/Json/*.fos )

# Resources
AddResources( FOnline Resources/FOnline )
AddResources( FOArt Resources/DataPacks/fo_art.zip Resources/DataPacks/fo_art_critters_h.zip )
AddResources( FOArt Resources/DataPacks/fo_art_critters_m.zip Resources/DataPacks/fo_art_critters_n.zip )
AddResources( BlackCombatArmor Resources/DataPacks/cablack.dat )
AddResources( Lieutenant Resources/DataPacks/lieutenant.dat )
AddResources( LongHairDude Resources/DataPacks/longhairdude.dat )
AddResources( FTRobots Resources/DataPacks/ftrobots.bos )
AddResources( FOSound Resources/DataPacks/fo_sound.zip )
AddResources( Music Resources/FOnlineMusic )
AddResources( Video Resources/FOnlineVideo )
AddResources( CommonData Resources/CommonData )
AddResources( ServerData Resources/ServerData )
# AddResources( Mapper Resources/Mapper )
# AddResources( VanBuren Resources/VanBuren )
# AddRawResources( Resources/Mapper )

# Configs
CreateConfig( Default ""
    ResourcesDir Resources
    ClientResourceEntries "Core FOnline FOArt BlackCombatArmor Lieutenant LongHairDude FTRobots Music Video CommonData"
    ServerResourceEntries "Protos Maps Dialogs CommonData ServerData"
    DataSynchronization True
    BakeExtraFileExtensions +json
    EmbeddedResources $Embedded
    ForceOpenGL True
    WindowName "The Life After"
    ListenPort 4008
    AdminPanelPort 0
    GameSleep 10
    MemoryDebugLevel 1
    Logging True
    LoggingDebugOutput False
    LoggingTime True
    LoggingThread False
    ProfilerMode 0
    ProfilerSampleInterval 50
    Languages "engl russ"
    Language engl
    Access_client "000000 00000000"
    Access_tester " "
    Access_moder " "
    Access_admin "admin admin"
    AccessNames_admin " "
    ServerHost localhost
    ServerPort 4008
    UpdateServerHost " "
    UpdateServerPort " "
    ProxyType 0
    ProxyHost localhost
    ProxyPort 1080
    ProxyUser " "
    ProxyPass " "
    MusicVolume 100
    SoundVolume 100
    ScreenWidth 1024
    ScreenHeight 768
    ScreenHudHeight 0
    FullScreen False
    AlwaysOnTop False
    FixedFPS 100
    VSync False
    MapHexagonal True
    MapHexWidth 32
    MapHexHeight 16
    MapHexLineHeight 12
    MapTileOffsX -8
    MapTileOffsY 34
    MapTileStep 2
    MapRoofOffsX -8
    MapRoofOffsY -64
    MapRoofSkipSize 2
    MapCameraAngle 25.6589
    MapFreeMovement False
    MapSmoothPath True
    MapDataPrefix "art/geometry/fallout_"
    LookDir "0 20 40 60 60"
    LookSneakDir "90 60 30 0 0"
    EffectValues "0 0 0 0 0 0 0 0 0 0"
    CritterSlotEnabled "True True True"
    CritterSlotSendData "True False True"
    StartYear 2240 )

CreateConfig( LocalTest Default
    ServerHost localhost
    ServerPort 4008 )
CreateConfig( LocalTest1 LocalTest
    TestCase Test1 )
CreateConfig( LocalTest2 LocalTest
    TestCase Test2 )
CreateConfig( LocalTest3 LocalTest
    TestCase Test3 )
CreateConfig( LocalTest4 LocalTest
    TestCase Test4 )
CreateConfig( LocalTest5 LocalTest
    TestCase Test5 )

CreateConfig( PublicGame Default
    ServerHost 111.222.111.222
    ServerPort 9999 )

CreateConfig( Mapper Default
    RoofAlpha 200
    SpritesZoomMax 10.0f
    SpritesZoomMin 0.2f
    Anim2CombatBegin Anim2Actions::BeginCombat
    Anim2CombatIdle Anim2Actions::IdleCombat
    Anim2CombatEnd Anim2Actions::EndCombat
    SplitTilesCollection True
    ConsoleHistorySize 100 )

CreateConfig( Debugging LocalTest
    ResourcesDir ${FO_RESOURCES_OUTPUT}
    EmbeddedResources ${FO_RESOURCES_OUTPUT}/Embedded
    RenderDebug True
    DataSynchronization False )
SetConfigForDebugging( Debugging )

# Test builds
CreatePackage( Testing LocalTest YES )
AddToPackage( Testing Client Windows win64 Raw )
AddToPackage( Testing Server Windows win64 Raw LocalTest1 )
AddToPackage( Testing Server Windows win64 Raw LocalTest2 )
AddToPackage( Testing Server Windows win64 Raw LocalTest3 )
AddToPackage( Testing Server Windows win64 Raw LocalTest4 )
AddToPackage( Testing Server Windows win64 Raw LocalTest5 )

# Production builds
CreatePackage( Production PublicGame NO )
AddToPackage( Production Client Windows win64 Raw )
AddToPackage( Production Server Windows win64 Raw )
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
