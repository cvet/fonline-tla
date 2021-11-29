# Project info
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
AddContent( Maps )
AddContent( Critters )
AddContent( Critters/Types )
AddContent( Items )
AddContent( Items/Static )
AddContent( Items/Custom )
AddContent( Dialogs )
AddContent( Texts )

# Scripts
AddScriptApi( Scripts/TLA.h )
AddAngelScriptSource( Scripts/*.fos )
AddAngelScriptSource( Scripts/Common/*.fos )
AddAngelScriptSource( Scripts/Json/*.fos )

# Resources
AddResources( Base Resources/FOnline )
AddResources( Music Resources/FOnlineMusic )
AddResources( Video Resources/FOnlineVideo )
AddResources( Mapper Resources/Mapper )
AddResources( VanBuren Resources/VanBuren )
AddRawResources( Resources/Mapper/Packs_Raw )

# Configs
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
CreateConfig( Multiplayer Default )
CreateConfig( Singleplayer Default )

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
