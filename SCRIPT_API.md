# TLA Script API

## Table of Content

* [Table of Content](#table-of-content)
* [Settings](#settings)
  - [General](#general)
  - [Common](#common)
  - [FileSystem](#filesystem)
  - [CommonGameplay](#commongameplay)
  - [ServerGameplay](#servergameplay)
  - [Network](#network)
  - [ServerNetwork](#servernetwork)
  - [ClientNetwork](#clientnetwork)
  - [Audio](#audio)
  - [View](#view)
  - [Geometry](#geometry)
  - [Render](#render)
  - [Timer](#timer)
  - [Baker](#baker)
  - [Critter](#critter)
  - [CritterView](#critterview)
  - [Hex](#hex)
  - [Platform](#platform)
  - [Input](#input)
  - [Mapper](#mapper)
  - [Client](#client)
  - [Server](#server)
* [Game entity](#game-entity)
  - [Game properties](#game-properties)
  - [Game server events](#game-server-events)
  - [Game client events](#game-client-events)
  - [Game common methods](#game-common-methods)
  - [Game server methods](#game-server-methods)
  - [Game client methods](#game-client-methods)
  - [Game mapper events](#game-mapper-events)
  - [Game mapper methods](#game-mapper-methods)
* [Player entity](#player-entity)
  - [Player properties](#player-properties)
  - [Player server events](#player-server-events)
  - [Player server methods](#player-server-methods)
* [Item entity](#item-entity)
  - [Item properties](#item-properties)
  - [Item server events](#item-server-events)
  - [Item server methods](#item-server-methods)
  - [Item client methods](#item-client-methods)
* [Critter entity](#critter-entity)
  - [Critter properties](#critter-properties)
  - [Critter server events](#critter-server-events)
  - [Critter server methods](#critter-server-methods)
  - [Critter client methods](#critter-client-methods)
* [Map entity](#map-entity)
  - [Map properties](#map-properties)
  - [Map server events](#map-server-events)
  - [Map server methods](#map-server-methods)
  - [Map client methods](#map-client-methods)
* [Location entity](#location-entity)
  - [Location properties](#location-properties)
  - [Location server events](#location-server-events)
  - [Location server methods](#location-server-methods)
* [Types](#types)
  - [VideoPlayback reference object](#videoplayback-reference-object)
  - [MapSpriteData reference object](#mapspritedata-reference-object)
  - [SpritePattern reference object](#spritepattern-reference-object)
  - [ident value object](#ident-value-object)
  - [tick_t value object](#tick_t-value-object)
  - [ucolor value object](#ucolor-value-object)
* [Enums](#enums)

## Settings

### General

* `CursorType Cursor (client only)`

  ...

* `CursorType DraggableCursor (client only)`

  ...

* `bool MsgboxInvert (client only)`

  ...

* `uint CombatMessagesType (client only)`

  ...

* `uint GlobalMapGroupMaxCount = 6`

  Макс размер группы

* `any CursorData (client only)`

  ...

* `string PlayerOffAppendix (client only)`

  ...

* `int DeadHitPoints`

  ...

* `bool IsConnected (client only)`

  ...

* `bool IsConnecting (client only)`

  ...

* `bool IsUpdating (client only)`

  ...

* `bool DebugInfo (client only)`

  ...

* `bool MapZooming (client only)`

  ...

* `uint Breaktime`

  ...

* `uint BruteForceTick`

  ...

* `uint CritterIdleTick`

  ...

* `bool RtAlwaysRun`

  ...

* `uint BagRefreshTime`

  ...

* `uint WisperDist`

  ...

* `uint AccountPlayTime`

  ...

* `bool HidePassword (client only)`

  ...

* `bool DisableLMenu (client only)`

  ...

* `uint DamageHitDelay`

  ...

* `bool CustomItemCost`

  ...

* `bool GmapActive (client only)`

  активна ли глобальная карта и все ли следующие нижеприведенные переменные корректны

* `bool GmapWait (client only)`

  включен режим ожидания ответа о подтверждении энкаунтера

* `float GmapZoom (client only)`

  текущий масштаб, не забывайте учитывать его при рисовании на карте

* `int GmapGroupX (client only)`

  ...

* `int GmapGroupY (client only)`

  ...

* `int GmapOffsetX (client only)`

  смещение карты от нулевой координаты (верхний-левый угол)

* `int GmapOffsetY (client only)`

  ...

* `int GmapGroupCurX (client only)`

  координаты группы игрока

* `int GmapGroupCurY (client only)`

  ...

* `int GmapGroupToX (client only)`

  координаты точки назначения

* `int GmapGroupToY (client only)`

  ...

* `float GmapGroupSpeed (client only)`

  текущая скорость передвижения

* `bool ShowGroups (client only)`

  ...

* `uint MinimumOfflineTime (server only)`

  ...

* `uint TimeoutTransfer`

  ...

* `uint TimeoutBattle`

  ...

* `bool RunOnTransfer`

  ...

* `bool RunOnCombat`

  ...

* `bool MainStoryLineActive = true`

  /  
  / Global variables  
  /

* `uint PermanentDeath = 0`

  Number of deaths to account blocking, zero to disable

* `uint HitAimEyes = 60`

  ...

* `uint HitAimHead = 40`

  ...

* `uint HitAimGroin = 30`

  ...

* `uint HitAimTorso = 0`

  ...

* `uint HitAimArms = 30`

  ...

* `uint HitAimLegs = 20`

  ...

* `bool NoPvpMaps = false`

  Отключение нопвп режима активно

* `uint MaxLifeLevelSoftCap = 0`

  Максимальный уровень персонажа, на котором происходит увеличение хп. 0  = не используется

* `uint EncounterTime = 0`

  Как часто пробовать создать энкаунтер, в миллисекундах

* `bool Production`

  ...

* `int ApCostAimArms`

  Old global vars

* `int ApCostAimEyes`

  ...

* `int ApCostAimGroin`

  ...

* `int ApCostAimHead`

  ...

* `int ApCostAimLegs`

  ...

* `int ApCostAimTorso`

  ...

* `int ApRegeneration`

  ...

* `int FixBoyDefaultExperience`

  ...

* `uint GlobalMapMoveTime`

  ...

* `int LevelCap`

  ...

* `bool LevelCapAddExperience`

  ...

* `int LookNormal`

  ...

* `int LookWeight`

  ...

* `int ReputationAccepted`

  ...

* `int ReputationAntipathy`

  ...

* `int ReputationLiked`

  ...

* `int ReputationHated`

  ...

* `int ReputationLoved`

  ...

* `int ReputationNeutral`

  ...

* `int RtApCostCritterRun`

  ...

* `int RtApCostCritterWalk`

  ...

* `int RtApCostDropItem`

  ...

* `int RtApCostMoveItemContainer`

  ...

* `int RtApCostMoveItemInventory`

  ...

* `int RtApCostPickCritter`

  ...

* `int RtApCostPickItem`

  ...

* `int RtApCostReloadWeapon`

  ...

* `int RtApCostUseItem`

  ...

* `int RtApCostUseSkill`

  ...

* `int SkillMaxValue`

  ...

* `int SkillModAdd2`

  ...

* `int SkillModAdd3`

  ...

* `int SkillModAdd4`

  ...

* `int SkillModAdd5`

  ...

* `int SkillModAdd6`

  ...

* `int StartSpecialPoints`

  ...

* `int StartTagSkillPoints`

  ...

* `bool Singleplayer`

  ...

* `bool AlwaysRun`

  ...

* `uint AlwaysRunMoveDist = 1`

  ...

* `uint AlwaysRunUseDist = 5`

  ...

* `int TimeMultiplier`

  ...

* `string ValidNameLettersCommon`

  ...

* `string ValidNameLettersCulture1`

  ...

* `string ValidNameLettersCulture2`

  ...


### Common

  ...

* `const bool ClientMode = false`

  Auto

* `const string ExternalConfig = `

  ...

* `const string CommandLine = `

  ...

* `const string[] CommandLineArgs = `

  ...

* `const int[] DummyIntVec = `

  ...

* `const string ImGuiColorStyle = Light`

  Light, Classic, Dark

* `const uint ScriptOverrunReportTime = 100`

  ...

* `const bool DebugBuild = false`

  ...


### FileSystem

  ...

* `const string ResourcesDir = Resources`

  Todo: remove hardcoded ResourcesDir in package.py

* `const string[] ClientResourceEntries = `

  ...

* `const string[] ServerResourceEntries = `

  ...

* `const string EmbeddedResources = @Embedded`

  ...

* `const bool DataSynchronization = true`

  ...


### CommonGameplay

  ...

* `const uint MinNameLength = 4`

  ...

* `const uint MaxNameLength = 12`

  ...

* `const string[] Languages = engl`

  ...

* `const uint TalkDistance = 3`

  ...

* `const uint GlobalMapWidth = 28`

  ...

* `const uint GlobalMapHeight = 30`

  ...

* `const uint GlobalMapZoneLength = 50`

  ...

* `const uint LookChecks = 0`

  ...

* `const uint[] LookDir = 0, 20, 40, 60, 60`

  ...

* `const uint[] LookSneakDir = 90, 60, 30, 0, 0`

  ...

* `const uint LookMinimum = 6`

  ...

* `const bool CritterBlockHex = false`

  ...


### ServerGameplay

  ...

* `const uint RegistrationTimeout = 5`

  ...

* `const uint NpcMaxTalkers = 1`

  ...

* `const uint DlgTalkMaxTime = 0`

  ...

* `const uint DlgBarterMaxTime = 0`

  ...

* `const uint WhisperDist = 2`

  ...

* `const uint ShoutDist = 200`

  ...

* `const bool NoAnswerShuffle = false`

  ...

* `const uint SneakDivider = 6`

  ...

* `const uint CritterIdlePeriod = 0`

  ...


### Network

  ...

* `const uint ServerPort = 4000`

  ...

* `const uint NetBufferSize = 4096`

  ...

* `const uint UpdateFileSendSize = 1000000`

  ...

* `const bool SecuredWebSockets = false`

  ...

* `const bool DisableTcpNagle = true`

  ...

* `const bool DisableZlibCompression = false`

  ...

* `const uint FloodSize = 2048`

  ...

* `const uint ArtificalLags = 0`

  ...


### ServerNetwork

  ...

* `const uint InactivityDisconnectTime = 0`

  ...

* `const string WssPrivateKey = `

  ...

* `const string WssCertificate = `

  ...


### ClientNetwork

  ...

* `const string ServerHost = localhost`

  ...

* `const uint PingPeriod = 2000`

  ...

* `uint ProxyType = 0`

  ...

* `string ProxyHost = `

  ...

* `uint ProxyPort = 8080`

  ...

* `string ProxyUser = `

  ...

* `string ProxyPass = `

  ...

* `uint Ping = 0`

  ...

* `bool DebugNet = false`

  ...


### Audio

  ...

* `bool DisableAudio = false`

  ...

* `uint SoundVolume = 100`

  ...

* `uint MusicVolume = 100`

  ...


### View

  ...

* `int ScreenWidth = 1024`

  ...

* `int ScreenHeight = 768`

  ...

* `const int MonitorWidth = 0`

  Auto

* `const int MonitorHeight = 0`

  Auto

* `int ScreenHudHeight = 0`

  ...

* `int ScrOx = 0`

  ...

* `int ScrOy = 0`

  ...

* `bool ShowCorners = false`

  ...

* `bool ShowDrawOrder = false`

  ...

* `bool ShowSpriteBorders = false`

  ...

* `const bool HideNativeCursor = false`

  ...

* `const uint FadingDuration = 1000`

  ...


### Geometry

  ...

* `const bool MapHexagonal = `

  ...

* `const bool MapSquare = `

  ...

* `const int MapDirCount = `

  ...

* `const int MapHexWidth = 32`

  hex/square width

* `const int MapHexHeight = 16`

  hex/square height

* `const int MapHexLineHeight = 12`

  hex/square line height

* `const int MapTileStep = 2`

  ...

* `const int MapTileOffsX = -8`

  tile default offsets

* `const int MapTileOffsY = 32`

  tile default offsets

* `const int MapRoofOffsX = -8`

  roof default offsets

* `const int MapRoofOffsY = -66`

  roof default offsets

* `const float MapCameraAngle = 25.6589f`

  angle for critters moving/rendering

* `const bool MapFreeMovement = false`

  ...

* `const bool MapSmoothPath = true`

  enable pathfinding path smoothing

* `const string MapDataPrefix = Geometry`

  path and prefix for names used for geometry sprites


### Render

  ...

* `const uint Animation3dSmoothTime = 150`

  ...

* `const uint Animation3dFPS = 30`

  ...

* `const string HeadBone = `

  Todo: move HeadBone to fo3d settings

* `const string[] LegBones = `

  Todo: move LegBones to fo3d settings

* `bool WindowCentered = true`

  ...

* `bool WindowResizable = false`

  ...

* `bool NullRenderer = false`

  ...

* `bool ForceOpenGL = false`

  ...

* `bool ForceDirect3D = false`

  ...

* `bool ForceMetal = false`

  ...

* `bool ForceGlslEsProfile = false`

  ...

* `bool RenderDebug = false`

  ...

* `bool VSync = false`

  ...

* `bool AlwaysOnTop = false`

  ...

* `float[] EffectValues = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0`

  ...

* `bool Fullscreen = false`

  ...

* `int Brightness = 0`

  ...

* `uint FPS = 0`

  ...

* `int Sleep = -1`

  -1 to disable, Sleep has priority over FixedFPS if both enabled

* `int FixedFPS = 100`

  0 to disable, Sleep has priority over FixedFPS if both enabled

* `const int FogExtraLength = 0`

  ...

* `const float CritterTurnAngle = 100.0f`

  ...

* `const float CritterBodyTurnFactor = 0.6f`

  ...

* `const float CritterHeadTurnFactor = 0.4f`

  ...

* `const int DefaultModelViewWidth = 0`

  ...

* `const int DefaultModelViewHeight = 0`

  ...

* `const int DefaultModelDrawWidth = 128`

  ...

* `const int DefaultModelDrawHeight = 128`

  ...

* `const int WalkAnimBaseSpeed = 60`

  ...

* `const int RunAnimStartSpeed = 80`

  ...

* `const int RunAnimBaseSpeed = 120`

  ...

* `const float ModelProjFactor = 40.0f`

  ...

* `const bool AtlasLinearFiltration = false`

  ...

* `const int DefaultParticleDrawWidth = 128`

  ...

* `const int DefaultParticleDrawHeight = 128`

  ...

* `const bool RecreateClientOnError = false`

  ...


### Timer

  ...

* `const int StartYear = 2000`

  ...

* `const uint DebuggingDeltaTimeCap = 100`

  ...


### Baker

  ...

* `const bool ForceBaking = false`

  ...

* `const bool SingleThreadBaking = false`

  ...

* `const string BakeOutput = `

  ...

* `const string[] BakeResourceEntries = `

  ...

* `const string[] BakeContentEntries = `

  ...

* `const string[] BakeExtraFileExtensions = fopts, fofnt, bmfc, fnt, acm, ogg, wav, ogv, json, ini, lfspine`

  Todo: move resource files control (include/exclude/pack rules) to cmake


### Critter

  ...

* `const bool[] CritterSlotEnabled = true, true`

  ...

* `const bool[] CritterSlotSendData = false, true`

  ...

* `const bool[] CritterSlotMultiItem = true, false`

  ...


### CritterView

  ...

* `const uint CritterFidgetTime = 50000`

  ...

* `const CritterActionAnim CombatAnimBegin = CritterActionAnim::None`

  ...

* `const CritterActionAnim CombatAnimIdle = CritterActionAnim::None`

  ...

* `const CritterActionAnim CombatAnimEnd = CritterActionAnim::None`

  ...

* `bool ShowCritterName = true`

  ...

* `bool ShowPlayerName = true`

  ...

* `bool ShowNpcName = true`

  ...

* `bool ShowDeadNpcName = true`

  ...

* `const int NameOffset = 0`

  ...


### Hex

  ...

* `const float SpritesZoomMax = MAX_ZOOM`

  ...

* `const float SpritesZoomMin = MIN_ZOOM`

  ...

* `const uint ScrollDelay = 10`

  ...

* `const int ScrollStep = 12`

  ...

* `const uint RainTick = 60`

  ...

* `const int16 RainSpeedX = 0`

  ...

* `const int16 RainSpeedY = 15`

  ...

* `const ucolor ChosenLightColor = ucolor::clear`

  ...

* `const uint8 ChosenLightDistance = 4`

  ...

* `const int ChosenLightIntensity = 2500`

  ...

* `const uint8 ChosenLightFlags = 0`

  ...

* `bool FullscreenMouseScroll = true`

  ...

* `bool WindowedMouseScroll = false`

  ...

* `bool ScrollCheck = true`

  ...

* `bool ScrollKeybLeft = false`

  ...

* `bool ScrollKeybRight = false`

  ...

* `bool ScrollKeybUp = false`

  ...

* `bool ScrollKeybDown = false`

  ...

* `bool ScrollMouseLeft = false`

  ...

* `bool ScrollMouseRight = false`

  ...

* `bool ScrollMouseUp = false`

  ...

* `bool ScrollMouseDown = false`

  ...

* `uint8 RoofAlpha = 200`

  ...

* `bool ShowTile = true`

  ...

* `bool ShowRoof = true`

  ...

* `bool ShowItem = true`

  ...

* `bool ShowScen = true`

  ...

* `bool ShowWall = true`

  ...

* `bool ShowCrit = true`

  ...

* `bool ShowFast = true`

  ...

* `bool HideCursor = false`

  ...

* `bool ShowMoveCursor = false`

  ...


### Platform

  ...

* `const bool WebBuild = `

  ...

* `const bool WindowsBuild = `

  ...

* `const bool LinuxBuild = `

  ...

* `const bool MacOsBuild = `

  ...

* `const bool AndroidBuild = `

  ...

* `const bool IOsBuild = `

  ...

* `const bool DesktopBuild = `

  ...

* `const bool TabletBuild = `

  ...


### Input

  ...

* `uint DoubleClickTime = 500`

  ...

* `uint ConsoleHistorySize = 100`

  ...

* `int MouseX = 0`

  ...

* `int MouseY = 0`

  ...


### Mapper

  ...

* `const string MapsDir = `

  ...

* `const string StartMap = `

  ...

* `int StartHexX = -1`

  ...

* `int StartHexY = -1`

  ...

* `bool SplitTilesCollection = true`

  ...


### Client

  ...

* `const string AutoLogin = `

  ...

* `const uint TextDelay = 3000`

  ...

* `const uint UpdaterInfoDelay = 1000`

  ...

* `const int UpdaterInfoPos = 0`

  <1 - top, 0 - center, >1 - bottom

* `const string DefaultSplash = `

  ...

* `const string DefaultSplashPack = `

  ...

* `string Language = engl`

  ...

* `bool WinNotify = true`

  ...

* `bool SoundNotify = false`

  ...

* `bool HelpInfo = false`

  ...


### Server

  ...

* `const string[] AccessAdmin = `

  ...

* `const string[] AccessClient = `

  ...

* `const string[] AccessModer = `

  ...

* `const string[] AccessTester = `

  ...

* `const uint AdminPanelPort = 0`

  ...

* `const string DbStorage = Memory`

  ...

* `const bool NoStart = false`

  ...

* `const bool CollapseLogOnStart = false`

  ...

* `const int ServerSleep = -1`

  ...

* `const int LoopsPerSecondCap = 1000`

  ...

* `const uint LockMaxWaitTime = 100`

  ...

* `const uint DataBaseCommitPeriod = 10`

  ...

* `const uint DataBaseMaxCommitJobs = 100`

  ...

* `const uint LoopAverageTimeInterval = 1000`

  ...

* `const bool WriteHealthFile = false`

  ...

* `const bool ProtoMapStaticGrid = false`

  ...

* `const bool MapInstanceStaticGrid = false`

  ...


## Game entity

  ...

* `Target: Server/Client`
* `Built-in: Yes`
* `Singleton: Yes`
* `Has proto: No`
* `Has statics: No`
* `Has abstract: No`

### Game properties

* `PrivateCommon ident CustomHolderId ReadOnly IsCommon`

  ...

* `PrivateCommon hstring CustomHolderEntry ReadOnly IsCommon`

  ...

* `PrivateServer ident[] InnerEntityIds ReadOnly IsCommon`

  ...

* `PrivateCommon uint16 Year ReadOnly`

  ...

* `PrivateCommon uint16 Month ReadOnly`

  ...

* `PrivateCommon uint16 Day ReadOnly`

  ...

* `PrivateCommon uint16 Hour ReadOnly`

  ...

* `PrivateCommon uint16 Minute ReadOnly`

  ...

* `PrivateCommon uint16 Second ReadOnly`

  ...

* `PrivateCommon uint16 TimeMultiplier ReadOnly`

  ...

* `PrivateServer ident LastEntityId ReadOnly`

  ...

* `PrivateCommon ident LastDeferredCallId ReadOnly`

  ...

* `PrivateCommon ident HistoryRecordsId ReadOnly`

  ...

* `PrivateServer uint LastGlobalMapTripId ReadOnly`

  ...

* `PrivateServer uint ArroyoMynocTimeout`

  Name:	arroyo_mynoc_defence  
  Author:	Sufir

* `PrivateServer ident BaseSierraRule`

  ...

* `PrivateServer ident BaseMariposaRule`

  ...

* `PrivateServer ident BaseCathedralRule`

  ...

* `PrivateServer uint8 BaseSierraOrg Max = 2`

  ...

* `PrivateServer uint8 BaseMariposaOrg Max = 2`

  ...

* `PrivateServer uint8 BaseCathedralOrg Max = 2`

  ...

* `PrivateServer ident BaseSierraTimeEventId`

  ...

* `PrivateServer ident BaseMariposaTimeEventId`

  ...

* `PrivateServer ident BaseCathedralTimeEventId`

  ...

* `PrivateServer uint BaseEnclaveScore`

  ...

* `PrivateServer uint BaseBosScore`

  ...

* `PrivateServer uint8[] BulletinBoard`

  ...

* `PrivateServer bool DenGhostIsDead`

  Author: marvi

* `PrivateServer bool DenVirginIsAway`

  ...

* `PrivateServer uint8[] GameEventManagerData`

  ...

* `PrivateServer uint=>uint8[] GameEventData`

  ...

* `PrivateServer uint8 RacingWinnersFound Max = 2`

  ...

* `PrivateServer ident RacingWinner`

  ...

* `PrivateServer int LastGlobalMapTrip`

  Индекс последней группы на глобальной карте

* `PrivateServer uint EndingV13DclawGenocide`

  ...

* `PrivateServer ident KlamCowboy`

  ...

* `PrivateServer uint16 KlamCowboyLevel`

  ...

* `PrivateServer ident KlamSmilyGeckoLocation`

  ...

* `PrivateServer uint KlamSmilyGeckoTimeout`

  ...

* `PrivateServer bool TribRaid`

  ...

* `PrivateServer ident[] PrimalTribeQuestPlayers`

  ...

* `PrivateServer uint=>uint8[] MobWaveData`

  Author: rifleman17  
  Специальный скрипт для реализации волновых нападений агрессивных мобов на некоей карте

* `PrivateServer bool NCRRanchBrahminIll`

  ...

* `PrivateServer ident NcrDustyOneHourInvokeId`

  Author: cvet  
  Для квеста Вечеринка у Дасти.

* `PrivateServer ident NcrDustyOneWeekInvokeId`

  ...

* `PrivateServer uint8 NCRDustyPartyStatusGlobal Max = 2`

  ...

* `PrivateServer uint8 NCRDustyRotgutCounter Max = 20`

  ...

* `PrivateServer uint8 NCRDustyBeerGammaCounter Max = 20`

  ...

* `PrivateServer bool NCRInvasion`

  ...

* `PrivateServer uint8 NCRKessStageGlobal`

  rifleman17 30/10/09

* `PrivateServer uint8 NcrSmitPosition Max = 12`

  ...

* `PrivateServer bool NcrSmitGateGuardAccessGranted`

  ...

* `PrivateServer uint8 NcrWestinPositionGlobal`

  ...

* `Protected CritterProperty[] RegProperties`

  ...

* `PrivateServer ident ReddMarionWanLocation`

  ...

* `PrivateServer uint ReddMarionWanTimeout`

  ...

* `PrivateServer bool ReddJohnsonBroadcast`

  ...

* `PrivateServer ident[] PermanentDeath`

  ...

* `Public string[] BestScores`

  ...

* `PrivateServer ident[] BestScoreCritterIds`

  ...

* `PrivateServer int[] BestScoreValues`

  ...

* `PrivateServer uint8 SFZax366StatusGlobal`

  ...

* `PrivateServer bool SFDevinHired`

  ...

* `PrivateServer uint MissilesCanada`

  ...

* `PrivateServer uint MissilesKishinev`

  ...

* `PrivateServer uint MissilesBaku`

  ...

* `PrivateServer uint MissilesTokio`

  ...

* `PrivateServer uint MissilesEburg`

  ...

* `PrivateServer uint MissilesVladik`

  ...

* `PrivateServer uint MissilesRay`

  ...

* `PrivateServer uint MissilesFukusima`

  ...

* `Public string[] BestEScores`

  ...

* `PrivateServer int ArroyoRaidersCount`

  Global

* `PrivateServer ident[] ArroyoLastDefenceGroup`

  ...

* `PrivateServer ident ArroyoMynocMap`

  ...

* `PrivateServer bool EncOceanTraderAlive`

  ...

* `PrivateServer bool GameEventCaches`

  ...

* `PrivateServer uint8 RacingEvent`

  ...

* `PrivateServer bool GEReplStationStatus`

  ...

* `PrivateServer uint8 NCRSiegeCampsNum Max = 10`

  ...

* `PrivateServer uint8 SFBosArmourCounter Max = 3`

  ...

* `PrivateServer uint8 SFInvasionStatus Max = 3`

  ...

* `PrivateServer uint8 DenLeannaThief`

  ...

* `PrivateServer uint8 DenCliffDealer`

  ...

* `PrivateServer uint8 DenAnanDollUse`

  ...

* `PrivateServer uint KlamSmilyGeckoCounter`

  ...

* `PrivateServer uint EndingArroyoTodd`

  ...

* `PrivateServer uint EndingV13DclawRevival`

  ...

* `PrivateServer uint GeckSkitrHired`

  ...

* `PrivateServer uint NRBbarmenHired`

  ...

* `PrivateServer uint NcrIsCurfewActive`

  ...

* `PrivateServer uint NcrMicGuaranteeCounter`

  ...

* `PrivateServer uint SFImperatorMemory Max = 100`

  ...

* `PrivateServer uint8 GCityGeckSold Max = 1`

  ...

* `PrivateServer uint8 VCBlackHired Max = 1`

  ...

* `PrivateServer uint EndingV13DclawSaved`

  Author: Sufir

* `PrivateServer bool VCHartmanMarchStatus`

  ...

* `PrivateServer uint8 RaidersDead`

  ...

### Game server events

* `OnInit()`

  ...

* `OnGenerateWorld()`

  ...

* `OnStart()`

  ...

* `OnFinish()`

  ...

* `OnLoop()`

  ...

* `OnPlayerRegistration(Player player, string name, TextPackName& disallowTextPack, uint& disallowStrNum, string& disallowLex)`

  ...

* `OnPlayerLogin(Player player, string name, ident id, TextPackName& disallowTextPack, uint& disallowStrNum, string& disallowLex)`

  ...

* `OnPlayerGetAccess(Player player, int arg1, string& arg2)`

  ...

* `OnPlayerAllowCommand(Player player, string arg1, uint8 arg2)`

  ...

* `OnPlayerLogout(Player player)`

  ...

* `OnPlayerInit(Player player)`

  ...

* `OnPlayerEnter(Player player)`

  ...

* `OnPlayerCritterSwitched(Player player, Critter cr, Critter prevCr)`

  ...

* `OnPlayerMoveCritter(Player player, Critter cr, uint& speed)`

  ...

* `OnPlayerDirCritter(Player player, Critter cr, int16& dirAngle)`

  ...

* `OnCritterTransit(Critter cr, Map prevMap)`

  ...

* `OnGlobalMapCritterIn(Critter cr)`

  ...

* `OnGlobalMapCritterOut(Critter cr)`

  ...

* `OnLocationInit(Location location, bool firstTime)`

  ...

* `OnLocationFinish(Location location)`

  ...

* `OnMapInit(Map map, bool firstTime)`

  ...

* `OnMapFinish(Map map)`

  ...

* `OnMapLoop(Map map)`

  ...

* `OnMapLoopEx(Map map, uint loopIndex)`

  ...

* `OnMapCritterIn(Map map, Critter cr)`

  ...

* `OnMapCritterOut(Map map, Critter cr)`

  ...

* `OnMapCheckLook(Map map, Critter cr, Critter target)`

  ...

* `OnMapCheckTrapLook(Map map, Critter cr, Item item)`

  ...

* `OnCritterInit(Critter cr, bool firstTime)`

  ...

* `OnCritterFinish(Critter cr)`

  ...

* `OnCritterLoad(Critter cr)`

  ...

* `OnCritterUnload(Critter cr)`

  ...

* `OnCritterIdle(Critter cr)`

  ...

* `OnCritterItemMoved(Critter cr, Item item, CritterItemSlot fromSlot)`

  ...

* `OnCritterTalk(Critter cr, Critter talker, bool begin, uint talkers)`

  ...

* `OnCritterBarter(Critter cr, Critter trader, bool begin, uint barterCount)`

  ...

* `OnItemInit(Item item, bool firstTime)`

  ...

* `OnItemFinish(Item item)`

  ...

* `OnStaticItemWalk(StaticItem item, Critter cr, bool isIn, uint8 dir)`

  ...

* `OnCritterPickItem(Critter cr, Item item)`

  ...

* `OnCritterPickScenery(Critter cr, StaticItem scenery)`

  ...

* `OnCritterRespawn(Critter critter)`

  ...

* `OnCritterKnockout(Critter critter)`

  ...

* `OnItemCheckMove(Item item, uint count, Entity from, Entity to)`

  ...

* `OnCritterCheckMoveItem(Critter cr, Item item, CritterItemSlot toSlot)`

  ...

* `OnCritterItemIn(Critter cr, Item item)`

  ...

* `OnCritterItemOut(Critter cr, Item item)`

  ...

* `OnNpcPlaneBegin(Critter critter, int planeId, int reason, Critter someCr, Item someItem)`

  ...

* `OnNpcPlaneEnd(Critter critter, int planeId, int reason, Critter someCr, Item someItem)`

  ...

* `OnNpcPlaneRun(Critter critter, int planeId, int reason, any& result0, any& result1, any& result2)`

  ...

* `OnCritterUseItemOn(Critter cr, Item item, Critter onCritter, Item onItem, StaticItem onScenery, uint param)`

  ...

* `OnCritterUseItem(Critter cr, Item item, uint param)`

  ...

* `OnCritterUseSkill(Critter cr, CritterProperty skill, Critter onCritter, Item onItem, StaticItem onScenery)`

  ...

* `OnCritterReloadWeapon(Critter cr, Item weapon, Item ammo)`

  ...

* `OnCritterAttack(Critter cr, Critter target, Item weapon, uint8 weaponMode, ProtoItem ammo)`

  ...

* `OnCritterAttacked(Critter cr, Critter attacker)`

  ...

* `OnCritterStealing(Critter cr, Critter thief, Item item, uint itemCount)`

  ...

* `OnItemsBarter(Item[] saleItems, uint[] saleItemsCount, Item[] buyItems, uint[] buyItemsCount, Critter player, Critter npc)`

  ...

* `OnCritterDead(Critter cr, Critter killer)`

  ...

* `OnLocationEnter(Location loc, Critter[] group, uint8 entrance)`

  ...

### Game client events

* `OnStart()`

  ...

* `OnFinish()`

  ...

* `OnAutoLogin(string login, string password)`

  ...

* `OnRegistrationSuccess()`

  ...

* `OnLoginSuccess()`

  ...

* `OnLoop()`

  ...

* `OnGetActiveScreens(int[]& screens)`

  ...

* `OnScreenChange(bool show, int screen, string=>any data)`

  ...

* `OnScreenScroll(int offsetX, int offsetY)`

  ...

* `OnRenderIface()`

  ...

* `OnRenderMap()`

  ...

* `OnMouseDown(MouseButton button)`

  ...

* `OnMouseUp(MouseButton button)`

  ...

* `OnMouseMove(int offsetX, int offsetY)`

  ...

* `OnKeyDown(KeyCode key, string text)`

  ...

* `OnKeyUp(KeyCode key)`

  ...

* `OnInputLost()`

  ...

* `OnCritterIn(Critter cr)`

  ...

* `OnCritterOut(Critter cr)`

  ...

* `OnItemMapIn(Item item)`

  ...

* `OnItemMapChanged(Item item, Item oldItem)`

  ...

* `OnItemMapOut(Item item)`

  ...

* `OnItemInvIn(Item item)`

  ...

* `OnItemInvChanged(Item item, Item oldItem)`

  ...

* `OnItemInvOut(Item item)`

  ...

* `OnCustomEntityIn(Entity entity)`

  ...

* `OnCustomEntityOut(Entity entity)`

  ...

* `OnMapLoad()`

  ...

* `OnMapUnload()`

  ...

* `OnReceiveItems(Item[] items, any contextParam)`

  ...

* `OnMapMessage(string& text, uint16& hexX, uint16& hexY, ucolor& color, uint& delay)`

  ...

* `OnInMessage(string text, int sayType, ident crId)`

  ...

* `OnOutMessage(string& text, int& sayType)`

  ...

* `OnMessageBox(int type, string text)`

  ...

* `OnCritterAction(bool localCall, Critter cr, CritterAction action, int actionData, AbstractItem contextItem)`

  ...

* `OnCritterAnimationProcess(bool animateStay, Critter cr, CritterStateAnim stateAnim, CritterActionAnim actionAnim, AbstractItem contextItem)`

  ...

* `OnCritterAnimation(hstring modelName, CritterStateAnim stateAnim, CritterActionAnim actionAnim, uint& pass, uint& flags, int& ox, int& oy, string& animName)`

  ...

* `OnCritterAnimationSubstitute(hstring baseModelName, CritterStateAnim baseStateAnim, CritterActionAnim baseActionAnim, hstring& modelName, CritterStateAnim& stateAnim, CritterActionAnim& actionAnim)`

  ...

* `OnCritterAnimationFallout(hstring modelName, CritterStateAnim stateAnim, CritterActionAnim actionAnim, uint& fStateAnim, uint& fActionAnim, uint& fStateAnimEx, uint& fActionAnimEx, uint& flags)`

  ...

* `OnScreenSizeChanged()`

  ...

* `OnItemCheckMove(Item item, uint count, Entity from, Entity to)`

  ...

* `OnCritterCheckMoveItem(Critter cr, Item item, CritterItemSlot toSlot)`

  ...

* `OnPreRenderIface()`

  ...

* `OnPostRenderIface()`

  ...

* `OnCritterActionEx(bool localCall, Critter cr, CritterAction action, int actionExt, AbstractItem actionItem)`

  ...

* `OnItemsCollection(int collection, Item[] items)`

  ...

* `OnContainerChanged()`

  ...

* `OnCritterSneak(Critter cr)`

  ...

### Game common methods

* `void BreakIntoDebugger()`

  ...

* `void BreakIntoDebugger(string message)`

  ...

* `void Log(string text)`

  ...

* `void RequestQuit()`

  ...

* `bool IsResourcePresent(string resourcePath)`

  ...

* `string ReadResource(string resourcePath)`

  ...

* `int SystemCall(string command)`

  ...

* `int SystemCall(string command, string& output)`

  ...

* `int Random(int minValue, int maxValue)`

  ...

* `uint DecodeUtf8(string text, uint& length)`

  ...

* `string EncodeUtf8(uint ucs)`

  ...

* `string Sha1(string text)`

  ...

* `string Sha2(string text)`

  ...

* `void OpenLink(string link)`

  ...

* `uint64 GetUnixTime()`

  ...

* `uint GetDistance(uint16 hx1, uint16 hy1, uint16 hx2, uint16 hy2)`

  ...

* `uint8 GetDirection(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy)`

  ...

* `uint8 GetDirection(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy, float offset)`

  ...

* `int16 GetDirAngle(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy)`

  ...

* `int16 GetLineDirAngle(int fromX, int fromY, int toX, int toY)`

  ...

* `uint8 AngleToDir(int16 dirAngle)`

  ...

* `int16 DirToAngle(uint8 dir)`

  ...

* `int16 RotateDirAngle(int16 dirAngle, bool clockwise, int16 step)`

  ...

* `int16 GetDirAngleDiff(int16 dirAngle1, int16 dirAngle2)`

  ...

* `void GetHexInterval(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy, int& ox, int& oy)`

  ...

* `string GetClipboardText()`

  ...

* `void SetClipboardText(string text)`

  ...

* `string GetGameVersion()`

  ...

* `ProtoItem GetProtoItem(hstring pid)`

  ...

* `ProtoItem[] GetProtoItems()`

  ...

* `ProtoItem[] GetProtoItems(ItemComponent component)`

  ...

* `ProtoItem[] GetProtoItems(ItemProperty property, int propertyValue)`

  ...

* `ProtoCritter GetProtoCritter(hstring pid)`

  ...

* `ProtoCritter[] GetProtoCritters()`

  ...

* `ProtoCritter[] GetProtoCritters(CritterComponent component)`

  ...

* `ProtoCritter[] GetProtoCritters(CritterProperty property, int propertyValue)`

  ...

* `ProtoMap GetProtoMap(hstring pid)`

  ...

* `ProtoMap[] GetProtoMaps()`

  ...

* `ProtoMap[] GetProtoMaps(MapComponent component)`

  ...

* `ProtoMap[] GetProtoMaps(MapProperty property, int propertyValue)`

  ...

* `ProtoLocation GetProtoLocation(hstring pid)`

  ...

* `ProtoLocation[] GetProtoLocations()`

  ...

* `ProtoLocation[] GetProtoLocations(LocationComponent component)`

  ...

* `ProtoLocation[] GetProtoLocations(LocationProperty property, int propertyValue)`

  ...

### Game server methods

* `ident CreatePlayer(string name, string password)`

  ...

* `Critter CreateCritter(hstring protoId, bool forPlayer)`

  ...

* `Critter LoadCritter(ident crId, bool forPlayer)`

  ...

* `void UnloadCritter(Critter cr)`

  ...

* `void DestroyUnloadedCritter(ident crId)`

  ...

* `ident DeferredCall(uint delay, ScriptFunc-void func)`

  ...

* `ident DeferredCall(uint delay, ScriptFunc-void, any func, any value)`

  ...

* `ident DeferredCall(uint delay, ScriptFunc-void, any[] func, any[] values)`

  ...

* `ident RepeatingDeferredCall(uint delay, ScriptFunc-void func)`

  ...

* `ident RepeatingDeferredCall(uint delay, ScriptFunc-void, any func, any value)`

  ...

* `ident RepeatingDeferredCall(uint delay, ScriptFunc-void, any[] func, any[] values)`

  ...

* `ident SavedDeferredCall(uint delay, ScriptFunc-void func)`

  ...

* `ident SavedDeferredCall(uint delay, ScriptFunc-void, any func, any value)`

  ...

* `ident SavedDeferredCall(uint delay, ScriptFunc-void, any[] func, any[] values)`

  ...

* `bool IsDeferredCallPending(ident id)`

  ...

* `bool CancelDeferredCall(ident id)`

  ...

* `uint GetDistance(Critter cr1, Critter cr2)`

  ...

* `uint GetTick()`

  ...

* `Item GetItem(ident itemId)`

  ...

* `Item MoveItem(Item item, Critter toCr)`

  ...

* `Item MoveItem(Item item, uint count, Critter toCr)`

  ...

* `Item MoveItem(Item item, Map toMap, uint16 toHx, uint16 toHy)`

  ...

* `Item MoveItem(Item item, uint count, Map toMap, uint16 toHx, uint16 toHy)`

  ...

* `Item MoveItem(Item item, Item toCont, ContainerItemStack stackId)`

  ...

* `Item MoveItem(Item item, uint count, Item toCont, ContainerItemStack stackId)`

  ...

* `void MoveItems(Item[] items, Critter toCr)`

  ...

* `void MoveItems(Item[] items, Map toMap, uint16 toHx, uint16 toHy)`

  ...

* `void MoveItems(Item[] items, Item toCont, ContainerItemStack stackId)`

  ...

* `void DestroyEntity(ident id)`

  ...

* `void DestroyEntity(Entity entity)`

  ...

* `void DestroyEntities(ident[] ids)`

  ...

* `void DestroyEntities(Entity[] entities)`

  ...

* `void DestroyItem(Item item)`

  ...

* `void DestroyItem(Item item, uint count)`

  ...

* `void DestroyItem(ident itemId)`

  ...

* `void DestroyItem(ident itemId, uint count)`

  ...

* `void DestroyItems(Item[] items)`

  ...

* `void DestroyItems(ident[] itemIds)`

  ...

* `void DestroyCritter(Critter cr)`

  ...

* `void DestroyCritter(ident crId)`

  ...

* `void DestroyCritters(Critter[] critters)`

  ...

* `void DestroyCritters(ident[] critterIds)`

  ...

* `void RadioMessage(uint16 channel, string text)`

  ...

* `void RadioMessageMsg(uint16 channel, TextPackName textPack, uint numStr)`

  ...

* `void RadioMessageMsg(uint16 channel, TextPackName textPack, uint numStr, string lexems)`

  ...

* `tick_t GetFullSecond()`

  ...

* `tick_t EvaluateFullSecond(uint16 year, uint16 month, uint16 day, uint16 hour, uint16 minute, uint16 second)`

  ...

* `void EvaluateGameTime(tick_t serverTime, uint16& year, uint16& month, uint16& day, uint16& dayOfWeek, uint16& hour, uint16& minute, uint16& second)`

  ...

* `Location CreateLocation(hstring locPid, uint16 wx, uint16 wy)`

  ...

* `Location CreateLocation(hstring locPid, uint16 wx, uint16 wy, Critter[] critters)`

  ...

* `void DestroyLocation(Location loc)`

  ...

* `void DestroyLocation(ident locId)`

  ...

* `Critter GetCritter(ident crId)`

  ...

* `Player GetPlayer(string name) ExcludeInSingleplayer PassOwnership`

  ...

* `Critter[] GetGlobalMapCritters(uint16 wx, uint16 wy, uint radius, CritterFindType findType)`

  ...

* `Map GetMap(ident mapId)`

  ...

* `Map GetMap(hstring mapPid)`

  ...

* `Map GetMap(hstring mapPid, uint skipCount)`

  ...

* `Map[] GetMaps()`

  ...

* `Map[] GetMaps(hstring pid)`

  ...

* `Location GetLocation(ident locId)`

  ...

* `Location GetLocation(hstring locPid)`

  ...

* `Location GetLocation(hstring locPid, uint skipCount)`

  ...

* `Location[] GetLocations()`

  ...

* `Location[] GetLocations(hstring pid)`

  ...

* `Location[] GetLocations(uint16 wx, uint16 wy, uint radius)`

  ...

* `Location[] GetVisibleLocations(uint16 wx, uint16 wy, uint radius, Critter cr)`

  ...

* `Location[] GetZoneLocations(uint16 zx, uint16 zy, uint zoneRadius)`

  ...

* `bool RunDialog(Critter cr, Critter npc, bool ignoreDistance)`

  ...

* `bool RunDialog(Critter cr, Critter npc, hstring dlgPack, bool ignoreDistance)`

  ...

* `bool RunDialog(Critter cr, hstring dlgPack, uint16 hx, uint16 hy, bool ignoreDistance)`

  ...

* `int64 GetWorldItemCount(hstring pid)`

  ...

* `void AddTextListener(int sayType, string firstStr, int parameter, ScriptFunc-void, Critter, string func)`

  ...

* `void RemoveTextListener(int sayType, string firstStr, int parameter)`

  ...

* `Item[] GetAllItems(hstring pid)`

  ...

* `Player[] GetOnlinePlayers() ExcludeInSingleplayer`

  ...

* `ident[] GetRegisteredPlayerIds() ExcludeInSingleplayer`

  ...

* `Critter[] GetAllNpc()`

  ...

* `Critter[] GetAllNpc(hstring pid)`

  ...

* `void GetTime(uint16& year, uint16& month, uint16& day, uint16& dayOfWeek, uint16& hour, uint16& minute, uint16& second, uint16& milliseconds)`

  ...

* `void SetTime(uint16 multiplier, uint16 year, uint16 month, uint16 day, uint16 hour, uint16 minute, uint16 second)`

  ...

* `bool CallStaticItemFunction(Critter cr, StaticItem staticItem, Item usedItem, any param)`

  ...

* `hstring[] GetDialogs()`

  ...

* `StaticItem[] GetStaticItemsForProtoMap(ProtoMap proto)`

  ...

* `void LoadImage(int imageSlot, string imageName)`

  ...

* `uint GetImageColor(int imageSlot, int x, int y)`

  ...

### Game client methods

* `bool IsFullscreen()`

  ...

* `void ToggleFullscreen()`

  ...

* `void MinimizeWindow()`

  ...

* `bool IsConnecting()`

  ...

* `bool IsConnected()`

  ...

* `ident DeferredCall(uint delay, ScriptFunc-void func)`

  ...

* `ident DeferredCall(uint delay, ScriptFunc-void, any func, any value)`

  ...

* `ident DeferredCall(uint delay, ScriptFunc-void, any[] func, any[] values)`

  ...

* `ident RepeatingDeferredCall(uint delay, ScriptFunc-void func)`

  ...

* `ident RepeatingDeferredCall(uint delay, ScriptFunc-void, any func, any value)`

  ...

* `ident RepeatingDeferredCall(uint delay, ScriptFunc-void, any[] func, any[] values)`

  ...

* `bool IsDeferredCallPending(ident id)`

  ...

* `bool CancelDeferredCall(ident id)`

  ...

* `uint GetDistance(Critter cr1, Critter cr2) ExcludeInSingleplayer`

  ...

* `uint GetTick()`

  ...

* `string CustomCall(string command)`

  ...

* `string CustomCall(string command, string separator)`

  ...

* `Critter GetChosen()`

  ...

* `Item GetItem(ident itemId) ExcludeInSingleplayer`

  ...

* `Critter GetCritter(ident crId) ExcludeInSingleplayer`

  ...

* `Critter[] GetCritters(CritterFindType findType) ExcludeInSingleplayer`

  ...

* `Critter[] GetCritters(hstring pid, CritterFindType findType) ExcludeInSingleplayer`

  ...

* `Critter[] SortCrittersByDeep(Critter[] critters) ExcludeInSingleplayer`

  ...

* `void FlushScreen(ucolor fromColor, ucolor toColor, tick_t duration)`

  ...

* `void QuakeScreen(int noise, tick_t duration)`

  ...

* `bool PlaySound(string soundName)`

  ...

* `bool PlayMusic(string musicName, tick_t repeatTime)`

  ...

* `void PlayVideo(string videoName, bool canInterrupt, bool enqueue)`

  ...

* `bool IsVideoPlaying()`

  ...

* `VideoPlayback CreateVideoPlayback(string videoName, bool looped) PassOwnership`

  ...

* `void DrawVideoPlayback(VideoPlayback video, int x, int y, int width, int height)`

  ...

* `void ConsoleMessage(string msg)`

  ...

* `void Message(string msg)`

  ...

* `void Message(int type, string msg)`

  ...

* `void Message(TextPackName textPack, uint strNum)`

  ...

* `void Message(int type, TextPackName textPack, uint strNum)`

  ...

* `string GetText(TextPackName textPack, uint strNum)`

  ...

* `string GetText(TextPackName textPack, uint strNum, uint skipCount)`

  ...

* `uint GetTextNumUpper(TextPackName textPack, uint strNum)`

  ...

* `uint GetTextNumLower(TextPackName textPack, uint strNum)`

  ...

* `uint GetTextCount(TextPackName textPack, uint strNum)`

  ...

* `bool IsTextPresent(TextPackName textPack, uint strNum)`

  ...

* `string ReplaceText(string text, string replace, ObjInfo-1 obj1)`

  ...

* `string FormatTags(string text, string lexems)`

  ...

* `int GetFog(uint16 zoneX, uint16 zoneY) ExcludeInSingleplayer`

  ...

* `tick_t GetFullSecond() ExcludeInSingleplayer`

  ...

* `tick_t EvaluateFullSecond(uint16 year, uint16 month, uint16 day, uint16 hour, uint16 minute, uint16 second) ExcludeInSingleplayer`

  ...

* `void EvaluateGameTime(tick_t serverTime, uint16& year, uint16& month, uint16& day, uint16& dayOfWeek, uint16& hour, uint16& minute, uint16& second) ExcludeInSingleplayer`

  ...

* `void Preload3dFiles(string[] fnames)`

  ...

* `void LoadFont(int fontIndex, string fontFname)`

  ...

* `void SetDefaultFont(int font)`

  ...

* `void SetEffect(EffectType effectType, int64 effectSubtype, string effectPath)`

  ...

* `void SimulateMouseClick(int x, int y, MouseButton button)`

  ...

* `void SimulateKeyboardPress(KeyCode key1, KeyCode key2, string key1Text, string key2Text)`

  ...

* `void GetTime(uint16& year, uint16& month, uint16& day, uint16& dayOfWeek, uint16& hour, uint16& minute, uint16& second, uint16& milliseconds) ExcludeInSingleplayer`

  ...

* `uint LoadSprite(string sprName)`

  ...

* `uint LoadSprite(hstring nameHash)`

  ...

* `uint LoadMapSprite(string sprName)`

  ...

* `uint LoadMapSprite(hstring nameHash)`

  ...

* `void FreeSprite(uint sprId)`

  ...

* `int GetSpriteWidth(uint sprId)`

  ...

* `int GetSpriteHeight(uint sprId)`

  ...

* `bool IsSpriteHit(uint sprId, int x, int y)`

  ...

* `void StopSprite(uint sprId)`

  ...

* `void SetSpriteTime(uint sprId, float normalizedTime)`

  ...

* `void PlaySprite(uint sprId, hstring animName, bool looped, bool reversed)`

  ...

* `void GetTextInfo(string text, int width, int height, int font, uint flags, int& resultWidth, int& resultHeight, int& resultLines)`

  ...

* `int GetTextLines(int width, int height, int font)`

  ...

* `void DrawSprite(uint sprId, int x, int y)`

  ...

* `void DrawSprite(uint sprId, int x, int y, ucolor color)`

  ...

* `void DrawSprite(uint sprId, int x, int y, ucolor color, bool offs)`

  ...

* `void DrawSprite(uint sprId, int x, int y, int w, int h)`

  ...

* `void DrawSprite(uint sprId, int x, int y, int w, int h, ucolor color)`

  ...

* `void DrawSprite(uint sprId, int x, int y, int w, int h, ucolor color, bool zoom, bool offs)`

  ...

* `void DrawSpritePattern(uint sprId, int x, int y, int w, int h, int sprWidth, int sprHeight, ucolor color)`

  ...

* `void DrawText(string text, int x, int y, int w, int h, ucolor color, int font, uint flags)`

  ...

* `void DrawPrimitive(int primitiveType, int[] data)`

  ...

* `void DrawCritter2d(hstring modelName, CritterStateAnim stateAnim, CritterActionAnim actionAnim, uint8 dir, int l, int t, int r, int b, bool scratch, bool center, ucolor color)`

  ...

* `void DrawCritter3d(uint instance, hstring modelName, CritterStateAnim stateAnim, CritterActionAnim actionAnim, int[] layers, float[] position, ucolor color)`

  ...

* `void PushDrawScissor(int x, int y, int w, int h)`

  ...

* `void PopDrawScissor()`

  ...

* `void ActivateOffscreenSurface(bool forceClear)`

  ...

* `void PresentOffscreenSurface(int effectSubtype)`

  ...

* `void PresentOffscreenSurface(int effectSubtype, int x, int y, int w, int h)`

  ...

* `void PresentOffscreenSurface(int effectSubtype, int fromX, int fromY, int fromW, int fromH, int toX, int toY, int toW, int toH)`

  ...

* `void ShowScreen(int screen)`

  ...

* `void ShowScreen(int screen, string=>any data)`

  ...

* `void HideScreen()`

  ...

* `void HideScreen(int screen)`

  ...

* `void SaveScreenshot(string filePath)`

  ...

* `void SaveText(string filePath, string text)`

  client->SprMngr.SaveTexture(nullptr, strex(filePath).formatPath(), true);

* `void SetCacheData(string name, uint8[] data)`

  ...

* `void SetCacheData(string name, uint8[] data, uint dataSize)`

  ...

* `uint8[] GetCacheData(string name)`

  ...

* `void SetCacheText(string name, string str)`

  ...

* `string GetCacheText(string name)`

  ...

* `bool IsCacheEntry(string name)`

  ...

* `void RemoveCacheEntry(string name)`

  ...

* `void SetUserConfig(string=>string keyValues)`

  ...

* `void SetUserConfig(string[] keyValues)`

  ...

* `void SetMousePos(int x, int y)`

  ...

* `void ChangeLanguage(string langName)`

  ...

* `void FlashUnfocusedWindow()`

  ...

* `void Login(string login, string password)`

  ...

* `void Register(string login, string password)`

  ...

* `void Connect()`

  ...

* `void Disconnect()`

  ...

* `string BuiltInCommand(string command)`

  ...

* `void SetScreenKeyboard(bool enabled)`

  ...

### Game mapper events

* `OnConsoleMessage(string& text)`

  ...

* `OnEditMapLoad(Map map)`

  ...

* `OnEditMapSave(Map map)`

  ...

* `OnInspectorProperties(Entity entity, int[]& properties)`

  ...

### Game mapper methods

* `Item AddItem(hstring pid, uint16 hx, uint16 hy)`

  ...

* `Critter AddCritter(hstring pid, uint16 hx, uint16 hy)`

  ...

* `Item GetItem(uint16 hx, uint16 hy)`

  ...

* `Item[] GetItems(uint16 hx, uint16 hy)`

  ...

* `Critter GetCritter(uint16 hx, uint16 hy, CritterFindType findType)`

  ...

* `Critter[] GetCritters(uint16 hx, uint16 hy, CritterFindType findType)`

  ...

* `void MoveEntity(Entity entity, uint16 hx, uint16 hy)`

  ...

* `void DeleteEntity(Entity entity)`

  ...

* `void DeleteEntities(Entity[] entities)`

  ...

* `void SelectEntity(Entity entity, bool set)`

  ...

* `void SelectEntities(Entity[] entities, bool set)`

  ...

* `Entity GetSelectedEntity()`

  ...

* `Entity[] GetSelectedEntities()`

  ...

* `Item AddTile(hstring pid, uint16 hx, uint16 hy, int layer, bool roof)`

  ...

* `Map LoadMap(string fileName)`

  ...

* `void UnloadMap(Map map)`

  ...

* `void SaveMap(Map map, string customName)`

  ...

* `void ShowMap(Map map)`

  ...

* `Map[] GetLoadedMaps(int& index)`

  ...

* `string[] GetMapFileNames(string dir)`

  ...

* `void ResizeMap(uint16 width, uint16 height)`

  ...

* `hstring[] TabGetItemPids(int tab, string subTab)`

  ...

* `hstring[] TabGetCritterPids(int tab, string subTab)`

  ...

* `void TabSetItemPids(int tab, string subTab, hstring[] itemPids)`

  ...

* `void TabSetCritterPids(int tab, string subTab, hstring[] critterPids)`

  ...

* `void TabDelete(int tab)`

  ...

* `void TabSelect(int tab, string subTab, bool show)`

  ...

* `void TabSetName(int tab, string tabName)`

  ...

* `string GetIfaceIniStr(string key)`

  ...

## Player entity

  ...

* `Target: Server/Client`
* `Built-in: Yes`
* `Singleton: No`
* `Has proto: No`
* `Has statics: No`
* `Has abstract: No`

### Player properties

* `PrivateCommon ident CustomHolderId ReadOnly IsCommon`

  ...

* `PrivateCommon hstring CustomHolderEntry ReadOnly IsCommon`

  ...

* `PrivateServer ident[] InnerEntityIds ReadOnly IsCommon`

  ...

* `PrivateServer ident ControlledCritterId ReadOnly Temporary`

  ...

* `PrivateServer ident LastControlledCritterId ReadOnly`

  ...

* `PrivateServer string Password`

  ...

* `PrivateServer uint[] ConnectionIp`

  ...

* `PrivateServer uint16[] ConnectionPort`

  ...

* `PrivateServer ident MainCritterId`

  Author: cvet

### Player server events

* `OnGetAccess(int arg1, string& arg2)`

  ...

* `OnAllowCommand(string arg1, uint8 arg2)`

  ...

* `OnLogout()`

  ...

### Player server methods

* `void SwitchCritter(Critter cr) ExcludeInSingleplayer`

  ...

* `Critter GetControlledCritter() ExcludeInSingleplayer`

  ...

* `int GetAccess()`

  ...

* `bool SetAccess(int access)`

  ...

* `void Message(string text)`

  ...

* `void Message(TextPackName textPack, uint numStr)`

  ...

* `void Message(TextPackName textPack, uint numStr, string lexems)`

  ...

* `bool IsWebConnected()`

  ...

## Item entity

  ...

* `Target: Server/Client`
* `Built-in: Yes`
* `Singleton: No`
* `Has proto: Yes`
* `Has statics: Yes`
* `Has abstract: Yes`

### Item properties

* `PrivateCommon ident CustomHolderId ReadOnly IsCommon`

  ...

* `PrivateCommon hstring CustomHolderEntry ReadOnly IsCommon`

  ...

* `PrivateServer ident[] InnerEntityIds ReadOnly IsCommon`

  ...

* `PrivateServer hstring InitScript ScriptFuncType = ItemInit`

  ...

* `PrivateServer hstring StaticScript ScriptFuncType = ItemStatic`

  ...

* `PrivateCommon bool Static ReadOnly`

  ...

* `PrivateCommon ItemOwnership Ownership ReadOnly`

  ...

* `PrivateCommon ident MapId ReadOnly`

  ...

* `PrivateCommon uint16 HexX ReadOnly`

  ...

* `PrivateCommon uint16 HexY ReadOnly`

  ...

* `PrivateCommon ident CritterId ReadOnly`

  ...

* `PrivateCommon CritterItemSlot CritterSlot ReadOnly`

  ...

* `PrivateCommon ident ContainerId ReadOnly`

  ...

* `PrivateCommon ContainerItemStack ContainerStack ReadOnly`

  ...

* `PrivateServer ident[] InnerItemIds ReadOnly`

  ...

* `PrivateCommon bool Stackable ReadOnly`

  ...

* `Public uint Count`

  ...

* `Public hstring PicMap Resource`

  ...

* `Public int16 OffsetX`

  ...

* `Public int16 OffsetY`

  ...

* `PrivateCommon CornerType Corner ReadOnly`

  ...

* `PrivateCommon bool DisableEgg ReadOnly`

  ...

* `PrivateCommon uint8[] BlockLines ReadOnly`

  ...

* `PrivateCommon bool ScrollBlock ReadOnly`

  ...

* `PrivateServer bool Hidden`

  ...

* `PrivateClient bool HideSprite`

  ...

* `PrivateCommon bool AlwaysHideSprite ReadOnly`

  ...

* `PrivateCommon bool HiddenInStatic ReadOnly`

  ...

* `Public bool NoBlock`

  ...

* `Public bool ShootThru`

  ...

* `Public bool LightThru`

  ...

* `Public bool AlwaysView`

  ...

* `Public bool LightSource`

  ...

* `Public int8 LightIntensity`

  ...

* `Public uint8 LightDistance`

  ...

* `Public uint8 LightFlags`

  ...

* `Public ucolor LightColor`

  ...

* `PrivateServer hstring TriggerScript ScriptFuncType = ItemTrigger`

  Todo: exclude item properties from engine:

* `Public bool IsTrigger`

  ...

* `Public hstring PicInv Resource`

  ...

* `PrivateCommon float FlyEffectSpeed ReadOnly`

  ...

* `PrivateCommon bool IsScenery ReadOnly`

  ...

* `PrivateCommon bool IsWall ReadOnly`

  ...

* `PrivateCommon bool IsTile ReadOnly`

  ...

* `PrivateCommon bool IsRoofTile ReadOnly`

  ...

* `PrivateCommon uint8 TileLayer ReadOnly`

  ...

* `PrivateCommon bool DrawFlatten ReadOnly`

  ...

* `PrivateCommon int8 DrawOrderOffsetHexY ReadOnly`

  ...

* `Public bool BadItem`

  ...

* `Public bool NoHighlight`

  ...

* `Public bool NoLightInfluence`

  ...

* `Public bool IsGag`

  ...

* `Public bool Colorize`

  ...

* `Public string Lexems`

  ...

* `PublicModifiable int16 SortValue`

  ...

* `Public bool IsTrap`

  ...

* `Protected int16 TrapValue`

  ...

* `Public bool IsRadio`

  ...

* `Protected uint16 RadioChannel`

  ...

* `Protected uint16 RadioFlags`

  ...

* `Protected uint8 RadioBroadcastSend`

  ...

* `Protected uint8 RadioBroadcastRecv`

  ...

* `PrivateCommon bool CanOpen ReadOnly`

  ...

* `Public bool Opened`

  ...

* `Public ucolor ColorizeColor`

  ...

* `PrivateServer bool CarIsBioEngine`

  ...

* `PrivateServer bool CarIsNoLockpick`

  ...

* `PrivateServer ident CaravanCabLeaderId`

  ...

* `PrivateServer uint ELockCloseAtSeconds`

  Время автоматического закрытия контейнера или двери

* `PrivateServer string ELockCode`

  ...

* `PrivateServer ident ExplodeInvokeId`

  Author: cvet, rifleman17

* `PrivateServer ident ExplodeSwitcherExplodeId`

  ...

* `PrivateServer ident ExplodeOwnerId`

  ...

* `PrivateServer int ExplodeBonusDamage`

  ...

* `PrivateServer int ExplodeBonusRadius`

  ...

* `PrivateServer uint ExplodeTimeRespawnMine`

  ...

* `PrivateServer uint GECachesNumParameters`

  Author rifleman17  
  Энкаунтер квест, периодически доступный. В караванах попадается охранник, который за деньги продает карту с координатами запертого ящика.

* `PrivateServer bool GeigerEnabled`

  ...

* `PrivateServer int GeigerCapacity`

  ...

* `PrivateServer ident GeigerTimeEvent`

  ...

* `PrivateServer uint QHunterCountFluteUse`

  ...

* `PrivateServer uint DoorAutoCloseTime`

  ...

* `PrivateServer hstring DoorAutoDialog`

  ...

* `PrivateServer bool IsGeck`

  ...

* `Protected uint LockerId`

  Author: cvet  
  Doors and keys stuff.  
  Lockers and doors

* `PrivateServer uint16 LockerComplexity`

  ...

* `Public bool Locker_Locked`

  ...

* `Public bool Locker_Jammed`

  ...

* `Public bool Locker_Broken`

  ...

* `Public bool Locker_NoOpen`

  ...

* `Public bool Locker_IsElectro`

  ...

* `Public bool Door_NoBlockMove`

  ...

* `Public bool Door_NoBlockShoot`

  ...

* `Public bool Door_NoBlockLight`

  ...

* `Public uint Container_Volume`

  ...

* `Public bool Container_Changeble`

  ...

* `Public bool Container_CannotPickUp`

  ...

* `PrivateServer bool Door_IsMultyHex`

  MultihexDoors не используется нигде.

* `PrivateServer uint8[] Door_MultyHexLine1`

  ...

* `PrivateServer uint8[] Door_MultyHexLine2`

  ...

* `PrivateServer uint[] Door_BlockerIds`

  ...

* `PrivateServer uint NavarroCountUseScaner`

  ...

* `PrivateServer hstring NCRPostmanLocPidStart`

  ...

* `PrivateServer hstring NCRPostmanLocPidRec`

  ...

* `PrivateServer hstring NCRPostmanMapPidRec`

  ...

* `PrivateServer hstring NCRPostmanNpcDidRec`

  ...

* `PrivateServer ident NCRPostmanPlayerID`

  ...

* `PrivateServer ident PetId`

  ...

* `PrivateServer hstring PetProto`

  ...

* `PrivateServer hstring PosterSNWall`

  Author: rifleman17  
  Постеры, которые можно вешать на стену  
  Игрок использует свернутый плакат в инвентаре, если стоит на нужном гексе, то на стену рядом вешается плакат  
  Гексы расставил Dagnir на картах личных складов

* `PrivateServer hstring PosterEWWall`

  ...

* `PrivateServer ident RatGrenadeInvokeId`

  ...

* `PrivateServer any[] ReddGatesGoodList`

  Author: rifleman17

* `PrivateServer any[] ReddGatesBadList`

  ...

* `PrivateServer uint8 RespawnItemMode`

  Самовосстанавлиающийся итем  
  аргументы:  
  RespTime время респауна в игровых минутах (RespawnItemRespTime)  
  Mode - режим респауна. (RespawnItemMode)  
  0 - в том же месте,  
  1 - в инвентаре НПЦ на той же карте,  
  2 - в контейнере на той же карте  
  3+ - если режим>2, то итем располагается гденибудь неподалеку от гекса с таким номером  
  респауну подвержены только итемы типов: Armor, Drug, Weapon, Misc, Key  
  Eсть дополнительная возможность указать номер переменной (поле RespawnItemVarNum), чье значение будет проверяться при попытке поднять итем  
  если значение переменной = 1, предмет будет поднят и после этого переменная будет установлена в 0

* `PrivateServer uint RespawnItemRespTime`

  ...

* `PrivateServer uint RespawnItemVarNum`

  ...

* `PrivateServer bool SeAndroidRadioListened`

  ...

* `PrivateServer LocationProperty SeAndroidVarNum`

  ...

* `PrivateServer ident SmokeGrenadeOwnerId`

  Author: rifleman17

* `PrivateCommon uint Weight`

  ...

* `PrivateCommon uint Volume`

  ...

* `PrivateCommon bool GroundLevel`

  ...

* `PrivateCommon bool IsShowAnim`

  ...

* `PrivateCommon bool IsShowAnimExt`

  ...

* `PrivateCommon bool IsCanTalk`

  ...

* `ProtectedModifiable uint8 Mode`

  ...

* `Public uint8 AnimHide0`

  ...

* `Public uint8 AnimHide1`

  ...

* `Public uint8 AnimShow0`

  ...

* `Public uint8 AnimShow1`

  ...

* `Public uint8 AnimStay0`

  ...

* `Public uint8 AnimStay1`

  ...

* `Public uint16 AnimWaitBase`

  ...

* `Public uint16 AnimWaitRndMax`

  ...

* `Public uint16 AnimWaitRndMin`

  ...

* `Public hstring Armor_CrTypeMale Group = Armor`

  Item  
  Armor

* `Public hstring Armor_CrTypeFemale Group = Armor`

  ...

* `Public int Armor_AC Group = Armor`

  ...

* `Public uint Armor_Perk Group = Armor`

  ...

* `Public int Armor_DRNormal Group = Armor`

  ...

* `Public int Armor_DRLaser Group = Armor`

  ...

* `Public int Armor_DRFire Group = Armor`

  ...

* `Public int Armor_DRPlasma Group = Armor`

  ...

* `Public int Armor_DRElectr Group = Armor`

  ...

* `Public int Armor_DREmp Group = Armor`

  ...

* `Public int Armor_DRExplode Group = Armor`

  ...

* `Public int Armor_DTNormal Group = Armor`

  ...

* `Public int Armor_DTLaser Group = Armor`

  ...

* `Public int Armor_DTFire Group = Armor`

  ...

* `Public int Armor_DTPlasma Group = Armor`

  ...

* `Public int Armor_DTElectr Group = Armor`

  ...

* `Public int Armor_DTEmp Group = Armor`

  ...

* `Public int Armor_DTExplode Group = Armor`

  ...

* `Public bool Weapon_IsUnarmed Group = WeaponUnarmed`

  Weapon unarmed

* `Public int Weapon_UnarmedTree Group = WeaponUnarmed`

  ...

* `Public int Weapon_UnarmedPriority Group = WeaponUnarmed`

  ...

* `Public int Weapon_UnarmedMinAgility Group = WeaponUnarmed`

  ...

* `Public int Weapon_UnarmedMinUnarmed Group = WeaponUnarmed`

  ...

* `Public int Weapon_UnarmedMinLevel Group = WeaponUnarmed`

  ...

* `Public uint Weapon_MaxAmmoCount Group = WeaponAmmo`

  Weapon Ammo

* `Public Caliber Weapon_Caliber Group = WeaponAmmo`

  ...

* `Public hstring Weapon_DefaultAmmoPid Group = WeaponAmmo`

  ...

* `Public CritterStateAnim Weapon_StateAnim Group = WeaponProperties`

  Weapon properties

* `Public int Weapon_MinStrength Group = WeaponProperties`

  ...

* `Public ItemPerks Weapon_Perk Group = WeaponProperties`

  ...

* `Public bool Weapon_IsTwoHanded Group = WeaponProperties`

  ...

* `Public uint Weapon_ActiveUses Group = WeaponProperties`

  ...

* `Public CritterProperty Weapon_Skill_0 Group = WeaponModes`

  Weapon modes

* `Public CritterProperty Weapon_Skill_1 Group = WeaponModes`

  ...

* `Public CritterProperty Weapon_Skill_2 Group = WeaponModes`

  ...

* `Public hstring Weapon_PicUse_0 Group = WeaponModes`

  ...

* `Public hstring Weapon_PicUse_1 Group = WeaponModes`

  ...

* `Public hstring Weapon_PicUse_2 Group = WeaponModes`

  ...

* `Public uint Weapon_MaxDist_0 Group = WeaponModes`

  ...

* `Public uint Weapon_MaxDist_1 Group = WeaponModes`

  ...

* `Public uint Weapon_MaxDist_2 Group = WeaponModes`

  ...

* `Public uint Weapon_Round_0 Group = WeaponModes`

  ...

* `Public uint Weapon_Round_1 Group = WeaponModes`

  ...

* `Public uint Weapon_Round_2 Group = WeaponModes`

  ...

* `Public uint Weapon_ApCost_0 Group = WeaponModes`

  ...

* `Public uint Weapon_ApCost_1 Group = WeaponModes`

  ...

* `Public uint Weapon_ApCost_2 Group = WeaponModes`

  ...

* `Public bool Weapon_Aim_0 Group = WeaponModes`

  ...

* `Public bool Weapon_Aim_1 Group = WeaponModes`

  ...

* `Public bool Weapon_Aim_2 Group = WeaponModes`

  ...

* `Public uint8 Weapon_SoundId_0 Group = WeaponModes`

  ...

* `Public uint8 Weapon_SoundId_1 Group = WeaponModes`

  ...

* `Public uint8 Weapon_SoundId_2 Group = WeaponModes`

  ...

* `Public DamageTypes Weapon_DmgType_0 Group = WeaponModes`

  ...

* `Public DamageTypes Weapon_DmgType_1 Group = WeaponModes`

  ...

* `Public DamageTypes Weapon_DmgType_2 Group = WeaponModes`

  ...

* `Public CritterActionAnim Weapon_ActionAnim_0 Group = WeaponModes`

  ...

* `Public CritterActionAnim Weapon_ActionAnim_1 Group = WeaponModes`

  ...

* `Public CritterActionAnim Weapon_ActionAnim_2 Group = WeaponModes`

  ...

* `Public int Weapon_DmgMin_0 Group = WeaponModes`

  ...

* `Public int Weapon_DmgMin_1 Group = WeaponModes`

  ...

* `Public int Weapon_DmgMin_2 Group = WeaponModes`

  ...

* `Public int Weapon_DmgMax_0 Group = WeaponModes`

  ...

* `Public int Weapon_DmgMax_1 Group = WeaponModes`

  ...

* `Public int Weapon_DmgMax_2 Group = WeaponModes`

  ...

* `Public bool Weapon_Remove_0 Group = WeaponModes`

  ...

* `Public bool Weapon_Remove_1 Group = WeaponModes`

  ...

* `Public bool Weapon_Remove_2 Group = WeaponModes`

  ...

* `Public hstring Weapon_Effect_0 Group = WeaponModes`

  ...

* `Public hstring Weapon_Effect_1 Group = WeaponModes`

  ...

* `Public hstring Weapon_Effect_2 Group = WeaponModes`

  ...

* `Public uint Weapon_ReloadAp Group = WeaponProperties`

  Weapon properties

* `Public int Weapon_UnarmedCriticalBonus Group = WeaponProperties`

  ...

* `Public uint Weapon_CriticalFailture Group = WeaponProperties`

  ...

* `Public bool Weapon_UnarmedArmorPiercing Group = WeaponProperties`

  ...

* `Public Caliber Ammo_Caliber Group = Ammo`

  Ammo

* `Public int Ammo_AcMod Group = Ammo`

  ...

* `Public int Ammo_DrMod Group = Ammo`

  ...

* `Public uint Ammo_DmgMult Group = Ammo`

  ...

* `Public uint Ammo_DmgDiv Group = Ammo`

  ...

* `Public uint Car_Speed Group = Car`

  Car

* `Public uint Car_Passability Group = Car`

  ...

* `Public uint Car_DeteriorationRate Group = Car`

  ...

* `Public uint Car_CrittersCapacity Group = Car`

  ...

* `Public uint Car_TankVolume Group = Car`

  ...

* `Public uint Car_MaxDeterioration Group = Car`

  ...

* `Public uint Car_FuelConsumption Group = Car`

  ...

* `Public uint Car_Entrance Group = Car`

  ...

* `Public uint Car_MovementType Group = Car`

  ...

* `Public bool Deteriorable Group = Deterioration`

  Deterioration

* `Protected bool IsBroken Group = Deterioration`

  ...

* `Protected bool BrokenEternal Group = Deterioration`

  ...

* `Protected bool BrokenLowBroken Group = Deterioration`

  ...

* `Protected bool BrokenNormBroken Group = Deterioration`

  ...

* `Protected bool BrokenHighBroken Group = Deterioration`

  ...

* `Protected bool BrokenNotresc Group = Deterioration`

  ...

* `Protected bool BrokenService Group = Deterioration`

  ...

* `Protected bool BrokenServiceExt Group = Deterioration`

  ...

* `Protected uint BrokenCount Group = Deterioration`

  ...

* `Protected uint Deterioration Group = Deterioration`

  ...

* `Public uint16 LockerCondition`

  ...

* `PrivateServer bool IsLockpick`

  ...

* `PrivateServer uint8 Lockpick_Points`

  ...

* `PrivateServer bool Lockpick_IsElectro`

  ...

* `Public bool IsHolodisk`

  ...

* `Protected uint HolodiskNum`

  ...

* `Public bool IsNoLoot`

  ...

* `Public bool IsNoSteal`

  ...

* `Public any Val0`

  ...

* `Public any Val1`

  ...

* `Public any Val2`

  ...

* `Public any Val3`

  ...

* `Public any Val4`

  ...

* `Public any Val5`

  ...

* `Public any Val6`

  ...

* `Public any Val7`

  ...

* `Public any Val8`

  ...

* `Public any Val9`

  ...

* `Public string ScriptModule`

  ...

* `Public string ScriptFunc`

  ...

* `Protected uint8 BrokenFlags`

  ...

* `Protected uint Cost`

  ...

* `Public uint8 SoundId`

  ...

* `Public uint8 Material`

  ...

* `Protected hstring AmmoPid`

  все это скорее всего не работает

* `Protected uint AmmoCount`

  ...

* `Public int8 Info`

  ...

* `Public bool IsCanUseOnSmth`

  ...

* `Public bool IsCanUse`

  ...

* `Public bool IsCanPickUp`

  ...

* `PrivateServer uint LastUsedTime`

  ...

* `PrivateServer bool IsQuestItem`

  ...

* `Protected uint8 Indicator`

  ...

* `Public uint8 IndicatorMax`

  ...

* `Protected uint16 Charge`

  ...

* `Public bool IsCanLook`

  items

* `Public bool IsWallTransEnd`

  ...

* `Public bool IsHasTimer`

  ...

* `Public bool IsBigGun`

  ...

* `Public bool IsMultiHex`

  ...

* `Public hstring ChildPid_0`

  child

* `Public hstring ChildPid_1`

  ...

* `Public hstring ChildPid_2`

  ...

* `Public hstring ChildPid_3`

  ...

* `Public hstring ChildPid_4`

  ...

* `Public string ChildLines_0`

  ...

* `Public string ChildLines_1`

  ...

* `Public string ChildLines_2`

  ...

* `Public string ChildLines_3`

  ...

* `Public string ChildLines_4`

  ...

* `Public ItemType Type`

  ...

* `PrivateServer int TriggerNum`

  ...

* `Public bool Container_MagicHandsGrnd`

  ...

* `Public int Grid_Type`

  ...

* `PrivateServer hstring Grid_ToMap`

  ...

* `PrivateServer hstring Grid_ToMapEntry`

  ...

* `PrivateServer uint8 Grid_ToMapDir`

  ...

* `PrivateServer hstring[] SceneryParams`

  ...

* `PrivateServer ident V13GorisEggPlayerId`

  ...

* `PrivateServer bool VCityCommonIsMail`

  ...

* `PrivateServer ident VCityCommonMailOwnerId`

  ...

### Item server events

* `OnFinish()`

  ...

* `OnCritterWalk(Critter critter, bool isIn, uint8 dir)`

  ...

* `OnCritterMove(Critter cr, CritterItemSlot fromSlot)`

  ...

* `OnCritterDrop(Critter cr)`

  ...

* `OnCritterUse(Critter cr, uint param)`

  ...

* `OnCritterUseOn(Critter cr, Critter onCritter, Item onItem, StaticItem onScenery, uint param)`

  ...

* `OnCritterUseOnSelf(Critter cr, Item usedItem, uint param)`

  ...

* `OnCritterUseSkill(Critter cr, CritterProperty skill)`

  ...

* `OnCritterAttack(Critter cr, Critter target, uint8 weaponMode, ProtoItem ammo)`

  ...

### Item server methods

* `void SetupScript(init-Item initFunc)`

  ...

* `void SetupScriptEx(hstring initFunc)`

  ...

* `Item AddItem(hstring pid, uint count, ContainerItemStack stackId)`

  ...

* `Item[] GetItems(ContainerItemStack stackId)`

  ...

* `Map GetMap()`

  ...

* `Map GetMapPosition(uint16& hx, uint16& hy)`

  ...

* `void Animate(hstring animName, bool looped, bool reversed) ExcludeInSingleplayer`

  ...

### Item client methods

* `Item Clone()`

  ...

* `Item Clone(uint count)`

  ...

* `void GetMapPos(uint16& hx, uint16& hy) ExcludeInSingleplayer`

  ...

* `void PlayAnim(hstring animName, bool looped, bool reversed)`

  ...

* `void StopAnim()`

  ...

* `void SetAnimTime(float normalizedTime)`

  ...

* `Item[] GetInnerItems() ExcludeInSingleplayer`

  ...

* `uint8 GetAlpha()`

  ...

* `void SetAlpha(uint8 alpha)`

  ...

## Critter entity

  ...

* `Target: Server/Client`
* `Built-in: Yes`
* `Singleton: No`
* `Has proto: Yes`
* `Has statics: No`
* `Has abstract: No`

### Critter properties

* `PrivateCommon ident CustomHolderId ReadOnly IsCommon`

  ...

* `PrivateCommon hstring CustomHolderEntry ReadOnly IsCommon`

  ...

* `PrivateServer ident[] InnerEntityIds ReadOnly IsCommon`

  ...

* `PrivateServer hstring InitScript ScriptFuncType = CritterInit`

  ...

* `PrivateServer ident MapId ReadOnly`

  ...

* `PrivateServer uint GlobalMapTripId ReadOnly Temporary`

  ...

* `PrivateCommon uint16 HexX ReadOnly`

  ...

* `PrivateCommon uint16 HexY ReadOnly`

  ...

* `PrivateCommon int16 HexOffsX ReadOnly`

  ...

* `PrivateCommon int16 HexOffsY ReadOnly`

  ...

* `PrivateCommon uint8 Dir ReadOnly`

  ...

* `PrivateCommon int16 DirAngle ReadOnly`

  ...

* `PrivateServer ident[] ItemIds ReadOnly`

  ...

* `Public hstring ModelName Resource`

  ...

* `Protected uint Multihex ReadOnly`

  ...

* `PrivateCommon CritterStateAnim AliveStateAnim ReadOnly`

  ...

* `PrivateCommon CritterStateAnim KnockoutStateAnim ReadOnly`

  ...

* `PrivateCommon CritterStateAnim DeadStateAnim ReadOnly`

  ...

* `PrivateCommon CritterActionAnim AliveActionAnim ReadOnly`

  ...

* `PrivateCommon CritterActionAnim KnockoutActionAnim ReadOnly`

  ...

* `PrivateCommon CritterActionAnim DeadActionAnim ReadOnly`

  ...

* `Public int ScaleFactor`

  ...

* `PrivateServer uint ShowCritterDist1`

  ...

* `PrivateServer uint ShowCritterDist2`

  ...

* `PrivateServer uint ShowCritterDist3`

  ...

* `PrivateClient int[] ModelLayers Temporary`

  ...

* `PrivateServer any[] TE_Identifier ReadOnly`

  ...

* `PrivateServer tick_t[] TE_FireTime ReadOnly`

  ...

* `PrivateServer hstring[] TE_FuncName ReadOnly`

  ...

* `PrivateServer uint[] TE_Rate ReadOnly`

  ...

* `PrivateServer uint IdlePeriod Temporary`

  ...

* `PrivateCommon bool ControlledByPlayer ReadOnly Temporary`

  ...

* `PrivateClient bool IsChosen ReadOnly Temporary`

  ...

* `PrivateClient bool IsPlayerOffline ReadOnly Temporary`

  ...

* `PrivateCommon bool IsAttached ReadOnly Temporary`

  ...

* `PrivateCommon ident AttachMaster ReadOnly Temporary`

  ...

* `PrivateClient bool HideSprite`

  ...

* `PrivateServer int MovingSpeed ReadOnly Temporary`

  ...

* `PrivateClient bool SexTagFemale`

  Todo: exclude critter properties from engine:

* `PrivateClient bool ModelInCombatMode`

  ...

* `Protected uint16 WorldX`

  ...

* `Protected uint16 WorldY`

  ...

* `PrivateCommon CritterCondition Condition ReadOnly`

  ...

* `PrivateClient int16 NameOffset`

  ...

* `PrivateServer uint8[] GlobalMapFog ReadOnly`

  ...

* `PrivateServer uint SneakCoefficient`

  ...

* `Protected uint LookDistance`

  ...

* `Public uint TalkDistance`

  ...

* `PrivateServer uint MaxTalkers`

  ...

* `Public hstring DialogId`

  ...

* `Public string Lexems`

  ...

* `PrivateServer ident[] KnownLocations`

  ...

* `Protected bool InSneakMode`

  ...

* `Public bool DeadDrawNoFlatten`

  ...

* `PrivateClient ucolor NameColor`

  ...

* `PrivateClient ucolor ContourColor`

  ...

* `PrivateServer ident ArroyoRaydersAttackedId`

  Name:   arroyo_rayders  
  Author: Sufir

* `PrivateServer ident BehemothOwner`

  Переменная в которой хранится Id владельца

* `PrivateServer int BehemothRadio`

  Переменная в которой хранится номер радиоканала

* `PrivateServer int BehemothLastComand`

  Переменная в которой хранится время последней команды.

* `PrivateServer int BehemothOrderType`

  Тип приказа выполняемого нпц

* `PrivateServer int BehemothLastOrder`

  Переменная в которой хранится время принятия последнего приказа

* `PrivateServer any BehemothParam_1`

  ...

* `PrivateServer any BehemothParam_2`

  ...

* `PrivateServer int BehemothLastReport`

  ...

* `PrivateServer uint8 BHHubHoloRemembered Max = 1`

  Author: rifleman17  
  Квесты Брокен Хиллс  
  Квест "Рога изобилия".

* `PrivateServer uint8 BHUranDiscount Max = 1`

  ...

* `PrivateServer int BBMsgPage`

  Author: rifleman17  
  Доска объявлений с возможностью оставлять сообщения

* `PrivateServer int BBSelectedMsg`

  ...

* `PrivateServer int KlamAldoBusy`

  ...

* `PrivateServer ident KlamAldoListenId`

  ...

* `PrivateServer ident KlamAldoReaderId`

  ...

* `PrivateServer ident=>uint BBMsgCount`

  ...

* `PrivateServer uint CaravanCrvId`

  ...

* `PrivateServer uint8 VCDeadPatrollers Max = 10`

  ...

* `Protected uint8 ReddWadeCaravanEscort Group = Quests Quest = 4300 Max = 11`

  pass

* `Protected uint8 ReddSavinelCaravanEscort Group = Quests Quest = 4301 Max = 11`

  ...

* `Protected uint8 ReddStanCaravanEscort Group = Quests Quest = 4302 Max = 11`

  ...

* `Protected uint8 NcrReddingCaravanEscort Group = Quests Quest = 4244 Max = 11`

  ...

* `Protected uint8 BHKitCaravanEscort Group = Quests Quest = 3600 Max = 11`

  ...

* `Protected uint8 VCShrimPatrol Group = Quests Quest = 8826 Max = 11`

  ...

* `Protected uint8 ArroyoSelmaCaravanEscort Group = Quests Quest = 1807 Max = 11`

  ...

* `Protected uint8 ArroyoGayzumCaravanEscort Group = Quests Quest = 1808 Max = 11`

  ...

* `Protected uint8 ArroyoLaumerCaravanEscort Group = Quests Quest = 1809 Max = 11`

  ...

* `Protected uint8 ModAurelianoCaravanEscort Group = Quests Quest = 3315 Max = 11`

  ...

* `PrivateServer uint8 CommonCrvResetCounter Max = 15`

  ...

* `PrivateServer uint8 ReddCrvResetCounter Max = 9`

  ...

* `PrivateServer uint8 NcrCrvResetCounter Max = 5`

  ...

* `PrivateServer uint8 BHCrvResetCounter Max = 5`

  ...

* `PrivateServer uint8 ArroyoCrvResetCounter Max = 15`

  ...

* `PrivateServer uint CaravanReaction`

  ...

* `PrivateServer uint CaravanNervosityLvl`

  ...

* `PrivateServer uint CaravanIdleCount`

  ...

* `PrivateServer ident=>uint LastSelectedCaravan`

  ...

* `PrivateCommon uint ApRegenerationTick Temporary`

  ...

* `Protected uint ApRegenerationTime`

  ...

* `PrivateServer uint CollectorTimeNextSearch`

  Author: rifleman17  
  Собиратель мусора  
  каждые NEXT_SEARCH_TIME собирает предметы на карте  в радиусе 5*PE от домашней позиции  
  если на карте есть контейнер, расположенный на EntryHex'e с номером ENTRY_CONTAINER, после того, как соберет все предметы, идет их складывать в этот  
  контейнер Внимание! используется ST_VAR0 для определения времени следующего поиска заняты события: CRITTER_EVENT_IDLE, CRITTER_EVENT_PLANE_END

* `PrivateServer ident CompRiddleMapId`

  Переменная ид карты на которой стоит сценери

* `PrivateServer uint CompRiddleHexX`

  Переменная с координатой сценери по оси X

* `PrivateServer uint CompRiddleHexY`

  Переменная с координатой сценери по оси Y

* `PrivateServer uint KnockoutAp`

  ...

* `Protected uint WaitEndTick`

  ...

* `PrivateServer CritterActionAnim ActionAnimKnockoutEnd`

  ...

* `PrivateServer uint8 NcrBusterLostCStatus Max = 4`

  Dappo's Lost Caravan quest Encounter Mob^ battle robot

* `PrivateServer uint8 QDappoLostRobotHexNum`

  ...

* `PrivateServer uint BankMoney Max = 999999`

  ...

* `PrivateServer uint8 DenHubBank5`

  ...

* `PrivateServer uint8 DenHubGuard5`

  ...

* `PrivateServer ident DenPoormanItemId`

  Author: cvet

* `PrivateServer uint8 DenVirginCount`

  Author: Tab10id

* `PrivateServer bool DenVirginIsHome`

  ...

* `PrivateServer ident=>uint UniqTimeout`

  Author: cvet, heX, Тринитротолуол, Tab10id

* `PrivateServer ident=>uint8 Loyality`

  ...

* `PrivateServer ident=>bool NpcStory`

  ...

* `PrivateServer ident=>bool NameMemNpcPlayer`

  ...

* `PrivateServer ident=>bool NameMemPlayerNpc`

  ...

* `PrivateServer ident=>bool TradeWas`

  ...

* `PrivateServer ident=>bool DenKliffBlessWas`

  ...

* `PrivateServer ident=>bool DenVirginiaSexWas`

  ...

* `PrivateServer ident=>bool NcrPlayerTalkPoliceman`

  ...

* `PrivateServer ident=>bool SFLoPanPayed`

  ...

* `PrivateServer ident=>uint8 ChanceOneFromTwo`

  ...

* `PrivateServer ident=>uint8 ChanceOneFromThree`

  ...

* `PrivateServer ident=>uint8 ChanceOneFromFive`

  ...

* `PrivateServer hstring=>uint8 CurrentDialogNumber`

  ...

* `PrivateServer tick_t LastDialogBoxShownTick`

  ...

* `Protected CritterProperty=>int DrugEffects`

  Author: cvet  
  Original Fallout2 system

* `Protected uint8 DoughnutsCounter Max = 20`

  ...

* `PrivateServer ident LastElectronicLocked`

  Author: rifleman17  
  Электронный замок на контейнеры, двери  
  Свойства предмета

* `PrivateServer uint EliTimeNextSing`

  Author rifleman17  
  Странствующий путник, Илай.  
  Может брать с собой одного игрока в качестве спутника  
  Если путника убьет персонаж, у которого есть база, после этого Илай отведет следующего игрока на базу убийцы.  
  не надо ставить его в СФ, иначе не выберется

* `PrivateServer ident[] EnemyStack`

  ...

* `Public bool IsNoEnemyStack`

  ...

* `PrivateServer uint16 EnergyBarierTerminalHx`

  Author: Tab10id  
  Скрипт приписывается итему в прототипе, во время инициализации вокруг итема выставлются итемы, играющие роль триггеров.  
  При переходе через итем-триггер, у игрока проверяется право на проход, если его нет, то в некотором радиусе ищутся охранники,  
  если они найдены, игрок останавливается и начинается диалог с охраной.  
  Под широкими барьерами кладутся дополнительные итемы-блокирующие проход в запертом состоянии.

* `PrivateServer uint16 EnergyBarierTerminalHy`

  ...

* `PrivateServer uint EnergyBarierNetNum`

  ...

* `PrivateServer int EnergyBarierHackBonus`

  ...

* `PrivateServer int EnergyBarierHitBonus`

  ...

* `PrivateServer uint FighterPatternCanGenStim`

  специализированный инструмент для настройки поведения нпц в команде на конкретной карте

* `PrivateServer int FighterPatternAllyAssistRadius`

  ...

* `PrivateServer int FighterPatternAssistAlliesNum`

  ...

* `PrivateServer int FighterPatternMustHealLvl`

  ...

* `PrivateServer int FighterPatternLocalAlarmDeads`

  ...

* `PrivateServer int FighterPatternGlobalAlarmDeads`

  ...

* `PrivateServer int FighterQuestMinHp`

  Author rifleman17  
  Специальный класс для реализации квестов на рукопашный или другой бой с НПЦ  
  только с одним игроком. Cмерть нпц засчитывается победой игрока

* `PrivateServer uint8 FighterQuestOnlyHandCombat`

  ...

* `PrivateServer uint FighterQuestTeamIdOld`

  ...

* `PrivateServer uint FighterQuestTeamIdFight`

  ...

* `PrivateServer ident FighterQuestPlayerId`

  ...

* `PrivateServer uint FighterQuestFightPriority`

  ...

* `PrivateServer uint FighterQuestVarNum`

  ...

* `PrivateServer uint FixboyPowerArmor Max = 1`

  ...

* `PrivateServer uint ModLourenceVenomedratRecipe Max = 1`

  ...

* `PrivateServer uint ModLourenceTNTRatRecipe Max = 1`

  ...

* `PrivateServer uint NavEmpRocketRecipe Max = 1`

  ...

* `PrivateServer uint FixboyDefault Max = 1`

  ...

* `PrivateServer uint SFRecipeSsupersledge Max = 1`

  ...

* `PrivateServer uint SFRecipePlasmagrenades Max = 1`

  ...

* `PrivateServer uint Fixboy700NitroExpress Max = 1`

  ...

* `PrivateServer uint FixboyAmmoPressOperator Max = 1`

  ...

* `PrivateServer uint8 RacingCheckPoints Max = 14`

  ...

* `PrivateServer ident RacingCheckpointLocId`

  ...

* `PrivateServer uint16 GERacingCritterHx`

  ...

* `PrivateServer uint16 GERacingCritterHy`

  ...

* `PrivateServer uint8 GERacingCritterDir`

  ...

* `PrivateServer uint GERacingNpcRole`

  ...

* `PrivateServer uint GERacingOpeningPhrases`

  ...

* `Protected uint8 GEReplExplodeTank Group = Quests Quest = 1826 Max = 4`

  Author: rifleman17

* `Protected uint8 GEReplNopasaran Group = Quests Quest = 1829 Max = 7`

  ...

* `Protected uint8 GEReplFindstation Group = Quests Quest = 1827 Max = 2`

  ...

* `PrivateServer uint8 GEReplNotifictions Max = 3`

  ...

* `PrivateServer uint GEReplEntryZombie`

  ...

* `PrivateServer uint GEReplLastOrder`

  ...

* `PrivateServer bool GEReplIsAddedAttackPlane`

  ...

* `PrivateServer uint HellMineTimeoutEnd`

  ...

* `PrivateServer bool HostileLQIsStoped`

  Author: rifleman17  
  Скрипт для реализации квестов, целью которых является зачистка некоей локации от мобов  
  Особенности:  
  - локация видна одному игроку  
  - если игрок убит, локация не исчезает  
  - если погибли все мобы, локация удаляется, переключается квестовая переменная "выполнено"  
  - на карте может быть несколько нпц-союзников, ведется отсчет погибших, может использоваться в квесте  
  - если игрок погиб, союзники сбрасывают планы атаки "Отступаем! Смена позиции" и уходят на исходную позицию  
  - противники и союзники ставятся на карте маппером, не скриптом, у них указывается соответствующий NPC_ROLE  
  - противникам и союзникам присваевается свой скрипт  
  - все параметры локации и карт прописываются в Maps.cfg, Locations.cfg  
  - все поля и свойства квеста сериализуются  
  - при атаке игроком мобов, защитники присоединяются, если даже игрок с ними не поговорил  
  - удаление локации контролируется таймаутом, при создании карты добавляется таймевент. Через два реальных дня локация будет удалена, статус квестовой  
  переменной будет переключен.  
  - внимание! для всех карт в локации устанавливается специфический скрипт  
  - для каждой карты в локации заняты Map::HostileLQPlayerId - код игрока, выполняющего квест; и Map::HostileLQVarNum - номер квестовой переменной. Чтобы в  
  контексте карты иметь доступ к описанию квеста.  
  TODO:  
  - изменить на групповой квест  
  - обработать убийство игроком союзников после того, как задача квеста выполнена  
  - изменть реализацию поведения криттеров, чтобы они допускали использование своих скриптов

* `PrivateServer uint=>uint8[] HostileLQData`

  ...

* `Protected uint8 SFAhs7Escort Group = Quests Quest = 4434 Max = 3`

  Author: rifleman17  
  Скрипты для квестовой локации "лаборатория хабологов".

* `PrivateServer ident SFHonomerPlayerId`

  ...

* `PrivateServer ident SFEscortLocation`

  ...

* `PrivateServer uint8 SFLabFailed Max = 1`

  ...

* `PrivateServer bool QHubLabIsDialogRun`

  ...

* `Protected uint8 BarterLourensRats1 Group = Quests Quest = 5200 Max = 4`

  Author: rifleman17  
  Квесты цепочки "Лучший охотник Пустоши."

* `Protected uint8 ModLourenceRatsFlute Group = Quests Quest = 3317 Max = 3`

  ...

* `PrivateServer uint8 BarterLourensRatBodycount Max = 11`

  ...

* `PrivateServer uint ModHoughRatsFluteTimeout`

  ...

* `PrivateServer uint ModLourenceToxinTimeout`

  ...

* `PrivateServer uint ModLourenceRatsFluteCounter Max = 5`

  ...

* `PrivateServer uint ModLourenceLureActive`

  ...

* `PrivateServer ident=>uint8 GuardedItemSkill`

  Author: rifleman17

* `Protected int8 V13DclawEggs Group = Quests Quest = 4902 Min = 0 Max = 7`

  Author: Sufir

* `Protected uint8 KlamTorrCowboy Group = Quests Quest = 3213 Max = 9`

  Author: Тринитротолуол  
  Пасти браминов.  
  Циклический, одиночный.  
  Примитивный квест. Стоять на пастбище указанное кол-во времени. С некоей долей вероятности на  
  браминов будут нападать волки, кротокрыссы и прочая живность. Необходимо защитить браминов.  
  Выдает Торр.  
  Количество и уровень мобов зависит от уровня игрока.  
  Если квест взят, то атака на браминов начинается во время, которое задано в скрипте.  
  И будет происходить вне зависимости от того пришел игрок на зашиту или нет.  
  Квест выдается в заданный интервал времени.  
  Мобы создаются не все сразу, а порциями, с интервалом в 1 минуту. Количество за один раз зависит от  
  кол-ва ентаеров. После окончания квеста мобы убегают с карты.  
  Скрипт полностью адаптирован к рестартам.

* `PrivateServer uint8 KlamCowboyCountGav`

  ...

* `PrivateServer uint16 KlamCowboyMobHx`

  ...

* `PrivateServer uint16 KlamCowboyMobHy`

  ...

* `Protected uint8 KlamDantonBramin Group = Quests Quest = 3211 Max = 8`

  Author: Тринитротолуол  
  Для квеста "Сгубить браминов".  
  Выдает Дантон.  
  Увести за собой и убить двоих браминов (с пастбища Эйдена). При этом есть шанс, равный 100%-(удача*10),  
  что игрока поймает на горячем Эйден. Дальше – несколько вариантов: либо сдать Дантона, либо убежать, либо бой,  
  либо убедить Эйдена отпустить игрока.

* `Protected uint8 KlamJosallDanton Group = Quests Quest = 3215 Max = 3`

  Author: Тринитротолуол  
  Для квеста "Проучить Дантона".

* `Protected uint KlamKuklachev Group = Quests Quest = 145 Max = 3`

  Author: DejaVu

* `Protected uint8 KlamSmilyGecko Group = Quests Quest = 3210 Max = 6`

  Author: heX  
  Групповой квест: Охота на Гекко  
  Выдает Смайли в Кламате  
  ver 2.2  
  отладка  
  #define debag

* `PrivateServer int KlamSmilyCurrentHp`

  ...

* `PrivateServer int KlamSmilyCountKills`

  ...

* `PrivateServer int KlamSmilyHealing`

  ...

* `PrivateServer uint8[] LimitedBarterData`

  Author: rifleman17  
  Бартер с ограничениями. Нпц покупает или продает вещи только из ограниченного списка.

* `PrivateServer bool IsGeck`

  ...

* `PrivateServer ident=>uint StealExpCount`

  ...

* `PrivateServer ident=>uint FirstAidCount`

  ...

* `Protected uint8 MainQuest Group = Quests Quest = 5001 Max = 21`

  Author: rifleman17

* `PrivateServer ident GCityCitizen`

  Author: rifleman17  
  Скрипты для города, который можно построить, использовав ГЕКК.  
  ГЭКК нужно использовать на пустынном энкаунтере (Content::Location::desert_1..Content::Location::desert_12)  
  Свойство, по которому будет проверяться, житель ли это города из ГЕКК или нет

* `PrivateServer uint MapGeckCityTraderSkillBarter`

  ...

* `PrivateServer uint MapKlamathRobotTimeNextSay`

  Author: Тринитротолуол, heX, rifleman17  
  Для удобства последующей заскриптовки карты, квесты "Пасти браминов", "Сгубить браминов"  
  и "Отнести мясо псам" вынесены в отдельные файлы.

* `Protected uint8 ModJoeGiantWasp Group = Quests Quest = 3307 Max = 3`

  Authors: cvet, rifleman17

* `Protected uint8 TribSulikRaid Group = Quests Quest = 4606 Max = 10`

  Author: Tab10id, Тринитротолуол

* `PrivateServer uint TribRaiderKillCount`

  ...

* `PrivateServer uint8 NCRElizeSlavers Max = 10`

  ...

* `PrivateServer uint16 MapPrimalTribeRaiderHx`

  ...

* `PrivateServer uint16 MapPrimalTribeRaiderHy`

  ...

* `Protected uint8 SFRonKillBeasts Group = Quests Quest = 4416 Max = 4`

  ...

* `Protected uint8 SFRonFindbodies Group = Quests Quest = 4417 Max = 6`

  ...

* `PrivateServer uint8 SFTankerCentaurNoticed Max = 1`

  ...

* `PrivateServer uint8 SFTankerFloaterNoticed Max = 1`

  ...

* `PrivateServer ident MapSFTankerBicycleId`

  ...

* `PrivateClient string TextOnHead Temporary`

  ...

* `PrivateClient uint TextOnHeadEndTime Temporary`

  ...

* `PrivateServer uint8 MirelurkCombatCurStage`

  ...

* `PrivateServer uint MirelurkCombatTimeNextStage`

  ...

* `PrivateServer uint MirelurkCombatLastBrokenBag`

  ...

* `PrivateServer ident MirelurkCombatDestroyingItem`

  ...

* `PrivateServer ident MobAttackedId`

  ...

* `PrivateServer int MobFury`

  ...

* `PrivateServer int MobFear`

  ...

* `PrivateServer int MobMaxFear`

  ...

* `PrivateServer int ModVampireFarmLocation`

  Author: rifleman17  
  Квест "Ночь нежна" - выяснить, почему ослабли коровы на одной из ферм модока.

* `PrivateServer uint8[] MonologueData`

  Author rifleman17  
  Монологи для НПЦ: несколько фраз. повторяемых через определенные промежутки времени.  
  Указывается первая и последняя строка монолога, время, через которое повторится монолог и т.д.  
  Строки должны быть записаны в FOTEXT.MSG  
  Строки монолога должны нумероваться подряд.  
  Если время следующего диалога равно нулю, все записи будут удалены после первого использования

* `Protected uint8 NavHenryEmpTest Group = Quests Quest = 4507 Max = 7`

  Author: rifleman17  
  Navarro sub1 quests

* `PrivateServer ident=>bool NavEmpTestedCritter`

  ...

* `PrivateServer uint NavarroTimeOutScan`

  ...

* `PrivateServer ident NavarroChipUsedId`

  ...

* `PrivateServer uint8 NcrAlexHoloFindStatus Max = 2`

  ...

* `Protected uint8 NCRFelixFindBrahmin Group = Quests Quest = 4276 Max = 3`

  Author: rifleman17  
  Все небольшие скрипты НКР

* `Protected uint8 NCRHubBook Group = Quests Quest = 4284 Max = 2`

  ...

* `Protected uint8 NCRFelixSaveBrahmin Group = Quests Quest = 4274 Max = 3`

  ...

* `PrivateServer uint8 NCRHubBookAccess1 Max = 1`

  ...

* `PrivateServer uint8 NCRHubBookAccess2 Max = 1`

  ...

* `PrivateServer uint8 NCRHubBookAccess3 Max = 1`

  ...

* `PrivateServer uint8 NCRHubBookAccess4 Max = 1`

  ...

* `PrivateServer uint8 NCRHubBookAccess5 Max = 1`

  ...

* `PrivateServer uint8 NCRHubBookAccess6 Max = 1`

  ...

* `PrivateServer uint8 NCRHubBookAccess7 Max = 1`

  ...

* `PrivateServer uint NCRHubBookQuestTimeout`

  ...

* `PrivateServer ident NcrCommonBeggarInvokeId`

  ...

* `PrivateServer uint8 NcrCommonBeggarPhraseNum`

  ...

* `PrivateServer ident NcrCommonBeggarHideMoneyInvocation`

  ...

* `PrivateServer ident NcrCommonBrahminId`

  ...

* `Protected uint8 QNcrElizeInvasion Group = Quests Quest = 4265 Max = 4`

  ...

* `Protected uint8 NCRKarlsonSon Group = Quests Quest = 4266 Max = 9`

  Author: rifleman17

* `PrivateServer ident NcrSonCatcherId`

  ...

* `PrivateServer uint8 NcrSonMovesCounter Max = 9`

  ...

* `PrivateServer uint NcrMichealMessageNum`

  Author: rifleman17  
  Майкл хочет пройти внутрь города, игроки ему помогают  
  после того, как диалогом вызывается соотвествующая функция, майrл отправляется к воротам, происходит небольшая сценка с охраной и он проходит внутрь  
  движение нужно начинать не сразу, а через некоторое время  
  Для квеста "Пропуск"

* `Protected uint8 MailDelivery Group = Quests Quest = 4248 Max = 3`

  Author: rifleman17

* `PrivateServer ident NcrMailRecieverId`

  ...

* `PrivateServer uint NcrMailTimeout`

  ...

* `Protected uint8 NcrRatchBuggy Group = Quests Quest = 4242 Max = 6`

  ...

* `Protected uint8 NcrShaimanProtest Group = Quests Quest = 4269 Max = 7`

  ...

* `PrivateServer uint NcrShaimanStringNum`

  ...

* `Protected uint8 NcrSiegeTerminate Group = Quests Quest = 4263 Max = 3`

  ...

* `PrivateServer uint8 NcrSiegeKillsCounter Max = 10`

  ...

* `PrivateServer uint NcrSmitVsVestinStatus Max = 6`

  Author: rifleman17

* `PrivateServer uint NcrSmitStringNum`

  ...

* `PrivateServer uint NcrSmitGateStringNum`

  ...

* `PrivateServer ident NcrSmitPlayerId`

  ...

* `PrivateServer uint NcrSmitIdleCount`

  ...

* `PrivateServer hstring NcrWestinMapPidTo`

  Скрипты советника Вейстина  
  rifleman17

* `PrivateServer uint NcrWestinHexNumTo`

  ...

* `PrivateServer ident NcrWestinEveryEveningInvokeId`

  ...

* `PrivateServer ident NcrWestinEveryMorningInvokeId`

  ...

* `Protected uint LastBagRefreshedTime`

  ...

* `PrivateServer uint LastNpcDialog`

  ...

* `PrivateServer uint NpcDialogStringNum`

  ...

* `PrivateServer int[] Planes`

  TODO:: void FOServer::ProcessAI( Npc* npc ) from ServerNpc.cpp engine 1519

* `PrivateServer uint NpcRevengeNpcHxHy`

  ...

* `PrivateServer uint NpcRevengeCountWait`

  ...

* `Protected uint8 NRWriKidnap Group = Quests Quest = 3707 Max = 12`

  Author: rifleman17  
  Квест "Проблемы мистера Райта: Заложник."

* `Protected uint8 NRSalvatoreKill Group = Quests Quest = 3710 Max = 3`

  ...

* `PrivateServer int NRWriKidnapNotifyTime`

  ...

* `PrivateServer int NRKidnapKillsCounter`

  ...

* `PrivateServer ident QNrWriKidnapInvokeId`

  ...

* `PrivateServer uint NukeStock`

  ...

* `PrivateServer uint NukeRestockTime`

  ...

* `PrivateServer uint8 PatternSniperCountRunning`

  ...

* `PrivateServer ident PetOwnerId`

  ...

* `PrivateServer uint PetLifeTime`

  ...

* `Protected bool IsGenerated`

  ...

* `PrivateServer int PokerWins`

  ...

* `PrivateServer uint PokerNumOfNpc`

  ...

* `PrivateServer ident=>uint PokerWincash`

  ...

* `PrivateServer ident=>uint PokerFraud`

  ...

* `PrivateServer ident=>uint PokerManywins`

  ...

* `PrivateServer any[] PokerData`

  ...

* `Protected uint8 QWarehouse Group = Quests Quest = 3040 Max = 4`

  ...

* `Protected uint8 QWarehouseSub1 Group = Quests Quest = 3041 Max = 4`

  ...

* `Protected uint8 QWarehouseSub2 Group = Quests Quest = 3042 Max = 4`

  ...

* `PrivateServer ident WarehouseDataId`

  ...

* `PrivateServer any[] WarehouseQuestData`

  ...

* `PrivateServer uint WarehouseOther`

  ...

* `PrivateServer hstring RatGrenadeProtoId`

  Author: rifleman17  
  Метательные крысы

* `PrivateServer ident RatGrenadeOwnerId`

  ...

* `PrivateServer uint8 ReddMineNuggets Max = 20`

  Author: rifleman17  
  Работы на шахтах Реддинга

* `Protected uint8 ReddMarionWan Group = Quests Quest = 5387 Max = 7`

  ...

* `PrivateServer uint ReddQWinamingoKills`

  ...

* `PrivateServer uint ReddQWinamingoHealing`

  ...

* `Protected uint8 ReddDoctorPoisoned Group = Quests Quest = 4311 Max = 3`

  ...

* `PrivateServer uint8 ReddRooneyCemetery Max = 4`

  ...

* `PrivateServer uint8 CanRepairWeapons Max = 1`

  Author: rifleman17  
  Скрипт для НПЦ, ремонтирующих оружие и броню.  
  - Ремонтируемый предмет игрок должен держать в основном слоте  
  - Ремонт может либо производиться мгновенно, либо за некий период.  
  - Одновременно НПЦ может ремонтировать только один предмет для одного игрока.  
  - От навыка ремонта НПЦ зависит скорость ремонта.  Линейная зависимость.  
  При 300 навыка - ремонт мгновенный, при 0 навыка - ремонт = 3 игровых часа для полностью поломанного предмета.  
  - От навыка торговли НПЦ и игрока зависит стоимость ремонта. Формула: [Стоимость] = 0.95*[Цена предмета]*[Навык торговли ремонтника]/[Навык торговли игрока]  
  для полностью поломанного предмета, но не менее 5% от цены предмета  
  - Для НПЦ назначены следующие переменные-флаги (локальная переменная для нпц максимум 1)  
  VAR_CAN_REPAIR_WEAPONS - признак, может ремонтировать хоть какое-то оружие  
  VAR_CAN_REPAIR_WEAPONS_SPECIAL - признак, может ремонтировать редкое оружие  
  VAR_CAN_REPAIR_ARMOUR - признак, может ремонтировать броню  
  VAR_CAN_REPAIR_SPECIAL_ARMOUR - признак, может ремонтировать редкую броню  
  Для настройки возможностей ремонта НПЦ используйте диалог и установку переменных, либо один из заготовленных скриптов (см. конец файла).

* `PrivateServer uint8 CanRepairWeaponsSpecial Max = 1`

  ...

* `PrivateServer uint8 CanRepairArmor Max = 1`

  ...

* `PrivateServer uint8 CanRepairArmorSpecial Max = 1`

  ...

* `PrivateServer ident=>uint RepairCompleteTime`

  ...

* `PrivateServer ident=>hstring RepairItemPid`

  ...

* `PrivateServer int ReplicationTime`

  Author: cvet

* `PrivateServer uint HellVisits`

  ...

* `PrivateServer bool ReplBankIsCanEnter`

  Author: cvet, rifleman17  
  Replication Bank

* `PrivateServer bool ReplBankeIsAttackGagPlayer`

  ...

* `PrivateServer uint8 ReplHellTurretHack Max = 100`

  Author: cvet

* `PrivateServer ident TerminalPlayerId`

  Author: cvet

* `PrivateServer uint TerminalDialogId`

  ...

* `Protected uint8 ModFarrelAmmiak Group = Quests Quest = 3316 Max = 2`

  Author: Tab10id

* `PrivateServer int RouletteCroupierNum`

  ...

* `PrivateServer int RouletteBetCoord1`

  ...

* `PrivateServer int RouletteBetCoord2`

  ...

* `PrivateServer int RouletteBetCoord3`

  ...

* `PrivateServer int RouletteBetSize`

  ...

* `PrivateServer int RouletteBetType`

  ...

* `PrivateServer uint[] RouletteData`

  ...

* `Protected bool CanSendSay`

  Игрок может отправлять текст на сервер. Переменную нужно уставлять вручную в dlg_ - функциях  
  введена, чтобы не отправляли любые тексты из любых диалогов

* `PrivateServer uint=>int Scores`

  ...

* `PrivateServer bool SEAndroidMonologEnd`

  Author: rifleman17  
  Квест-специальный энкаунтер. Две последовательные локации  
  На первой игрок находит труп нпц с рацией, если он возьмет рацию, может услышать сообщение о том, что где-то в Пустоши найден военный склад. На самом деле  
  это - ловушка, в которой его поджидает сумасшедший ученый. При заходе на вторую локацию персонаж попадает на хирургический стол, где его оперируют и персонаж  
  превращается в андроида.

* `PrivateServer uint SETalkingHeadStringNum`

  Autor: Cracker  
  Talking head special encounter scripts

* `PrivateServer ident SETeleportEatId`

  ...

* `Protected uint8 SFAhs7HubJudgement Group = Quests Quest = 4430 Max = 8`

  Author: rifleman17  
  Common san-francisco scripts

* `PrivateServer uint SFLoPanBlackmailSum Max = 2000`

  ...

* `PrivateServer ident SFHububJudgementLocId`

  ...

* `PrivateServer uint8 SFHubJudgementKills Max = 4`

  ...

* `PrivateServer ident SfMercMaster`

  ...

* `PrivateServer ident SFCommonOneWeekInvokeId`

  ...

* `PrivateServer ident SFCommonFightPlayerId`

  ...

* `PrivateServer ident=>uint ClickCounter`

  ...

* `Protected uint8 SFInvasionMirelurkKills Group = Quests Quest = 4409 Max = 7`

  Author: rifleman17  
  Нашествие болотников на Сан-Франциско.

* `Protected uint8 BHRocketBase Group = Quests Quest = 3610 Max = 5`

  Author: rifleman17  
  Квест "Рискованное дельце"

* `Protected uint8 NcrElizeSlvrsHunting Group = Quests Quest = 4246 Max = 7`

  ...

* `PrivateServer uint NcrElizeSlvrsHuntingStatus Max = 23`

  ...

* `Protected uint8 NcrSantiagoSpyMission Group = Quests Quest = 4271 Max = 21`

  ...

* `PrivateServer uint QSpyMissonStringNum`

  ...

* `Public uint TimeoutBattle Temporary`

  ...

* `Protected uint TimeoutTransfer Temporary`

  ...

* `PrivateCommon uint WalkSpeedBase`

  Critter

* `VirtualProtected uint WalkSpeed`

  ...

* `VirtualProtected bool IsNoMove`

  ...

* `PrivateCommon bool IsNoMoveBase`

  ...

* `VirtualProtected bool IsNoRun`

  ...

* `PrivateCommon bool IsNoRunBase`

  ...

* `VirtualPublic int Strength`

  ...

* `Public int StrengthBase Group = SpecialBase`

  ...

* `VirtualProtected int Perception`

  ...

* `Protected int PerceptionBase Group = SpecialBase`

  ...

* `VirtualPublic int Endurance`

  ...

* `Public int EnduranceBase Group = SpecialBase`

  ...

* `VirtualProtected int Charisma`

  ...

* `Protected int CharismaBase Group = SpecialBase`

  ...

* `VirtualProtected int Intellect`

  ...

* `Protected int IntellectBase Group = SpecialBase`

  ...

* `VirtualPublic int Agility`

  ...

* `Public int AgilityBase Group = SpecialBase`

  ...

* `VirtualProtected int Luck`

  ...

* `Protected int LuckBase Group = SpecialBase`

  ...

* `VirtualProtected int ArmorClass`

  ...

* `Public int CurrentHp`

  ...

* `VirtualPublic int MaxLife`

  ...

* `Public int MaxLifeBase`

  ...

* `Protected int ActionPointsBase`

  ...

* `Protected int ArmorClassBase`

  ...

* `VirtualProtected int MeleeDamage`

  ...

* `Protected int MeleeDamageBase`

  ...

* `VirtualProtected bool IsOverweight`

  ...

* `VirtualProtected int CarryWeight`

  ...

* `Protected int CarryWeightBase`

  ...

* `VirtualProtected int Sequence`

  ...

* `Protected int SequenceBase`

  ...

* `VirtualProtected int HealingRate`

  ...

* `Protected int HealingRateBase`

  ...

* `VirtualProtected int CriticalChance`

  ...

* `Protected int CriticalChanceBase`

  ...

* `VirtualProtected int MaxCritical`

  ...

* `Protected int MaxCriticalBase`

  ...

* `Protected int Toxic`

  ...

* `Protected int Radioactive`

  ...

* `Protected int KillExperience`

  ...

* `Protected uint BodyType`

  ...

* `Protected int LocomotionType`

  ...

* `Protected int DamageType`

  ...

* `Public int Age`

  ...

* `Public GenderType Gender`

  ...

* `Protected int PoisoningLevel`

  ...

* `Protected int RadiationLevel`

  ...

* `Protected int UnspentSkillPoints`

  ...

* `Protected int UnspentPerks`

  ...

* `Protected int Karma`

  ...

* `Protected int ReplicationMoney`

  ...

* `Protected int ReplicationCount`

  ...

* `Protected int ReplicationCost`

  ...

* `Protected int RateObject`

  ...

* `Protected int BonusLook`

  ...

* `Protected int NpcRole`

  ...

* `Protected int AiId`

  ...

* `Protected int TeamId`

  ...

* `Protected hstring NextCrType`

  ...

* `PrivateServer ident DeadBlockerId`

  ...

* `Protected int CurrentArmorPerk`

  ...

* `PrivateServer ident NextReplicationMap`

  ...

* `PrivateServer hstring NextReplicationEntry`

  ...

* `Public int PlayerKarma`

  ...

* `Public int ArmorPerk`

  ...

* `PrivateServer ident LastStealCrId`

  ...

* `PrivateServer uint StealCount`

  ...

* `PrivateServer uint GlobalMapMoveCounter`

  ...

* `Protected int Experience`

  ...

* `Protected int MaxMoveApBase`

  ...

* `Public hstring AnimType`

  ...

* `Protected bool IsNoUnarmed`

  ...

* `Protected hstring[] KnownLocProtoId`

  ...

* `Protected bool IsNoHome`

  ...

* `PrivateServer ident HomeMapId`

  ...

* `PrivateServer hstring HomeMapPid`

  ...

* `PrivateServer uint16 HomeHexX`

  ...

* `PrivateServer uint16 HomeHexY`

  ...

* `PrivateServer uint8 HomeDir`

  ...

* `Protected bool IsNoTalk`

  ...

* `PrivateServer uint16 MapLeaveHexX`

  ...

* `PrivateServer uint16 MapLeaveHexY`

  ...

* `Protected uint[] KnownLockerId`

  ...

* `Protected uint SpecialSkillPickOnGround Group = SpecialSkills`

  Special skill values

* `Protected uint SpecialSkillLootCritter Group = SpecialSkills`

  ...

* `Protected ident FollowLeaderId`

  Group & Global map

* `PrivateServer ident LastSendEntrancesLocId`

  ...

* `PrivateServer tick_t LastSendEntrancesTick`

  ...

* `Protected uint CrTypeAliasBase`

  Models

* `VirtualProtected uint CrTypeAlias`

  ...

* `Public hstring ModelNameBase`

  ...

* `Protected bool IsNoArmor`

  ...

* `PrivateCommon bool[] Anims ReadOnly`

  ...

* `Protected bool IsNoAim`

  Modes

* `Protected uint[] Kills`

  Kills

* `Protected uint KillMen Group = Kills`

  ...

* `Protected uint KillWomen Group = Kills`

  ...

* `Protected uint KillAlien Group = Kills`

  ...

* `Protected uint KillChildren Group = Kills`

  ...

* `Protected uint KillFloater Group = Kills`

  ...

* `Protected uint KillRat Group = Kills`

  ...

* `Protected uint KillCentaur Group = Kills`

  ...

* `Protected int ReputationDen Group = Reputations`

  Reputations

* `Protected int ReputationKlamath Group = Reputations`

  ...

* `Protected int ReputationModoc Group = Reputations`

  ...

* `Protected int ReputationVaultCity Group = Reputations`

  ...

* `Protected int ReputationGecko Group = Reputations`

  ...

* `Protected int ReputationBrokenHills Group = Reputations`

  ...

* `Protected int ReputationNewReno Group = Reputations`

  ...

* `Protected int ReputationSierra Group = Reputations`

  ...

* `Protected int ReputationVault15 Group = Reputations`

  ...

* `Protected int ReputationNCR Group = Reputations`

  ...

* `Protected int ReputationCathedral Group = Reputations`

  ...

* `Protected int ReputationSAD Group = Reputations`

  ...

* `Protected int ReputationRedding Group = Reputations`

  ...

* `Protected int ReputationSF Group = Reputations`

  ...

* `Protected int ReputationNavarro Group = Reputations`

  ...

* `Protected int ReputationArroyo Group = Reputations`

  ...

* `Protected int ReputationPrimalTribe Group = Reputations`

  ...

* `Protected int ReputationRangers Group = Reputations`

  ...

* `Protected int ReputationVault13 Group = Reputations`

  ...

* `Protected int ReputationSacramento Group = Reputations`

  ...

* `Protected bool[] Addictions`

  Addictions

* `VirtualProtected bool IsAddicted`

  ...

* `Protected bool IsJetAddicted`

  ...

* `Protected bool IsBuffoutAddicted`

  ...

* `Protected bool IsMentatsAddicted`

  ...

* `Protected bool IsPsychoAddicted`

  ...

* `Protected bool IsRadawayAddicted`

  ...

* `VirtualProtected int[] DamageResistance`

  Damage resistance

* `VirtualProtected int NormalResistance`

  ...

* `VirtualProtected int PoisonResistance`

  ...

* `VirtualProtected int RadiationResistance`

  ...

* `VirtualProtected int ExplodeResistance`

  ...

* `Protected int NormalResistanceBase Group = ResistsBase`

  ...

* `Protected int LaserResistanceBase Group = ResistsBase`

  ...

* `Protected int FireResistanceBase Group = ResistsBase`

  ...

* `Protected int PlasmaResistanceBase Group = ResistsBase`

  ...

* `Protected int ElectricityResistanceBase Group = ResistsBase`

  ...

* `Protected int EmpResistanceBase Group = ResistsBase`

  ...

* `Protected int ExplodeResistanceBase Group = ResistsBase`

  ...

* `Protected int PoisonResistanceBase Group = ResistsBase`

  ...

* `Protected int RadiationResistanceBase Group = ResistsBase`

  ...

* `VirtualProtected int[] DamageThreshold`

  ...

* `Protected int NormalThresholdBase Group = ThresholdsBase`

  ...

* `Protected int LaserThresholdBase Group = ThresholdsBase`

  ...

* `Protected int FireThresholdBase Group = ThresholdsBase`

  ...

* `Protected int PlasmaThresholdBase Group = ThresholdsBase`

  ...

* `Protected int ElectricityThresholdBase Group = ThresholdsBase`

  ...

* `Protected int EmpThresholdBase Group = ThresholdsBase`

  ...

* `Protected int ExplodeThresholdBase Group = ThresholdsBase`

  ...

* `Protected int PoisonThresholdBase Group = ThresholdsBase`

  ...

* `Protected int RadiationThresholdBase Group = ThresholdsBase`

  ...

* `Protected bool IsPoisoned`

  Damages

* `Protected bool IsRadiated`

  ...

* `VirtualPublic bool IsInjured`

  ...

* `Public bool IsDamagedEye`

  ...

* `Public bool IsDamagedRightArm`

  ...

* `Public bool IsDamagedLeftArm`

  ...

* `Public bool IsDamagedRightLeg`

  ...

* `Public bool IsDamagedLeftLeg`

  ...

* `Public any Var0`

  Custom vars

* `Public any Var1`

  ...

* `Public any Var2`

  ...

* `Public any Var3`

  ...

* `Public any Var4`

  ...

* `Public any Var5`

  ...

* `Public any Var6`

  ...

* `Public any Var7`

  ...

* `Public any Var8`

  ...

* `Public any Var9`

  ...

* `Protected int SkillSmallGuns Group = Skills`

  Skills

* `Protected int SkillBigGuns Group = Skills`

  ...

* `Protected int SkillEnergyWeapons Group = Skills`

  ...

* `Protected int SkillUnarmed Group = Skills`

  ...

* `Protected int SkillMeleeWeapons Group = Skills`

  ...

* `Protected int SkillThrowing Group = Skills`

  ...

* `Protected int SkillFirstAid Group = Skills`

  ...

* `Protected int SkillDoctor Group = Skills`

  ...

* `Protected int SkillSneak Group = Skills`

  ...

* `Protected int SkillLockpick Group = Skills`

  ...

* `Protected int SkillSteal Group = Skills`

  ...

* `Protected int SkillTraps Group = Skills`

  ...

* `Protected int SkillScience Group = Skills`

  ...

* `Protected int SkillRepair Group = Skills`

  ...

* `Protected int SkillSpeech Group = Skills`

  ...

* `Protected int SkillBarter Group = Skills`

  ...

* `Protected int SkillGambling Group = Skills`

  ...

* `Protected int SkillOutdoorsman Group = Skills`

  ...

* `VirtualProtected CritterProperty[] TagSkills`

  Tag skills

* `Protected CritterProperty TagSkill1`

  ...

* `Protected CritterProperty TagSkill2`

  ...

* `Protected CritterProperty TagSkill3`

  ...

* `Protected uint8 PerkBookworm Group = Perks`

  Perks

* `Protected uint8 PerkAwareness Group = Perks`

  ...

* `Protected uint8 PerkBonusHthAttacks Group = Perks`

  ...

* `Protected uint8 PerkBonusHthDamage Group = Perks`

  ...

* `Protected uint8 PerkBonusRangedDamage Group = Perks`

  ...

* `Protected uint8 PerkBonusRateOfFire Group = Perks`

  ...

* `Protected uint8 PerkEarlierSequence Group = Perks`

  ...

* `Protected uint8 PerkFasterHealing Group = Perks`

  ...

* `Protected uint8 PerkMoreCriticals Group = Perks`

  ...

* `Protected uint8 PerkNightVision Group = Perks`

  ...

* `Protected uint8 PerkRadResistance Group = Perks`

  ...

* `Protected uint8 PerkToughness Group = Perks`

  ...

* `Protected uint8 PerkStrongBack Group = Perks`

  ...

* `Protected uint8 PerkSharpshooter Group = Perks`

  ...

* `Protected uint8 PerkSurvivalist Group = Perks`

  ...

* `Protected uint8 PerkEducated Group = Perks`

  ...

* `Protected uint8 PerkHealer Group = Perks`

  ...

* `Protected uint8 PerkFortuneFinder Group = Perks`

  ...

* `Protected uint8 PerkBetterCriticals Group = Perks`

  ...

* `Protected uint8 PerkEmpathy Group = Perks`

  ...

* `Protected uint8 PerkSlayer Group = Perks`

  ...

* `Protected uint8 PerkSniper Group = Perks`

  ...

* `Protected uint8 PerkSilentDeath Group = Perks`

  ...

* `Protected uint8 PerkActionBoy Group = Perks`

  ...

* `Protected uint8 PerkMentalBlock Group = Perks`

  ...

* `Protected uint8 PerkLifegiver Group = Perks`

  ...

* `Protected uint8 PerkDodger Group = Perks`

  ...

* `Protected uint8 PerkSnakeater Group = Perks`

  ...

* `Protected uint8 PerkMrFixit Group = Perks`

  ...

* `Protected uint8 PerkMedic Group = Perks`

  ...

* `Protected uint8 PerkMasterThief Group = Perks`

  ...

* `Protected uint8 PerkSpeaker Group = Perks`

  ...

* `Protected uint8 PerkHeaveHo Group = Perks`

  ...

* `Protected uint8 PerkFriendlyFoe Group = Perks`

  ...

* `Protected uint8 PerkPickpocket Group = Perks`

  ...

* `Protected uint8 PerkGhost Group = Perks`

  ...

* `Protected uint8 PerkCultOfPersonality Group = Perks`

  ...

* `Protected uint8 PerkScrounger Group = Perks`

  ...

* `Protected uint8 PerkExplorer Group = Perks`

  ...

* `Protected uint8 PerkFlowerChild Group = Perks`

  ...

* `Protected uint8 PerkPathfinder Group = Perks`

  ...

* `Protected uint8 PerkAnimalFriend Group = Perks`

  ...

* `Protected uint8 PerkScout Group = Perks`

  ...

* `Protected uint8 PerkMysteriousStranger Group = Perks`

  ...

* `Protected uint8 PerkRanger Group = Perks`

  ...

* `Protected uint8 PerkSmoothTalker Group = Perks`

  ...

* `Protected uint8 PerkSwiftLearner Group = Perks`

  ...

* `Protected uint8 PerkTag Group = Perks`

  ...

* `Protected uint8 PerkMutate Group = Perks`

  ...

* `Public uint8 PerkAdrenalineRush Group = Perks`

  ...

* `Protected uint8 PerkCautiousNature Group = Perks`

  ...

* `Protected uint8 PerkComprehension Group = Perks`

  ...

* `Protected uint8 PerkDemolitionExpert Group = Perks`

  ...

* `Protected uint8 PerkGambler Group = Perks`

  ...

* `Protected uint8 PerkGainStrength Group = Perks`

  ...

* `Protected uint8 PerkGainPerception Group = Perks`

  ...

* `Protected uint8 PerkGainEndurance Group = Perks`

  ...

* `Protected uint8 PerkGainCharisma Group = Perks`

  ...

* `Protected uint8 PerkGainIntelligence Group = Perks`

  ...

* `Protected uint8 PerkGainAgility Group = Perks`

  ...

* `Protected uint8 PerkGainLuck Group = Perks`

  ...

* `Protected uint8 PerkHarmless Group = Perks`

  ...

* `Protected uint8 PerkHereAndNow Group = Perks`

  ...

* `Protected uint8 PerkHthEvade Group = Perks`

  ...

* `Protected uint8 PerkKamaSutraMaster Group = Perks`

  ...

* `Protected uint8 PerkKarmaBeacon Group = Perks`

  ...

* `Protected uint8 PerkLightStep Group = Perks`

  ...

* `Protected uint8 PerkLivingAnatomy Group = Perks`

  ...

* `Protected uint8 PerkMagneticPersonality Group = Perks`

  ...

* `Protected uint8 PerkNegotiator Group = Perks`

  ...

* `Protected uint8 PerkPackRat Group = Perks`

  ...

* `Protected uint8 PerkPyromaniac Group = Perks`

  ...

* `Protected uint8 PerkQuickRecovery Group = Perks`

  ...

* `Protected uint8 PerkSalesman Group = Perks`

  ...

* `Protected uint8 PerkStonewall Group = Perks`

  ...

* `Protected uint8 PerkThief Group = Perks`

  ...

* `Protected uint8 PerkWeaponHandling Group = Perks`

  ...

* `Protected uint8 PerkVaultCityTraining Group = Perks`

  ...

* `Protected uint8 PerkExpertExcrement Group = Perks`

  ...

* `Protected uint8 PerkTerminator Group = Perks`

  ...

* `Protected uint8 PerkGeckoSkinning Group = Perks`

  ...

* `Protected uint8 PerkVaultCityInoculations Group = Perks`

  ...

* `Protected uint8 PerkDermalImpact Group = Perks`

  ...

* `Protected uint8 PerkDermalImpactEnh Group = Perks`

  ...

* `Protected uint8 PerkPhoenixImplants Group = Perks`

  ...

* `Protected uint8 PerkPhoenixImplantsEnh Group = Perks`

  ...

* `Protected uint8 PerkNcrPerception Group = Perks`

  ...

* `Protected uint8 PerkNcrEndurance Group = Perks`

  ...

* `Protected uint8 PerkNcrBarter Group = Perks`

  ...

* `Protected uint8 PerkNcrRepair Group = Perks`

  ...

* `Protected uint8 PerkVampireAccuracy Group = Perks`

  ...

* `Protected uint8 PerkVampireRegeneration Group = Perks`

  ...

* `Protected uint8 PerkQuickPockets Group = Perks`

  ...

* `Protected uint8 PerkMasterTrader Group = Perks`

  ...

* `Protected uint8 PerkSilentRunning Group = Perks`

  ...

* `Protected uint8 PerkBonusMove Group = Perks`

  ...

* `Protected uint8 KarmaPerkBerserker Group = KarmaPerks`

  Karma perks

* `Protected uint8 KarmaPerkChampion Group = KarmaPerks`

  ...

* `Protected uint KarmaPerkChildkiller Group = KarmaPerks`

  ...

* `Protected uint8 KarmaPerkSexpert Group = KarmaPerks`

  ...

* `Protected uint8 KarmaPerkPrizefighter Group = KarmaPerks`

  ...

* `Protected uint8 KarmaPerkGigolo Group = KarmaPerks`

  ...

* `Protected uint8 KarmaPerkGraveDigger Group = KarmaPerks`

  ...

* `Protected uint8 KarmaPerkMarried Group = KarmaPerks`

  ...

* `Protected uint8 KarmaPerkPornStar Group = KarmaPerks`

  ...

* `Protected uint8 KarmaPerkSlaver Group = KarmaPerks`

  ...

* `Protected uint8 KarmaPerkVirginWastes Group = KarmaPerks`

  ...

* `Protected uint8 KarmaPerkManSalvatore Group = KarmaPerks`

  ...

* `Protected uint8 KarmaPerkManBishop Group = KarmaPerks`

  ...

* `Protected uint8 KarmaPerkManMordino Group = KarmaPerks`

  ...

* `Protected uint8 KarmaPerkManWright Group = KarmaPerks`

  ...

* `Protected uint8 KarmaPerkSeparated Group = KarmaPerks`

  ...

* `Protected uint8 KarmaPerkPedobear Group = KarmaPerks`

  ...

* `Protected uint8 KarmaPerkVcGuardsman Group = KarmaPerks`

  ...

* `Protected bool IsTraitFastMetabolism Group = Traits`

  Traits

* `Protected bool IsTraitBruiser Group = Traits`

  ...

* `Protected bool IsTraitSmallFrame Group = Traits`

  ...

* `Protected bool IsTraitOneHander Group = Traits`

  ...

* `Protected bool IsTraitFinesse Group = Traits`

  ...

* `Protected bool IsTraitKamikaze Group = Traits`

  ...

* `Protected bool IsTraitHeavyHanded Group = Traits`

  ...

* `Protected bool IsTraitFastShot Group = Traits`

  ...

* `Protected bool IsTraitBloodyMess Group = Traits`

  ...

* `Protected bool IsTraitJinxed Group = Traits`

  ...

* `Protected bool IsTraitJinxedII Group = Traits`

  ...

* `Protected bool IsTraitGoodNatured Group = Traits`

  ...

* `Protected bool IsTraitChemReliant Group = Traits`

  ...

* `Protected bool IsTraitChemResistant Group = Traits`

  ...

* `Protected bool IsTraitSexAppeal Group = Traits`

  ...

* `Protected bool IsTraitSkilled Group = Traits`

  ...

* `Protected bool IsTraitNightPerson Group = Traits`

  ...

* `Protected uint TimeoutSkFirstAid Group = Timeouts`

  Timeouts

* `Protected uint TimeoutSkDoctor Group = Timeouts`

  ...

* `Protected uint TimeoutSkRepair Group = Timeouts`

  ...

* `Protected uint TimeoutSkScience Group = Timeouts`

  ...

* `Protected uint TimeoutSkLockpick Group = Timeouts`

  ...

* `Protected uint TimeoutSkSteal Group = Timeouts`

  ...

* `Protected uint TimeoutSkOutdoorsman Group = Timeouts`

  ...

* `Protected uint TimeoutRemoveFromGame Group = Timeouts`

  ...

* `Protected uint TimeoutReplication Group = Timeouts`

  ...

* `Protected uint TimeoutKarmaVoting Group = Timeouts`

  ...

* `Protected uint TimeoutSneak Group = Timeouts`

  ...

* `Protected uint TimeoutHealing Group = Timeouts`

  ...

* `Protected uint TimeoutStealing Group = Timeouts`

  ...

* `Protected uint TimeoutAggressor Group = Timeouts`

  ...

* `PrivateServer ident MercMasterId Group = Mercs`

  Id хозяина мерка

* `PrivateServer bool MercAlwaysRun Group = Mercs`

  Признак мерк перемещаетя бегом при следовании за хозяином

* `PrivateServer bool MercCancelOnAttack Group = Mercs`

  Признак отменяет ли мерк службу если хозяин атакует самого мерка

* `PrivateServer uint MercLoseDist Group = Mercs`

  Дистанция при превышении которой мерк "отстает" от хозяина и отменяет режиме мерка

* `PrivateServer uint MercMasterDist Group = Mercs`

  Дистанция которой придерживается мерк в режиме следования за хозяином

* `PrivateServer int MercType Group = Mercs`

  Тип мерка см. Merch

* `PrivateServer bool MercDefendMaster Group = Mercs`

  Признак: мерк защищает хозяина если тот атакован

* `PrivateServer bool MercAssistMaster Group = Mercs`

  Признак: если хозяин атакует цель мерк присоединяется к атаке

* `PrivateServer uint MercCancelTime Group = Mercs`

  Время завершения службы

* `PrivateServer bool MercCancelOnGlobal Group = Mercs`

  Признак: мерк отменяет службу если хозяин вышел на глобальную карту

* `PrivateServer bool MercWaitForMaster Group = Mercs`

  Признак: мерк ожидает хозяина на конкретном месте

* `Protected uint8 ArroyoMynocDefence Group = Quests Quest = 4702 Max = 8`

  Quest

* `Protected uint8 ArroyoCassidyLetter Group = Quests Quest = 4705 Max = 4`

  ...

* `Protected uint8 ArroyoMynocOil Group = Quests Quest = 4701 Max = 3`

  ...

* `Protected uint8 ArroyoProofOfDeath Group = Quests Quest = 4706 Max = 4`

  ...

* `Protected uint8 ArroyoLetterToLinnett Group = Quests Quest = 4707 Max = 4`

  ...

* `Protected uint8 KlamSallyFindProstitute Group = Quests Quest = 3224 Max = 3`

  ...

* `Protected uint8 KlamBobWater Group = Quests Quest = 3201 Max = 3`

  ...

* `Protected uint8 KlamFindTrappers Group = Quests Quest = 3223 Max = 11`

  ...

* `Protected uint8 KlamBugenLure Group = Quests Quest = 3230 Max = 9`

  ...

* `Protected uint8 KlamNotifyHusband Group = Quests Quest = 3229 Max = 4`

  ...

* `Protected uint8 KlamEidenBramin Group = Quests Quest = 3221 Max = 6`

  ...

* `Protected uint8 KlamSmilyModoc Group = Quests Quest = 3206 Max = 2`

  ...

* `Protected uint8 DenBillRacingWin Group = Quests Quest = 3152 Max = 7`

  ...

* `Protected uint8 DenLeannaCondom Group = Quests Quest = 3100 Max = 3`

  ...

* `Protected uint8 QDenAnanDoll Group = Quests Quest = 3145 Max = 3`

  ...

* `Protected uint8 DenAnanRedoll Group = Quests Quest = 3146 Max = 3`

  ...

* `Protected uint8 DenGhost Group = Quests Quest = 3103 Max = 11`

  ...

* `Protected uint8 DenBillRacingOpening Group = Quests Quest = 3151 Max = 2`

  ...

* `Protected uint8 DenCarstopJeffry Group = Quests Quest = 3106 Max = 4`

  ...

* `Protected uint8 DenCarstopBrahmin Group = Quests Quest = 3127 Max = 11`

  ...

* `Protected uint8 DenCarstopBreeder Group = Quests Quest = 3126 Max = 3`

  ...

* `Protected uint8 DenJoeySteal Group = Quests Quest = 3112 Max = 4`

  ...

* `Protected uint8 DenJaneDolg Group = Quests Quest = 3117 Max = 3`

  ...

* `Protected uint8 DenJanePsycho Group = Quests Quest = 3116 Max = 3`

  ...

* `Protected uint8 DenLaraPostal Group = Quests Quest = 3131 Max = 4`

  ...

* `Protected uint8 DenFlikJet Group = Quests Quest = 3135 Max = 4`

  ...

* `Protected uint8 DenLaraBand Group = Quests Quest = 3134 Max = 3`

  ...

* `Protected uint8 DenJoeyLoan Group = Quests Quest = 3107 Max = 3`

  ...

* `Protected uint8 DenLaraBos Group = Quests Quest = 3132 Max = 3`

  ...

* `Protected uint8 QDenCliffDealer Group = Quests Quest = 3144 Max = 4`

  ...

* `Protected uint8 DenFredStim Group = Quests Quest = 3137 Max = 2`

  ...

* `Protected uint8 DenJaneVodka Group = Quests Quest = 3122 Max = 4`

  ...

* `Protected uint8 DenMomSlut Group = Quests Quest = 3101 Max = 3`

  ...

* `Protected uint8 DenSmittyBatt Group = Quests Quest = 3139 Max = 3`

  ...

* `Protected uint8 DenJaneMeat Group = Quests Quest = 3121 Max = 4`

  ...

* `Protected uint8 DenJaneStim Group = Quests Quest = 3123 Max = 4`

  ...

* `Protected uint8 DenLaraMolotovCoctail Group = Quests Quest = 3105 Max = 3`

  ...

* `Protected uint8 DenLeannaBuy Group = Quests Quest = 3142 Max = 4`

  ...

* `Protected uint8 DenSmittyBoots Group = Quests Quest = 3128 Max = 3`

  ...

* `Protected uint8 DenJaneGuns Group = Quests Quest = 3124 Max = 4`

  ...

* `Protected uint8 DenSmittyKey Group = Quests Quest = 3140 Max = 3`

  ...

* `Protected uint8 DenJaneArmor Group = Quests Quest = 3125 Max = 4`

  ...

* `Protected uint8 DenSmittyAmmo Group = Quests Quest = 3141 Max = 4`

  ...

* `Protected uint8 DenJaneHunt Group = Quests Quest = 3115 Max = 3`

  ...

* `Protected uint8 DenJoeyKnife Group = Quests Quest = 3109 Max = 3`

  ...

* `Protected uint8 DenJoeyLara Group = Quests Quest = 3111 Max = 4`

  ...

* `Protected uint8 DenJaneRadio Group = Quests Quest = 3113 Max = 4`

  ...

* `Protected uint8 DenJoeyJet Group = Quests Quest = 3110 Max = 4`

  ...

* `Protected uint8 DenLaraTrust Group = Quests Quest = 3130 Max = 2`

  ...

* `Protected uint8 DenLeannaWine Group = Quests Quest = 3143 Max = 4`

  ...

* `Protected uint8 DenMomRadscorp Group = Quests Quest = 3102 Max = 2`

  ...

* `Protected uint8 DenSmittyFixit Group = Quests Quest = 3104 Max = 4`

  ...

* `Protected uint8 QDenLeannaThief Group = Quests Quest = 3138 Max = 4`

  ...

* `Protected uint8 ModJoeFarm Group = Quests Quest = 3306 Max = 3`

  ...

* `Protected uint8 ModHose Group = Quests Quest = 3300 Max = 3`

  ...

* `Protected uint8 ModBaltasGecko Group = Quests Quest = 3302 Max = 3`

  ...

* `Protected uint8 ModLourenceRatsColony Group = Quests Quest = 3324 Max = 4`

  ...

* `Protected uint8 ModLourenceFloater Group = Quests Quest = 3320 Max = 4`

  ...

* `Protected uint8 ModJoeVampire Group = Quests Quest = 3308 Max = 11`

  ...

* `Protected uint8 BHMarcusEscort Group = Quests Quest = 3608 Max = 5`

  ...

* `Protected uint8 BHSuperNewTechnology Group = Quests Quest = 3604 Max = 5`

  ...

* `Protected uint8 ReddDocRadio Group = Quests Quest = 4330 Max = 6`

  ...

* `Protected uint8 ReddDocRadioTroy Group = Quests Quest = 4331 Max = 1`

  ...

* `Protected uint8 ReddDocRadioFung Group = Quests Quest = 4332 Max = 1`

  ...

* `Protected uint8 ReddDocRadioHoliday Group = Quests Quest = 4333 Max = 1`

  ...

* `Protected uint8 ReddDocRadioJubiley Group = Quests Quest = 4334 Max = 1`

  ...

* `Protected uint8 ReddHubbChildkiller Group = Quests Quest = 4312 Max = 7`

  ...

* `Protected uint8 ReddMarionVinamingo Group = Quests Quest = 4303 Max = 18`

  ...

* `Protected uint8 ReddDoctorDelivery Group = Quests Quest = 5310 Max = 3`

  ...

* `Protected uint8 NavHenryProtoMaterials Group = Quests Quest = 4509 Max = 2`

  ...

* `Protected uint8 NavSoftJob Group = Quests Quest = 4506 Max = 2`

  ...

* `Protected uint8 NcrHatePatrol Group = Quests Quest = 4292 Max = 11`

  ...

* `Protected uint8 NcrSantiagaFindSpyStatus Group = Quests Quest = 4273 Max = 21`

  ...

* `Protected uint8 NcrBusterBrokenrifles Group = Quests Quest = 4286 Max = 15`

  ...

* `Protected uint8 NcrKessMedBoardStatus Group = Quests Quest = 4232 Max = 3`

  ...

* `Protected uint8 NcrDorotyFindHenryPapers Group = Quests Quest = 4288 Max = 2`

  ...

* `Protected uint8 NcrLeadSmit2Dustybar Group = Quests Quest = 4218 Max = 4`

  ...

* `Protected uint8 NcrKyleReddRecon Group = Quests Quest = 4270 Max = 2`

  ...

* `Protected uint8 NcrDuppoFindDasies Group = Quests Quest = 4289 Max = 2`

  ...

* `Protected uint8 NcrDappoLostC Group = Quests Quest = 4228 Max = 5`

  ...

* `Protected uint8 QChosen Group = Quests Quest = 5003 Max = 15`

  ...

* `Protected uint8 NRBarmenEscort Group = Quests Quest = 3714 Max = 4`

  ...

* `Protected uint8 SFAhs7ImperatorFormat Group = Quests Quest = 4421 Max = 7`

  ...

* `Protected uint8 SFEvaHelpWithZax Group = Quests Quest = 4402 Max = 10`

  ...

* `Protected uint8 SFKenliImperatorRestore Group = Quests Quest = 4420 Max = 10`

  ...

* `Protected uint8 SFLoPanBlackmail Group = Quests Quest = 4411 Max = 3`

  ...

* `Protected uint8 SFTigangRecipe Group = Quests Quest = 4440 Max = 2`

  ...

* `Protected uint8 SFNarcoman Group = Quests Quest = 4410 Max = 2`

  ...

* `Protected uint8 SFAhs7Invitations Group = Quests Quest = 4428 Max = 5`

  ...

* `Protected uint8 SFSlimSidnancy Group = Quests Quest = 4424 Max = 6`

  ...

* `Protected uint8 VCLetterToTodd Group = Quests Quest = 8848 Max = 10`

  ...

* `Protected uint8 VCValeryMail Group = Quests Quest = 8811 Max = 4`

  ...

* `Protected uint8 VCCindyLetter Group = Quests Quest = 8847 Max = 6`

  ...

* `Protected uint8 VCHartmannRecon Group = Quests Quest = 8829 Max = 5`

  ...

* `Protected uint8 VCHartmanNcrHelp Group = Quests Quest = 8834 Max = 4`

  ...

* `Protected uint8 VCBarmenDelivery Group = Quests Quest = 8805 Max = 2`

  ...

* `Protected uint8 VCCharlie Group = Quests Quest = 8802 Max = 4`

  ...

* `Protected uint8 VCTroyFreshBlood Group = Quests Quest = 8808 Max = 8`

  ...

* `Protected uint8 VCAndrewDeliveries Group = Quests Quest = 8803 Max = 3`

  ...

* `Protected uint8 VCBlackEscort Group = Quests Quest = 8817 Max = 5`

  ...

* `Protected uint8 VCHartmanFight Group = Quests Quest = 8819 Max = 2`

  ...

* `Protected uint8 VCLynettScareNewcomers Group = Quests Quest = 8841 Max = 5`

  ...

* `Protected uint8 VCHartmanRifles Group = Quests Quest = 8822 Max = 3`

  ...

* `Protected uint8 VCHeleneTroyBeauty Group = Quests Quest = 8813 Max = 4`

  ...

* `Protected uint8 TribSulikStuff Group = Quests Quest = 4602 Max = 10`

  ...

* `Protected uint8 TribMuscoTest Group = Quests Quest = 4605 Max = 10`

  ...

* `Protected uint8 TribShamanPowder Group = Quests Quest = 4603 Max = 10`

  ...

* `Protected uint8 TribMaiaraBook Group = Quests Quest = 4604 Max = 10`

  ...

* `Protected uint8 TribManotaNecklace Group = Quests Quest = 4601 Max = 10`

  ...

* `PrivateServer uint BHDeadSaboteursCounter Max = 40`

  Other

* `PrivateServer uint8 SpecialAndroid Max = 3`

  ...

* `PrivateServer uint8 VCLynettRefuse Max = 2`

  ...

* `PrivateServer uint DialogTimeout`

  ...

* `PrivateServer uint EncLoyalityHubologists`

  ...

* `PrivateServer uint EncLoyalityNcr`

  ...

* `PrivateServer uint EncLoyalityVCity`

  ...

* `PrivateServer uint EncLoyalityRedding`

  ...

* `PrivateServer uint EncLoyalityBroken`

  ...

* `PrivateServer uint EncLoyalityGecko`

  ...

* `PrivateServer uint EncLoyalityArroyo`

  ...

* `PrivateServer uint EncLoyalityKlamath`

  ...

* `PrivateServer uint EncLoyalityModoc`

  ...

* `PrivateServer uint EncLoyalityDen`

  ...

* `PrivateServer uint EncLoyalityReno`

  ...

* `PrivateServer uint EncLoyalityEnclave`

  ...

* `PrivateServer uint EncLoyalitySf`

  ...

* `PrivateServer uint8 ModLourenceToxinRecipe Max = 1`

  ...

* `PrivateServer uint8 SFChitinArmorRecipeKnown Max = 1`

  ...

* `PrivateServer uint8 SpyCathActive Max = 1`

  ...

* `PrivateServer uint8 HasNotCard Max = 1`

  ...

* `PrivateServer uint SexExp Max = 501`

  ...

* `PrivateServer uint ScenFraction Max = 10`

  ...

* `PrivateServer uint8 ArroyoDocHealing Max = 2`

  ...

* `PrivateServer uint8 AtollTesla Max = 2`

  ...

* `PrivateServer uint8 AtollMoney Max = 2`

  ...

* `PrivateServer uint BHEscortNpcId`

  ...

* `PrivateServer uint8 ScenBosSoldier Max = 10`

  ...

* `PrivateServer uint8 SFInvasionBadge Max = 1`

  ...

* `PrivateServer uint8 ScenBosScriber Max = 10`

  ...

* `PrivateServer uint8 ScenEnclaveSoldier Max = 10`

  ...

* `PrivateServer uint8 ScenEnclaveScient Max = 10`

  ...

* `PrivateServer uint8 DenJaneTraderFred Max = 10`

  ...

* `PrivateServer uint8 DenJaneJobCounter Max = 10`

  ...

* `PrivateServer uint8 DenJoeyCounter Max = 10`

  ...

* `PrivateServer uint8 DenLaraBosCounter Max = 10`

  ...

* `PrivateServer uint8 DenJaneTraderMom Max = 10`

  ...

* `PrivateServer uint8 DenNarcCommMember Max = 10`

  ...

* `PrivateServer uint8 DenJaneTraderLean Max = 10`

  ...

* `PrivateServer uint8 EncOceanTraderFamiliar Max = 5`

  ...

* `PrivateServer uint8 ModBaltasArmor1 Max = 10`

  ...

* `PrivateServer uint8 GeckGaroldTrain Max = 1`

  ...

* `PrivateServer uint8 GeckSkitrTransit Max = 3`

  ...

* `PrivateServer uint8 KlamBaknerBeer Max = 1`

  ...

* `Protected uint8 ModBaltasArmor Max = 10`

  ...

* `PrivateServer uint8 KlamVaccination Max = 2`

  ...

* `PrivateServer uint8 KlamVaccinationB1 Max = 1`

  ...

* `PrivateServer uint8 KlamVaccinationB2 Max = 1`

  ...

* `PrivateServer uint8 KlamVaccinationB3 Max = 1`

  ...

* `PrivateServer uint8 KlamGoldBeer Max = 1`

  ...

* `PrivateServer uint8 KlamSallyPay Max = 5`

  ...

* `PrivateServer uint8 ModBaltasArmor2 Max = 10`

  ...

* `PrivateServer uint8 KlamVicFixittrash Max = 1`

  ...

* `PrivateServer uint8 ModHoseTools Max = 1`

  ...

* `PrivateServer uint8 ModVampireReaction Max = 2`

  ...

* `PrivateServer uint8 NcrAlexQuestStatus Max = 7`

  ...

* `PrivateServer uint8 NcrDustyPartyStatusChar Max = 2`

  ...

* `PrivateServer uint8 NcrMiraTroubleStatusChar Max = 4`

  ...

* `PrivateServer uint8 NcrBeggarTalk Max = 1`

  ...

* `PrivateServer uint8 NcrDorothyGammaStatusChar Max = 2`

  ...

* `PrivateServer uint8 NcrDumontBrkradioStatusChar Max = 10`

  ...

* `PrivateServer uint8 NcrCaptainFlirtStatusChar Max = 1`

  ...

* `PrivateServer uint8 NcrIsNightGuardAccessFranted Max = 1`

  ...

* `PrivateServer uint8 NcrClausHistory Max = 1`

  ...

* `PrivateServer uint8 NcrJubileyTailsStatus Max = 15`

  ...

* `PrivateServer uint8 NcrRondoDorotyStatus Max = 3`

  ...

* `PrivateServer uint8 NcrFergusStory Max = 1`

  ...

* `PrivateServer uint8 NcrCaptainSmitAccessGranted Max = 1`

  ...

* `PrivateServer uint8 NcrJubileyTailsCounter Max = 15`

  ...

* `PrivateServer uint8 NcrBusterDorotyStatus Max = 3`

  ...

* `PrivateServer uint8 NcrFergusSecret Max = 1`

  ...

* `PrivateServer uint8 NcrGunterStory Max = 1`

  ...

* `PrivateServer uint ScenRangerRank Max = 13000`

  ...

* `PrivateServer uint8 NcrDustyFoodDeliveryStatus Max = 3`

  ...

* `PrivateServer uint8 NcrPlayerLeadSmit2Dustybar Max = 5`

  ...

* `PrivateServer uint8 NcrKarlStory Max = 1`

  ...

* `PrivateServer uint8 NcrCarlsonStory Max = 1`

  ...

* `PrivateServer uint8 NcrKukComp Max = 1`

  ...

* `PrivateServer uint8 NcrMicQStatus Max = 2`

  ...

* `PrivateServer uint8 ScenRanger Max = 5`

  ...

* `PrivateServer uint8 NcrDumontHistory Max = 1`

  ...

* `PrivateServer uint8 NcrMicQCptnDumbCounter Max = 10`

  ...

* `PrivateServer uint8 NcrPlayerHasMultipass Max = 1`

  ...

* `PrivateServer uint8 NcrSmitVsVestinResult Max = 5`

  ...

* `PrivateServer uint8 NRJukeboxSeen Max = 1`

  ...

* `PrivateServer uint8 VCTrainigAccess Max = 1`

  ...

* `PrivateServer uint8 NcrLennyFight Max = 1`

  ...

* `PrivateServer uint8 NcrRatchPlayerPoints Max = 15`

  ...

* `PrivateServer uint8 NRJesusTrain Max = 10`

  ...

* `PrivateServer uint8 PurgSuppluysTaken Max = 1`

  ...

* `PrivateServer uint8 NcrWestinPillsStatus Max = 6`

  ...

* `PrivateServer uint8 NcrWestinPlayerGetPrepayment Max = 2`

  ...

* `PrivateServer uint8 SFHubJudgementIgnatStory Max = 1`

  ...

* `PrivateServer uint8 ReddMinesPlayerThief Max = 1`

  ...

* `PrivateServer uint8 ReddDocMedicals Max = 100`

  ...

* `PrivateServer uint8 NcrWestinPills Max = 2`

  ...

* `PrivateServer uint8 SFHubbStatus Max = 9`

  ...

* `PrivateServer uint8 SFInvasionSandbagsTaken Max = 6`

  ...

* `PrivateServer uint8 SFInvasionSandbagsGiven Max = 50`

  ...

* `PrivateServer uint8 SFImperatorCancelNum Max = 4`

  ...

* `PrivateServer uint8 VCShiComputerAccess Max = 1`

  ...

* `PrivateServer uint8 TribManotaStory Max = 1`

  ...

* `PrivateServer uint8 VCKnowsAboutDelivery Max = 1`

  ...

* `PrivateServer uint8 VCCitizenship Max = 1`

  ...

* `PrivateServer uint8 VCHartmanFightStatus Max = 3`

  ...

* `PrivateServer uint8 VCFreshBloodCounter Max = 3`

  ...

* `PrivateServer uint8 VCForgeryWitnessInhome Max = 1`

  ...

* `PrivateServer uint8 VCLynetOrMaclure Max = 2`

  ...

* `PrivateServer uint8 VCMutCharleyHired Max = 1`

  ...

* `PrivateServer uint8 VCCavesCounter Max = 4`

  ...

* `PrivateServer uint8 VCPrisonerBulled Max = 3`

  ...

* `PrivateServer uint8 VCLynettTalk Max = 1`

  ...

* `PrivateServer uint8 VCPatrolCounter Max = 3`

  ...

* `PrivateServer uint NpcDialogTimeWait`

  ...

* `PrivateServer int8 KlamTrappersRadaway`

  ...

* `Protected uint[] HoloInfo`

  ...

* `PrivateServer hstring[] FavoriteItemPid`

  ...

* `Protected bool IsNoFavoriteItem`

  ...

* `Protected int Level`

  ...

* `Protected int KarmaVoting`

  ...

* `Protected bool IsNoPvp`

  ...

* `Protected bool IsEndCombat`

  ...

* `Protected bool IsDlgScriptBarter`

  ...

* `Protected bool IsUnlimitedAmmo`

  ...

* `Protected bool IsNoDrop`

  ...

* `Protected bool IsNoLooseLimbs`

  ...

* `Protected bool IsDeadAges`

  ...

* `Protected bool IsNoHeal`

  ...

* `Protected bool IsInvulnerable`

  ...

* `Protected bool IsSpecialDead`

  ...

* `Protected bool IsRangeHth`

  ...

* `Protected bool IsNoKnock`

  ...

* `Protected bool IsNoSupply`

  ...

* `Protected bool IsNoKarmaOnKill`

  ...

* `Protected bool IsBarterOnlyCash`

  ...

* `VirtualPrivateServer int BarterCoefficient`

  ...

* `Protected TransferTypes TransferType`

  ...

* `Protected ident TransferContainerId`

  ...

* `Public bool IsNoBarter`

  ...

* `Public bool IsNoSteal`

  675

* `Public bool IsNoLoot`

  ...

* `Protected bool IsNoPush`

  ...

* `VirtualProtected uint ItemsWeight`

  ...

* `VirtualProtected int ActionPoints`

  ...

* `PrivateCommon int CurrentAp`

  ...

* `Protected int BagId`

  ...

* `PrivateServer ident LastWeaponId`

  ...

* `PrivateServer bool LastWeaponNotFound`

  ...

* `ProtectedModifiable hstring HandsProtoItemId`

  ...

* `ProtectedModifiable uint8 HandsItemMode`

  ...

* `PrivateServer uint8 LastWeaponUse`

  ...

* `Protected bool IsNoItemGarbager`

  ...

* `PrivateServer ident TownSupplyVictimId`

  Town supply  
  Author: cvet

* `PrivateServer ident TownSupplyHostileId`

  ...

* `PrivateServer uint8[] TravellerRoute`

  Author: rifleman17  
  Скрипт для реализации нпц-путешественников. (Beta)  
  НПЦ перемещаются между различными городами по глобальной карте в случайном порядке.  
  НПЦ либо честно идет по глобальной карте по прямой, и при заходе на энкаунтер разбирается с мобами, затем продолжает движение  
  Либо просто телепортируется в следующую точку маршрута.  
  НПЦ находится в каждом городе определенное время.  
  Список точек маршрута и настройки нпц сохраняются в TravellerRoute для каждого нпц.  
  Следующая точка маршрута выбирается в момент достижения предыдущей.  
  Существует проблема: путешественник может застрять в некоем месте, например, на береговой линии, если пойдет из СФ в ароййо  
  Поэтому при отправлении засекаем время начала движения, и назначаем время телепорта путешественника в точку назначения через 1 игровой месяц

* `Protected uint8 V13Dclaw Group = Quests Quest = 4900 Max = 5`

  //Old script name: V13DClawLib.fosh. Patched 01.10 22:41:24  
  Author: Sufir

* `Protected uint8 VCAmandaHelpJoshua Group = Quests Quest = 8836 Max = 9`

  ...

* `PrivateServer uint8 VCMailRemembered Max = 1`

  ...

* `PrivateServer uint8 VCBeautyHoloRemembered Max = 1`

  ...

* `PrivateServer uint VCityCommonBarkusTimeSay`

  ...

* `PrivateServer ident[] SquadMarchSquads`

  Система отдачи приказов, выполнения для нпц и контроля выполнения для игроков  
  Приказы на перемещения по карте

* `PrivateServer uint8[] SquadMarchQueue`

  ...

* `Protected uint8 VCHartmanMarch Group = Quests Quest = 8823 Max = 4`

  //Old script name: VcGuardsman.fos. Patched 01.10 21:59:42  
  //// FOS Server  
  Author: rifleman17  
  Скрипты для квестовой линии "Гвардеец Города-Убежища"

* `Protected uint8 VCHartmannClearCave Group = Quests Quest = 8832 Max = 4`

  ...

* `PrivateServer uint8 VCDeadAllyCounter Max = 10`

  ...

* `PrivateServer uint8 VCGuardRank Max = 4`

  ...

* `PrivateServer ident VCReconCaveId`

  ...

* `PrivateServer ident VCGuardsmanTriggerPlayerId`

  ...

* `Protected uint8 VCLynettArest Group = Quests Quest = 8843 Max = 5`

  Author: rifleman17  
  Скрипты для квестовой цепочки на поддержку Линетт. ГУ.

* `Protected uint8 VCLynettForgery Group = Quests Quest = 8845 Max = 6`

  ...

* `PrivateServer ident VCLynettPrisonerId`

  ...

* `PrivateServer int ReddingMortonBrothers`

  ...

* `PrivateServer uint8 SpecialEncounterBaxChurch Max = 1`

  ...

* `PrivateServer uint8 SpecialEncounteTim Max = 1`

  ...

* `PrivateServer uint8 RacingSneakersTrap Max = 1`

  ...

* `PrivateServer uint8 SpecialEncounterBridge Max = 1`

  ...

* `PrivateServer uint8 SpecialEncounterHoly1 Max = 1`

  ...

* `PrivateServer uint8 SpecialEncounterHoly2 Max = 1`

  ...

* `PrivateServer uint8 SpecialEncounterToxic Max = 1`

  ...

* `PrivateServer uint8 SpecialEncounterPariah Max = 1`

  ...

* `PrivateServer uint8 SpecialEncounterBrahmin Max = 1`

  ...

* `PrivateServer uint8 SpecialEncounterWhale Max = 1`

  ...

* `PrivateServer uint8 SpecialEncounterHead Max = 1`

  ...

* `PrivateServer uint8 SpecialEncounterShuttle Max = 1`

  ...

* `PrivateServer uint8 SpecialEncounterGuardian Max = 1`

  ...

* `PrivateServer uint8 SpecialEncounterWoodsman Max = 1`

  ...

* `PrivateServer uint8 SpecialEncounterUnwashed Max = 1`

  ...

* `PrivateServer uint8 SpecialEncounterTeleport Max = 2`

  ...

* `PrivateServer uint8 SpecialWastelandChildren Max = 1`

  ...

* `PrivateServer uint8 SpecialEncounterKotw Max = 3`

  ...

* `PrivateServer uint8 SpecialSoldierHolo Max = 3`

  ...

* `PrivateServer uint8 SpecialTrapperHolo Max = 3`

  ...

* `PrivateServer uint8 SpecialDollHolo Max = 3`

  ...

* `PrivateServer uint8 SpecialEncounterZergLaboratory Max = 3`

  ...

* `PrivateServer uint8 SpecialEncounterDoughnutWarehouse Max = 3`

  ...

* `PrivateServer uint8 SpecialEncounterAtomChurch Max = 3`

  ...

* `PrivateServer int GeckoFindWoody`

  ...

* `PrivateServer uint8 NcrDappoLostCCtatus Max = 5`

  ...

### Critter server events

* `OnIdle()`

  ...

* `OnFinish()`

  ...

* `OnCritterAppeared(Critter appearedCr)`

  ...

* `OnCritterAppearedDist1(Critter appearedCr)`

  ...

* `OnCritterAppearedDist2(Critter appearedCr)`

  ...

* `OnCritterAppearedDist3(Critter appearedCr)`

  ...

* `OnCritterDisappeared(Critter disappearedCr)`

  ...

* `OnCritterDisappearedDist1(Critter disappearedCr)`

  ...

* `OnCritterDisappearedDist2(Critter disappearedCr)`

  ...

* `OnCritterDisappearedDist3(Critter disappearedCr)`

  ...

* `OnItemOnMapAppeared(Item item, Critter dropper)`

  ...

* `OnItemOnMapDisappeared(Item item, Critter picker)`

  ...

* `OnItemOnMapChanged(Item item)`

  ...

* `OnTalk(Critter playerCr, bool begin, uint talkers)`

  ...

* `OnBarter(Critter playerCr, bool begin, uint barterCount)`

  ...

* `OnMoveItem(Item item, CritterItemSlot fromSlot)`

  ...

* `OnDropItem(Item item)`

  ...

* `OnSomeCritterMoveItem(Critter cr, Item item, CritterItemSlot fromSlot)`

  ...

* `OnSomeCritterDropItem(Critter cr, Item item)`

  ...

* `OnNpcPlaneBegin(int planeId, int reason, Critter someCr, Item someItem)`

  ...

* `OnNpcPlaneEnd(int planeId, int reason, Critter someCr, Item someItem)`

  ...

* `OnNpcPlaneRun(int planeId, int reason, any& result0, any& result1, any& result2)`

  ...

* `OnPlayerSaidTextFromScenery(int sceneryPid, uint16 hexX, uint16 hexY, string text)`

  ...

* `OnMessage(Critter sender, int msg, any value)`

  ...

* `OnUseItem(Item item, uint param)`

  ...

* `OnUseItemOn(Item item, Critter onCritter, Item onItem, StaticItem onScenery, uint param)`

  ...

* `OnSomeUseItemOnMe(Critter whoUse, Item item, uint param)`

  ...

* `OnSomeCritterUseItem(Critter fromCr, Item item, Critter onCritter, Item onItem, StaticItem onScenery, uint param) Deferred`

  ...

* `OnUseSkill(CritterProperty skill)`

  ...

* `OnUseSkillOn(CritterProperty skill, Critter onCritter, Item onItem, StaticItem onScenery)`

  ...

* `OnSomeUseSkillOnMe(Critter whoUse, CritterProperty skill)`

  ...

* `OnSomeCritterUseSkill(Critter fromCr, CritterProperty skill, Critter onCritter, Item onItem, StaticItem onScenery) Deferred`

  ...

* `OnAttack(Critter target, Item weapon, uint8 weaponMode, ProtoItem ammo)`

  ...

* `OnAttacked(Critter attacker)`

  ...

* `OnSomeCritterAttack(Critter attacker, Critter target, Item weapon, uint8 weaponMode, ProtoItem ammo)`

  ...

* `OnSomeCritterAttacked(Critter target, Critter attacker)`

  ...

* `OnStealing(Critter thief, Item item, uint itemCount)`

  ...

* `OnSomeCritterStealing(Critter thief, Critter fromCr, Item item, uint count)`

  ...

* `OnKill(Critter victim)`

  ...

* `OnDead(Critter killer)`

  ...

* `OnSomeCritterDead(Critter killed, Critter killer) Deferred`

  ...

* `OnRespawn()`

  ...

* `OnGlobalMapProcess(int type, Item car, float x, float y, float toX, float toY, float speed, uint encounterDescriptor, bool waitForAnswer)`

  ...

* `OnGlobalMapInvite(Item car, uint encounterDescriptor, int combatMode, ident mapId, uint16 hexX, uint16 hexY, uint8 dir)`

  ...

### Critter server methods

* `void SetupScript(init-Critter initFunc)`

  ...

* `void SetupScriptEx(hstring initFunc)`

  ...

* `bool IsMoving()`

  ...

* `Player GetPlayer() ExcludeInSingleplayer`

  ...

* `Map GetMap()`

  ...

* `void TransitToHex(uint16 hx, uint16 hy, uint8 dir)`

  ...

* `void TransitToMap(Map map, uint16 hx, uint16 hy, uint8 dir)`

  ...

* `void TransitToMap(Map map, uint16 hx, uint16 hy, uint8 dir, bool force_hex)`

  ...

* `void TransitToGlobal()`

  ...

* `void TransitToGlobalWithGroup(Critter[] group)`

  ...

* `void TransitToGlobalGroup(Critter globalCr)`

  ...

* `bool IsAlive()`

  ...

* `bool IsKnockout()`

  ...

* `bool IsDead()`

  ...

* `void RefreshView()`

  ...

* `void ViewMap(Map map, uint look, uint16 hx, uint16 hy, uint8 dir)`

  ...

* `void Say(uint8 howSay, string text)`

  ...

* `void SayMsg(uint8 howSay, TextPackName textPack, uint numStr)`

  ...

* `void SayMsg(uint8 howSay, TextPackName textPack, uint numStr, string lexems)`

  ...

* `void SetDir(uint8 dir)`

  ...

* `void SetDirAngle(int16 dir_angle)`

  ...

* `Critter[] GetCritters(bool lookOnMe, CritterFindType findType)`

  ...

* `Critter[] GetTalkingCritters()`

  ...

* `uint GetTalkingCrittersCount()`

  ...

* `Critter[] GetGlobalMapGroupCritters()`

  ...

* `bool IsSee(Critter cr)`

  ...

* `bool IsSeenBy(Critter cr)`

  ...

* `bool IsSee(Item item)`

  ...

* `uint CountItem(hstring protoId)`

  ...

* `void DestroyItem(hstring pid)`

  ...

* `void DestroyItem(hstring pid, uint count)`

  ...

* `Item AddItem(hstring pid, uint count)`

  ...

* `Item GetItem(ident itemId)`

  ...

* `Item GetItem(hstring protoId)`

  ...

* `Item GetItem(ItemComponent component)`

  ...

* `Item GetItem(ItemProperty property, int propertyValue)`

  ...

* `Item[] GetItems()`

  ...

* `Item[] GetItems(ItemComponent component)`

  ...

* `Item[] GetItems(ItemProperty property, int propertyValue)`

  ...

* `Item[] GetItems(hstring protoId)`

  ...

* `void ChangeItemSlot(ident itemId, CritterItemSlot slot)`

  ...

* `void SetCondition(CritterCondition cond, CritterActionAnim actionAnim, AbstractItem contextItem)`

  ...

* `void CloseDialog()`

  ...

* `void Action(CritterAction action, int actionData, AbstractItem contextItem)`

  ...

* `void Animate(CritterStateAnim stateAnim, CritterActionAnim actionAnim, AbstractItem contextItem, bool clearSequence, bool delayPlay) ExcludeInSingleplayer`

  ...

* `void SetConditionAnims(CritterCondition cond, CritterStateAnim stateAnim, CritterActionAnim actionAnim)`

  ...

* `void PlaySound(string soundName, bool sendSelf)`

  ...

* `bool IsKnownLocation(ident locId)`

  ...

* `void SetKnownLocation(ident locId)`

  ...

* `void RemoveKnownLocation(ident locId)`

  ...

* `void SetFog(uint16 zoneX, uint16 zoneY, int fog)`

  ...

* `int GetFog(uint16 zoneX, uint16 zoneY)`

  ...

* `void SendItems(Item[] items)`

  ...

* `void SendItems(Item[] items, bool owned, bool withInnerEntities, any contextParam)`

  ...

* `void Disconnect() ExcludeInSingleplayer`

  ...

* `bool IsOnline() ExcludeInSingleplayer`

  ...

* `void MoveToCritter(Critter target, uint cut, uint speed)`

  ...

* `void MoveToHex(uint16 hx, uint16 hy, uint cut, uint speed)`

  ...

* `MovingState GetMovingState()`

  ...

* `MovingState GetMovingState(ident& gagId)`

  ...

* `void StopMoving()`

  ...

* `void ChangeMovingSpeed(int speed)`

  ...

* `void AttachToCritter(Critter cr)`

  ...

* `void DetachFromCritter()`

  ...

* `void DetachAllCritters()`

  ...

* `Critter[] GetAttachedCritters()`

  ...

* `void AddTimeEvent(ScriptFunc-uint, Critter, any, uint& func, tick_t duration, any identifier)`

  ...

* `void AddTimeEvent(ScriptFunc-uint, Critter, any, uint& func, tick_t duration, any identifier, uint rate)`

  ...

* `uint GetTimeEvents(any identifier)`

  ...

* `uint GetTimeEvents(any identifier, uint[]& indexes, tick_t[]& durations, uint[]& rates)`

  ...

* `uint GetTimeEvents(any[] findIdentifiers, any[]& identifiers, uint[]& indexes, tick_t[]& durations, uint[]& rates)`

  ...

* `void ChangeTimeEvent(uint index, tick_t newDuration, uint newRate)`

  ...

* `void RemoveTimeEvent(uint index)`

  ...

* `uint RemoveTimeEvents(any identifier)`

  ...

* `uint RemoveTimeEvents(any[] identifiers)`

  ...

* `tick_t GetPlayerOfflineTime()`

  ...

* `void RefreshDialogTime()`

  ...

* `bool IsFree()`

  ...

* `bool IsBusy()`

  ...

* `void Wait(uint ms)`

  ...

### Critter client methods

* `void SetName(string name)`

  ...

* `bool IsOffline() ExcludeInSingleplayer`

  ...

* `bool IsAlive() ExcludeInSingleplayer`

  ...

* `bool IsKnockout() ExcludeInSingleplayer`

  ...

* `bool IsDead() ExcludeInSingleplayer`

  ...

* `bool IsOnMap()`

  ...

* `bool IsMoving() ExcludeInSingleplayer`

  ...

* `bool IsModel()`

  ...

* `bool IsAnimAvailable(CritterStateAnim stateAnim, CritterActionAnim actionAnim)`

  ...

* `bool IsAnimPlaying()`

  ...

* `CritterStateAnim GetStateAnim()`

  ...

* `void Animate(CritterStateAnim stateAnim, CritterActionAnim actionAnim)`

  ...

* `void Animate(CritterStateAnim stateAnim, CritterActionAnim actionAnim, AbstractItem contextItem)`

  ...

* `void StopAnim()`

  ...

* `uint CountItem(hstring protoId) ExcludeInSingleplayer`

  ...

* `Item GetItem(ident itemId) ExcludeInSingleplayer`

  ...

* `Item GetItem(hstring protoId) ExcludeInSingleplayer`

  ...

* `Item GetItem(ItemComponent component) ExcludeInSingleplayer`

  ...

* `Item GetItem(ItemProperty property, int propertyValue) ExcludeInSingleplayer`

  ...

* `Item[] GetItems() ExcludeInSingleplayer`

  ...

* `Item[] GetItems(ItemComponent component) ExcludeInSingleplayer`

  ...

* `Item[] GetItems(ItemProperty property, int propertyValue) ExcludeInSingleplayer`

  ...

* `bool GetTextPos(int& x, int& y)`

  ...

* `void RunParticle(string particleName, hstring boneName, float moveX, float moveY, float moveZ)`

  ...

* `void AddAnimCallback(CritterStateAnim stateAnim, CritterActionAnim actionAnim, float normalizedTime, callback-Critter animCallback)`

  ...

* `bool GetBonePos(hstring boneName, int& boneX, int& boneY)`

  ...

* `void MoveToHex(uint16 hx, uint16 hy, int ox, int oy, uint speed)`

  ...

* `void MoveToDir(int dir, uint speed)`

  ...

* `void StopMove()`

  ...

* `void ChangeDir(uint8 dir)`

  ...

* `void ChangeDirAngle(int16 dirAngle)`

  ...

* `uint8 GetAlpha()`

  ...

* `void SetAlpha(uint8 alpha)`

  ...

* `void SetContour(ContourType contour)`

  ...

* `void MoveItemLocally(ident itemId, uint itemCount, ident swapItemId, CritterItemSlot toSlot)`

  ...

* `bool IsFree()`

  ...

* `bool IsBusy()`

  ...

* `void Wait(uint ms)`

  ...

## Map entity

  ...

* `Target: Server/Client`
* `Built-in: Yes`
* `Singleton: No`
* `Has proto: Yes`
* `Has statics: No`
* `Has abstract: No`

### Map properties

* `PrivateCommon ident CustomHolderId ReadOnly IsCommon`

  ...

* `PrivateCommon hstring CustomHolderEntry ReadOnly IsCommon`

  ...

* `PrivateServer ident[] InnerEntityIds ReadOnly IsCommon`

  ...

* `PrivateServer hstring InitScript ScriptFuncType = MapInit`

  ...

* `PrivateServer ident LocId ReadOnly`

  ...

* `PrivateServer uint LocMapIndex ReadOnly`

  ...

* `PrivateServer ident[] CritterIds ReadOnly`

  ...

* `PrivateServer ident[] ItemIds ReadOnly`

  ...

* `PrivateCommon uint16 Width ReadOnly`

  ...

* `PrivateCommon uint16 Height ReadOnly`

  ...

* `PrivateServer uint LoopTime1`

  Todo: exclude map properties from engine:

* `PrivateServer uint LoopTime2`

  ...

* `PrivateServer uint LoopTime3`

  ...

* `PrivateServer uint LoopTime4`

  ...

* `PrivateServer uint LoopTime5`

  ...

* `PrivateClient uint16 WorkHexX ReadOnly`

  ...

* `PrivateClient uint16 WorkHexY ReadOnly`

  ...

* `PrivateClient float SpritesZoom ReadOnly`

  ...

* `PrivateCommon int CurDayTime`

  ...

* `PrivateCommon int[] DayTime`

  ...

* `PrivateCommon uint8[] DayColor`

  ...

* `PrivateServer ident KlamAldoId`

  ...

* `PrivateServer uint CasinoLimit`

  Author: cvet, rifleman17

* `PrivateServer uint CasinoTimeRenew`

  ...

* `PrivateServer uint=>uint8[] CompRiddleData`

  ...

* `PrivateServer ident=>uint[] ElevatorData`

  ...

* `PrivateServer uint=>uint[] EnergyBarierHitBonus`

  ...

* `PrivateServer uint=>any[] EnergyBarierTerminal`

  ...

* `PrivateServer uint=>any[] EnergyBarierTerminalInfo`

  ...

* `PrivateServer bool FighterPatternEnemySpotted`

  ...

* `PrivateServer uint=>uint FighterPatternDeadAllies`

  ...

* `PrivateServer uint=>uint FixBoyWorkBenchTimeout`

  Таймаут на крафт для станка. Если равен = 0 значит истек.

* `PrivateServer uint=>uint FixBoyWorkBenchCharges`

  Число зарядов станка если =0 запускается таймаут на обновление.

* `PrivateServer ident HostileLQPlayerId`

  ...

* `PrivateServer uint HostileLQVarNum`

  ...

* `PrivateServer bool SFLabHonomerInside`

  ...

* `PrivateServer bool QIntroInitiated`

  ...

* `PrivateServer bool IntroDoorsOpen`

  ...

* `PrivateServer int RainCapacity`

  Author: cvet  
  Coast generic encounters  
  Rain processed

* `PrivateServer bool MapCoastRainUp`

  ...

* `PrivateServer ident GeckCityDoor`

  ...

* `PrivateServer uint GeckCityCharges`

  ...

* `PrivateServer uint GeckCityTimeBroken`

  ...

* `PrivateServer int MapRadiationMinDose`

  Author: cvet  
  Radiation generic map

* `PrivateServer int MapRadiationMaxDose`

  ...

* `PrivateServer ident NcrMichaelCritterId`

  ...

* `PrivateServer uint NcrSiegeComplexity`

  ...

* `PrivateServer bool IsNoPvPMap`

  ...

* `PrivateServer uint8[] NpcRevengeData`

  ...

* `PrivateServer uint=>uint ResourcesData`

  ...

* `PrivateServer bool NoLogOut`

  Todo: добавить поддержку Map::NoLogOut

* `PrivateServer uint VCLastBarDialog`

  ...

* `PrivateServer bool WarehouseTurretActive`

  Author: cvet

### Map server events

* `OnFinish()`

  ...

* `OnLoop()`

  ...

* `OnLoopEx(int loopIndex)`

  ...

* `OnCheckLook(Critter cr, Critter target)`

  ...

* `OnCheckTrapLook(Critter cr, Item item)`

  ...

* `OnCritterIn(Critter cr)`

  ...

* `OnCritterOut(Critter cr)`

  ...

* `OnCritterDead(Critter cr, Critter killer)`

  ...

* `OnLoopEx1()`

  ...

* `OnLoopEx2()`

  ...

* `OnLoopEx3()`

  ...

* `OnLoopEx4()`

  ...

### Map server methods

* `void SetupScript(init-Map initFunc)`

  ...

* `void SetupScriptEx(hstring initFunc)`

  ...

* `Location GetLocation()`

  ...

* `Item AddItem(uint16 hx, uint16 hy, hstring protoId, uint count)`

  ...

* `Item AddItem(uint16 hx, uint16 hy, hstring protoId, uint count, ItemProperty=>int props)`

  ...

* `Item GetItem(ident itemId)`

  ...

* `Item GetItem(uint16 hx, uint16 hy, hstring pid)`

  ...

* `Item GetItem(uint16 hx, uint16 hy, ItemComponent component)`

  ...

* `Item GetItem(uint16 hx, uint16 hy, ItemProperty property, int propertyValue)`

  ...

* `Item GetItem(uint16 hx, uint16 hy, uint radius, ItemComponent component)`

  ...

* `Item GetItem(uint16 hx, uint16 hy, uint radius, ItemProperty property, int propertyValue)`

  ...

* `Item[] GetItems()`

  ...

* `Item[] GetItems(uint16 hx, uint16 hy)`

  ...

* `Item[] GetItems(uint16 hx, uint16 hy, uint radius)`

  ...

* `Item[] GetItems(uint16 hx, uint16 hy, uint radius, hstring pid)`

  ...

* `Item[] GetItems(hstring pid)`

  ...

* `Item[] GetItems(ItemComponent component)`

  ...

* `Item[] GetItems(ItemProperty property, int propertyValue)`

  ...

* `Item[] GetItems(uint16 hx, uint16 hy, ItemComponent component)`

  ...

* `Item[] GetItems(uint16 hx, uint16 hy, ItemProperty property, int propertyValue)`

  ...

* `Item[] GetItems(uint16 hx, uint16 hy, uint radius, ItemComponent component)`

  ...

* `Item[] GetItems(uint16 hx, uint16 hy, uint radius, ItemProperty property, int propertyValue)`

  ...

* `StaticItem GetStaticItem(ident id)`

  ...

* `StaticItem GetStaticItem(uint16 hx, uint16 hy, hstring pid)`

  ...

* `StaticItem[] GetStaticItems(uint16 hx, uint16 hy)`

  ...

* `StaticItem[] GetStaticItems(uint16 hx, uint16 hy, uint radius, hstring pid)`

  ...

* `StaticItem[] GetStaticItems(hstring pid)`

  ...

* `StaticItem[] GetStaticItems(ItemComponent component)`

  ...

* `StaticItem[] GetStaticItems(ItemProperty property, int propertyValue)`

  ...

* `StaticItem[] GetStaticItems()`

  ...

* `Critter GetCritter(ident crid)`

  ...

* `Critter GetCritter(uint16 hx, uint16 hy)`

  ...

* `Critter GetCritter(CritterComponent component, CritterFindType findType)`

  ...

* `Critter GetCritter(CritterProperty property, int propertyValue, CritterFindType findType)`

  ...

* `Critter[] GetCritters(uint16 hx, uint16 hy, uint radius, CritterFindType findType)`

  ...

* `Critter[] GetCritters(CritterFindType findType)`

  ...

* `Critter[] GetCritters(hstring pid, CritterFindType findType)`

  ...

* `Critter[] GetCritters(CritterComponent component, CritterFindType findType)`

  ...

* `Critter[] GetCritters(CritterProperty property, int propertyValue, CritterFindType findType)`

  ...

* `Critter[] GetCrittersInPath(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy, float angle, uint dist, CritterFindType findType)`

  ...

* `Critter[] GetCrittersInPath(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy, float angle, uint dist, CritterFindType findType, uint16& preBlockHx, uint16& preBlockHy, uint16& blockHx, uint16& blockHy)`

  ...

* `Critter[] GetCrittersWhoSeeHex(uint16 hx, uint16 hy, CritterFindType findType)`

  ...

* `Critter[] GetCrittersWhoSeePath(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy, CritterFindType findType)`

  ...

* `Critter[] GetCrittersSeeing(Critter cr, bool lookOnThem, CritterFindType findType)`

  ...

* `Critter[] GetCrittersSeeing(Critter[] critters, bool lookOnThem, CritterFindType findType)`

  ...

* `void GetHexInPath(uint16 fromHx, uint16 fromHy, uint16& toHx, uint16& toHy, float angle, uint dist)`

  ...

* `void GetWallHexInPath(uint16 fromHx, uint16 fromHy, uint16& toHx, uint16& toHy, float angle, uint dist)`

  ...

* `uint GetPathLength(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy, uint cut)`

  ...

* `uint GetPathLength(Critter cr, uint16 toHx, uint16 toHy, uint cut)`

  ...

* `Critter AddNpc(hstring protoId, uint16 hx, uint16 hy, uint8 dir)`

  ...

* `Critter AddNpc(hstring protoId, uint16 hx, uint16 hy, uint8 dir, CritterProperty=>int props)`

  ...

* `Critter AddNpc(hstring protoId, uint16 hx, uint16 hy, uint8 dir, CritterProperty=>any props)`

  ...

* `bool IsHexMovable(uint16 hexX, uint16 hexY)`

  ...

* `bool IsHexesMovable(uint16 hexX, uint16 hexY, uint radius)`

  ...

* `bool IsHexShootable(uint16 hexX, uint16 hexY)`

  ...

* `void SetText(uint16 hexX, uint16 hexY, ucolor color, string text)`

  ...

* `void SetTextMsg(uint16 hexX, uint16 hexY, ucolor color, TextPackName textPack, uint strNum)`

  ...

* `void SetTextMsg(uint16 hexX, uint16 hexY, ucolor color, TextPackName textPack, uint strNum, string lexems)`

  ...

* `void RunEffect(hstring effPid, uint16 hx, uint16 hy, uint radius)`

  ...

* `void RunFlyEffect(hstring effPid, Critter fromCr, Critter toCr, uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy)`

  ...

* `bool CheckPlaceForItem(uint16 hx, uint16 hy, hstring pid)`

  ...

* `void BlockHex(uint16 hx, uint16 hy, bool full)`

  ...

* `void UnblockHex(uint16 hx, uint16 hy)`

  Todo: notify clients about manual hex block

* `void PlaySound(string soundName)`

  ...

* `void PlaySound(string soundName, uint16 hx, uint16 hy, uint radius)`

  ...

* `void Regenerate()`

  ...

* `bool MoveHexByDir(uint16& hx, uint16& hy, uint8 dir, uint steps)`

  ...

* `void VerifyTrigger(Critter cr, uint16 hx, uint16 hy, uint8 dir)`

  ...

### Map client methods

* `void DrawMap()`

  ...

* `void DrawMapTexts()`

  ...

* `void Message(string text, uint16 hx, uint16 hy, tick_t showTime, ucolor color, bool fade, int endOx, int endOy)`

  ...

* `void DrawMapSprite(MapSpriteData mapSpr)`

  ...

* `void RebuildFog()`

  ...

* `Item GetItem(ident itemId) ExcludeInSingleplayer`

  ...

* `Item[] GetVisibleItems()`

  ...

* `Item[] GetVisibleItemsOnHex(uint16 hx, uint16 hy)`

  ...

* `Critter GetCritter(ident critterId) ExcludeInSingleplayer`

  ...

* `Critter[] GetCritters() ExcludeInSingleplayer`

  ...

* `Critter[] GetCritters(CritterFindType findType) ExcludeInSingleplayer`

  ...

* `Critter[] GetCritters(hstring pid, CritterFindType findType) ExcludeInSingleplayer`

  ...

* `Critter[] GetCritters(uint16 hx, uint16 hy, uint radius, CritterFindType findType) ExcludeInSingleplayer`

  ...

* `Critter[] GetCrittersInPath(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy, float angle, uint dist, CritterFindType findType) ExcludeInSingleplayer`

  ...

* `Critter[] GetCrittersWithBlockInPath(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy, float angle, uint dist, CritterFindType findType, uint16& preBlockHx, uint16& preBlockHy, uint16& blockHx, uint16& blockHy) ExcludeInSingleplayer`

  ...

* `void GetHexInPath(uint16 fromHx, uint16 fromHy, uint16& toHx, uint16& toHy, float angle, uint dist) ExcludeInSingleplayer`

  ...

* `uint8[] GetPath(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy, uint cut) ExcludeInSingleplayer`

  ...

* `uint8[] GetPath(Critter cr, uint16 toHx, uint16 toHy, uint cut) ExcludeInSingleplayer`

  ...

* `uint GetPathLength(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy, uint cut) ExcludeInSingleplayer`

  ...

* `uint GetPathLength(Critter cr, uint16 toHx, uint16 toHy, uint cut) ExcludeInSingleplayer`

  ...

* `void MoveScreenToHex(uint16 hx, uint16 hy, uint speed, bool canStop)`

  ...

* `void MoveScreenOffset(int ox, int oy, uint speed, bool canStop)`

  ...

* `void LockScreenScroll(Critter cr, bool softLock, bool unlockIfSame)`

  ...

* `bool MoveHexByDir(uint16& hx, uint16& hy, uint8 dir, uint steps) ExcludeInSingleplayer`

  ...

* `Item GetTile(uint16 hx, uint16 hy, bool roof)`

  ...

* `Item GetTile(uint16 hx, uint16 hy, bool roof, uint8 layer)`

  ...

* `Item[] GetTiles(uint16 hx, uint16 hy, bool roof)`

  ...

* `void RedrawMap()`

  ...

* `void ChangeZoom(float targetZoom)`

  ...

* `bool GetHexScreenPos(uint16 hx, uint16 hy, int& x, int& y)`

  ...

* `bool GetHexAtScreenPos(int x, int y, uint16& hx, uint16& hy)`

  ...

* `bool GetHexAtScreenPos(int x, int y, uint16& hx, uint16& hy, int& ox, int& oy)`

  ...

* `Item GetItemAtScreenPos(int x, int y)`

  ...

* `Critter GetCritterAtScreenPos(int x, int y)`

  ...

* `Critter GetCritterAtScreenPos(int x, int y, int extraRange)`

  ...

* `Entity GetEntityAtScreenPos(int x, int y)`

  ...

* `bool IsMapHexPassed(uint16 hx, uint16 hy)`

  ...

* `bool IsMapHexShooted(uint16 hx, uint16 hy)`

  ...

* `void SetShootBorders(bool enabled, uint dist)`

  ...

* `SpritePattern RunSpritePattern(string spriteName, uint spriteCount)`

  ...

* `void SetCursorPos(Critter cr, int mouseX, int mouseY, bool showSteps, bool forceRefresh)`

  ...

* `void SetCrittersContour(ContourType contour)`

  ...

* `void ResetCritterContour()`

  ...

## Location entity

  ...

* `Target: Server/Client`
* `Built-in: Yes`
* `Singleton: No`
* `Has proto: Yes`
* `Has statics: No`
* `Has abstract: No`

### Location properties

* `PrivateCommon ident CustomHolderId ReadOnly IsCommon`

  ...

* `PrivateCommon hstring CustomHolderEntry ReadOnly IsCommon`

  ...

* `PrivateServer ident[] InnerEntityIds ReadOnly IsCommon`

  ...

* `PrivateServer hstring InitScript ScriptFuncType = LocationInit`

  Todo: implement Location InitScript

* `PrivateServer ident[] MapIds ReadOnly`

  ...

* `PrivateServer hstring[] MapProtos ReadOnly`

  ...

* `PrivateServer hstring[] MapEntrances ReadOnly`

  Todo: exclude location properties from engine:

* `PrivateServer hstring EntranceScript ScriptFuncType = LocationEntrance`

  ...

* `PrivateServer uint16 WorldX`

  ...

* `PrivateServer uint16 WorldY`

  ...

* `PrivateServer uint16 Radius`

  ...

* `PrivateServer bool Hidden`

  ...

* `PrivateServer ucolor Color`

  ...

* `PrivateServer bool GECachesCacheChecked`

  ...

* `PrivateServer uint8 RacingCheckpointNumber Max = 14`

  ...

* `PrivateServer ident StorehouseContId`

  Author: rifleman17  
  Хранилище отобранных у игроков и других нпц предметов на глобальной карте

* `PrivateServer uint MaxPlayers`

  ...

* `PrivateServer bool AutoGarbage`

  ...

* `PrivateServer bool GeckVisible`

  Todo: improve GeckVisible mechanics

* `PrivateServer hstring[] Automaps`

  ...

* `PrivateServer ident[] GeckCityMembers`

  ...

* `PrivateServer ident GeckCityLeader`

  ...

* `PrivateServer ident LocModVampireFarmQuesterId`

  ...

* `PrivateServer bool LocDefendersHostile`

  ...

* `PrivateServer ident NRWriGuardDead`

  ...

* `PrivateServer bool NRKidnapAllMarodeursDead`

  ...

* `PrivateServer uint LastLootTransfer`

  ...

* `PrivateServer bool SeAndroidPlayerIn`

  ...

* `PrivateServer ident SeAndroidPlayerId`

  ...

* `PrivateServer bool SeAndroidMinesTriggered`

  ...

* `PrivateServer uint SeAndroidTFounded`

  ...

* `PrivateServer uint SeAndroidLFounded`

  ...

* `PrivateServer uint SeAndroidDFounded`

  ...

* `PrivateServer uint SeAndroidRFounded`

  ...

* `PrivateServer uint SeAndroidPFounded`

  ...

* `PrivateServer uint SeAndroidCFounded`

  ...

* `PrivateServer uint8 SiloMissileLaunched Max = 2`

  ...

* `PrivateServer bool IsEncounter`

  ...

### Location server events

* `OnFinish()`

  ...

### Location server methods

* `void SetupScript(init-Map initFunc)`

  ...

* `void SetupScriptEx(hstring initFunc)`

  ...

* `uint GetMapCount()`

  ...

* `Map GetMap(hstring mapPid)`

  ...

* `Map GetMapByIndex(uint index)`

  ...

* `Map[] GetMaps()`

  ...

* `void GetEntrance(uint entranceIndex, uint& mapIndex, hstring& entrance)`

  ...

* `uint GetEntrances(int[]& mapsIndex, hstring[]& entrances)`

  ...

* `void Regenerate()`

  ...

## Types

### VideoPlayback reference object

  ...

* `bool Stopped`

  ...

### MapSpriteData reference object

  ...

* `bool Valid`

  ...

* `uint SprId`

  ...

* `uint16 HexX`

  ...

* `uint16 HexY`

  ...

* `hstring ProtoId`

  ...

* `int OffsX`

  ...

* `int OffsY`

  ...

* `bool IsFlat`

  ...

* `bool NoLight`

  ...

* `DrawOrderType DrawOrder`

  ...

* `int DrawOrderHyOffset`

  ...

* `CornerType Corner`

  ...

* `bool DisableEgg`

  ...

* `ucolor Color`

  ...

* `ucolor ContourColor`

  ...

* `bool IsTweakOffs`

  ...

* `int TweakOffsX`

  ...

* `int TweakOffsY`

  ...

* `bool IsTweakAlpha`

  ...

* `uint8 TweakAlpha`

  ...

### SpritePattern reference object

  ...

* `bool Finished`

  ...

* `string SprName`

  ...

* `uint SprCount`

  ...

* `uint16 EveryHexX`

  ...

* `uint16 EveryHexY`

  ...

* `bool InteractWithRoof`

  ...

* `bool CheckTileProperty`

  ...

* `ItemProperty TileProperty`

  ...

* `int ExpectedTilePropertyValue`

  ...

* `void Finish()`

  ...

### ident value object

  ...

* `Alias to: uint`
* `Type: HardStrong`
* `Flags: HardStrong`

### tick_t value object

  ...

* `Alias to: uint`
* `Type: RelaxedStrong`
* `Flags: RelaxedStrong`

### ucolor value object

  Color type

* `Alias to: uint`
* `Type: HardStrong`
* `Flags: HardStrong`

## Enums

* `EffectType`

  ...

  - `None = 0`

  - `GenericSprite = 0x00000001`

  - `CritterSprite = 0x00000002`

  - `TileSprite = 0x00000004`

  - `RoofSprite = 0x00000008`

  - `RainSprite = 0x00000010`

  - `SkinnedMesh = 0x00000400`

  - `Interface = 0x00001000`

  - `ContourStrict = 0x00002000`

  - `ContourDynamic = 0x00004000`

  - `Font = 0x00010000`

  - `Primitive = 0x00100000`

  - `Light = 0x00200000`

  - `Fog = 0x00400000`

  - `FlushRenderTarget = 0x01000000`

  - `FlushPrimitive = 0x04000000`

  - `FlushMap = 0x08000000`

  - `FlushLight = 0x10000000`

  - `FlushFog = 0x20000000`

  - `Offscreen = 0x40000000`

* `DrawOrderType`

  ...

  - `Tile = 0`

  - `Tile1 = 1`

  - `Tile2 = 2`

  - `Tile3 = 3`

  - `Tile4 = 4`

  - `HexGrid = 5`

  - `FlatScenery = 8`

  - `Ligth = 9`

  - `DeadCritter = 10`

  - `FlatItem = 13`

  - `Track = 16`

  - `NormalBegin = 20`

  - `Scenery = 23`

  - `Item = 26`

  - `Critter = 29`

  - `Particles = 30`

  - `NormalEnd = 32`

  - `Roof = 33`

  - `Roof1 = 34`

  - `Roof2 = 35`

  - `Roof3 = 36`

  - `Roof4 = 37`

  - `RoofParticles = 38`

  - `Last = 39`

* `ContourType`

  ...

  - `None = 0`

  - `Red = 1`

  - `Yellow = 2`

  - `Custom = 3`

* `EggAppearenceType`

  ...

  - `None = 0`

  - `Always = 1`

  - `ByX = 2`

  - `ByY = 3`

  - `ByXAndY = 4`

  - `ByXOrY = 5`

* `CritterItemSlot`

  ...

  - `Inventory = 0`

  - `Main = 1`

  - `Outside = 255`

  - `Secondary = 2`

  - `Armor = 3`

* `CritterCondition`

  ...

  - `Alive = 0`

  - `Knockout = 1`

  - `Dead = 2`

* `CritterAction`

  Critter actions  
  Flags for chosen:  
  l - hardcoded local call  
  s - hardcoded server call  
  for all others critters actions call only server  
  flags actionExt item

  - `None = 0`

  - `MoveItem = 2`

  - `SwapItems = 3`

  - `DropItem = 5`

  - `Knockout = 16`

  - `StandUp = 17`

  - `Fidget = 18`

  - `Dead = 19`

  - `Connect = 20`

  - `Disconnect = 21`

  - `Respawn = 22`

  - `Refresh = 23`

  - `UseItem = 4`

  - `UseWeapon = 6`

  - `ReloadWeapon = 7`

  - `UseSkill = 8`

  - `PickItem = 9`

  - `PickCritter = 10`

  - `OperateContainer = 11`

  - `Barter = 12`

  - `Dodge = 13`

  - `Damage = 14`

  - `DamageForce = 15`

  - `UnloadWeapon = 24`

  - `PrepareWeapon = 25`

  - `FinishAttack = 26`

* `CritterStateAnim`

  ...

  - `None = 0`

  - `Unarmed = 1`

  - `Knife = 4`

  - `Club = 5`

  - `Hammer = 6`

  - `Spear = 7`

  - `Pistol = 8`

  - `SMG = 9`

  - `Shootgun = 10`

  - `HeavyRifle = 11`

  - `Minigun = 12`

  - `RocketLauncher = 13`

  - `Flamer = 14`

  - `Rifle = 15`

  - `Sword = 16`

  - `LongSword = 17`

  - `Axe = 18`

  - `Bow = 19`

* `CritterActionAnim`

  ...

  - `None = 0`

  - `Idle = 1`

  - `Walk = 3`

  - `WalkBack = 15`

  - `Limp = 4`

  - `Run = 5`

  - `RunBack = 16`

  - `TurnRight = 17`

  - `TurnLeft = 18`

  - `PanicRun = 6`

  - `SneakWalk = 7`

  - `SneakRun = 8`

  - `IdleProneFront = 86`

  - `DeadFront = 102`

  - `IdleStunned = 2`

  - `Stand = 10`

  - `Crouch = 11`

  - `Prone = 12`

  - `ShowWeapon = 20`

  - `HideWeapon = 21`

  - `PrepareWeapon = 22`

  - `TurnOffWeapon = 23`

  - `Fidget = 24`

  - `Climbing = 26`

  - `PickUp = 27`

  - `Use = 28`

  - `SwitchItems = 29`

  - `Reload = 30`

  - `Repair = 31`

  - `Loot = 35`

  - `Steal = 36`

  - `Push = 37`

  - `BeginCombat = 40`

  - `IdleCombat = 41`

  - `EndCombat = 42`

  - `PunchRight = 43`

  - `PunchLeft = 44`

  - `PunchCombo = 45`

  - `KickHi = 46`

  - `KickLo = 47`

  - `KickCombo = 48`

  - `Thrust1H = 49`

  - `Thrust2H = 50`

  - `Swing1H = 51`

  - `Swing2H = 52`

  - `Throw = 53`

  - `Single = 54`

  - `Burst = 55`

  - `Sweep = 56`

  - `Butt = 57`

  - `Flame = 58`

  - `NoRecoil = 59`

  - `DodgeFront = 70`

  - `DodgeBack = 71`

  - `DamageFront = 72`

  - `DamageBack = 73`

  - `DamageMulFront = 74`

  - `DamageMulBack = 75`

  - `WalkDamageFront = 76`

  - `WalkDamageBack = 77`

  - `LimpDamageFront = 78`

  - `LimpDamageBack = 79`

  - `RunDamageFront = 80`

  - `RunDamageBack = 81`

  - `KnockFront = 82`

  - `KnockBack = 83`

  - `LaydownFront = 84`

  - `LaydownBack = 85`

  - `IdleProneBack = 87`

  - `StandupFront = 88`

  - `StandupBack = 89`

  - `DamageProneFront = 90`

  - `DamageProneBack = 91`

  - `DamageMulProneFront = 92`

  - `DamageMulProneBack = 93`

  - `TwitchProneFront = 94`

  - `TwitchProneBack = 95`

  - `DeadProneFront = 100`

  - `DeadProneBack = 101`

  - `DeadBack = 103`

  - `DeadBloodySingle = 110`

  - `DeadBloodyBurst = 111`

  - `DeadBurst = 112`

  - `DeadPulse = 113`

  - `DeadPulseDust = 114`

  - `DeadLaser = 115`

  - `DeadFused = 116`

  - `DeadExplode = 117`

  - `DeadBurn = 118`

  - `DeadBurnRun = 119`

  - `Dance = 150`

* `CritterFindType`

  ...

  - `Any = 0`

  - `NonDead = 0x01`

  - `Dead = 0x02`

  - `Players = 0x10`

  - `Npc = 0x20`

  - `NonDeadPlayers = 0x11`

  - `DeadPlayers = 0x12`

  - `NonDeadNpc = 0x21`

  - `DeadNpc = 0x22`

* `ItemOwnership`

  ...

  - `MapHex = 0`

  - `CritterInventory = 1`

  - `ItemContainer = 2`

  - `Nowhere = 3`

* `ContainerItemStack`

  ...

  - `Root = 0`

  - `Any = 0xFFFFFFFF`

* `CornerType`

  ...

  - `NorthSouth = 0`

  - `West = 1`

  - `East = 2`

  - `South = 3`

  - `North = 4`

  - `EastWest = 5`

* `EventExceptionPolicy`

  ...

  - `IgnoreAndContinueChain = 0`

  - `StopChainAndReturnTrue = 1`

  - `StopChainAndReturnFalse = 2`

* `EventPriority`

  ...

  - `Lowest = 0`

  - `Low = 1000000`

  - `Normal = 2000000`

  - `High = 3000000`

  - `Highest = 4000000`

* `TextPackName`

  ...

  - `None = 0`

  - `Game = 1`

  - `Dialogs = 2`

  - `Items = 3`

  - `Maps = 4`

  - `Locations = 5`

  - `Protos = 6`

  - `Text = 10`

  - `Combat = 11`

  - `Quest = 12`

  - `GlobalMap = 13`

  - `Holo = 14`

* `KeyCode`

  ...

  - `None = 0x00`

  - `Escape = 0x01`

  - `C1 = 0x02`

  - `C2 = 0x03`

  - `C3 = 0x04`

  - `C4 = 0x05`

  - `C5 = 0x06`

  - `C6 = 0x07`

  - `C7 = 0x08`

  - `C8 = 0x09`

  - `C9 = 0x0A`

  - `C0 = 0x0B`

  - `Minus = 0x0C`

  - `Equals = 0x0D`

  - `Back = 0x0E`

  - `Tab = 0x0F`

  - `Q = 0x10`

  - `W = 0x11`

  - `E = 0x12`

  - `R = 0x13`

  - `T = 0x14`

  - `Y = 0x15`

  - `U = 0x16`

  - `I = 0x17`

  - `O = 0x18`

  - `P = 0x19`

  - `Lbracket = 0x1A`

  - `Rbracket = 0x1B`

  - `Return = 0x1C`

  - `Lcontrol = 0x1D`

  - `A = 0x1E`

  - `S = 0x1F`

  - `D = 0x20`

  - `F = 0x21`

  - `G = 0x22`

  - `H = 0x23`

  - `J = 0x24`

  - `K = 0x25`

  - `L = 0x26`

  - `Semicolon = 0x27`

  - `Apostrophe = 0x28`

  - `Grave = 0x29`

  - `Lshift = 0x2A`

  - `Backslash = 0x2B`

  - `Z = 0x2C`

  - `X = 0x2D`

  - `C = 0x2E`

  - `V = 0x2F`

  - `B = 0x30`

  - `N = 0x31`

  - `M = 0x32`

  - `Comma = 0x33`

  - `Period = 0x34`

  - `Slash = 0x35`

  - `Rshift = 0x36`

  - `Multiply = 0x37`

  - `Lmenu = 0x38`

  - `Space = 0x39`

  - `Capital = 0x3A`

  - `F1 = 0x3B`

  - `F2 = 0x3C`

  - `F3 = 0x3D`

  - `F4 = 0x3E`

  - `F5 = 0x3F`

  - `F6 = 0x40`

  - `F7 = 0x41`

  - `F8 = 0x42`

  - `F9 = 0x43`

  - `F10 = 0x44`

  - `Numlock = 0x45`

  - `Scroll = 0x46`

  - `Numpad7 = 0x47`

  - `Numpad8 = 0x48`

  - `Numpad9 = 0x49`

  - `Subtract = 0x4A`

  - `Numpad4 = 0x4B`

  - `Numpad5 = 0x4C`

  - `Numpad6 = 0x4D`

  - `Add = 0x4E`

  - `Numpad1 = 0x4F`

  - `Numpad2 = 0x50`

  - `Numpad3 = 0x51`

  - `Numpad0 = 0x52`

  - `Decimal = 0x53`

  - `F11 = 0x57`

  - `F12 = 0x58`

  - `Numpadenter = 0x9C`

  - `Rcontrol = 0x9D`

  - `Divide = 0xB5`

  - `Sysrq = 0xB7`

  - `Rmenu = 0xB8`

  - `Pause = 0xC5`

  - `Home = 0xC7`

  - `Up = 0xC8`

  - `Prior = 0xC9`

  - `Left = 0xCB`

  - `Right = 0xCD`

  - `End = 0xCF`

  - `Down = 0xD0`

  - `Next = 0xD1`

  - `Insert = 0xD2`

  - `Delete = 0xD3`

  - `Lwin = 0xDB`

  - `Rwin = 0xDC`

  - `Text = 0xFF`

* `MouseButton`

  ...

  - `Left = 0`

  - `Right = 1`

  - `Middle = 2`

  - `WheelUp = 3`

  - `WheelDown = 4`

  - `Ext0 = 5`

  - `Ext1 = 6`

  - `Ext2 = 7`

  - `Ext3 = 8`

  - `Ext4 = 9`

* `MovingState`

  ...

  - `InProgress = 0`

  - `Success = 1`

  - `TargetNotFound = 2`

  - `CantMove = 3`

  - `GagCritter = 4`

  - `GagItem = 5`

  - `InternalError = 6`

  - `HexTooFar = 7`

  - `HexBusy = 8`

  - `HexBusyRing = 9`

  - `Deadlock = 10`

  - `TraceFailed = 11`

  - `NotAlive = 12`

  - `Attached = 13`

* `CursorType`

  ...

  - `Default = 0`

  - `Move = 1`

  - `UseItem = 2`

  - `UseWeapon = 3`

  - `UseSkill = 4`

  - `Hand = 5`

* `AnchorStyle`

  Anchor styles

  - `None = 0`

  - `Left = 1`

  - `Right = 2`

  - `Top = 4`

  - `Bottom = 8`

* `DockStyle`

  Dock styles

  - `None = 0`

  - `Left = 1`

  - `Right = 2`

  - `Top = 3`

  - `Bottom = 4`

  - `Fill = 5`

* `SpriteLayout`

  ...

  - `None = 0`

  - `Tile = 1`

  - `Center = 2`

  - `Stretch = 3`

  - `Zoom = 4`

* `CombatText`

  Combat text

  - `RunAway = 0`

  - `Move = 1`

  - `Attack = 2`

  - `Miss = 3`

  - `HitHead = 10`

  - `HitLeftArm = 11`

  - `HitRightArm = 12`

  - `HitTorso = 13`

  - `HitRightLeg = 14`

  - `HitLeftLeg = 15`

  - `HitEyes = 16`

  - `HitGroin = 17`

* `Area`

  Area

  - `NoPref = 0`

  - `Always = 1`

  - `Sometimes = 2`

  - `BeSure = 3`

  - `BeCareful = 4`

  - `BeAbsSure = 5`

* `AttackWho`

  AttackWho

  - `WhoAttackMe = 0`

  - `Strongest = 1`

  - `Weakest = 2`

  - `Whomever = 3`

  - `Closest = 4`

* `BestWeap`

  BestWeap

  - `NoPref = 0`

  - `Never = 1`

  - `Random = 2`

  - `Unarmed = 3`

  - `RangedOvMelee = 4`

  - `MeleeOvRanged = 5`

  - `UnarmOvThrown = 6`

* `ChemUse`

  ChemUse

  - `Clean = 0`

  - `Sometimes = 1`

  - `StimsHurtLo = 2`

  - `StimsHurtHi = 3`

  - `Anytime = 4`

  - `Always = 5`

* `Disposition`

  Disposition

  - `MinusOne = 0`

  - `None = 1`

  - `Coward = 2`

  - `Defensive = 3`

  - `Aggressive = 4`

  - `Berserk = 5`

  - `Random = 10`

  - `DCharge = 11`

  - `OnYourOwn = 12`

  - `Stay = 13`

  - `StayClose = 14`

  - `Snipe = 15`

* `HurtToMuch`

  HurtToMuch

  - `None = 0`

  - `Crippled = 1`

  - `Blind = 2`

  - `CripArms = 3`

* `RunAway`

  RunAway

  - `None = 0`

  - `Coward = 1`

  - `FingerHurts = 2`

  - `Bleeding = 3`

  - `NotFeelGood = 4`

  - `Tourniquet = 5`

  - `Never = 6`

* `Fallout2AIPackets`

  Count of packets

  - `Count = 282`

  - `PlayerAi = 0`

  - `ArroyoWarrior = 1`

  - `ArroyoVillager = 2`

  - `ArroyoElder = 3`

  - `ArroyoShaman = 4`

  - `SporePlant = 5`

  - `Brahmin = 6`

  - `Rat = 7`

  - `Scorpion = 8`

  - `Mantis = 9`

  - `Deathclaw = 10`

  - `DrugAddict = 11`

  - `GenericGuards = 12`

  - `Thugs = 13`

  - `Peasants = 14`

  - `Child = 15`

  - `Slaver = 16`

  - `StoreOwner = 17`

  - `VaultGuard = 18`

  - `Doctor = 19`

  - `Slag = 20`

  - `GenericDog = 21`

  - `ToughGuard = 22`

  - `Kamakazi = 23`

  - `ToughCitizen = 24`

  - `WimpyPeasant = 25`

  - `Gecko = 26`

  - `FightingMantis = 27`

  - `BrainMoleRat = 28`

  - `VaultDeathclaws = 29`

  - `RepairBot = 30`

  - `SecurityBot = 31`

  - `ToughBot = 32`

  - `Coward = 33`

  - `Torr = 34`

  - `GhoulPeasant = 35`

  - `GhoulGuard = 36`

  - `GhoulMerchant = 37`

  - `Berserker = 38`

  - `WimpyGecko = 39`

  - `Boxer = 40`

  - `Patron = 41`

  - `DrugDealer = 42`

  - `BoxingFan = 43`

  - `Pimp = 44`

  - `Prostitute = 45`

  - `Slave = 46`

  - `SuperMutant = 47`

  - `MutatedRat = 48`

  - `LonerCitizen = 49`

  - `Cyberdog = 50`

  - `ReactorGhoul = 51`

  - `ReddingAddict = 52`

  - `PartyVicBerserk = 53`

  - `PartyVicAggressive = 54`

  - `PartyVicDefensive = 55`

  - `PartyVicCoward = 56`

  - `PartyVicCustom = 57`

  - `PartyMyronBerserk = 58`

  - `PartyMyronAggressive = 59`

  - `PartyMyronDefensive = 60`

  - `PartyMyronCoward = 61`

  - `PartyMyronCustom = 62`

  - `PartyMarcusBerserk = 63`

  - `PartyMarcusAggressive = 64`

  - `PartyMarcusDefensive = 65`

  - `PartyMarcusCoward = 66`

  - `PartyMarcusCustom = 67`

  - `PartyMacraeBerserk = 68`

  - `PartyMacraeAggressive = 69`

  - `PartyMacraeDefensive = 70`

  - `PartyMacraeCoward = 71`

  - `PartyMacraeCustom = 72`

  - `PartySulikBerserk = 73`

  - `PartySulikAggressive = 74`

  - `PartySulikDefensive = 75`

  - `PartySulikCoward = 76`

  - `PartySulikCustom = 77`

  - `PartyLennyBerserk = 78`

  - `PartyLennyAggressive = 79`

  - `PartyLennyDefensive = 80`

  - `PartyLennyCoward = 81`

  - `PartyLennyCustom = 82`

  - `PartyCyberdogBerserk = 83`

  - `PartyCyberdogAggressive = 84`

  - `PartyCyberdogDefensive = 85`

  - `PartyCyberdogCoward = 86`

  - `PartyCyberdogCustom = 87`

  - `PartyDocBerserk = 88`

  - `PartyDocAggressive = 89`

  - `PartyDocDefensive = 90`

  - `PartyDocCoward = 91`

  - `PartyDocCustom = 92`

  - `PartyGorisBerserk = 93`

  - `PartyGorisAggressive = 94`

  - `PartyGorisDefensive = 95`

  - `PartyGorisCoward = 96`

  - `PartyGorisCustom = 97`

  - `PartyDavinBerserk = 98`

  - `PartyDavinAggressive = 99`

  - `PartyDavinDefensive = 100`

  - `PartyDavinCoward = 101`

  - `PartyDavinCustom = 102`

  - `PartyMariaBerserk = 103`

  - `PartyMariaAggressive = 104`

  - `PartyMariaDefensive = 105`

  - `PartyMariaCoward = 106`

  - `PartyMariaCustom = 107`

  - `PartyLaddieBerserk = 108`

  - `PartyLaddieAggressive = 109`

  - `PartyLaddieDefensive = 110`

  - `PartyLaddieCoward = 111`

  - `PartyLaddieCustom = 112`

  - `PartyRobobrainBerserk = 113`

  - `PartyRobobrainAggressive = 114`

  - `PartyRobobrainDefensive = 115`

  - `PartyRobobrainCoward = 116`

  - `PartyRobobrainCustom = 117`

  - `PartyBessBerserk = 118`

  - `PartyBessAggressive = 119`

  - `PartyBessDefensive = 120`

  - `PartyBessCoward = 121`

  - `PartyBessCustom = 122`

  - `ScaredBrahmin = 123`

  - `BountyHunter = 124`

  - `MysteriousStranger = 125`

  - `Dunton = 126`

  - `NcrRangers = 127`

  - `Mobsters = 128`

  - `MastersArmy = 129`

  - `Alien = 130`

  - `MeanDeathclaw = 131`

  - `Floater = 132`

  - `Centaur = 133`

  - `EnclavePatrol = 134`

  - `MercCaptain = 135`

  - `MercRaider = 136`

  - `ShadowWhoWalks = 137`

  - `TheDragon = 138`

  - `Lopan = 139`

  - `ReddingMiner = 140`

  - `Kaga = 141`

  - `EndBoss = 142`

  - `Dumar = 143`

  - `FireGeckos = 144`

  - `CrazedRobot = 145`

  - `RatGod = 146`

  - `ToughMerchant = 147`

  - `CrazyAddict = 148`

  - `Algernon = 149`

  - `Oz7 = 150`

  - `Oz9 = 151`

  - `Badger = 152`

  - `Shi = 153`

  - `Chip = 154`

  - `Ryan = 155`

  - `ShiGuard = 156`

  - `Elron = 157`

  - `ElronGuard = 158`

  - `RonCruz = 159`

  - `NikkiGoldman = 160`

  - `Punk = 161`

  - `Khan = 162`

  - `ToughKhan = 163`

  - `PartyDogmeatAgressive = 164`

  - `PartyDogmeatBerserk = 165`

  - `PartyDogmeatCoward = 166`

  - `PartyDogmeatCustom = 167`

  - `PartyDogmeatDefensive = 168`

  - `PartyPariadogAgressive = 169`

  - `PartyPariadogBerserk = 170`

  - `PartyPariadogCoward = 171`

  - `PartyPariadogCustom = 172`

  - `PartyPariadogDefensive = 173`

  - `RobotTurret = 174`

  - `NavarroGuard = 175`

  - `GunTurret = 176`

  - `TheBrain = 177`

  - `BrahminWimpy = 178`

  - `AddictWimpy = 179`

  - `PeasantNoMove = 180`

  - `CaravanGuard = 181`

  - `CaravanDriver = 182`

  - `PeasantKamakazi = 183`

  - `PrimitiveCoward = 184`

  - `PrimitiveKamakazi = 185`

  - `DogTough = 186`

  - `Fo1PlayerAi = 187`

  - `Fo1Berzerker = 188`

  - `Fo1Careful = 189`

  - `Fo1Cow = 190`

  - `Fo1Guard = 191`

  - `Fo1Loser = 192`

  - `Fo1Peasant = 193`

  - `Fo1SuperMutant = 194`

  - `Fo1Dog = 195`

  - `Fo1Ghoul = 196`

  - `Fo1MutantGuards = 197`

  - `Fo1Bouncer = 198`

  - `Fo1Rats = 199`

  - `Fo1MoleRats = 200`

  - `Fo1Radscorpion = 201`

  - `Fo1GuardGungHo = 202`

  - `Fo1GuardSadistic = 203`

  - `Fo1GuardHumorous = 204`

  - `Fo1GuardQuiet = 205`

  - `Fo1GuardSmartass = 206`

  - `Fo1GenericRaider = 207`

  - `Fo1RaiderGuard = 208`

  - `Fo1RaiderLeader = 209`

  - `Fo1ShadySandsPeasant = 210`

  - `Fo1ShadySandsGuard = 211`

  - `Fo1ShadySandsLeader = 212`

  - `Fo1Rippers = 213`

  - `Fo1Blades = 214`

  - `Fo1Gunrunners = 215`

  - `Fo1Regulators = 216`

  - `Fo1Adytowner = 217`

  - `Fo1GenericFollower = 218`

  - `Fo1FollowerScout = 219`

  - `Fo1FollowerGuard = 220`

  - `Fo1FollowerLeader = 221`

  - `Fo1RipperLeader = 222`

  - `Fo1BladeScout = 223`

  - `Fo1BladeLeader = 224`

  - `Fo1GunrunnerLeader = 225`

  - `Fo1AdytumLeader = 226`

  - `Fo1GhoulCoward = 227`

  - `Fo1GhoulNormal = 228`

  - `Fo1GhoulBrave = 229`

  - `Fo1GarlHonor = 230`

  - `Fo1EmptySlot1 = 231`

  - `Fo1EmptySlot2 = 232`

  - `Fo1SuperMutantGuard = 233`

  - `Fo1SuperMutantNormal = 234`

  - `Fo1SuperMutantAggressive = 235`

  - `Fo1SuperMutantSgt = 236`

  - `Fo1Merchant = 237`

  - `Fo1HubPeasants = 238`

  - `Fo1HubThief = 239`

  - `Fo1HubMutants = 240`

  - `Fo1Deathclaw = 241`

  - `Fo1JunktownPeasant = 242`

  - `Fo1JunktownGuard = 243`

  - `Fo1Killian = 244`

  - `Fo1JunktownThug = 245`

  - `Fo1Skulz = 246`

  - `Fo1Gizmo = 247`

  - `Fo1Sellbabies = 248`

  - `Fo1BrotherhoodInitiate = 249`

  - `Fo1BrotherhoodScribe = 250`

  - `Fo1BrotherhoodKnight = 251`

  - `Fo1BrotherhoodPaladin = 252`

  - `Fo1Nightkin = 253`

  - `Fo1BrainwashedChildren = 254`

  - `Fo1LittleKids = 255`

  - `Fo1ChildrenTrue = 256`

  - `Fo1Master = 257`

  - `Fo1Robots = 258`

  - `Fo1Centaur = 259`

  - `Fo1Floater = 260`

  - `Fo1Eyeball = 261`

  - `Fo1Marcelles = 262`

  - `Fo1GuardRookie = 263`

  - `Fo1CocHubBrainwashed = 264`

  - `Fo1GhoulNasty = 265`

  - `Fo1SuperMutantNecro = 266`

  - `Fo1BosElders = 267`

  - `Fo1BosRhombus = 268`

  - `Fo1CocMorpheus = 269`

  - `Fo1CocLasher = 270`

  - `Fo1CocJain = 271`

  - `Fo1HubUnderground = 272`

  - `Fo1HubPolice = 273`

  - `Fo1Decker = 274`

  - `Fo1Cain = 275`

  - `Fo1Ian = 276`

  - `Fo1Tycho = 277`

  - `Fo1Vaultdweller = 278`

  - `Fo1Stranger = 279`

  - `Fo1GhoulMindless = 280`

  - `Fo1Runaway = 281`

* `Bags`

  Bags

  - `Internal = 0`

  - `Empty = 1`

  - `CaveBanditLvl1 = 12`

  - `CaveBanditLvl2 = 18`

  - `CaravanBlackGuard = 25`

  - `VaultCityGuard = 65`

  - `VaultCityMilitary = 67`

  - `AllSlavesMaleSlaver = 147`

  - `RDRCBHCaravanMasterTrader = 164`

  - `RDRCBHCaravanBigGunGuardMale = 163`

  - `RDRCBHCaravanBigGunGuardFemale = 165`

  - `RDRCGCaravanGenericGhoul = 166`

  - `RDRCGCaravanReactorGhoul = 167`

  - `RDRCGCaravanReactorGhoul2 = 168`

  - `RDRCRaidersRaiderMale = 169`

  - `RDRCRaidersRaiderMale2 = 170`

  - `RDRCRaidersRaiderFemale = 171`

  - `RDRCRaidersRaiderFemale2 = 172`

  - `NavarroEnclavePatrolMale2 = 174`

  - `SFBand1MercenearyFemale2 = 182`

  - `SFBand2ElronologistMale2 = 184`

  - `SFCaravanGrandMasterTraderMale = 191`

  - `SFCaravanVaultCityPatrolMale = 192`

  - `SFCaravanVaultCityPatrolMale2 = 193`

  - `SFCaravanVaultCityPatrolFemale = 194`

  - `SFCaravanVaultCityPatrolFemale2 = 195`

  - `AllUnityBigGunGuardFemale = 201`

  - `NCRCaravanNCRRangerMale = 225`

  - `AllBountyHunters1 = 234`

  - `AllBountyHunters2 = 235`

  - `AllBountyHunters3 = 236`

  - `AllBountyHunters4 = 237`

  - `AllBountyHunters5 = 238`

  - `AllBountyHunters6 = 239`

  - `AllBountyHunters7 = 240`

  - `AllBountyHunters8 = 241`

  - `AllBountyHunters9 = 242`

  - `AllBountyHunters10 = 243`

  - `BaseEnclaveEngineer = 260`

  - `BaseEnclaveInfantry = 261`

  - `BaseBosEngineer = 262`

  - `BaseBosInfantry = 263`

  - `BaseSaboteur = 264`

  - `EnclaveSoldier = 265`

  - `BaseBosPaladin = 266`

  - `Sniper1 = 270`

  - `Sniper2 = 271`

  - `Medic1 = 274`

  - `Medic2 = 275`

  - `Term1 = 276`

  - `Slayer1 = 280`

  - `Slayer2 = 281`

  - `Slayer3 = 282`

  - `Eli = 283`

* `GenericDescriptionsTypes`

  Generic descriptions types

  - `InventoryMain = 0`

  - `InventorySpecial = 1`

  - `InventoryStats = 2`

  - `InventoryResist = 3`

* `ItemLookTypes`

  Item look types

  - `Default = 0`

  - `OnlyName = 1`

  - `Map = 2`

  - `Barter = 3`

  - `Inventory = 4`

  - `WmCar = 5`

* `CritterLookTypes`

  Critter look types

  - `OnlyName = 0`

  - `LookShort = 1`

  - `LookFull = 2`

* `Fonts`

  Fonts

  - `Default = 0`

  - `OldFo = 1`

  - `Num = 2`

  - `BigNum = 3`

  - `SandNum = 4`

  - `Special = 5`

  - `Thin = 6`

  - `Fat = 7`

  - `Big = 8`

* `DialogBoxType`

  ...

  - `None = 0`

  - `AskFollowGlobalGroupRuler = 1`

  - `NcrIllBrahmin = 2`

  - `PurgatoryInvite = 3`

* `MessageSpecifications`

  message specs  
  note: MessageSpecifications::AimedHit must be MessageSpecifications::Hit+1, MessageSpecifications::CritAimedHit must be MessageSpecifications::CritHit+1  
  Message scpecifications

  - `None = 0`

  - `Miss = 1`

  - `CritMiss = 2`

  - `CritMissDamage = 3`

  - `Hit = 4`

  - `AimedHit = 5`

  - `CritHit = 6`

  - `CritAimedHit = 7`

  - `HitDead = 8`

  - `AimedHitDead = 9`

  - `CritHitDead = 10`

  - `CritAimedHitDead = 11`

  - `Oops = 12`

  - `HitRandomly = 13`

* `FalloutAnims1`

  Fallout anims1

  - `None = 0`

  - `Unarmed = 1`

  - `Dead = 2`

  - `Knockout = 3`

  - `Knife = 4`

  - `Club = 5`

  - `Hammer = 6`

  - `Spear = 7`

  - `Pistol = 8`

  - `Uzi = 9`

  - `Shootgun = 10`

  - `Rifle = 11`

  - `Minigun = 12`

  - `RocketLauncher = 13`

  - `Aim = 14`

* `FalloutAnims2`

  Fallout anims2

  - `None = 0`

  - `Stay = 1`

  - `Walk = 2`

  - `Show = 3`

  - `Hide = 4`

  - `DodgeWeapon = 5`

  - `Thrust = 6`

  - `Swing = 7`

  - `PrepareWeapon = 8`

  - `TurnoffWeapon = 9`

  - `Shoot = 10`

  - `Burst = 11`

  - `Flame = 12`

  - `ThrowWeapon = 13`

  - `DamageFront = 15`

  - `DamageBack = 16`

* `FalloutAnims2Unarmed`

  ...

  - `Unknown = 0`

  - `KnockFront = 1`

  - `KnockBack = 2`

  - `StandupBack = 8`

  - `StandupFront = 10`

  - `Pickup = 11`

  - `Use = 12`

  - `DodgeEmpty = 14`

  - `Punch = 17`

  - `Kick = 18`

  - `ThrowEmpty = 19`

  - `Run = 20`

* `FalloutAnims2Dead`

  ...

  - `Unknown = 0`

  - `DeadFront = 1`

  - `DeadBack = 2`

  - `DeadBloodySingle = 4`

  - `DeadBurn = 5`

  - `DeadBloodyBurst = 6`

  - `DeadBurst = 7`

  - `DeadPulse = 8`

  - `DeadLaser = 9`

  - `DeadBurn2 = 10`

  - `DeadPulseDust = 11`

  - `DeadExplode = 12`

  - `DeadFused = 13`

  - `DeadBurnRun = 14`

  - `DeadFront2 = 15`

  - `DeadBack2 = 16`

* `DamageTypes`

  Damage types

  - `None = 0`

  - `Normal = 1`

  - `Laser = 2`

  - `Fire = 3`

  - `Plasma = 4`

  - `Electricity = 5`

  - `Emp = 6`

  - `Explode = 7`

  - `Poison = 8`

  - `Radiation = 9`

* `GenderType`

  Gender

  - `Male = 0`

  - `Female = 1`

  - `It = 2`

* `ItemPerks`

  Item perks

  - `ItemPerkNone = 0`

  - `LongRange = 1`

  - `Accurate = 2`

  - `Penetrate = 3`

  - `Knockback = 4`

  - `ScopeRange = 5`

  - `FastReload = 6`

  - `NightSight = 7`

  - `Flameboy = 8`

  - `EnhancedKnockout = 9`

* `ArmorPerks`

  ...

  - `None = 0`

  - `Powered = 1`

  - `Combat = 2`

  - `AdvancedI = 3`

  - `AdvancedII = 4`

  - `Charisma = 5`

* `BodyTypes`

  Body types

  - `Men = 0`

  - `Women = 1`

  - `Children = 2`

  - `SuperMutant = 3`

  - `Ghoul = 4`

  - `Brahmin = 5`

  - `Radscorpion = 6`

  - `Rat = 7`

  - `Floater = 8`

  - `Centaur = 9`

  - `Robot = 10`

  - `Dog = 11`

  - `Manti = 12`

  - `Deadclaw = 13`

  - `Plant = 14`

  - `Gecko = 15`

  - `Alien = 16`

  - `GiantAnt = 17`

  - `BigBadBoss = 18`

  - `GiantBeetle = 19`

  - `GiantWasp = 20`

* `HitLocations`

  Hit locations

  - `LocationNone = 0`

  - `LocationHead = 1`

  - `LocationLeftArm = 2`

  - `LocationRightArm = 3`

  - `LocationTorso = 4`

  - `LocationRightLeg = 5`

  - `LocationLeftLeg = 6`

  - `LocationEyes = 7`

  - `LocationGroin = 8`

  - `LocationUncalled = 9`

* `Caliber`

  Weapon calibers

  - `None = 0`

  - `Rocket = 1`

  - `FlameThrowerFuel = 2`

  - `C_EnergyCell = 3`

  - `D_EnergyCell = 4`

  - `Bullet_223 = 5`

  - `Bullet_5mm = 6`

  - `Bullet_40 = 7`

  - `Bullet_10mm = 8`

  - `Bullet_44 = 9`

  - `Bullet_14mm = 10`

  - `Bullet_12Gauge = 11`

  - `Bullet_9mm = 12`

  - `Bullet_BB = 13`

  - `Bullet_45 = 14`

  - `Bullet_2mm = 15`

  - `Bullet_47mmCaseless = 16`

  - `Bullet_HNNeedler = 17`

  - `Bullet_762mm = 18`

  - `Bullet_700NitroExpress = 19`

  - `SignalRocket = 20`

* `Addictions`

  Addictions

  - `NukaCola = 0`

  - `Buffout = 1`

  - `Mentats = 2`

  - `Psycho = 3`

  - `Radaway = 4`

  - `Jet = 5`

  - `Tragic = 6`

* `KarmaLevel`

  Karma level

  - `Unknown = 0`

  - `SaviorOfTheDamned = 1`

  - `GuardianOfTheWastes = 2`

  - `ShieldOfHope = 3`

  - `Defender = 4`

  - `Wanderer = 5`

  - `Betrayer = 6`

  - `SwordOfDespair = 7`

  - `ScourgeOfTheWastes = 8`

  - `DemonSpawn = 9`

* `ReputationLevel`

  ReputationLevel

  - `Unknown = 0`

  - `Idolized = 1`

  - `Liked = 2`

  - `Accepted = 3`

  - `Neutral = 4`

  - `Antipathy = 5`

  - `Hated = 6`

  - `Vilified = 7`

* `EScores`

  EScores

  - `EvilOfHour = 0`

  - `HeroOfHour = 1`

  - `KarmaOnHour = 2`

  - `Speaker = 3`

  - `Trader = 4`

  - `Zomby = 5`

  - `Paty = 6`

  - `Maniac = 7`

  - `Scaut = 8`

  - `Doctor = 9`

  - `Shooter = 10`

  - `Melee = 11`

  - `Unarmed = 12`

  - `Thief = 13`

  - `Driver = 14`

  - `Killer = 15`

  - `Sniper = 16`

  - `Adventurer = 17`

  - `Cracker = 18`

  - `UnarmedDamage = 19`

  - `Ritch = 20`

  - `ChosenOne = 21`

  - `SierraCur = 40`

  - `MariposaCur = 41`

  - `CathedralCur = 42`

  - `SierraBest = 43`

  - `MariposaBest = 44`

  - `CathedralBest = 45`

  - `SierraOrg = 46`

  - `MariposaOrg = 47`

  - `CathedralOrg = 48`

  - `BaseBestOrg = 49`

* `HoloBax`

  Holodisk numbers

  - `None = 0`

  - `MainInfo = 100`

  - `SermonDead = 101`

  - `SermonCharacter = 102`

  - `SermonNasty = 103`

  - `SermonBehavior = 104`

  - `MythNeutral = 105`

* `TransferTypes`

  Transfer types

  - `Close = 0`

  - `HexContUp = 1`

  - `HexContDown = 2`

  - `SelfCont = 3`

  - `CritLoot = 4`

  - `CritSteal = 5`

  - `CritBarter = 6`

  - `FarCont = 7`

  - `FarCrit = 8`

* `ItemType`

  Items types

  - `None = 0`

  - `Armor = 1`

  - `Drug = 2`

  - `Weapon = 3`

  - `Ammo = 4`

  - `Misc = 5`

  - `Key = 7`

  - `Container = 8`

  - `Door = 9`

  - `Grid = 10`

  - `Generic = 11`

  - `Wall = 12`

  - `Car = 13`

* `GameComponent`

  ...

  - `Invalid = 0`

* `PlayerComponent`

  ...

  - `Invalid = 0`

* `ItemComponent`

  ...

  - `Invalid = 0`

* `CritterComponent`

  ...

  - `Invalid = 0`

* `MapComponent`

  ...

  - `Invalid = 0`

* `LocationComponent`

  ...

  - `Invalid = 0`

* `GameProperty`

  ...

  - `Invalid = 0xFFFF`

  - `CustomHolderId = 0`

  - `CustomHolderEntry = 1`

  - `InnerEntityIds = 2`

  - `Year = 3`

  - `Month = 4`

  - `Day = 5`

  - `Hour = 6`

  - `Minute = 7`

  - `Second = 8`

  - `TimeMultiplier = 9`

  - `LastEntityId = 10`

  - `LastDeferredCallId = 11`

  - `HistoryRecordsId = 12`

  - `LastGlobalMapTripId = 13`

  - `ArroyoMynocTimeout = 14`

  - `BaseSierraRule = 15`

  - `BaseMariposaRule = 16`

  - `BaseCathedralRule = 17`

  - `BaseSierraOrg = 18`

  - `BaseMariposaOrg = 19`

  - `BaseCathedralOrg = 20`

  - `BaseSierraTimeEventId = 21`

  - `BaseMariposaTimeEventId = 22`

  - `BaseCathedralTimeEventId = 23`

  - `BaseEnclaveScore = 24`

  - `BaseBosScore = 25`

  - `BulletinBoard = 26`

  - `DenGhostIsDead = 27`

  - `DenVirginIsAway = 28`

  - `GameEventManagerData = 29`

  - `GameEventData = 30`

  - `RacingWinnersFound = 31`

  - `RacingWinner = 32`

  - `LastGlobalMapTrip = 33`

  - `EndingV13DclawGenocide = 34`

  - `KlamCowboy = 35`

  - `KlamCowboyLevel = 36`

  - `KlamSmilyGeckoLocation = 37`

  - `KlamSmilyGeckoTimeout = 38`

  - `TribRaid = 39`

  - `PrimalTribeQuestPlayers = 40`

  - `MobWaveData = 41`

  - `NCRRanchBrahminIll = 42`

  - `NcrDustyOneHourInvokeId = 43`

  - `NcrDustyOneWeekInvokeId = 44`

  - `NCRDustyPartyStatusGlobal = 45`

  - `NCRDustyRotgutCounter = 46`

  - `NCRDustyBeerGammaCounter = 47`

  - `NCRInvasion = 48`

  - `NCRKessStageGlobal = 49`

  - `NcrSmitPosition = 50`

  - `NcrSmitGateGuardAccessGranted = 51`

  - `NcrWestinPositionGlobal = 52`

  - `RegProperties = 53`

  - `ReddMarionWanLocation = 54`

  - `ReddMarionWanTimeout = 55`

  - `ReddJohnsonBroadcast = 56`

  - `PermanentDeath = 57`

  - `BestScores = 58`

  - `BestScoreCritterIds = 59`

  - `BestScoreValues = 60`

  - `SFZax366StatusGlobal = 61`

  - `SFDevinHired = 62`

  - `MissilesCanada = 63`

  - `MissilesKishinev = 64`

  - `MissilesBaku = 65`

  - `MissilesTokio = 66`

  - `MissilesEburg = 67`

  - `MissilesVladik = 68`

  - `MissilesRay = 69`

  - `MissilesFukusima = 70`

  - `BestEScores = 71`

  - `ArroyoRaidersCount = 72`

  - `ArroyoLastDefenceGroup = 73`

  - `ArroyoMynocMap = 74`

  - `EncOceanTraderAlive = 75`

  - `GameEventCaches = 76`

  - `RacingEvent = 77`

  - `GEReplStationStatus = 78`

  - `NCRSiegeCampsNum = 79`

  - `SFBosArmourCounter = 80`

  - `SFInvasionStatus = 81`

  - `DenLeannaThief = 82`

  - `DenCliffDealer = 83`

  - `DenAnanDollUse = 84`

  - `KlamSmilyGeckoCounter = 85`

  - `EndingArroyoTodd = 86`

  - `EndingV13DclawRevival = 87`

  - `GeckSkitrHired = 88`

  - `NRBbarmenHired = 89`

  - `NcrIsCurfewActive = 90`

  - `NcrMicGuaranteeCounter = 91`

  - `SFImperatorMemory = 92`

  - `GCityGeckSold = 93`

  - `VCBlackHired = 94`

  - `EndingV13DclawSaved = 95`

  - `VCHartmanMarchStatus = 96`

  - `RaidersDead = 97`

* `PlayerProperty`

  ...

  - `Invalid = 0xFFFF`

  - `CustomHolderId = 0`

  - `CustomHolderEntry = 1`

  - `InnerEntityIds = 2`

  - `ControlledCritterId = 3`

  - `LastControlledCritterId = 4`

  - `Password = 5`

  - `ConnectionIp = 6`

  - `ConnectionPort = 7`

  - `MainCritterId = 8`

* `ItemProperty`

  ...

  - `Invalid = 0xFFFF`

  - `CustomHolderId = 0`

  - `CustomHolderEntry = 1`

  - `InnerEntityIds = 2`

  - `InitScript = 3`

  - `StaticScript = 4`

  - `Static = 5`

  - `Ownership = 6`

  - `MapId = 7`

  - `HexX = 8`

  - `HexY = 9`

  - `CritterId = 10`

  - `CritterSlot = 11`

  - `ContainerId = 12`

  - `ContainerStack = 13`

  - `InnerItemIds = 14`

  - `Stackable = 15`

  - `Count = 16`

  - `PicMap = 17`

  - `OffsetX = 18`

  - `OffsetY = 19`

  - `Corner = 20`

  - `DisableEgg = 21`

  - `BlockLines = 22`

  - `ScrollBlock = 23`

  - `Hidden = 24`

  - `HideSprite = 25`

  - `AlwaysHideSprite = 26`

  - `HiddenInStatic = 27`

  - `NoBlock = 28`

  - `ShootThru = 29`

  - `LightThru = 30`

  - `AlwaysView = 31`

  - `LightSource = 32`

  - `LightIntensity = 33`

  - `LightDistance = 34`

  - `LightFlags = 35`

  - `LightColor = 36`

  - `TriggerScript = 37`

  - `IsTrigger = 38`

  - `PicInv = 39`

  - `FlyEffectSpeed = 40`

  - `IsScenery = 41`

  - `IsWall = 42`

  - `IsTile = 43`

  - `IsRoofTile = 44`

  - `TileLayer = 45`

  - `DrawFlatten = 46`

  - `DrawOrderOffsetHexY = 47`

  - `BadItem = 48`

  - `NoHighlight = 49`

  - `NoLightInfluence = 50`

  - `IsGag = 51`

  - `Colorize = 52`

  - `Lexems = 53`

  - `SortValue = 54`

  - `IsTrap = 55`

  - `TrapValue = 56`

  - `IsRadio = 57`

  - `RadioChannel = 58`

  - `RadioFlags = 59`

  - `RadioBroadcastSend = 60`

  - `RadioBroadcastRecv = 61`

  - `CanOpen = 62`

  - `Opened = 63`

  - `ColorizeColor = 64`

  - `CarIsBioEngine = 65`

  - `CarIsNoLockpick = 66`

  - `CaravanCabLeaderId = 67`

  - `ELockCloseAtSeconds = 68`

  - `ELockCode = 69`

  - `ExplodeInvokeId = 70`

  - `ExplodeSwitcherExplodeId = 71`

  - `ExplodeOwnerId = 72`

  - `ExplodeBonusDamage = 73`

  - `ExplodeBonusRadius = 74`

  - `ExplodeTimeRespawnMine = 75`

  - `GECachesNumParameters = 76`

  - `GeigerEnabled = 77`

  - `GeigerCapacity = 78`

  - `GeigerTimeEvent = 79`

  - `QHunterCountFluteUse = 80`

  - `DoorAutoCloseTime = 81`

  - `DoorAutoDialog = 82`

  - `IsGeck = 83`

  - `LockerId = 84`

  - `LockerComplexity = 85`

  - `Locker_Locked = 86`

  - `Locker_Jammed = 87`

  - `Locker_Broken = 88`

  - `Locker_NoOpen = 89`

  - `Locker_IsElectro = 90`

  - `Door_NoBlockMove = 91`

  - `Door_NoBlockShoot = 92`

  - `Door_NoBlockLight = 93`

  - `Container_Volume = 94`

  - `Container_Changeble = 95`

  - `Container_CannotPickUp = 96`

  - `Door_IsMultyHex = 97`

  - `Door_MultyHexLine1 = 98`

  - `Door_MultyHexLine2 = 99`

  - `Door_BlockerIds = 100`

  - `NavarroCountUseScaner = 101`

  - `NCRPostmanLocPidStart = 102`

  - `NCRPostmanLocPidRec = 103`

  - `NCRPostmanMapPidRec = 104`

  - `NCRPostmanNpcDidRec = 105`

  - `NCRPostmanPlayerID = 106`

  - `PetId = 107`

  - `PetProto = 108`

  - `PosterSNWall = 109`

  - `PosterEWWall = 110`

  - `RatGrenadeInvokeId = 111`

  - `ReddGatesGoodList = 112`

  - `ReddGatesBadList = 113`

  - `RespawnItemMode = 114`

  - `RespawnItemRespTime = 115`

  - `RespawnItemVarNum = 116`

  - `SeAndroidRadioListened = 117`

  - `SeAndroidVarNum = 118`

  - `SmokeGrenadeOwnerId = 119`

  - `Weight = 120`

  - `Volume = 121`

  - `GroundLevel = 122`

  - `IsShowAnim = 123`

  - `IsShowAnimExt = 124`

  - `IsCanTalk = 125`

  - `Mode = 126`

  - `AnimHide0 = 127`

  - `AnimHide1 = 128`

  - `AnimShow0 = 129`

  - `AnimShow1 = 130`

  - `AnimStay0 = 131`

  - `AnimStay1 = 132`

  - `AnimWaitBase = 133`

  - `AnimWaitRndMax = 134`

  - `AnimWaitRndMin = 135`

  - `Armor_CrTypeMale = 136`

  - `Armor_CrTypeFemale = 137`

  - `Armor_AC = 138`

  - `Armor_Perk = 139`

  - `Armor_DRNormal = 140`

  - `Armor_DRLaser = 141`

  - `Armor_DRFire = 142`

  - `Armor_DRPlasma = 143`

  - `Armor_DRElectr = 144`

  - `Armor_DREmp = 145`

  - `Armor_DRExplode = 146`

  - `Armor_DTNormal = 147`

  - `Armor_DTLaser = 148`

  - `Armor_DTFire = 149`

  - `Armor_DTPlasma = 150`

  - `Armor_DTElectr = 151`

  - `Armor_DTEmp = 152`

  - `Armor_DTExplode = 153`

  - `Weapon_IsUnarmed = 154`

  - `Weapon_UnarmedTree = 155`

  - `Weapon_UnarmedPriority = 156`

  - `Weapon_UnarmedMinAgility = 157`

  - `Weapon_UnarmedMinUnarmed = 158`

  - `Weapon_UnarmedMinLevel = 159`

  - `Weapon_MaxAmmoCount = 160`

  - `Weapon_Caliber = 161`

  - `Weapon_DefaultAmmoPid = 162`

  - `Weapon_StateAnim = 163`

  - `Weapon_MinStrength = 164`

  - `Weapon_Perk = 165`

  - `Weapon_IsTwoHanded = 166`

  - `Weapon_ActiveUses = 167`

  - `Weapon_Skill_0 = 168`

  - `Weapon_Skill_1 = 169`

  - `Weapon_Skill_2 = 170`

  - `Weapon_PicUse_0 = 171`

  - `Weapon_PicUse_1 = 172`

  - `Weapon_PicUse_2 = 173`

  - `Weapon_MaxDist_0 = 174`

  - `Weapon_MaxDist_1 = 175`

  - `Weapon_MaxDist_2 = 176`

  - `Weapon_Round_0 = 177`

  - `Weapon_Round_1 = 178`

  - `Weapon_Round_2 = 179`

  - `Weapon_ApCost_0 = 180`

  - `Weapon_ApCost_1 = 181`

  - `Weapon_ApCost_2 = 182`

  - `Weapon_Aim_0 = 183`

  - `Weapon_Aim_1 = 184`

  - `Weapon_Aim_2 = 185`

  - `Weapon_SoundId_0 = 186`

  - `Weapon_SoundId_1 = 187`

  - `Weapon_SoundId_2 = 188`

  - `Weapon_DmgType_0 = 189`

  - `Weapon_DmgType_1 = 190`

  - `Weapon_DmgType_2 = 191`

  - `Weapon_ActionAnim_0 = 192`

  - `Weapon_ActionAnim_1 = 193`

  - `Weapon_ActionAnim_2 = 194`

  - `Weapon_DmgMin_0 = 195`

  - `Weapon_DmgMin_1 = 196`

  - `Weapon_DmgMin_2 = 197`

  - `Weapon_DmgMax_0 = 198`

  - `Weapon_DmgMax_1 = 199`

  - `Weapon_DmgMax_2 = 200`

  - `Weapon_Remove_0 = 201`

  - `Weapon_Remove_1 = 202`

  - `Weapon_Remove_2 = 203`

  - `Weapon_Effect_0 = 204`

  - `Weapon_Effect_1 = 205`

  - `Weapon_Effect_2 = 206`

  - `Weapon_ReloadAp = 207`

  - `Weapon_UnarmedCriticalBonus = 208`

  - `Weapon_CriticalFailture = 209`

  - `Weapon_UnarmedArmorPiercing = 210`

  - `Ammo_Caliber = 211`

  - `Ammo_AcMod = 212`

  - `Ammo_DrMod = 213`

  - `Ammo_DmgMult = 214`

  - `Ammo_DmgDiv = 215`

  - `Car_Speed = 216`

  - `Car_Passability = 217`

  - `Car_DeteriorationRate = 218`

  - `Car_CrittersCapacity = 219`

  - `Car_TankVolume = 220`

  - `Car_MaxDeterioration = 221`

  - `Car_FuelConsumption = 222`

  - `Car_Entrance = 223`

  - `Car_MovementType = 224`

  - `Deteriorable = 225`

  - `IsBroken = 226`

  - `BrokenEternal = 227`

  - `BrokenLowBroken = 228`

  - `BrokenNormBroken = 229`

  - `BrokenHighBroken = 230`

  - `BrokenNotresc = 231`

  - `BrokenService = 232`

  - `BrokenServiceExt = 233`

  - `BrokenCount = 234`

  - `Deterioration = 235`

  - `LockerCondition = 236`

  - `IsLockpick = 237`

  - `Lockpick_Points = 238`

  - `Lockpick_IsElectro = 239`

  - `IsHolodisk = 240`

  - `HolodiskNum = 241`

  - `IsNoLoot = 242`

  - `IsNoSteal = 243`

  - `Val0 = 244`

  - `Val1 = 245`

  - `Val2 = 246`

  - `Val3 = 247`

  - `Val4 = 248`

  - `Val5 = 249`

  - `Val6 = 250`

  - `Val7 = 251`

  - `Val8 = 252`

  - `Val9 = 253`

  - `ScriptModule = 254`

  - `ScriptFunc = 255`

  - `BrokenFlags = 256`

  - `Cost = 257`

  - `SoundId = 258`

  - `Material = 259`

  - `AmmoPid = 260`

  - `AmmoCount = 261`

  - `Info = 262`

  - `IsCanUseOnSmth = 263`

  - `IsCanUse = 264`

  - `IsCanPickUp = 265`

  - `LastUsedTime = 266`

  - `IsQuestItem = 267`

  - `Indicator = 268`

  - `IndicatorMax = 269`

  - `Charge = 270`

  - `IsCanLook = 271`

  - `IsWallTransEnd = 272`

  - `IsHasTimer = 273`

  - `IsBigGun = 274`

  - `IsMultiHex = 275`

  - `ChildPid_0 = 276`

  - `ChildPid_1 = 277`

  - `ChildPid_2 = 278`

  - `ChildPid_3 = 279`

  - `ChildPid_4 = 280`

  - `ChildLines_0 = 281`

  - `ChildLines_1 = 282`

  - `ChildLines_2 = 283`

  - `ChildLines_3 = 284`

  - `ChildLines_4 = 285`

  - `Type = 286`

  - `TriggerNum = 287`

  - `Container_MagicHandsGrnd = 288`

  - `Grid_Type = 289`

  - `Grid_ToMap = 290`

  - `Grid_ToMapEntry = 291`

  - `Grid_ToMapDir = 292`

  - `SceneryParams = 293`

  - `V13GorisEggPlayerId = 294`

  - `VCityCommonIsMail = 295`

  - `VCityCommonMailOwnerId = 296`

* `CritterProperty`

  ...

  - `Invalid = 0xFFFF`

  - `CustomHolderId = 0`

  - `CustomHolderEntry = 1`

  - `InnerEntityIds = 2`

  - `InitScript = 3`

  - `MapId = 4`

  - `GlobalMapTripId = 5`

  - `HexX = 6`

  - `HexY = 7`

  - `HexOffsX = 8`

  - `HexOffsY = 9`

  - `Dir = 10`

  - `DirAngle = 11`

  - `ItemIds = 12`

  - `ModelName = 13`

  - `Multihex = 14`

  - `AliveStateAnim = 15`

  - `KnockoutStateAnim = 16`

  - `DeadStateAnim = 17`

  - `AliveActionAnim = 18`

  - `KnockoutActionAnim = 19`

  - `DeadActionAnim = 20`

  - `ScaleFactor = 21`

  - `ShowCritterDist1 = 22`

  - `ShowCritterDist2 = 23`

  - `ShowCritterDist3 = 24`

  - `ModelLayers = 25`

  - `TE_Identifier = 26`

  - `TE_FireTime = 27`

  - `TE_FuncName = 28`

  - `TE_Rate = 29`

  - `IdlePeriod = 30`

  - `ControlledByPlayer = 31`

  - `IsChosen = 32`

  - `IsPlayerOffline = 33`

  - `IsAttached = 34`

  - `AttachMaster = 35`

  - `HideSprite = 36`

  - `MovingSpeed = 37`

  - `SexTagFemale = 38`

  - `ModelInCombatMode = 39`

  - `WorldX = 40`

  - `WorldY = 41`

  - `Condition = 42`

  - `NameOffset = 43`

  - `GlobalMapFog = 44`

  - `SneakCoefficient = 45`

  - `LookDistance = 46`

  - `TalkDistance = 47`

  - `MaxTalkers = 48`

  - `DialogId = 49`

  - `Lexems = 50`

  - `KnownLocations = 51`

  - `InSneakMode = 52`

  - `DeadDrawNoFlatten = 53`

  - `NameColor = 54`

  - `ContourColor = 55`

  - `ArroyoRaydersAttackedId = 56`

  - `BehemothOwner = 57`

  - `BehemothRadio = 58`

  - `BehemothLastComand = 59`

  - `BehemothOrderType = 60`

  - `BehemothLastOrder = 61`

  - `BehemothParam_1 = 62`

  - `BehemothParam_2 = 63`

  - `BehemothLastReport = 64`

  - `BHHubHoloRemembered = 65`

  - `BHUranDiscount = 66`

  - `BBMsgPage = 67`

  - `BBSelectedMsg = 68`

  - `KlamAldoBusy = 69`

  - `KlamAldoListenId = 70`

  - `KlamAldoReaderId = 71`

  - `BBMsgCount = 72`

  - `CaravanCrvId = 73`

  - `VCDeadPatrollers = 74`

  - `ReddWadeCaravanEscort = 75`

  - `ReddSavinelCaravanEscort = 76`

  - `ReddStanCaravanEscort = 77`

  - `NcrReddingCaravanEscort = 78`

  - `BHKitCaravanEscort = 79`

  - `VCShrimPatrol = 80`

  - `ArroyoSelmaCaravanEscort = 81`

  - `ArroyoGayzumCaravanEscort = 82`

  - `ArroyoLaumerCaravanEscort = 83`

  - `ModAurelianoCaravanEscort = 84`

  - `CommonCrvResetCounter = 85`

  - `ReddCrvResetCounter = 86`

  - `NcrCrvResetCounter = 87`

  - `BHCrvResetCounter = 88`

  - `ArroyoCrvResetCounter = 89`

  - `CaravanReaction = 90`

  - `CaravanNervosityLvl = 91`

  - `CaravanIdleCount = 92`

  - `LastSelectedCaravan = 93`

  - `ApRegenerationTick = 94`

  - `ApRegenerationTime = 95`

  - `CollectorTimeNextSearch = 96`

  - `CompRiddleMapId = 97`

  - `CompRiddleHexX = 98`

  - `CompRiddleHexY = 99`

  - `KnockoutAp = 100`

  - `WaitEndTick = 101`

  - `ActionAnimKnockoutEnd = 102`

  - `NcrBusterLostCStatus = 103`

  - `QDappoLostRobotHexNum = 104`

  - `BankMoney = 105`

  - `DenHubBank5 = 106`

  - `DenHubGuard5 = 107`

  - `DenPoormanItemId = 108`

  - `DenVirginCount = 109`

  - `DenVirginIsHome = 110`

  - `UniqTimeout = 111`

  - `Loyality = 112`

  - `NpcStory = 113`

  - `NameMemNpcPlayer = 114`

  - `NameMemPlayerNpc = 115`

  - `TradeWas = 116`

  - `DenKliffBlessWas = 117`

  - `DenVirginiaSexWas = 118`

  - `NcrPlayerTalkPoliceman = 119`

  - `SFLoPanPayed = 120`

  - `ChanceOneFromTwo = 121`

  - `ChanceOneFromThree = 122`

  - `ChanceOneFromFive = 123`

  - `CurrentDialogNumber = 124`

  - `LastDialogBoxShownTick = 125`

  - `DrugEffects = 126`

  - `DoughnutsCounter = 127`

  - `LastElectronicLocked = 128`

  - `EliTimeNextSing = 129`

  - `EnemyStack = 130`

  - `IsNoEnemyStack = 131`

  - `EnergyBarierTerminalHx = 132`

  - `EnergyBarierTerminalHy = 133`

  - `EnergyBarierNetNum = 134`

  - `EnergyBarierHackBonus = 135`

  - `EnergyBarierHitBonus = 136`

  - `FighterPatternCanGenStim = 137`

  - `FighterPatternAllyAssistRadius = 138`

  - `FighterPatternAssistAlliesNum = 139`

  - `FighterPatternMustHealLvl = 140`

  - `FighterPatternLocalAlarmDeads = 141`

  - `FighterPatternGlobalAlarmDeads = 142`

  - `FighterQuestMinHp = 143`

  - `FighterQuestOnlyHandCombat = 144`

  - `FighterQuestTeamIdOld = 145`

  - `FighterQuestTeamIdFight = 146`

  - `FighterQuestPlayerId = 147`

  - `FighterQuestFightPriority = 148`

  - `FighterQuestVarNum = 149`

  - `FixboyPowerArmor = 150`

  - `ModLourenceVenomedratRecipe = 151`

  - `ModLourenceTNTRatRecipe = 152`

  - `NavEmpRocketRecipe = 153`

  - `FixboyDefault = 154`

  - `SFRecipeSsupersledge = 155`

  - `SFRecipePlasmagrenades = 156`

  - `Fixboy700NitroExpress = 157`

  - `FixboyAmmoPressOperator = 158`

  - `RacingCheckPoints = 159`

  - `RacingCheckpointLocId = 160`

  - `GERacingCritterHx = 161`

  - `GERacingCritterHy = 162`

  - `GERacingCritterDir = 163`

  - `GERacingNpcRole = 164`

  - `GERacingOpeningPhrases = 165`

  - `GEReplExplodeTank = 166`

  - `GEReplNopasaran = 167`

  - `GEReplFindstation = 168`

  - `GEReplNotifictions = 169`

  - `GEReplEntryZombie = 170`

  - `GEReplLastOrder = 171`

  - `GEReplIsAddedAttackPlane = 172`

  - `HellMineTimeoutEnd = 173`

  - `HostileLQIsStoped = 174`

  - `HostileLQData = 175`

  - `SFAhs7Escort = 176`

  - `SFHonomerPlayerId = 177`

  - `SFEscortLocation = 178`

  - `SFLabFailed = 179`

  - `QHubLabIsDialogRun = 180`

  - `BarterLourensRats1 = 181`

  - `ModLourenceRatsFlute = 182`

  - `BarterLourensRatBodycount = 183`

  - `ModHoughRatsFluteTimeout = 184`

  - `ModLourenceToxinTimeout = 185`

  - `ModLourenceRatsFluteCounter = 186`

  - `ModLourenceLureActive = 187`

  - `GuardedItemSkill = 188`

  - `V13DclawEggs = 189`

  - `KlamTorrCowboy = 190`

  - `KlamCowboyCountGav = 191`

  - `KlamCowboyMobHx = 192`

  - `KlamCowboyMobHy = 193`

  - `KlamDantonBramin = 194`

  - `KlamJosallDanton = 195`

  - `KlamKuklachev = 196`

  - `KlamSmilyGecko = 197`

  - `KlamSmilyCurrentHp = 198`

  - `KlamSmilyCountKills = 199`

  - `KlamSmilyHealing = 200`

  - `LimitedBarterData = 201`

  - `IsGeck = 202`

  - `StealExpCount = 203`

  - `FirstAidCount = 204`

  - `MainQuest = 205`

  - `GCityCitizen = 206`

  - `MapGeckCityTraderSkillBarter = 207`

  - `MapKlamathRobotTimeNextSay = 208`

  - `ModJoeGiantWasp = 209`

  - `TribSulikRaid = 210`

  - `TribRaiderKillCount = 211`

  - `NCRElizeSlavers = 212`

  - `MapPrimalTribeRaiderHx = 213`

  - `MapPrimalTribeRaiderHy = 214`

  - `SFRonKillBeasts = 215`

  - `SFRonFindbodies = 216`

  - `SFTankerCentaurNoticed = 217`

  - `SFTankerFloaterNoticed = 218`

  - `MapSFTankerBicycleId = 219`

  - `TextOnHead = 220`

  - `TextOnHeadEndTime = 221`

  - `MirelurkCombatCurStage = 222`

  - `MirelurkCombatTimeNextStage = 223`

  - `MirelurkCombatLastBrokenBag = 224`

  - `MirelurkCombatDestroyingItem = 225`

  - `MobAttackedId = 226`

  - `MobFury = 227`

  - `MobFear = 228`

  - `MobMaxFear = 229`

  - `ModVampireFarmLocation = 230`

  - `MonologueData = 231`

  - `NavHenryEmpTest = 232`

  - `NavEmpTestedCritter = 233`

  - `NavarroTimeOutScan = 234`

  - `NavarroChipUsedId = 235`

  - `NcrAlexHoloFindStatus = 236`

  - `NCRFelixFindBrahmin = 237`

  - `NCRHubBook = 238`

  - `NCRFelixSaveBrahmin = 239`

  - `NCRHubBookAccess1 = 240`

  - `NCRHubBookAccess2 = 241`

  - `NCRHubBookAccess3 = 242`

  - `NCRHubBookAccess4 = 243`

  - `NCRHubBookAccess5 = 244`

  - `NCRHubBookAccess6 = 245`

  - `NCRHubBookAccess7 = 246`

  - `NCRHubBookQuestTimeout = 247`

  - `NcrCommonBeggarInvokeId = 248`

  - `NcrCommonBeggarPhraseNum = 249`

  - `NcrCommonBeggarHideMoneyInvocation = 250`

  - `NcrCommonBrahminId = 251`

  - `QNcrElizeInvasion = 252`

  - `NCRKarlsonSon = 253`

  - `NcrSonCatcherId = 254`

  - `NcrSonMovesCounter = 255`

  - `NcrMichealMessageNum = 256`

  - `MailDelivery = 257`

  - `NcrMailRecieverId = 258`

  - `NcrMailTimeout = 259`

  - `NcrRatchBuggy = 260`

  - `NcrShaimanProtest = 261`

  - `NcrShaimanStringNum = 262`

  - `NcrSiegeTerminate = 263`

  - `NcrSiegeKillsCounter = 264`

  - `NcrSmitVsVestinStatus = 265`

  - `NcrSmitStringNum = 266`

  - `NcrSmitGateStringNum = 267`

  - `NcrSmitPlayerId = 268`

  - `NcrSmitIdleCount = 269`

  - `NcrWestinMapPidTo = 270`

  - `NcrWestinHexNumTo = 271`

  - `NcrWestinEveryEveningInvokeId = 272`

  - `NcrWestinEveryMorningInvokeId = 273`

  - `LastBagRefreshedTime = 274`

  - `LastNpcDialog = 275`

  - `NpcDialogStringNum = 276`

  - `Planes = 277`

  - `NpcRevengeNpcHxHy = 278`

  - `NpcRevengeCountWait = 279`

  - `NRWriKidnap = 280`

  - `NRSalvatoreKill = 281`

  - `NRWriKidnapNotifyTime = 282`

  - `NRKidnapKillsCounter = 283`

  - `QNrWriKidnapInvokeId = 284`

  - `NukeStock = 285`

  - `NukeRestockTime = 286`

  - `PatternSniperCountRunning = 287`

  - `PetOwnerId = 288`

  - `PetLifeTime = 289`

  - `IsGenerated = 290`

  - `PokerWins = 291`

  - `PokerNumOfNpc = 292`

  - `PokerWincash = 293`

  - `PokerFraud = 294`

  - `PokerManywins = 295`

  - `PokerData = 296`

  - `QWarehouse = 297`

  - `QWarehouseSub1 = 298`

  - `QWarehouseSub2 = 299`

  - `WarehouseDataId = 300`

  - `WarehouseQuestData = 301`

  - `WarehouseOther = 302`

  - `RatGrenadeProtoId = 303`

  - `RatGrenadeOwnerId = 304`

  - `ReddMineNuggets = 305`

  - `ReddMarionWan = 306`

  - `ReddQWinamingoKills = 307`

  - `ReddQWinamingoHealing = 308`

  - `ReddDoctorPoisoned = 309`

  - `ReddRooneyCemetery = 310`

  - `CanRepairWeapons = 311`

  - `CanRepairWeaponsSpecial = 312`

  - `CanRepairArmor = 313`

  - `CanRepairArmorSpecial = 314`

  - `RepairCompleteTime = 315`

  - `RepairItemPid = 316`

  - `ReplicationTime = 317`

  - `HellVisits = 318`

  - `ReplBankIsCanEnter = 319`

  - `ReplBankeIsAttackGagPlayer = 320`

  - `ReplHellTurretHack = 321`

  - `TerminalPlayerId = 322`

  - `TerminalDialogId = 323`

  - `ModFarrelAmmiak = 324`

  - `RouletteCroupierNum = 325`

  - `RouletteBetCoord1 = 326`

  - `RouletteBetCoord2 = 327`

  - `RouletteBetCoord3 = 328`

  - `RouletteBetSize = 329`

  - `RouletteBetType = 330`

  - `RouletteData = 331`

  - `CanSendSay = 332`

  - `Scores = 333`

  - `SEAndroidMonologEnd = 334`

  - `SETalkingHeadStringNum = 335`

  - `SETeleportEatId = 336`

  - `SFAhs7HubJudgement = 337`

  - `SFLoPanBlackmailSum = 338`

  - `SFHububJudgementLocId = 339`

  - `SFHubJudgementKills = 340`

  - `SfMercMaster = 341`

  - `SFCommonOneWeekInvokeId = 342`

  - `SFCommonFightPlayerId = 343`

  - `ClickCounter = 344`

  - `SFInvasionMirelurkKills = 345`

  - `BHRocketBase = 346`

  - `NcrElizeSlvrsHunting = 347`

  - `NcrElizeSlvrsHuntingStatus = 348`

  - `NcrSantiagoSpyMission = 349`

  - `QSpyMissonStringNum = 350`

  - `TimeoutBattle = 351`

  - `TimeoutTransfer = 352`

  - `WalkSpeedBase = 353`

  - `WalkSpeed = 354`

  - `IsNoMove = 355`

  - `IsNoMoveBase = 356`

  - `IsNoRun = 357`

  - `IsNoRunBase = 358`

  - `Strength = 359`

  - `StrengthBase = 360`

  - `Perception = 361`

  - `PerceptionBase = 362`

  - `Endurance = 363`

  - `EnduranceBase = 364`

  - `Charisma = 365`

  - `CharismaBase = 366`

  - `Intellect = 367`

  - `IntellectBase = 368`

  - `Agility = 369`

  - `AgilityBase = 370`

  - `Luck = 371`

  - `LuckBase = 372`

  - `ArmorClass = 373`

  - `CurrentHp = 374`

  - `MaxLife = 375`

  - `MaxLifeBase = 376`

  - `ActionPointsBase = 377`

  - `ArmorClassBase = 378`

  - `MeleeDamage = 379`

  - `MeleeDamageBase = 380`

  - `IsOverweight = 381`

  - `CarryWeight = 382`

  - `CarryWeightBase = 383`

  - `Sequence = 384`

  - `SequenceBase = 385`

  - `HealingRate = 386`

  - `HealingRateBase = 387`

  - `CriticalChance = 388`

  - `CriticalChanceBase = 389`

  - `MaxCritical = 390`

  - `MaxCriticalBase = 391`

  - `Toxic = 392`

  - `Radioactive = 393`

  - `KillExperience = 394`

  - `BodyType = 395`

  - `LocomotionType = 396`

  - `DamageType = 397`

  - `Age = 398`

  - `Gender = 399`

  - `PoisoningLevel = 400`

  - `RadiationLevel = 401`

  - `UnspentSkillPoints = 402`

  - `UnspentPerks = 403`

  - `Karma = 404`

  - `ReplicationMoney = 405`

  - `ReplicationCount = 406`

  - `ReplicationCost = 407`

  - `RateObject = 408`

  - `BonusLook = 409`

  - `NpcRole = 410`

  - `AiId = 411`

  - `TeamId = 412`

  - `NextCrType = 413`

  - `DeadBlockerId = 414`

  - `CurrentArmorPerk = 415`

  - `NextReplicationMap = 416`

  - `NextReplicationEntry = 417`

  - `PlayerKarma = 418`

  - `ArmorPerk = 419`

  - `LastStealCrId = 420`

  - `StealCount = 421`

  - `GlobalMapMoveCounter = 422`

  - `Experience = 423`

  - `MaxMoveApBase = 424`

  - `AnimType = 425`

  - `IsNoUnarmed = 426`

  - `KnownLocProtoId = 427`

  - `IsNoHome = 428`

  - `HomeMapId = 429`

  - `HomeMapPid = 430`

  - `HomeHexX = 431`

  - `HomeHexY = 432`

  - `HomeDir = 433`

  - `IsNoTalk = 434`

  - `MapLeaveHexX = 435`

  - `MapLeaveHexY = 436`

  - `KnownLockerId = 437`

  - `SpecialSkillPickOnGround = 438`

  - `SpecialSkillLootCritter = 439`

  - `FollowLeaderId = 440`

  - `LastSendEntrancesLocId = 441`

  - `LastSendEntrancesTick = 442`

  - `CrTypeAliasBase = 443`

  - `CrTypeAlias = 444`

  - `ModelNameBase = 445`

  - `IsNoArmor = 446`

  - `Anims = 447`

  - `IsNoAim = 448`

  - `Kills = 449`

  - `KillMen = 450`

  - `KillWomen = 451`

  - `KillAlien = 452`

  - `KillChildren = 453`

  - `KillFloater = 454`

  - `KillRat = 455`

  - `KillCentaur = 456`

  - `ReputationDen = 457`

  - `ReputationKlamath = 458`

  - `ReputationModoc = 459`

  - `ReputationVaultCity = 460`

  - `ReputationGecko = 461`

  - `ReputationBrokenHills = 462`

  - `ReputationNewReno = 463`

  - `ReputationSierra = 464`

  - `ReputationVault15 = 465`

  - `ReputationNCR = 466`

  - `ReputationCathedral = 467`

  - `ReputationSAD = 468`

  - `ReputationRedding = 469`

  - `ReputationSF = 470`

  - `ReputationNavarro = 471`

  - `ReputationArroyo = 472`

  - `ReputationPrimalTribe = 473`

  - `ReputationRangers = 474`

  - `ReputationVault13 = 475`

  - `ReputationSacramento = 476`

  - `Addictions = 477`

  - `IsAddicted = 478`

  - `IsJetAddicted = 479`

  - `IsBuffoutAddicted = 480`

  - `IsMentatsAddicted = 481`

  - `IsPsychoAddicted = 482`

  - `IsRadawayAddicted = 483`

  - `DamageResistance = 484`

  - `NormalResistance = 485`

  - `PoisonResistance = 486`

  - `RadiationResistance = 487`

  - `ExplodeResistance = 488`

  - `NormalResistanceBase = 489`

  - `LaserResistanceBase = 490`

  - `FireResistanceBase = 491`

  - `PlasmaResistanceBase = 492`

  - `ElectricityResistanceBase = 493`

  - `EmpResistanceBase = 494`

  - `ExplodeResistanceBase = 495`

  - `PoisonResistanceBase = 496`

  - `RadiationResistanceBase = 497`

  - `DamageThreshold = 498`

  - `NormalThresholdBase = 499`

  - `LaserThresholdBase = 500`

  - `FireThresholdBase = 501`

  - `PlasmaThresholdBase = 502`

  - `ElectricityThresholdBase = 503`

  - `EmpThresholdBase = 504`

  - `ExplodeThresholdBase = 505`

  - `PoisonThresholdBase = 506`

  - `RadiationThresholdBase = 507`

  - `IsPoisoned = 508`

  - `IsRadiated = 509`

  - `IsInjured = 510`

  - `IsDamagedEye = 511`

  - `IsDamagedRightArm = 512`

  - `IsDamagedLeftArm = 513`

  - `IsDamagedRightLeg = 514`

  - `IsDamagedLeftLeg = 515`

  - `Var0 = 516`

  - `Var1 = 517`

  - `Var2 = 518`

  - `Var3 = 519`

  - `Var4 = 520`

  - `Var5 = 521`

  - `Var6 = 522`

  - `Var7 = 523`

  - `Var8 = 524`

  - `Var9 = 525`

  - `SkillSmallGuns = 526`

  - `SkillBigGuns = 527`

  - `SkillEnergyWeapons = 528`

  - `SkillUnarmed = 529`

  - `SkillMeleeWeapons = 530`

  - `SkillThrowing = 531`

  - `SkillFirstAid = 532`

  - `SkillDoctor = 533`

  - `SkillSneak = 534`

  - `SkillLockpick = 535`

  - `SkillSteal = 536`

  - `SkillTraps = 537`

  - `SkillScience = 538`

  - `SkillRepair = 539`

  - `SkillSpeech = 540`

  - `SkillBarter = 541`

  - `SkillGambling = 542`

  - `SkillOutdoorsman = 543`

  - `TagSkills = 544`

  - `TagSkill1 = 545`

  - `TagSkill2 = 546`

  - `TagSkill3 = 547`

  - `PerkBookworm = 548`

  - `PerkAwareness = 549`

  - `PerkBonusHthAttacks = 550`

  - `PerkBonusHthDamage = 551`

  - `PerkBonusRangedDamage = 552`

  - `PerkBonusRateOfFire = 553`

  - `PerkEarlierSequence = 554`

  - `PerkFasterHealing = 555`

  - `PerkMoreCriticals = 556`

  - `PerkNightVision = 557`

  - `PerkRadResistance = 558`

  - `PerkToughness = 559`

  - `PerkStrongBack = 560`

  - `PerkSharpshooter = 561`

  - `PerkSurvivalist = 562`

  - `PerkEducated = 563`

  - `PerkHealer = 564`

  - `PerkFortuneFinder = 565`

  - `PerkBetterCriticals = 566`

  - `PerkEmpathy = 567`

  - `PerkSlayer = 568`

  - `PerkSniper = 569`

  - `PerkSilentDeath = 570`

  - `PerkActionBoy = 571`

  - `PerkMentalBlock = 572`

  - `PerkLifegiver = 573`

  - `PerkDodger = 574`

  - `PerkSnakeater = 575`

  - `PerkMrFixit = 576`

  - `PerkMedic = 577`

  - `PerkMasterThief = 578`

  - `PerkSpeaker = 579`

  - `PerkHeaveHo = 580`

  - `PerkFriendlyFoe = 581`

  - `PerkPickpocket = 582`

  - `PerkGhost = 583`

  - `PerkCultOfPersonality = 584`

  - `PerkScrounger = 585`

  - `PerkExplorer = 586`

  - `PerkFlowerChild = 587`

  - `PerkPathfinder = 588`

  - `PerkAnimalFriend = 589`

  - `PerkScout = 590`

  - `PerkMysteriousStranger = 591`

  - `PerkRanger = 592`

  - `PerkSmoothTalker = 593`

  - `PerkSwiftLearner = 594`

  - `PerkTag = 595`

  - `PerkMutate = 596`

  - `PerkAdrenalineRush = 597`

  - `PerkCautiousNature = 598`

  - `PerkComprehension = 599`

  - `PerkDemolitionExpert = 600`

  - `PerkGambler = 601`

  - `PerkGainStrength = 602`

  - `PerkGainPerception = 603`

  - `PerkGainEndurance = 604`

  - `PerkGainCharisma = 605`

  - `PerkGainIntelligence = 606`

  - `PerkGainAgility = 607`

  - `PerkGainLuck = 608`

  - `PerkHarmless = 609`

  - `PerkHereAndNow = 610`

  - `PerkHthEvade = 611`

  - `PerkKamaSutraMaster = 612`

  - `PerkKarmaBeacon = 613`

  - `PerkLightStep = 614`

  - `PerkLivingAnatomy = 615`

  - `PerkMagneticPersonality = 616`

  - `PerkNegotiator = 617`

  - `PerkPackRat = 618`

  - `PerkPyromaniac = 619`

  - `PerkQuickRecovery = 620`

  - `PerkSalesman = 621`

  - `PerkStonewall = 622`

  - `PerkThief = 623`

  - `PerkWeaponHandling = 624`

  - `PerkVaultCityTraining = 625`

  - `PerkExpertExcrement = 626`

  - `PerkTerminator = 627`

  - `PerkGeckoSkinning = 628`

  - `PerkVaultCityInoculations = 629`

  - `PerkDermalImpact = 630`

  - `PerkDermalImpactEnh = 631`

  - `PerkPhoenixImplants = 632`

  - `PerkPhoenixImplantsEnh = 633`

  - `PerkNcrPerception = 634`

  - `PerkNcrEndurance = 635`

  - `PerkNcrBarter = 636`

  - `PerkNcrRepair = 637`

  - `PerkVampireAccuracy = 638`

  - `PerkVampireRegeneration = 639`

  - `PerkQuickPockets = 640`

  - `PerkMasterTrader = 641`

  - `PerkSilentRunning = 642`

  - `PerkBonusMove = 643`

  - `KarmaPerkBerserker = 644`

  - `KarmaPerkChampion = 645`

  - `KarmaPerkChildkiller = 646`

  - `KarmaPerkSexpert = 647`

  - `KarmaPerkPrizefighter = 648`

  - `KarmaPerkGigolo = 649`

  - `KarmaPerkGraveDigger = 650`

  - `KarmaPerkMarried = 651`

  - `KarmaPerkPornStar = 652`

  - `KarmaPerkSlaver = 653`

  - `KarmaPerkVirginWastes = 654`

  - `KarmaPerkManSalvatore = 655`

  - `KarmaPerkManBishop = 656`

  - `KarmaPerkManMordino = 657`

  - `KarmaPerkManWright = 658`

  - `KarmaPerkSeparated = 659`

  - `KarmaPerkPedobear = 660`

  - `KarmaPerkVcGuardsman = 661`

  - `IsTraitFastMetabolism = 662`

  - `IsTraitBruiser = 663`

  - `IsTraitSmallFrame = 664`

  - `IsTraitOneHander = 665`

  - `IsTraitFinesse = 666`

  - `IsTraitKamikaze = 667`

  - `IsTraitHeavyHanded = 668`

  - `IsTraitFastShot = 669`

  - `IsTraitBloodyMess = 670`

  - `IsTraitJinxed = 671`

  - `IsTraitJinxedII = 672`

  - `IsTraitGoodNatured = 673`

  - `IsTraitChemReliant = 674`

  - `IsTraitChemResistant = 675`

  - `IsTraitSexAppeal = 676`

  - `IsTraitSkilled = 677`

  - `IsTraitNightPerson = 678`

  - `TimeoutSkFirstAid = 679`

  - `TimeoutSkDoctor = 680`

  - `TimeoutSkRepair = 681`

  - `TimeoutSkScience = 682`

  - `TimeoutSkLockpick = 683`

  - `TimeoutSkSteal = 684`

  - `TimeoutSkOutdoorsman = 685`

  - `TimeoutRemoveFromGame = 686`

  - `TimeoutReplication = 687`

  - `TimeoutKarmaVoting = 688`

  - `TimeoutSneak = 689`

  - `TimeoutHealing = 690`

  - `TimeoutStealing = 691`

  - `TimeoutAggressor = 692`

  - `MercMasterId = 693`

  - `MercAlwaysRun = 694`

  - `MercCancelOnAttack = 695`

  - `MercLoseDist = 696`

  - `MercMasterDist = 697`

  - `MercType = 698`

  - `MercDefendMaster = 699`

  - `MercAssistMaster = 700`

  - `MercCancelTime = 701`

  - `MercCancelOnGlobal = 702`

  - `MercWaitForMaster = 703`

  - `ArroyoMynocDefence = 704`

  - `ArroyoCassidyLetter = 705`

  - `ArroyoMynocOil = 706`

  - `ArroyoProofOfDeath = 707`

  - `ArroyoLetterToLinnett = 708`

  - `KlamSallyFindProstitute = 709`

  - `KlamBobWater = 710`

  - `KlamFindTrappers = 711`

  - `KlamBugenLure = 712`

  - `KlamNotifyHusband = 713`

  - `KlamEidenBramin = 714`

  - `KlamSmilyModoc = 715`

  - `DenBillRacingWin = 716`

  - `DenLeannaCondom = 717`

  - `QDenAnanDoll = 718`

  - `DenAnanRedoll = 719`

  - `DenGhost = 720`

  - `DenBillRacingOpening = 721`

  - `DenCarstopJeffry = 722`

  - `DenCarstopBrahmin = 723`

  - `DenCarstopBreeder = 724`

  - `DenJoeySteal = 725`

  - `DenJaneDolg = 726`

  - `DenJanePsycho = 727`

  - `DenLaraPostal = 728`

  - `DenFlikJet = 729`

  - `DenLaraBand = 730`

  - `DenJoeyLoan = 731`

  - `DenLaraBos = 732`

  - `QDenCliffDealer = 733`

  - `DenFredStim = 734`

  - `DenJaneVodka = 735`

  - `DenMomSlut = 736`

  - `DenSmittyBatt = 737`

  - `DenJaneMeat = 738`

  - `DenJaneStim = 739`

  - `DenLaraMolotovCoctail = 740`

  - `DenLeannaBuy = 741`

  - `DenSmittyBoots = 742`

  - `DenJaneGuns = 743`

  - `DenSmittyKey = 744`

  - `DenJaneArmor = 745`

  - `DenSmittyAmmo = 746`

  - `DenJaneHunt = 747`

  - `DenJoeyKnife = 748`

  - `DenJoeyLara = 749`

  - `DenJaneRadio = 750`

  - `DenJoeyJet = 751`

  - `DenLaraTrust = 752`

  - `DenLeannaWine = 753`

  - `DenMomRadscorp = 754`

  - `DenSmittyFixit = 755`

  - `QDenLeannaThief = 756`

  - `ModJoeFarm = 757`

  - `ModHose = 758`

  - `ModBaltasGecko = 759`

  - `ModLourenceRatsColony = 760`

  - `ModLourenceFloater = 761`

  - `ModJoeVampire = 762`

  - `BHMarcusEscort = 763`

  - `BHSuperNewTechnology = 764`

  - `ReddDocRadio = 765`

  - `ReddDocRadioTroy = 766`

  - `ReddDocRadioFung = 767`

  - `ReddDocRadioHoliday = 768`

  - `ReddDocRadioJubiley = 769`

  - `ReddHubbChildkiller = 770`

  - `ReddMarionVinamingo = 771`

  - `ReddDoctorDelivery = 772`

  - `NavHenryProtoMaterials = 773`

  - `NavSoftJob = 774`

  - `NcrHatePatrol = 775`

  - `NcrSantiagaFindSpyStatus = 776`

  - `NcrBusterBrokenrifles = 777`

  - `NcrKessMedBoardStatus = 778`

  - `NcrDorotyFindHenryPapers = 779`

  - `NcrLeadSmit2Dustybar = 780`

  - `NcrKyleReddRecon = 781`

  - `NcrDuppoFindDasies = 782`

  - `NcrDappoLostC = 783`

  - `QChosen = 784`

  - `NRBarmenEscort = 785`

  - `SFAhs7ImperatorFormat = 786`

  - `SFEvaHelpWithZax = 787`

  - `SFKenliImperatorRestore = 788`

  - `SFLoPanBlackmail = 789`

  - `SFTigangRecipe = 790`

  - `SFNarcoman = 791`

  - `SFAhs7Invitations = 792`

  - `SFSlimSidnancy = 793`

  - `VCLetterToTodd = 794`

  - `VCValeryMail = 795`

  - `VCCindyLetter = 796`

  - `VCHartmannRecon = 797`

  - `VCHartmanNcrHelp = 798`

  - `VCBarmenDelivery = 799`

  - `VCCharlie = 800`

  - `VCTroyFreshBlood = 801`

  - `VCAndrewDeliveries = 802`

  - `VCBlackEscort = 803`

  - `VCHartmanFight = 804`

  - `VCLynettScareNewcomers = 805`

  - `VCHartmanRifles = 806`

  - `VCHeleneTroyBeauty = 807`

  - `TribSulikStuff = 808`

  - `TribMuscoTest = 809`

  - `TribShamanPowder = 810`

  - `TribMaiaraBook = 811`

  - `TribManotaNecklace = 812`

  - `BHDeadSaboteursCounter = 813`

  - `SpecialAndroid = 814`

  - `VCLynettRefuse = 815`

  - `DialogTimeout = 816`

  - `EncLoyalityHubologists = 817`

  - `EncLoyalityNcr = 818`

  - `EncLoyalityVCity = 819`

  - `EncLoyalityRedding = 820`

  - `EncLoyalityBroken = 821`

  - `EncLoyalityGecko = 822`

  - `EncLoyalityArroyo = 823`

  - `EncLoyalityKlamath = 824`

  - `EncLoyalityModoc = 825`

  - `EncLoyalityDen = 826`

  - `EncLoyalityReno = 827`

  - `EncLoyalityEnclave = 828`

  - `EncLoyalitySf = 829`

  - `ModLourenceToxinRecipe = 830`

  - `SFChitinArmorRecipeKnown = 831`

  - `SpyCathActive = 832`

  - `HasNotCard = 833`

  - `SexExp = 834`

  - `ScenFraction = 835`

  - `ArroyoDocHealing = 836`

  - `AtollTesla = 837`

  - `AtollMoney = 838`

  - `BHEscortNpcId = 839`

  - `ScenBosSoldier = 840`

  - `SFInvasionBadge = 841`

  - `ScenBosScriber = 842`

  - `ScenEnclaveSoldier = 843`

  - `ScenEnclaveScient = 844`

  - `DenJaneTraderFred = 845`

  - `DenJaneJobCounter = 846`

  - `DenJoeyCounter = 847`

  - `DenLaraBosCounter = 848`

  - `DenJaneTraderMom = 849`

  - `DenNarcCommMember = 850`

  - `DenJaneTraderLean = 851`

  - `EncOceanTraderFamiliar = 852`

  - `ModBaltasArmor1 = 853`

  - `GeckGaroldTrain = 854`

  - `GeckSkitrTransit = 855`

  - `KlamBaknerBeer = 856`

  - `ModBaltasArmor = 857`

  - `KlamVaccination = 858`

  - `KlamVaccinationB1 = 859`

  - `KlamVaccinationB2 = 860`

  - `KlamVaccinationB3 = 861`

  - `KlamGoldBeer = 862`

  - `KlamSallyPay = 863`

  - `ModBaltasArmor2 = 864`

  - `KlamVicFixittrash = 865`

  - `ModHoseTools = 866`

  - `ModVampireReaction = 867`

  - `NcrAlexQuestStatus = 868`

  - `NcrDustyPartyStatusChar = 869`

  - `NcrMiraTroubleStatusChar = 870`

  - `NcrBeggarTalk = 871`

  - `NcrDorothyGammaStatusChar = 872`

  - `NcrDumontBrkradioStatusChar = 873`

  - `NcrCaptainFlirtStatusChar = 874`

  - `NcrIsNightGuardAccessFranted = 875`

  - `NcrClausHistory = 876`

  - `NcrJubileyTailsStatus = 877`

  - `NcrRondoDorotyStatus = 878`

  - `NcrFergusStory = 879`

  - `NcrCaptainSmitAccessGranted = 880`

  - `NcrJubileyTailsCounter = 881`

  - `NcrBusterDorotyStatus = 882`

  - `NcrFergusSecret = 883`

  - `NcrGunterStory = 884`

  - `ScenRangerRank = 885`

  - `NcrDustyFoodDeliveryStatus = 886`

  - `NcrPlayerLeadSmit2Dustybar = 887`

  - `NcrKarlStory = 888`

  - `NcrCarlsonStory = 889`

  - `NcrKukComp = 890`

  - `NcrMicQStatus = 891`

  - `ScenRanger = 892`

  - `NcrDumontHistory = 893`

  - `NcrMicQCptnDumbCounter = 894`

  - `NcrPlayerHasMultipass = 895`

  - `NcrSmitVsVestinResult = 896`

  - `NRJukeboxSeen = 897`

  - `VCTrainigAccess = 898`

  - `NcrLennyFight = 899`

  - `NcrRatchPlayerPoints = 900`

  - `NRJesusTrain = 901`

  - `PurgSuppluysTaken = 902`

  - `NcrWestinPillsStatus = 903`

  - `NcrWestinPlayerGetPrepayment = 904`

  - `SFHubJudgementIgnatStory = 905`

  - `ReddMinesPlayerThief = 906`

  - `ReddDocMedicals = 907`

  - `NcrWestinPills = 908`

  - `SFHubbStatus = 909`

  - `SFInvasionSandbagsTaken = 910`

  - `SFInvasionSandbagsGiven = 911`

  - `SFImperatorCancelNum = 912`

  - `VCShiComputerAccess = 913`

  - `TribManotaStory = 914`

  - `VCKnowsAboutDelivery = 915`

  - `VCCitizenship = 916`

  - `VCHartmanFightStatus = 917`

  - `VCFreshBloodCounter = 918`

  - `VCForgeryWitnessInhome = 919`

  - `VCLynetOrMaclure = 920`

  - `VCMutCharleyHired = 921`

  - `VCCavesCounter = 922`

  - `VCPrisonerBulled = 923`

  - `VCLynettTalk = 924`

  - `VCPatrolCounter = 925`

  - `NpcDialogTimeWait = 926`

  - `KlamTrappersRadaway = 927`

  - `HoloInfo = 928`

  - `FavoriteItemPid = 929`

  - `IsNoFavoriteItem = 930`

  - `Level = 931`

  - `KarmaVoting = 932`

  - `IsNoPvp = 933`

  - `IsEndCombat = 934`

  - `IsDlgScriptBarter = 935`

  - `IsUnlimitedAmmo = 936`

  - `IsNoDrop = 937`

  - `IsNoLooseLimbs = 938`

  - `IsDeadAges = 939`

  - `IsNoHeal = 940`

  - `IsInvulnerable = 941`

  - `IsSpecialDead = 942`

  - `IsRangeHth = 943`

  - `IsNoKnock = 944`

  - `IsNoSupply = 945`

  - `IsNoKarmaOnKill = 946`

  - `IsBarterOnlyCash = 947`

  - `BarterCoefficient = 948`

  - `TransferType = 949`

  - `TransferContainerId = 950`

  - `IsNoBarter = 951`

  - `IsNoSteal = 952`

  - `IsNoLoot = 953`

  - `IsNoPush = 954`

  - `ItemsWeight = 955`

  - `ActionPoints = 956`

  - `CurrentAp = 957`

  - `BagId = 958`

  - `LastWeaponId = 959`

  - `LastWeaponNotFound = 960`

  - `HandsProtoItemId = 961`

  - `HandsItemMode = 962`

  - `LastWeaponUse = 963`

  - `IsNoItemGarbager = 964`

  - `TownSupplyVictimId = 965`

  - `TownSupplyHostileId = 966`

  - `TravellerRoute = 967`

  - `V13Dclaw = 968`

  - `VCAmandaHelpJoshua = 969`

  - `VCMailRemembered = 970`

  - `VCBeautyHoloRemembered = 971`

  - `VCityCommonBarkusTimeSay = 972`

  - `SquadMarchSquads = 973`

  - `SquadMarchQueue = 974`

  - `VCHartmanMarch = 975`

  - `VCHartmannClearCave = 976`

  - `VCDeadAllyCounter = 977`

  - `VCGuardRank = 978`

  - `VCReconCaveId = 979`

  - `VCGuardsmanTriggerPlayerId = 980`

  - `VCLynettArest = 981`

  - `VCLynettForgery = 982`

  - `VCLynettPrisonerId = 983`

  - `ReddingMortonBrothers = 984`

  - `SpecialEncounterBaxChurch = 985`

  - `SpecialEncounteTim = 986`

  - `RacingSneakersTrap = 987`

  - `SpecialEncounterBridge = 988`

  - `SpecialEncounterHoly1 = 989`

  - `SpecialEncounterHoly2 = 990`

  - `SpecialEncounterToxic = 991`

  - `SpecialEncounterPariah = 992`

  - `SpecialEncounterBrahmin = 993`

  - `SpecialEncounterWhale = 994`

  - `SpecialEncounterHead = 995`

  - `SpecialEncounterShuttle = 996`

  - `SpecialEncounterGuardian = 997`

  - `SpecialEncounterWoodsman = 998`

  - `SpecialEncounterUnwashed = 999`

  - `SpecialEncounterTeleport = 1000`

  - `SpecialWastelandChildren = 1001`

  - `SpecialEncounterKotw = 1002`

  - `SpecialSoldierHolo = 1003`

  - `SpecialTrapperHolo = 1004`

  - `SpecialDollHolo = 1005`

  - `SpecialEncounterZergLaboratory = 1006`

  - `SpecialEncounterDoughnutWarehouse = 1007`

  - `SpecialEncounterAtomChurch = 1008`

  - `GeckoFindWoody = 1009`

  - `NcrDappoLostCCtatus = 1010`

* `MapProperty`

  ...

  - `Invalid = 0xFFFF`

  - `CustomHolderId = 0`

  - `CustomHolderEntry = 1`

  - `InnerEntityIds = 2`

  - `InitScript = 3`

  - `LocId = 4`

  - `LocMapIndex = 5`

  - `CritterIds = 6`

  - `ItemIds = 7`

  - `Width = 8`

  - `Height = 9`

  - `LoopTime1 = 10`

  - `LoopTime2 = 11`

  - `LoopTime3 = 12`

  - `LoopTime4 = 13`

  - `LoopTime5 = 14`

  - `WorkHexX = 15`

  - `WorkHexY = 16`

  - `SpritesZoom = 17`

  - `CurDayTime = 18`

  - `DayTime = 19`

  - `DayColor = 20`

  - `KlamAldoId = 21`

  - `CasinoLimit = 22`

  - `CasinoTimeRenew = 23`

  - `CompRiddleData = 24`

  - `ElevatorData = 25`

  - `EnergyBarierHitBonus = 26`

  - `EnergyBarierTerminal = 27`

  - `EnergyBarierTerminalInfo = 28`

  - `FighterPatternEnemySpotted = 29`

  - `FighterPatternDeadAllies = 30`

  - `FixBoyWorkBenchTimeout = 31`

  - `FixBoyWorkBenchCharges = 32`

  - `HostileLQPlayerId = 33`

  - `HostileLQVarNum = 34`

  - `SFLabHonomerInside = 35`

  - `QIntroInitiated = 36`

  - `IntroDoorsOpen = 37`

  - `RainCapacity = 38`

  - `MapCoastRainUp = 39`

  - `GeckCityDoor = 40`

  - `GeckCityCharges = 41`

  - `GeckCityTimeBroken = 42`

  - `MapRadiationMinDose = 43`

  - `MapRadiationMaxDose = 44`

  - `NcrMichaelCritterId = 45`

  - `NcrSiegeComplexity = 46`

  - `IsNoPvPMap = 47`

  - `NpcRevengeData = 48`

  - `ResourcesData = 49`

  - `NoLogOut = 50`

  - `VCLastBarDialog = 51`

  - `WarehouseTurretActive = 52`

* `LocationProperty`

  ...

  - `Invalid = 0xFFFF`

  - `CustomHolderId = 0`

  - `CustomHolderEntry = 1`

  - `InnerEntityIds = 2`

  - `InitScript = 3`

  - `MapIds = 4`

  - `MapProtos = 5`

  - `MapEntrances = 6`

  - `EntranceScript = 7`

  - `WorldX = 8`

  - `WorldY = 9`

  - `Radius = 10`

  - `Hidden = 11`

  - `Color = 12`

  - `GECachesCacheChecked = 13`

  - `RacingCheckpointNumber = 14`

  - `StorehouseContId = 15`

  - `MaxPlayers = 16`

  - `AutoGarbage = 17`

  - `GeckVisible = 18`

  - `Automaps = 19`

  - `GeckCityMembers = 20`

  - `GeckCityLeader = 21`

  - `LocModVampireFarmQuesterId = 22`

  - `LocDefendersHostile = 23`

  - `NRWriGuardDead = 24`

  - `NRKidnapAllMarodeursDead = 25`

  - `LastLootTransfer = 26`

  - `SeAndroidPlayerIn = 27`

  - `SeAndroidPlayerId = 28`

  - `SeAndroidMinesTriggered = 29`

  - `SeAndroidTFounded = 30`

  - `SeAndroidLFounded = 31`

  - `SeAndroidDFounded = 32`

  - `SeAndroidRFounded = 33`

  - `SeAndroidPFounded = 34`

  - `SeAndroidCFounded = 35`

  - `SiloMissileLaunched = 36`

  - `IsEncounter = 37`
