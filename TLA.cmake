# SetupGame option value option value...
# - DEV_NAME (default: "Unknown")
# - NICE_NAME (default: "Unknown")
# - COMPANY_NAME (default: "Unknown")
# - GAME_VERSION (default: "0.0.1")
# - ENGINE_VERSION (default: "")
# - MULTIPLAYER_SCRIPTING (default: YES)
# - SINGLEPLAYER_SCRIPTING (default: YES)
# - NATIVE_SCRIPTING (default: YES)
# - ANGELSCRIPT_SCRIPTING (default: YES)
# - MONO_SCRIPTING (default: YES)
# AddContent dir(s)
# AddResources packName dir(s)
# AddRawResources dir(s)
# AddScriptApi headerPath(s)
# AddNativeIncludeDir target dir(s)
# AddNativeSource target pathPattern(s)
# AddAngelScriptSource pathPattern(s)
# AddMonoAssembly assembly
# AddMonoReference assembly target ref(s)
# AddMonoSource assembly target pathPattern(s)
# CreateConfig config inheritenConfig
# TweakConfig config option value
# CreatePackage package config debug
# AddToPackage package binary platform arch packType [customConfig]

SetupGame( DEV_NAME "TLA"
    NICE_NAME "FOnline: The Life After"
    COMPANY_NAME "MyCorpLtd"
    GAME_VERSION "0.1.0"
    MULTIPLAYER_SCRIPTING YES
    SINGLEPLAYER_SCRIPTING YES
    ANGELSCRIPT_SCRIPTING YES 
	NATIVE_SCRIPTING YES 
	MONO_SCRIPTING NO )

# Content
AddContent( TLA/Critters )
AddContent( TLA/Items )
AddContent( TLA/Maps )
AddContent( TLA/Scenery )
# FOnlineSDK/Modules/Core; FOnlineSDK/Modules/Scores; FOnlineSDK/Modules/BuildSystem; TLA; FonlineCommon; Fonline-JSON;

# Resources
AddResources( "Pack1" "Resources/FOnline" )
AddResources( "Pack2" "Resources/FOnlineMusic" )
AddResources( "Pack3" "Resources/FOnlineVideo" )
AddResources( "Pack4" "Resources/Mapper" )
AddResources( "Pack5" "Resources/VanBuren" )
AddRawResources( "Resources/Mapper/Packs_Raw" )

# Scripts
AddScriptApi( "Scripts/MyScriptApi.h" )
AddAngelScriptSource( "Scripts/Test.fos" )

# Default config
CreateConfig( Default "" )
TweakConfig( Default WindowName "The Life After" )
TweakConfig( Default ListenPort 4008 )
TweakConfig( Default AdminPanelPort 0 )
TweakConfig( Default GameSleep 10 )
TweakConfig( Default MemoryDebugLevel 1 )
TweakConfig( Default Logging True )
TweakConfig( Default LoggingDebugOutput False )
TweakConfig( Default LoggingTime True )
TweakConfig( Default LoggingThread False )
TweakConfig( Default ProfilerMode 0 )
TweakConfig( Default ProfilerSampleInterval 50 )
TweakConfig( Default Language_0 engl )
TweakConfig( Default Language_1 russ )
TweakConfig( Default Access_client "000000 00000000" )
TweakConfig( Default Access_tester "" )
TweakConfig( Default Access_moder "" )
TweakConfig( Default Access_admin "admin admin" )
TweakConfig( Default AccessNames_admin "" )
TweakConfig( Default Language engl )
TweakConfig( Default RemoteHost localhost )
TweakConfig( Default RemotePort 4008 )
TweakConfig( Default UpdateServerHost "" )
TweakConfig( Default UpdateServerPort "" )
TweakConfig( Default ProxyType 0 )
TweakConfig( Default ProxyHost localhost )
TweakConfig( Default ProxyPort 1080 )
TweakConfig( Default ProxyUser "" )
TweakConfig( Default ProxyPass "" )
TweakConfig( Default MusicVolume 100 )
TweakConfig( Default SoundVolume 100 )
TweakConfig( Default ScreenWidth 1024 )
TweakConfig( Default ScreenHeight 768 )
TweakConfig( Default FullScreen False )
TweakConfig( Default AlwaysOnTop False )
TweakConfig( Default FixedFPS 100 )
TweakConfig( Default VSync False )

# Test builds
CreatePackage( "Test" "LocalTest" YES )
AddToPackage( "Test" "Client" "Windows" "win32" "Raw" )
AddToPackage( "Test" "Client" "Web" "wasm" "Raw" "LocalWebTest" )
AddToPackage( "Test" "Server" "Windows" "win64" "Raw" )
CreatePackage( "ProductionTest" "LocalTest" NO )
AddToPackage( "ProductionTest" "Client" "Windows" "win32" "Raw" )
AddToPackage( "ProductionTest" "Client" "Web" "wasm" "Raw" "LocalWebTest" )
AddToPackage( "ProductionTest" "Server" "Windows" "win64" "Raw" )
AddToPackage( "Test" "Single" "Windows" "win32" "Raw" )

# Production builds
CreatePackage( "Production" Default NO )
AddToPackage( "Production" "Client" "Windows" "win32+win64" "Raw" )
AddToPackage( "Production" "Client" "Windows" "win32+win64" "Wix" )
AddToPackage( "Production" "Client" "Windows" "win32" "Zip" )
AddToPackage( "Production" "Client" "Android" "arm+arm64+x86" "Apk" )
AddToPackage( "Production" "Client" "Web" "wasm" "Raw" )
AddToPackage( "Production" "Client" "macOS" "x64" "Bundle" )
AddToPackage( "Production" "Client" "iOS" "arm64" "Bundle" )
AddToPackage( "Production" "Client" "Linux" "x64" "AppImage" )
AddToPackage( "Production" "Server" "Windows" "win64" "Raw" )
AddToPackage( "Production" "Server" "Windows" "win64" "Zip" )
AddToPackage( "Production" "Server" "Linux" "x64" "Raw" )
AddToPackage( "Production" "Server" "Linux" "x64" "Tar" )
AddToPackage( "Production" "Server" "Linux" "x64" "AppImage" )
