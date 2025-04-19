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

  ...

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

  ...

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

* `bool ForceGNM = false`

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

* `const uint AnimWalkSpeed = 80`

  ...

* `const uint AnimRunSpeed = 160`

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

* `const string PlayerOffAppendix = _off`

  ...

* `bool ShowCritterName = true`

  ...

* `bool ShowCritterHeadText = true`

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

  ...

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

  ...

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

  ...

* `PrivateServer bool NCRRanchBrahminIll`

  ...

* `PrivateServer ident NcrDustyOneHourInvokeId`

  ...

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

  ...

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

  ...

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

  ...

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

* `OnPlayerCheckMove(Player player, Critter cr, uint& speed)`

  ...

* `OnPlayerCheckDir(Player player, Critter cr, int16& dirAngle)`

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

* `OnInMessage(string text, int& sayType, ident crId, uint& delay)`

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
  param message ...

* `void Log(string text)`

  ...  
  param text ...

* `void RequestQuit()`

  ...

* `bool IsResourcePresent(string resourcePath)`

  ...  
  param resourcePath ...  
  return ...

* `string ReadResource(string resourcePath)`

  ...  
  param resourcePath ...  
  return ...

* `int SystemCall(string command)`

  ...  
  param command ...  
  return ...

* `int SystemCall(string command, string& output)`

  ...  
  param command ...  
  param output ...  
  return ...

* `int Random(int minValue, int maxValue)`

  ...  
  param minValue ...  
  param maxValue ...  
  return ...

* `uint DecodeUtf8(string text, uint& length)`

  ...  
  param text ...  
  param length ...  
  return ...

* `string EncodeUtf8(uint ucs)`

  ...  
  param ucs ...  
  return ...

* `string Sha1(string text)`

  ...  
  param text ...  
  return ...

* `string Sha2(string text)`

  ...  
  param text ...  
  return ...

* `void OpenLink(string link)`

  ...  
  param link ...

* `uint64 GetUnixTime()`

  ...  
  return ...

* `uint GetDistance(uint16 hx1, uint16 hy1, uint16 hx2, uint16 hy2)`

  ...  
  param hx1 ...  
  param hy1 ...  
  param hx2 ...  
  param hy2 ...  
  return ...

* `uint8 GetDirection(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy)`

  ...  
  param fromHx ...  
  param fromHy ...  
  param toHx ...  
  param toHy ...  
  return ...

* `uint8 GetDirection(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy, float offset)`

  ...  
  param fromHx ...  
  param fromHy ...  
  param toHx ...  
  param toHy ...  
  param offset ...  
  return ...

* `int16 GetDirAngle(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy)`

  ...  
  param fromHx ...  
  param fromHy ...  
  param toHx ...  
  param toHy ...  
  return ...

* `int16 GetLineDirAngle(int fromX, int fromY, int toX, int toY)`

  ...  
  param fromX ...  
  param fromY ...  
  param toX ...  
  param toY ...  
  return ...

* `uint8 AngleToDir(int16 dirAngle)`

  ...  
  param dirAngle ...  
  return ...

* `int16 DirToAngle(uint8 dir)`

  ...  
  param dir ...  
  return ...

* `int16 RotateDirAngle(int16 dirAngle, bool clockwise, int16 step)`

  ...  
  param dirAngle ...  
  param clockwise ...  
  param step ...  
  return ...

* `void GetHexInterval(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy, int& ox, int& oy)`

  ...  
  param fromHx ...  
  param fromHy ...  
  param toHx ...  
  param toHy ...  
  param ox ...  
  param oy ...

* `string GetClipboardText()`

  ...  
  return ...

* `void SetClipboardText(string text)`

  ...  
  param text ...

* `string GetGameVersion()`

  ...  
  return ...

* `ProtoItem GetProtoItem(hstring pid)`

  ...  
  param pid ...  
  return ...

* `ProtoItem[] GetProtoItems()`

  ...  
  return ...

* `ProtoItem[] GetProtoItems(ItemComponent component)`

  ...  
  param component ...  
  return ...

* `ProtoItem[] GetProtoItems(ItemProperty property, int propertyValue)`

  ...  
  param property ...  
  param propertyValue ...  
  return ...

* `ProtoCritter GetProtoCritter(hstring pid)`

  ...  
  param pid ...  
  return ...

* `ProtoCritter[] GetProtoCritters()`

  ...  
  return ...

* `ProtoCritter[] GetProtoCritters(CritterComponent component)`

  ...  
  param component ...  
  return ...

* `ProtoCritter[] GetProtoCritters(CritterProperty property, int propertyValue)`

  ...  
  param property ...  
  param propertyValue ...  
  return ...

* `ProtoMap GetProtoMap(hstring pid)`

  ...  
  param pid ...  
  return ...

* `ProtoMap[] GetProtoMaps()`

  ...  
  return ...

* `ProtoMap[] GetProtoMaps(MapComponent component)`

  ...  
  param component ...  
  return ...

* `ProtoMap[] GetProtoMaps(MapProperty property, int propertyValue)`

  ...  
  param property ...  
  param propertyValue ...  
  return ...

* `ProtoLocation GetProtoLocation(hstring pid)`

  ...  
  param pid ...  
  return ...

* `ProtoLocation[] GetProtoLocations()`

  ...  
  return ...

* `ProtoLocation[] GetProtoLocations(LocationComponent component)`

  ...  
  param component ...  
  return ...

* `ProtoLocation[] GetProtoLocations(LocationProperty property, int propertyValue)`

  ...  
  param property ...  
  param propertyValue ...  
  return ...

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
  param cr1 ...  
  param cr2 ...  
  return ...

* `uint GetTick()`

  ...  
  return ...

* `Item GetItem(ident itemId)`

  ...  
  param itemId ...  
  return ...

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
  param item ...

* `void DestroyItem(Item item, uint count)`

  ...  
  param item ...  
  param count ...

* `void DestroyItem(ident itemId)`

  ...  
  param itemId ...

* `void DestroyItem(ident itemId, uint count)`

  ...  
  param itemId ...  
  param count ...

* `void DestroyItems(Item[] items)`

  ...  
  param items ...

* `void DestroyItems(ident[] itemIds)`

  ...  
  param itemIds ...

* `void DestroyCritter(Critter cr)`

  ...  
  param cr ...

* `void DestroyCritter(ident crId)`

  ...  
  param crId ...

* `void DestroyCritters(Critter[] critters)`

  ...  
  param critters ...

* `void DestroyCritters(ident[] critterIds)`

  ...  
  param critterIds ...

* `void RadioMessage(uint16 channel, string text)`

  ...  
  param channel ...  
  param text ...

* `void RadioMessageMsg(uint16 channel, TextPackName textPack, uint numStr)`

  ...  
  param channel ...  
  param textMsg ...  
  param numStr ...

* `void RadioMessageMsg(uint16 channel, TextPackName textPack, uint numStr, string lexems)`

  ...  
  param channel ...  
  param textMsg ...  
  param numStr ...  
  param lexems ...

* `tick_t GetFullSecond()`

  ...  
  return ...

* `tick_t EvaluateFullSecond(uint16 year, uint16 month, uint16 day, uint16 hour, uint16 minute, uint16 second)`

  ...  
  param year ...  
  param month ...  
  param day ...  
  param hour ...  
  param minute ...  
  param second ...  
  return ...

* `void EvaluateGameTime(tick_t serverTime, uint16& year, uint16& month, uint16& day, uint16& dayOfWeek, uint16& hour, uint16& minute, uint16& second)`

  ...  
  param fullSecond ...  
  param year ...  
  param month ...  
  param day ...  
  param dayOfWeek ...  
  param hour ...  
  param minute ...  
  param second ...

* `Location CreateLocation(hstring locPid, uint16 wx, uint16 wy)`

  ...  
  param locPid ...  
  param wx ...  
  param wy ...  
  return ...

* `Location CreateLocation(hstring locPid, uint16 wx, uint16 wy, Critter[] critters)`

  ...  
  param locPid ...  
  param wx ...  
  param wy ...  
  param critters ...  
  return ...

* `void DestroyLocation(Location loc)`

  ...  
  param loc ...

* `void DestroyLocation(ident locId)`

  ...  
  param locId ...

* `Critter GetCritter(ident crId)`

  ...  
  param crId ...  
  return ...

* `Player GetPlayer(string name) ExcludeInSingleplayer PassOwnership`

  ...  
  param name ...  
  return ...

* `Critter[] GetGlobalMapCritters(uint16 wx, uint16 wy, uint radius, CritterFindType findType)`

  ...  
  param wx ...  
  param wy ...  
  param radius ...  
  param findType ...  
  return ...

* `Map GetMap(ident mapId)`

  ...  
  param mapId ...  
  return ...

* `Map GetMap(hstring mapPid)`

  ...

* `Map GetMap(hstring mapPid, uint skipCount)`

  ...  
  param mapPid ...  
  param skipCount ...  
  return ...

* `Map[] GetMaps()`

  ...  
  return ...

* `Map[] GetMaps(hstring pid)`

  ...  
  param pid ...  
  return ...

* `Location GetLocation(ident locId)`

  ...  
  param locId ...  
  return ...

* `Location GetLocation(hstring locPid)`

  ...  
  param locPid ...  
  return ...

* `Location GetLocation(hstring locPid, uint skipCount)`

  ...  
  param locPid ...  
  param skipCount ...  
  return ...

* `Location[] GetLocations()`

  ...  
  return ...

* `Location[] GetLocations(hstring pid)`

  ...  
  param pid ...  
  return ...

* `Location[] GetLocations(uint16 wx, uint16 wy, uint radius)`

  ...  
  param wx ...  
  param wy ...  
  param radius ...  
  return ...

* `Location[] GetVisibleLocations(uint16 wx, uint16 wy, uint radius, Critter cr)`

  ...  
  param wx ...  
  param wy ...  
  param radius ...  
  param cr ...  
  return ...

* `Location[] GetZoneLocations(uint16 zx, uint16 zy, uint zoneRadius)`

  ...  
  param zx ...  
  param zy ...  
  param zoneRadius ...  
  return ...

* `bool RunDialog(Critter cr, Critter npc, bool ignoreDistance)`

  ...  
  param cr ...  
  param npc ...  
  param ignoreDistance ...  
  return ...

* `bool RunDialog(Critter cr, Critter npc, hstring dlgPack, bool ignoreDistance)`

  ...  
  param cr ...  
  param npc ...  
  param dlgPack ...  
  param ignoreDistance ...  
  return ...

* `bool RunDialog(Critter cr, hstring dlgPack, uint16 hx, uint16 hy, bool ignoreDistance)`

  ...  
  param cr ...  
  param dlgPack ...  
  param hx ...  
  param hy ...  
  param ignoreDistance ...  
  return ...

* `int64 GetWorldItemCount(hstring pid)`

  ...  
  param pid ...  
  return ...

* `void AddTextListener(int sayType, string firstStr, int parameter, ScriptFunc-void, Critter, string func)`

  ...  
  param sayType ...  
  param firstStr ...  
  param parameter ...  
  param func ...  
  return ...

* `void RemoveTextListener(int sayType, string firstStr, int parameter)`

  ...  
  param sayType ...  
  param firstStr ...  
  param parameter ...

* `Item[] GetAllItems(hstring pid)`

  ...  
  param pid ...  
  return ...

* `Player[] GetOnlinePlayers() ExcludeInSingleplayer`

  ...  
  return ...

* `ident[] GetRegisteredPlayerIds() ExcludeInSingleplayer`

  ...  
  return ...

* `Critter[] GetAllNpc()`

  ...  
  return ...

* `Critter[] GetAllNpc(hstring pid)`

  ...  
  param pid ...  
  return ...

* `void GetTime(uint16& year, uint16& month, uint16& day, uint16& dayOfWeek, uint16& hour, uint16& minute, uint16& second, uint16& milliseconds)`

  ...  
  param year ...  
  param month ...  
  param day ...  
  param dayOfWeek ...  
  param hour ...  
  param minute ...  
  param second ...  
  param milliseconds ...

* `void SetTime(uint16 multiplier, uint16 year, uint16 month, uint16 day, uint16 hour, uint16 minute, uint16 second)`

  ...  
  param multiplier ...  
  param year ...  
  param month ...  
  param day ...  
  param hour ...  
  param minute ...  
  param second ...

* `bool CallStaticItemFunction(Critter cr, StaticItem staticItem, Item usedItem, any param)`

  ...  
  param cr ...  
  param staticItem ...  
  param usedItem ...  
  param param ...  
  return ...

* `hstring[] GetDialogs()`

  ...  
  return ...

* `StaticItem[] GetStaticItemsForProtoMap(ProtoMap proto)`

  ...  
  param proto ...  
  return ...

* `void LoadImage(int imageSlot, string imageName)`

  ...

* `uint GetImageColor(int imageSlot, int x, int y)`

  ...

### Game client methods

* `bool IsFullscreen()`

  ...  
  return ...

* `void ToggleFullscreen()`

  ...

* `void MinimizeWindow()`

  ...

* `bool IsConnecting()`

  ...  
  return ...

* `bool IsConnected()`

  ...  
  return ...

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
  param cr1 ...  
  param cr2 ...  
  return ...

* `uint GetTick()`

  ...  
  return ...

* `string CustomCall(string command)`

  ...  
  param command ...  
  param separator ...  
  return ...

* `string CustomCall(string command, string separator)`

  ...  
  param command ...  
  param separator ...  
  return ...

* `Critter GetChosen()`

  ...  
  return ...

* `Item GetItem(ident itemId) ExcludeInSingleplayer`

  ...  
  param itemId ...  
  return ...

* `Critter GetCritter(ident crId) ExcludeInSingleplayer`

  ...  
  param crId ...  
  return ...

* `Critter[] GetCritters(CritterFindType findType) ExcludeInSingleplayer`

  ...  
  param findType ...  
  return ...

* `Critter[] GetCritters(hstring pid, CritterFindType findType) ExcludeInSingleplayer`

  ...  
  param pid ...  
  param findType ...  
  return ...

* `void FlushScreen(ucolor fromColor, ucolor toColor, tick_t duration)`

  ...  
  param fromColor ...  
  param toColor ...  
  param duration ...

* `void QuakeScreen(int noise, tick_t duration)`

  ...  
  param noise ...  
  param ms ...

* `bool PlaySound(string soundName)`

  ...  
  param soundName ...  
  return ...

* `bool PlayMusic(string musicName, tick_t repeatTime)`

  ...  
  param musicName ...  
  param repeatTime ...  
  return ...

* `void PlayVideo(string videoName, bool canInterrupt, bool enqueue)`

  ...  
  param videoName ...  
  param canInterrupt ...  
  param enqueue

* `bool IsVideoPlaying()`

  ...  
  return ...

* `VideoPlayback CreateVideoPlayback(string videoName, bool looped) PassOwnership`

  ...  
  param videoName ...  
  param looped ...  
  return ...

* `void DrawVideoPlayback(VideoPlayback video, int x, int y, int width, int height)`

  ...  
  param video ...  
  param x ...  
  param y ...  
  param width ...  
  param height ...

* `void ConsoleMessage(string msg)`

  ...  
  param msg ...

* `void Message(string msg)`

  ...  
  param msg ...

* `void Message(int type, string msg)`

  ...  
  param type ...  
  param msg ...

* `void Message(TextPackName textPack, uint strNum)`

  ...  
  param textPack ...  
  param strNum ...

* `void Message(int type, TextPackName textPack, uint strNum)`

  ...  
  param type ...  
  param textPack ...  
  param strNum ...

* `string GetText(TextPackName textPack, uint strNum)`

  ...  
  param textPack ...  
  param strNum ...  
  return ...

* `string GetText(TextPackName textPack, uint strNum, uint skipCount)`

  ...  
  param textPack ...  
  param strNum ...  
  param skipCount ...  
  return ...

* `uint GetTextNumUpper(TextPackName textPack, uint strNum)`

  ...  
  param textPack ...  
  param strNum ...  
  return ...

* `uint GetTextNumLower(TextPackName textPack, uint strNum)`

  ...  
  param textPack ...  
  param strNum ...  
  return ...

* `uint GetTextCount(TextPackName textPack, uint strNum)`

  ...  
  param textPack ...  
  param strNum ...  
  return ...

* `bool IsTextPresent(TextPackName textPack, uint strNum)`

  ...  
  param textPack ...  
  param strNum ...  
  return ...

* `string ReplaceText(string text, string replace, ObjInfo-1 obj1)`

  ...  
  param text ...  
  param replace ...  
  param str ...  
  return ...

* `string FormatTags(string text, string lexems)`

  ...  
  param text ...  
  param lexems ...  
  return ...

* `int GetFog(uint16 zoneX, uint16 zoneY) ExcludeInSingleplayer`

  ...  
  param zoneX ...  
  param zoneY ...  
  return ...

* `tick_t GetFullSecond() ExcludeInSingleplayer`

  ...  
  return ...

* `tick_t EvaluateFullSecond(uint16 year, uint16 month, uint16 day, uint16 hour, uint16 minute, uint16 second) ExcludeInSingleplayer`

  ...  
  param year ...  
  param month ...  
  param day ...  
  param hour ...  
  param minute ...  
  param second ...  
  return ...

* `void EvaluateGameTime(tick_t serverTime, uint16& year, uint16& month, uint16& day, uint16& dayOfWeek, uint16& hour, uint16& minute, uint16& second) ExcludeInSingleplayer`

  ...  
  param fullSecond ...  
  param year ...  
  param month ...  
  param day ...  
  param dayOfWeek ...  
  param hour ...  
  param minute ...  
  param second ...

* `void Preload3dFiles(string[] fnames)`

  ...  
  param fnames ...

* `void LoadFont(int fontIndex, string fontFname)`

  ...  
  param fontIndex ...  
  param fontFname ...  
  return ...

* `void SetDefaultFont(int font)`

  ...  
  param font ...

* `void SetEffect(EffectType effectType, int64 effectSubtype, string effectPath)`

  ...  
  param effectType ...  
  param effectSubtype ...  
  param effectPath ...  
  return ...

* `void SimulateMouseClick(int x, int y, MouseButton button)`

  ...  
  param x ...  
  param y ...  
  param button ...

* `void SimulateKeyboardPress(KeyCode key1, KeyCode key2, string key1Text, string key2Text)`

  ...  
  param key1 ...  
  param key2 ...  
  param key1Text ...  
  param key2Text ...

* `void GetTime(uint16& year, uint16& month, uint16& day, uint16& dayOfWeek, uint16& hour, uint16& minute, uint16& second, uint16& milliseconds) ExcludeInSingleplayer`

  ...  
  param year ...  
  param month ...  
  param day ...  
  param dayOfWeek ...  
  param hour ...  
  param minute ...  
  param second ...  
  param milliseconds ...

* `uint LoadSprite(string sprName)`

  ...  
  param sprName ...  
  return ...

* `uint LoadSprite(hstring nameHash)`

  ...  
  param nameHash ...  
  return ...

* `uint LoadMapSprite(string sprName)`

  ...  
  param sprName ...  
  return ...

* `uint LoadMapSprite(hstring nameHash)`

  ...  
  param nameHash ...  
  return ...

* `void FreeSprite(uint sprId)`

  ...  
  param sprId ...

* `int GetSpriteWidth(uint sprId)`

  ...  
  param sprId ...  
  return ...

* `int GetSpriteHeight(uint sprId)`

  ...  
  param sprId ...  
  return ...

* `bool IsSpriteHit(uint sprId, int x, int y)`

  ...  
  param sprId ...  
  param x ...  
  param y ...  
  return ...

* `void StopSprite(uint sprId)`

  ...

* `void SetSpriteTime(uint sprId, float normalizedTime)`

  ...

* `void PlaySprite(uint sprId, hstring animName, bool looped, bool reversed)`

  ...

* `void GetTextInfo(string text, int w, int h, int font, int flags, int& tw, int& th, int& lines)`

  ...  
  param text ...  
  param w ...  
  param h ...  
  param font ...  
  param flags ...  
  param tw ...  
  param th ...  
  param lines ...

* `int GetTextLines(int w, int h, int font)`

  ...

* `void DrawSprite(uint sprId, int x, int y)`

  ...  
  param sprId ...  
  param x ...  
  param y ...

* `void DrawSprite(uint sprId, int x, int y, ucolor color)`

  ...  
  param sprId ...  
  param x ...  
  param y ...  
  param color ...

* `void DrawSprite(uint sprId, int x, int y, ucolor color, bool offs)`

  ...  
  param sprId ...  
  param x ...  
  param y ...  
  param color ...  
  param offs ...

* `void DrawSprite(uint sprId, int x, int y, int w, int h)`

  ...  
  param sprId ...  
  param x ...  
  param y ...  
  param w ...  
  param h ...

* `void DrawSprite(uint sprId, int x, int y, int w, int h, ucolor color)`

  ...  
  param sprId ...  
  param x ...  
  param y ...  
  param w ...  
  param h ...  
  param color ...

* `void DrawSprite(uint sprId, int x, int y, int w, int h, ucolor color, bool zoom, bool offs)`

  ...  
  param sprId ...  
  param x ...  
  param y ...  
  param w ...  
  param h ...  
  param color ...  
  param zoom ...  
  param offs ...

* `void DrawSpritePattern(uint sprId, int x, int y, int w, int h, int sprWidth, int sprHeight, ucolor color)`

  ...  
  param sprId ...  
  param x ...  
  param y ...  
  param w ...  
  param h ...  
  param sprWidth ...  
  param sprHeight ...  
  param color ...

* `void DrawText(string text, int x, int y, int w, int h, ucolor color, int font, int flags)`

  ...  
  param text ...  
  param x ...  
  param y ...  
  param w ...  
  param h ...  
  param color ...  
  param font ...  
  param flags ...

* `void DrawPrimitive(int primitiveType, int[] data)`

  ...  
  param primitiveType ...  
  param data ...

* `void DrawCritter2d(hstring modelName, CritterStateAnim stateAnim, CritterActionAnim actionAnim, uint8 dir, int l, int t, int r, int b, bool scratch, bool center, ucolor color)`

  ...  
  param modelName ...  
  param stateAnim ...  
  param actionAnim ...  
  param dir ...  
  param l ...  
  param t ...  
  param r ...  
  param b ...  
  param scratch ...  
  param center ...  
  param color ...

* `void DrawCritter3d(uint instance, hstring modelName, CritterStateAnim stateAnim, CritterActionAnim actionAnim, int[] layers, float[] position, ucolor color)`

  ...  
  param instance ...  
  param modelName ...  
  param stateAnim ...  
  param actionAnim ...  
  param layers ...  
  param position ...  
  param color ...

* `void PushDrawScissor(int x, int y, int w, int h)`

  ...  
  param x ...  
  param y ...  
  param w ...  
  param h ...

* `void PopDrawScissor()`

  ...

* `void ActivateOffscreenSurface(bool forceClear)`

  ...  
  param forceClear ...

* `void PresentOffscreenSurface(int effectSubtype)`

  ...  
  param effectSubtype ...

* `void PresentOffscreenSurface(int effectSubtype, int x, int y, int w, int h)`

  ...  
  param effectSubtype ...  
  param x ...  
  param y ...  
  param w ...  
  param h ...

* `void PresentOffscreenSurface(int effectSubtype, int fromX, int fromY, int fromW, int fromH, int toX, int toY, int toW, int toH)`

  ...  
  param effectSubtype ...  
  param fromX ...  
  param fromY ...  
  param fromW ...  
  param fromH ...  
  param toX ...  
  param toY ...  
  param toW ...  
  param toH ...

* `void ShowScreen(int screen)`

  ...  
  param screen ...  
  param data ...

* `void ShowScreen(int screen, string=>any data)`

  ...  
  param screen ...  
  param data ...

* `void HideScreen()`

  ...

* `void HideScreen(int screen)`

  ...  
  param screen ...

* `void SaveScreenshot(string filePath)`

  ...  
  param filePath ...

* `void SaveText(string filePath, string text)`

  ...  
  param filePath ...  
  param text ...  
  return ...

* `void SetCacheData(string name, uint8[] data)`

  ...  
  param name ...  
  param data ...

* `void SetCacheData(string name, uint8[] data, uint dataSize)`

  ...  
  param name ...  
  param data ...  
  param dataSize ...

* `uint8[] GetCacheData(string name)`

  ...  
  param name ...  
  return ...

* `void SetCacheText(string name, string str)`

  ...  
  param name ...  
  param str ...

* `string GetCacheText(string name)`

  ...  
  param name ...  
  return ...

* `bool IsCacheEntry(string name)`

  ...  
  param name ...  
  return ...

* `void RemoveCacheEntry(string name)`

  ...  
  param name ...

* `void SetUserConfig(string=>string keyValues)`

  ...  
  param keyValues ...

* `void SetUserConfig(string[] keyValues)`

  ...  
  param keyValues ...

* `void SetMousePos(int x, int y)`

  ...  
  param x ...  
  param y ...

* `void MoveItemLocally(uint itemCount, ident itemId, ident swapItemId, CritterItemSlot toSlot)`

  ...  
  param itemCount ...  
  param itemId ...  
  param swapItemId ...  
  param toSlot ...  
  return ...

* `void ChangeLanguage(string langName)`

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
  param pid ...  
  param hx ...  
  param hy ...  
  return ...

* `Critter AddCritter(hstring pid, uint16 hx, uint16 hy)`

  ...  
  param pid ...  
  param hx ...  
  param hy ...  
  return ...

* `Item GetItem(uint16 hx, uint16 hy)`

  ...  
  param hx ...  
  param hy ...  
  return ...

* `Item[] GetItems(uint16 hx, uint16 hy)`

  ...  
  param hx ...  
  param hy ...  
  return ...

* `Critter GetCritter(uint16 hx, uint16 hy, CritterFindType findType)`

  ...  
  param hx ...  
  param hy ...  
  param findType ...  
  return ...

* `Critter[] GetCritters(uint16 hx, uint16 hy, CritterFindType findType)`

  ...  
  param hx ...  
  param hy ...  
  param findType ...  
  return ...

* `void MoveEntity(Entity entity, uint16 hx, uint16 hy)`

  ...  
  param entity ...  
  param hx ...  
  param hy ...

* `void DeleteEntity(Entity entity)`

  ...  
  param entity ...

* `void DeleteEntities(Entity[] entities)`

  ...  
  param entities ...

* `void SelectEntity(Entity entity, bool set)`

  ...  
  param entity ...  
  param set ...

* `void SelectEntities(Entity[] entities, bool set)`

  ...  
  param entities ...  
  param set ...

* `Entity GetSelectedEntity()`

  ...  
  return ...

* `Entity[] GetSelectedEntities()`

  ...  
  return ...

* `Item AddTile(hstring pid, uint16 hx, uint16 hy, int layer, bool roof)`

  ...  
  param hx ...  
  param hy ...  
  param ox ...  
  param oy ...  
  param layer ...  
  param roof ...  
  param picHash ...

* `Map LoadMap(string fileName)`

  ...  
  param fileName ...  
  return ...

* `void UnloadMap(Map map)`

  ...  
  param map ...

* `void SaveMap(Map map, string customName)`

  ...  
  param map ...  
  param customName ...

* `void ShowMap(Map map)`

  ...  
  param map ...

* `Map[] GetLoadedMaps(int& index)`

  ...  
  param index ...  
  return ...

* `string[] GetMapFileNames(string dir)`

  ...  
  param dir ...  
  return ...

* `void ResizeMap(uint16 width, uint16 height)`

  ...  
  param width ...  
  param height ...

* `hstring[] TabGetItemPids(int tab, string subTab)`

  ...  
  param tab ...  
  param subTab ...  
  return ...

* `hstring[] TabGetCritterPids(int tab, string subTab)`

  ...  
  param tab ...  
  param subTab ...  
  return ...

* `void TabSetItemPids(int tab, string subTab, hstring[] itemPids)`

  ...  
  param tab ...  
  param subTab ...  
  param itemPids ...

* `void TabSetCritterPids(int tab, string subTab, hstring[] critterPids)`

  ...  
  param tab ...  
  param subTab ...  
  param critterPids ...

* `void TabDelete(int tab)`

  ...  
  param tab ...

* `void TabSelect(int tab, string subTab, bool show)`

  ...  
  param tab ...  
  param subTab ...  
  param show ...

* `void TabSetName(int tab, string tabName)`

  ...  
  param tab ...  
  param tabName ...

* `string GetIfaceIniStr(string key)`

  ...  
  param key ...  
  return ...

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

  ...

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
  return ...

* `int GetAccess()`

  ...  
  return ...

* `bool SetAccess(int access)`

  ...  
  param access ...  
  return ...

* `void Message(string text)`

  ...  
  param text ...

* `void Message(TextPackName textPack, uint numStr)`

  ...  
  param textMsg ...  
  param numStr ...

* `void Message(TextPackName textPack, uint numStr, string lexems)`

  ...  
  param textMsg ...  
  param numStr ...  
  param lexems ...

* `bool IsWebConnected()`

  ...  
  return ...

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

  ...

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

  ...

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

  ...

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

  ...

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

  ...

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

  ...

* `PrivateServer hstring PosterEWWall`

  ...

* `PrivateServer ident RatGrenadeInvokeId`

  ...

* `PrivateServer any[] ReddGatesGoodList`

  ...

* `PrivateServer any[] ReddGatesBadList`

  ...

* `PrivateServer uint8 RespawnItemMode`

  ...

* `PrivateServer uint RespawnItemRespTime`

  ...

* `PrivateServer uint RespawnItemVarNum`

  ...

* `PrivateServer bool SeAndroidRadioListened`

  ...

* `PrivateServer LocationProperty SeAndroidVarNum`

  ...

* `PrivateServer ident SmokeGrenadeOwnerId`

  ...

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

  ...

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

  ...

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

  ...

* `Public Caliber Weapon_Caliber Group = WeaponAmmo`

  ...

* `Public hstring Weapon_DefaultAmmoPid Group = WeaponAmmo`

  ...

* `Public CritterStateAnim Weapon_StateAnim Group = WeaponProperties`

  ...

* `Public int Weapon_MinStrength Group = WeaponProperties`

  ...

* `Public ItemPerks Weapon_Perk Group = WeaponProperties`

  ...

* `Public bool Weapon_IsTwoHanded Group = WeaponProperties`

  ...

* `Public uint Weapon_ActiveUses Group = WeaponProperties`

  ...

* `Public CritterProperty Weapon_Skill_0 Group = WeaponModes`

  ...

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

  ...

* `Public int Weapon_UnarmedCriticalBonus Group = WeaponProperties`

  ...

* `Public uint Weapon_CriticalFailture Group = WeaponProperties`

  ...

* `Public bool Weapon_UnarmedArmorPiercing Group = WeaponProperties`

  ...

* `Public Caliber Ammo_Caliber Group = Ammo`

  ...

* `Public int Ammo_AcMod Group = Ammo`

  ...

* `Public int Ammo_DrMod Group = Ammo`

  ...

* `Public uint Ammo_DmgMult Group = Ammo`

  ...

* `Public uint Ammo_DmgDiv Group = Ammo`

  ...

* `Public uint Car_Speed Group = Car`

  ...

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

  ...

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

  ...

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

  ...

* `Public bool IsWallTransEnd`

  ...

* `Public bool IsHasTimer`

  ...

* `Public bool IsBigGun`

  ...

* `Public bool IsMultiHex`

  ...

* `Public hstring ChildPid_0`

  ...

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
  param initFunc ...

* `void SetupScriptEx(hstring initFunc)`

  ...  
  param initFunc ...

* `Item AddItem(hstring pid, uint count, ContainerItemStack stackId)`

  ...  
  param pid ...  
  param count ...  
  param stackId ...  
  return ...

* `Item[] GetItems(ContainerItemStack stackId)`

  ...  
  param stackId ...  
  return ...

* `Map GetMap()`

  ...

* `Map GetMapPosition(uint16& hx, uint16& hy)`

  ...  
  param hx ...  
  param hy ...  
  return ...

* `void Animate(hstring animName, bool looped, bool reversed) ExcludeInSingleplayer`

  ...  
  param animName ...  
  param looped ...  
  param reversed ...

### Item client methods

* `Item Clone()`

  ...  
  return ...

* `Item Clone(uint count)`

  ...  
  param count ...  
  return ...

* `void GetMapPos(uint16& hx, uint16& hy) ExcludeInSingleplayer`

  ...  
  param hx ...  
  param hy ...

* `void Animate(hstring animName, bool looped, bool reversed)`

  ...  
  param animName ...  
  param looped ...  
  param reversed ...

* `void PlayAnim(hstring animName, bool looped, bool reversed)`

  ...

* `void StopAnim()`

  ...

* `void SetAnimTime(float normalizedTime)`

  ...

* `Item[] GetInnerItems() ExcludeInSingleplayer`

  ...  
  return ...

* `uint8 GetAlpha()`

  ...  
  return ...

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

* `PrivateServer uint MovingSpeed ReadOnly Temporary`

  ...

* `PrivateClient bool SexTagFemale`

  ...

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

* `PrivateClient uint AttackDistanceHint`

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

  ...

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

  ...

* `PrivateServer uint8 BHUranDiscount Max = 1`

  ...

* `PrivateServer int BBMsgPage`

  ...

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

  ...

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

  ...

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

  ...

* `PrivateServer uint8 QDappoLostRobotHexNum`

  ...

* `PrivateServer uint BankMoney Max = 999999`

  ...

* `PrivateServer uint8 DenHubBank5`

  ...

* `PrivateServer uint8 DenHubGuard5`

  ...

* `PrivateServer ident DenPoormanItemId`

  ...

* `PrivateServer uint8 DenVirginCount`

  ...

* `PrivateServer bool DenVirginIsHome`

  ...

* `PrivateServer ident=>uint UniqTimeout`

  ...

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

  ...

* `Protected uint8 DoughnutsCounter Max = 20`

  ...

* `PrivateServer ident LastElectronicLocked`

  ...

* `PrivateServer uint EliTimeNextSing`

  ...

* `PrivateServer ident[] EnemyStack`

  ...

* `Public bool IsNoEnemyStack`

  ...

* `PrivateServer uint16 EnergyBarierTerminalHx`

  ...

* `PrivateServer uint16 EnergyBarierTerminalHy`

  ...

* `PrivateServer uint EnergyBarierNetNum`

  ...

* `PrivateServer int EnergyBarierHackBonus`

  ...

* `PrivateServer int EnergyBarierHitBonus`

  ...

* `PrivateServer uint FighterPatternCanGenStim`

  ...

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

  ...

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

  ...

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

  ...

* `PrivateServer uint=>uint8[] HostileLQData`

  ...

* `Protected uint8 SFAhs7Escort Group = Quests Quest = 4434 Max = 3`

  ...

* `PrivateServer ident SFHonomerPlayerId`

  ...

* `PrivateServer ident SFEscortLocation`

  ...

* `PrivateServer uint8 SFLabFailed Max = 1`

  ...

* `PrivateServer bool QHubLabIsDialogRun`

  ...

* `Protected uint8 BarterLourensRats1 Group = Quests Quest = 5200 Max = 4`

  ...

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

  ...

* `Protected int8 V13DclawEggs Group = Quests Quest = 4902 Min = 0 Max = 7`

  ...

* `Protected uint8 KlamTorrCowboy Group = Quests Quest = 3213 Max = 9`

  ...

* `PrivateServer uint8 KlamCowboyCountGav`

  ...

* `PrivateServer uint16 KlamCowboyMobHx`

  ...

* `PrivateServer uint16 KlamCowboyMobHy`

  ...

* `Protected uint8 KlamDantonBramin Group = Quests Quest = 3211 Max = 8`

  ...

* `Protected uint8 KlamJosallDanton Group = Quests Quest = 3215 Max = 3`

  ...

* `Protected uint KlamKuklachev Group = Quests Quest = 145 Max = 3`

  ...

* `Protected uint8 KlamSmilyGecko Group = Quests Quest = 3210 Max = 6`

  ...

* `PrivateServer int KlamSmilyCurrentHp`

  ...

* `PrivateServer int KlamSmilyCountKills`

  ...

* `PrivateServer int KlamSmilyHealing`

  ...

* `PrivateServer uint8[] LimitedBarterData`

  ...

* `PrivateServer bool IsGeck`

  ...

* `PrivateServer ident=>uint StealExpCount`

  ...

* `PrivateServer ident=>uint FirstAidCount`

  ...

* `Protected uint8 MainQuest Group = Quests Quest = 5001 Max = 21`

  ...

* `PrivateServer ident GCityCitizen`

  ...

* `PrivateServer uint MapGeckCityTraderSkillBarter`

  ...

* `PrivateServer uint MapKlamathRobotTimeNextSay`

  ...

* `Protected uint8 ModJoeGiantWasp Group = Quests Quest = 3307 Max = 3`

  ...

* `Protected uint8 TribSulikRaid Group = Quests Quest = 4606 Max = 10`

  ...

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

  ...

* `PrivateServer uint8[] MonologueData`

  ...

* `Protected uint8 NavHenryEmpTest Group = Quests Quest = 4507 Max = 7`

  ...

* `PrivateServer ident=>bool NavEmpTestedCritter`

  ...

* `PrivateServer uint NavarroTimeOutScan`

  ...

* `PrivateServer ident NavarroChipUsedId`

  ...

* `PrivateServer uint8 NcrAlexHoloFindStatus Max = 2`

  ...

* `Protected uint8 NCRFelixFindBrahmin Group = Quests Quest = 4276 Max = 3`

  ...

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

  ...

* `PrivateServer ident NcrSonCatcherId`

  ...

* `PrivateServer uint8 NcrSonMovesCounter Max = 9`

  ...

* `PrivateServer uint NcrMichealMessageNum`

  ...

* `Protected uint8 MailDelivery Group = Quests Quest = 4248 Max = 3`

  ...

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

  ...

* `PrivateServer uint NcrSmitStringNum`

  ...

* `PrivateServer uint NcrSmitGateStringNum`

  ...

* `PrivateServer ident NcrSmitPlayerId`

  ...

* `PrivateServer uint NcrSmitIdleCount`

  ...

* `PrivateServer hstring NcrWestinMapPidTo`

  ...

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

  ...

* `PrivateServer uint NpcRevengeNpcHxHy`

  ...

* `PrivateServer uint NpcRevengeCountWait`

  ...

* `Protected uint8 NRWriKidnap Group = Quests Quest = 3707 Max = 12`

  ...

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

  ...

* `PrivateServer ident RatGrenadeOwnerId`

  ...

* `PrivateServer uint8 ReddMineNuggets Max = 20`

  ...

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

  ...

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

  ...

* `PrivateServer uint HellVisits`

  ...

* `PrivateServer bool ReplBankIsCanEnter`

  ...

* `PrivateServer bool ReplBankeIsAttackGagPlayer`

  ...

* `PrivateServer uint8 ReplHellTurretHack Max = 100`

  ...

* `PrivateServer ident TerminalPlayerId`

  ...

* `PrivateServer uint TerminalDialogId`

  ...

* `Protected uint8 ModFarrelAmmiak Group = Quests Quest = 3316 Max = 2`

  ...

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

  ...

* `PrivateServer uint=>int Scores`

  ...

* `PrivateServer bool SEAndroidMonologEnd`

  ...

* `PrivateServer uint SETalkingHeadStringNum`

  ...

* `PrivateServer ident SETeleportEatId`

  ...

* `Protected uint8 SFAhs7HubJudgement Group = Quests Quest = 4430 Max = 8`

  ...

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

  ...

* `Protected uint8 BHRocketBase Group = Quests Quest = 3610 Max = 5`

  ...

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

  ...

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

  ...

* `Protected uint SpecialSkillLootCritter Group = SpecialSkills`

  ...

* `Protected ident FollowLeaderId`

  ...

* `PrivateServer ident LastSendEntrancesLocId`

  ...

* `PrivateServer tick_t LastSendEntrancesTick`

  ...

* `Protected uint CrTypeAliasBase`

  ...

* `VirtualProtected uint CrTypeAlias`

  ...

* `Public hstring ModelNameBase`

  ...

* `Protected bool IsNoArmor`

  ...

* `PrivateCommon bool[] Anims ReadOnly`

  ...

* `Protected bool IsNoAim`

  ...

* `Protected uint[] Kills`

  ...

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

  ...

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

  ...

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

  ...

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

  ...

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

  ...

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

  ...

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

  ...

* `Protected CritterProperty TagSkill1`

  ...

* `Protected CritterProperty TagSkill2`

  ...

* `Protected CritterProperty TagSkill3`

  ...

* `Protected uint8 PerkBookworm Group = Perks`

  ...

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

  ...

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

  ...

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

  ...

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

  ...

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

  ...

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

  ...

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

  ...

* `PrivateServer ident TownSupplyHostileId`

  ...

* `PrivateServer uint8[] TravellerRoute`

  ...

* `Protected uint8 V13Dclaw Group = Quests Quest = 4900 Max = 5`

  ...

* `Protected uint8 VCAmandaHelpJoshua Group = Quests Quest = 8836 Max = 9`

  ...

* `PrivateServer uint8 VCMailRemembered Max = 1`

  ...

* `PrivateServer uint8 VCBeautyHoloRemembered Max = 1`

  ...

* `PrivateServer uint VCityCommonBarkusTimeSay`

  ...

* `PrivateServer ident[] SquadMarchSquads`

  ...

* `PrivateServer uint8[] SquadMarchQueue`

  ...

* `Protected uint8 VCHartmanMarch Group = Quests Quest = 8823 Max = 4`

  ...

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

  ...

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
  param initFunc ...

* `void SetupScriptEx(hstring initFunc)`

  ...  
  param initFunc ...

* `bool IsMoving()`

  ...  
  return ...

* `Player GetPlayer() ExcludeInSingleplayer`

  ...  
  return ...

* `Map GetMap()`

  ...  
  return ...

* `void TransitToHex(uint16 hx, uint16 hy, uint8 dir)`

  ...  
  param hx ...  
  param hy ...  
  param dir ...

* `void TransitToMap(Map map, uint16 hx, uint16 hy, uint8 dir)`

  ...  
  param map ...  
  param hx ...  
  param hy ...  
  param dir ...

* `void TransitToMap(Map map, uint16 hx, uint16 hy, uint8 dir, bool force_hex)`

  ...

* `void TransitToGlobal()`

  ...

* `void TransitToGlobalWithGroup(Critter[] group)`

  ...  
  param group ...

* `void TransitToGlobalGroup(Critter globalCr)`

  ...  
  param globalCr ...

* `bool IsAlive()`

  ...  
  return ...

* `bool IsKnockout()`

  ...  
  return ...

* `bool IsDead()`

  ...  
  return ...

* `void RefreshView()`

  ...

* `void ViewMap(Map map, uint look, uint16 hx, uint16 hy, uint8 dir)`

  ...  
  param map ...  
  param look ...  
  param hx ...  
  param hy ...  
  param dir ...

* `void Say(uint8 howSay, string text)`

  ...  
  param howSay ...  
  param text ...

* `void SayMsg(uint8 howSay, TextPackName textPack, uint numStr)`

  ...  
  param howSay ...  
  param textMsg ...  
  param numStr ...

* `void SayMsg(uint8 howSay, TextPackName textPack, uint numStr, string lexems)`

  ...  
  param howSay ...  
  param textMsg ...  
  param numStr ...  
  param lexems ...

* `void SetDir(uint8 dir)`

  ...  
  param dir ...

* `void SetDirAngle(int16 dir_angle)`

  ...  
  param dir_angle ...

* `Critter[] GetCritters(bool lookOnMe, CritterFindType findType)`

  ...  
  param lookOnMe ...  
  param findType ...  
  return ...

* `Critter[] GetTalkingCritters()`

  ...  
  return ...

* `uint GetTalkingCrittersCount()`

  ...

* `Critter[] GetGlobalMapGroupCritters()`

  ...

* `bool IsSee(Critter cr)`

  ...  
  param cr ...  
  return ...

* `bool IsSeenBy(Critter cr)`

  ...  
  param cr ...  
  return ...

* `bool IsSee(Item item)`

  ...  
  param item ...  
  return ...

* `uint CountItem(hstring protoId)`

  ...  
  param protoId ...  
  return ...

* `void DestroyItem(hstring pid)`

  ...  
  param pid ...

* `void DestroyItem(hstring pid, uint count)`

  ...  
  param pid ...  
  param count ...

* `Item AddItem(hstring pid, uint count)`

  ...  
  param pid ...  
  param count ...  
  return ...

* `Item GetItem(ident itemId)`

  ...  
  param itemId ...  
  return ...

* `Item GetItem(hstring protoId)`

  ...  
  param protoId ...  
  return ...

* `Item GetItem(ItemComponent component)`

  ...  
  param component ...  
  return ...

* `Item GetItem(ItemProperty property, int propertyValue)`

  ...  
  param property ...  
  param propertyValue ...  
  return ...

* `Item[] GetItems()`

  ...  
  return ...

* `Item[] GetItems(ItemComponent component)`

  ...  
  param component ...  
  return ...

* `Item[] GetItems(ItemProperty property, int propertyValue)`

  ...  
  param property ...  
  param propertyValue ...  
  return ...

* `Item[] GetItems(hstring protoId)`

  ...  
  param protoId ...  
  return ...

* `void ChangeItemSlot(ident itemId, CritterItemSlot slot)`

  ...  
  param itemId ...  
  param slot ...

* `void SetCondition(CritterCondition cond, CritterActionAnim actionAnim, AbstractItem contextItem)`

  ...  
  param cond ...  
  param actionAnim ...  
  param contextItem ...

* `void CloseDialog()`

  ...

* `void Action(CritterAction action, int actionData, AbstractItem contextItem)`

  ...  
  param action ...  
  param actionData ...  
  param contextItem ...

* `void Animate(CritterStateAnim stateAnim, CritterActionAnim actionAnim, AbstractItem contextItem, bool clearSequence, bool delayPlay) ExcludeInSingleplayer`

  ...  
  param stateAnim ...  
  param actionAnim ...  
  param contextItem ...  
  param clearSequence ...  
  param delayPlay ...

* `void SetConditionAnims(CritterCondition cond, CritterStateAnim stateAnim, CritterActionAnim actionAnim)`

  ...  
  param cond ...  
  param stateAnim ...  
  param actionAnim ...

* `void PlaySound(string soundName, bool sendSelf)`

  ...  
  param soundName ...  
  param sendSelf ...

* `bool IsKnownLocation(ident locId)`

  ...  
  param locId ...  
  return ...

* `void SetKnownLocation(ident locId)`

  ...  
  param locId ...  
  return ...

* `void RemoveKnownLocation(ident locId)`

  ...  
  param locId ...  
  return ...

* `void SetFog(uint16 zoneX, uint16 zoneY, int fog)`

  ...  
  param zoneX ...  
  param zoneY ...  
  param fog ...

* `int GetFog(uint16 zoneX, uint16 zoneY)`

  ...  
  param zoneX ...  
  param zoneY ...  
  return ...

* `void SendItems(Item[] items)`

  ...  
  param items ...

* `void SendItems(Item[] items, bool owned, bool withInnerEntities, any contextParam)`

  ...  
  param items ...  
  param contextParam ...

* `void Disconnect() ExcludeInSingleplayer`

  ...

* `bool IsOnline() ExcludeInSingleplayer`

  ...  
  return ...

* `void MoveToCritter(Critter target, uint cut, uint speed)`

  ...  
  param target ...  
  param cut ...  
  param speed ...

* `void MoveToHex(uint16 hx, uint16 hy, uint cut, uint speed)`

  ...  
  param hx ...  
  param hy ...  
  param cut ...  
  param speed ...

* `MovingState GetMovingState()`

  ...  
  return ...

* `MovingState GetMovingState(ident& gagId)`

  ...

* `void StopMoving()`

  ...

* `void ChangeMovingSpeed(uint speed)`

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
  param func ...  
  param duration ...  
  param identifier ...

* `void AddTimeEvent(ScriptFunc-uint, Critter, any, uint& func, tick_t duration, any identifier, uint rate)`

  ...  
  param func ...  
  param duration ...  
  param identifier ...  
  param rate ...

* `uint GetTimeEvents(any identifier)`

  ...  
  param identifier ...  
  return ...

* `uint GetTimeEvents(any identifier, uint[]& indexes, tick_t[]& durations, uint[]& rates)`

  ...  
  param identifier ...  
  param indexes ...  
  param durations ...  
  param rates ...  
  return ...

* `uint GetTimeEvents(any[] findIdentifiers, any[]& identifiers, uint[]& indexes, tick_t[]& durations, uint[]& rates)`

  ...  
  param findIdentifiers ...  
  param identifiers ...  
  param indexes ...  
  param durations ...  
  param rates ...  
  return ...

* `void ChangeTimeEvent(uint index, tick_t newDuration, uint newRate)`

  ...  
  param index ...  
  param newDuration ...  
  param newRate ...

* `void RemoveTimeEvent(uint index)`

  ...  
  param index ...

* `uint RemoveTimeEvents(any identifier)`

  ...  
  param identifier ...  
  return ...

* `uint RemoveTimeEvents(any[] identifiers)`

  ...  
  param identifiers ...  
  return ...

* `tick_t GetPlayerOfflineTime()`

  ...

* `void RefreshDialogTime()`

  ...

* `bool IsFree()`

  ...  
  return ...

* `bool IsBusy()`

  ...  
  return ...

* `void Wait(uint ms)`

  ...  
  param ms ...

### Critter client methods

* `void SetName(string name)`

  ...  
  param name ...

* `bool IsOffline() ExcludeInSingleplayer`

  ...  
  return ...

* `bool IsAlive() ExcludeInSingleplayer`

  ...  
  return ...

* `bool IsKnockout() ExcludeInSingleplayer`

  ...  
  return ...

* `bool IsDead() ExcludeInSingleplayer`

  ...  
  return ...

* `bool IsOnMap()`

  ...  
  return ...

* `bool IsMoving() ExcludeInSingleplayer`

  ...  
  return ...

* `bool IsModel()`

  ...  
  return ...

* `bool IsAnimAvailable(CritterStateAnim stateAnim, CritterActionAnim actionAnim)`

  ...  
  param stateAnim ...  
  param actionAnim ...  
  return ...

* `bool IsAnimPlaying()`

  ...  
  return ...

* `CritterStateAnim GetStateAnim()`

  ...  
  return ...

* `void Animate(CritterStateAnim stateAnim, CritterActionAnim actionAnim)`

  ...  
  param stateAnim ...  
  param actionAnim ...

* `void Animate(CritterStateAnim stateAnim, CritterActionAnim actionAnim, AbstractItem contextItem)`

  ...  
  param stateAnim ...  
  param actionAnim ...  
  param contextItem ...

* `void StopAnim()`

  ...

* `uint CountItem(hstring protoId) ExcludeInSingleplayer`

  ...  
  param protoId ...  
  return ...

* `Item GetItem(ident itemId) ExcludeInSingleplayer`

  ...  
  param itemId ...  
  return ...

* `Item GetItem(hstring protoId) ExcludeInSingleplayer`

  ...  
  param protoId ...  
  return ...

* `Item GetItem(ItemComponent component) ExcludeInSingleplayer`

  ...  
  param component ...  
  return ...

* `Item GetItem(ItemProperty property, int propertyValue) ExcludeInSingleplayer`

  ...  
  param property ...  
  param propertyValue ...  
  return ...

* `Item[] GetItems() ExcludeInSingleplayer`

  ...  
  return ...

* `Item[] GetItems(ItemComponent component) ExcludeInSingleplayer`

  ...  
  param component ...  
  return ...

* `Item[] GetItems(ItemProperty property, int propertyValue) ExcludeInSingleplayer`

  ...  
  param property ...  
  param propertyValue ...  
  return ...

* `void GetNameTextInfo(bool& nameVisible, int& x, int& y, int& w, int& h, int& lines)`

  ...  
  param nameVisible ...  
  param x ...  
  param y ...  
  param w ...  
  param h ...  
  param lines ...

* `void GetTextPos(int& x, int& y)`

  ...  
  param x ...  
  param y ...

* `void RunParticle(string particleName, hstring boneName, float moveX, float moveY, float moveZ)`

  ...  
  param particleName ...  
  param boneName ...  
  param moveX ...  
  param moveY ...  
  param moveZ ...

* `void AddAnimCallback(CritterStateAnim stateAnim, CritterActionAnim actionAnim, float normalizedTime, callback-Critter animCallback)`

  ...  
  param stateAnim ...  
  param actionAnim ...  
  param normalizedTime ...  
  param animCallback ...

* `bool GetBonePos(hstring boneName, int& boneX, int& boneY)`

  ...  
  param boneName ...  
  param boneX ...  
  param boneY ...  
  return ...

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
  return ...

* `void SetAlpha(uint8 alpha)`

  ...

* `void SetContour(ContourType contour)`

  ...

* `bool IsFree()`

  ...  
  return ...

* `bool IsBusy()`

  ...  
  return ...

* `void Wait(uint ms)`

  ...  
  param ms ...

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

  ...

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

  ...

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

  ...

* `PrivateServer bool MapCoastRainUp`

  ...

* `PrivateServer ident GeckCityDoor`

  ...

* `PrivateServer uint GeckCityCharges`

  ...

* `PrivateServer uint GeckCityTimeBroken`

  ...

* `PrivateServer int MapRadiationMinDose`

  ...

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

* `PrivateServer uint VCLastBarDialog`

  ...

* `PrivateServer bool WarehouseTurretActive`

  ...

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
  param initFunc ...

* `void SetupScriptEx(hstring initFunc)`

  ...  
  param initFunc ...

* `Location GetLocation()`

  ...  
  return ...

* `Item AddItem(uint16 hx, uint16 hy, hstring protoId, uint count)`

  ...  
  param hx ...  
  param hy ...  
  param protoId ...  
  param count ...  
  return ...

* `Item AddItem(uint16 hx, uint16 hy, hstring protoId, uint count, ItemProperty=>int props)`

  ...  
  param hx ...  
  param hy ...  
  param protoId ...  
  param count ...  
  param props ...  
  return ...

* `Item GetItem(ident itemId)`

  ...  
  param itemId ...  
  return ...

* `Item GetItem(uint16 hx, uint16 hy, hstring pid)`

  ...  
  param hx ...  
  param hy ...  
  param pid ...  
  return ...

* `Item GetItem(uint16 hx, uint16 hy, ItemComponent component)`

  ...  
  param hx ...  
  param hy ...  
  param component ...  
  return ...

* `Item GetItem(uint16 hx, uint16 hy, ItemProperty property, int propertyValue)`

  ...  
  param hx ...  
  param hy ...  
  param property ...  
  param propertyValue ...  
  return ...

* `Item GetItem(uint16 hx, uint16 hy, uint radius, ItemComponent component)`

  ...  
  param hx ...  
  param hy ...  
  param radius ...  
  param component ...  
  return ...

* `Item GetItem(uint16 hx, uint16 hy, uint radius, ItemProperty property, int propertyValue)`

  ...  
  param hx ...  
  param hy ...  
  param radius ...  
  param property ...  
  param propertyValue ...  
  return ...

* `Item[] GetItems()`

  ...  
  return ...

* `Item[] GetItems(uint16 hx, uint16 hy)`

  ...  
  param hx ...  
  param hy ...  
  return ...

* `Item[] GetItems(uint16 hx, uint16 hy, uint radius)`

  ...  
  param hx ...  
  param hy ...  
  param radius ...  
  return ...

* `Item[] GetItems(uint16 hx, uint16 hy, uint radius, hstring pid)`

  ...  
  param hx ...  
  param hy ...  
  param radius ...  
  param pid ...  
  return ...

* `Item[] GetItems(hstring pid)`

  ...  
  param pid ...  
  return ...

* `Item[] GetItems(ItemComponent component)`

  ...  
  param component ...  
  return ...

* `Item[] GetItems(ItemProperty property, int propertyValue)`

  ...  
  param property ...  
  param propertyValue ...  
  return ...

* `Item[] GetItems(uint16 hx, uint16 hy, ItemComponent component)`

  ...  
  param hx ...  
  param hy ...  
  param component ...  
  return ...

* `Item[] GetItems(uint16 hx, uint16 hy, ItemProperty property, int propertyValue)`

  ...  
  param hx ...  
  param hy ...  
  param property ...  
  param propertyValue ...  
  return ...

* `Item[] GetItems(uint16 hx, uint16 hy, uint radius, ItemComponent component)`

  ...  
  param hx ...  
  param hy ...  
  param radius ...  
  param component ...  
  return ...

* `Item[] GetItems(uint16 hx, uint16 hy, uint radius, ItemProperty property, int propertyValue)`

  ...  
  param hx ...  
  param hy ...  
  param radius ...  
  param property ...  
  param propertyValue ...  
  return ...

* `StaticItem GetStaticItem(ident id)`

  ...  
  param id ...  
  return ...

* `StaticItem GetStaticItem(uint16 hx, uint16 hy, hstring pid)`

  ...  
  param hx ...  
  param hy ...  
  param pid ...  
  return ...

* `StaticItem[] GetStaticItems(uint16 hx, uint16 hy)`

  ...  
  param hx ...  
  param hy ...  
  return ...

* `StaticItem[] GetStaticItems(uint16 hx, uint16 hy, uint radius, hstring pid)`

  ...  
  param hx ...  
  param hy ...  
  param radius ...  
  param pid ...  
  return ...

* `StaticItem[] GetStaticItems(hstring pid)`

  ...  
  param pid ...  
  return ...

* `StaticItem[] GetStaticItems(ItemComponent component)`

  ...  
  param component ...  
  return ...

* `StaticItem[] GetStaticItems(ItemProperty property, int propertyValue)`

  ...  
  param property ...  
  param propertyValue ...  
  return ...

* `StaticItem[] GetStaticItems()`

  ...  
  return ...

* `Critter GetCritter(ident crid)`

  ...  
  param crid ...  
  return ...

* `Critter GetCritter(uint16 hx, uint16 hy)`

  ...  
  param hx ...  
  param hy ...  
  return ...

* `Critter GetCritter(CritterComponent component, CritterFindType findType)`

  ...  
  param component ...  
  param findType ...  
  return ...

* `Critter GetCritter(CritterProperty property, int propertyValue, CritterFindType findType)`

  ...  
  param property ...  
  param propertyValue ...  
  param findType ...  
  return ...

* `Critter[] GetCritters(uint16 hx, uint16 hy, uint radius, CritterFindType findType)`

  ...  
  param hx ...  
  param hy ...  
  param radius ...  
  param findType ...  
  return ...

* `Critter[] GetCritters(CritterFindType findType)`

  ...  
  param findType ...  
  return ...

* `Critter[] GetCritters(hstring pid, CritterFindType findType)`

  ...  
  param pid ...  
  param findType ...  
  return ...

* `Critter[] GetCritters(CritterComponent component, CritterFindType findType)`

  ...  
  param component ...  
  param findType ...  
  return ...

* `Critter[] GetCritters(CritterProperty property, int propertyValue, CritterFindType findType)`

  ...  
  param property ...  
  param propertyValue ...  
  param findType ...  
  return ...

* `Critter[] GetCrittersInPath(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy, float angle, uint dist, CritterFindType findType)`

  ...  
  param fromHx ...  
  param fromHy ...  
  param toHx ...  
  param toHy ...  
  param angle ...  
  param dist ...  
  param findType ...  
  return ...

* `Critter[] GetCrittersInPath(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy, float angle, uint dist, CritterFindType findType, uint16& preBlockHx, uint16& preBlockHy, uint16& blockHx, uint16& blockHy)`

  ...  
  param fromHx ...  
  param fromHy ...  
  param toHx ...  
  param toHy ...  
  param angle ...  
  param dist ...  
  param findType ...  
  param preBlockHx ...  
  param preBlockHy ...  
  param blockHx ...  
  param blockHy ...  
  return ...

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
  param fromHx ...  
  param fromHy ...  
  param toHx ...  
  param toHy ...  
  param angle ...  
  param dist ...

* `void GetWallHexInPath(uint16 fromHx, uint16 fromHy, uint16& toHx, uint16& toHy, float angle, uint dist)`

  ...  
  param fromHx ...  
  param fromHy ...  
  param toHx ...  
  param toHy ...  
  param angle ...  
  param dist ...

* `uint GetPathLength(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy, uint cut)`

  ...  
  param fromHx ...  
  param fromHy ...  
  param toHx ...  
  param toHy ...  
  param cut ...  
  return ...

* `uint GetPathLength(Critter cr, uint16 toHx, uint16 toHy, uint cut)`

  ...  
  param cr ...  
  param toHx ...  
  param toHy ...  
  param cut ...  
  return ...

* `Critter AddNpc(hstring protoId, uint16 hx, uint16 hy, uint8 dir)`

  ...  
  param protoId ...  
  param hx ...  
  param hy ...  
  param dir ...  
  return ...

* `Critter AddNpc(hstring protoId, uint16 hx, uint16 hy, uint8 dir, CritterProperty=>int props)`

  ...  
  param protoId ...  
  param hx ...  
  param hy ...  
  param dir ...  
  param props ...  
  return ...

* `Critter AddNpc(hstring protoId, uint16 hx, uint16 hy, uint8 dir, CritterProperty=>any props)`

  ...  
  param protoId ...  
  param hx ...  
  param hy ...  
  param dir ...  
  param props ...  
  return ...

* `bool IsHexMovable(uint16 hexX, uint16 hexY)`

  ...  
  param hexX ...  
  param hexY ...  
  return ...

* `bool IsHexesMovable(uint16 hexX, uint16 hexY, uint radius)`

  ...  
  param hexX ...  
  param hexY ...  
  param radius ...  
  return ...

* `bool IsHexShootable(uint16 hexX, uint16 hexY)`

  ...  
  param hexX ...  
  param hexY ...  
  return ...

* `void SetText(uint16 hexX, uint16 hexY, ucolor color, string text)`

  ...  
  param hexX ...  
  param hexY ...  
  param color ...  
  param text ...

* `void SetTextMsg(uint16 hexX, uint16 hexY, ucolor color, TextPackName textPack, uint strNum)`

  ...  
  param hexX ...  
  param hexY ...  
  param color ...  
  param textMsg ...  
  param strNum ...

* `void SetTextMsg(uint16 hexX, uint16 hexY, ucolor color, TextPackName textPack, uint strNum, string lexems)`

  ...  
  param hexX ...  
  param hexY ...  
  param color ...  
  param textMsg ...  
  param strNum ...  
  param lexems ...

* `void RunEffect(hstring effPid, uint16 hx, uint16 hy, uint radius)`

  ...  
  param effPid ...  
  param hx ...  
  param hy ...  
  param radius ...

* `void RunFlyEffect(hstring effPid, Critter fromCr, Critter toCr, uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy)`

  ...  
  param effPid ...  
  param fromCr ...  
  param toCr ...  
  param fromHx ...  
  param fromHy ...  
  param toHx ...  
  param toHy ...

* `bool CheckPlaceForItem(uint16 hx, uint16 hy, hstring pid)`

  ...  
  param hx ...  
  param hy ...  
  param pid ...  
  return ...

* `void BlockHex(uint16 hx, uint16 hy, bool full)`

  ...  
  param hx ...  
  param hy ...  
  param full ...

* `void UnblockHex(uint16 hx, uint16 hy)`

  ...  
  param hx ...  
  param hy ...

* `void PlaySound(string soundName)`

  ...  
  param soundName ...

* `void PlaySound(string soundName, uint16 hx, uint16 hy, uint radius)`

  ...  
  param soundName ...  
  param hx ...  
  param hy ...  
  param radius ...

* `void Regenerate()`

  ...  
  return ...

* `bool MoveHexByDir(uint16& hx, uint16& hy, uint8 dir, uint steps)`

  ...  
  param hx ...  
  param hy ...  
  param dir ...  
  param steps ...  
  return ...

* `void VerifyTrigger(Critter cr, uint16 hx, uint16 hy, uint8 dir)`

  ...  
  param cr ...  
  param hx ...  
  param hy ...  
  param dir ...

### Map client methods

* `void DrawMap()`

  ...

* `void DrawMapTexts()`

  ...

* `void Message(string text, uint16 hx, uint16 hy, tick_t showTime, ucolor color, bool fade, int endOx, int endOy)`

  ...  
  param text ...  
  param hx ...  
  param hy ...  
  param showTime ...  
  param color ...  
  param fade ...  
  param endOx ...  
  param endOy ...

* `void DrawMapSprite(MapSpriteData mapSpr)`

  ...  
  param mapSpr ...

* `void RebuildFog()`

  ...

* `Item GetItem(ident itemId) ExcludeInSingleplayer`

  ...  
  param itemId ...  
  return ...

* `Item[] GetVisibleItems()`

  ...  
  return ...

* `Item[] GetVisibleItemsOnHex(uint16 hx, uint16 hy)`

  ...  
  param hx ...  
  param hy ...  
  return ...

* `Critter GetCritter(ident critterId) ExcludeInSingleplayer`

  ...  
  param critterId ...  
  return ...

* `Critter[] GetCritters() ExcludeInSingleplayer`

  ...  
  param findType ...  
  return ...

* `Critter[] GetCritters(CritterFindType findType) ExcludeInSingleplayer`

  ...  
  param findType ...  
  return ...

* `Critter[] GetCritters(hstring pid, CritterFindType findType) ExcludeInSingleplayer`

  ...  
  param pid ...  
  param findType ...  
  return ...

* `Critter[] GetCritters(uint16 hx, uint16 hy, uint radius, CritterFindType findType) ExcludeInSingleplayer`

  ...  
  param hx ...  
  param hy ...  
  param radius ...  
  param findType ...  
  return ...

* `Critter[] GetCrittersInPath(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy, float angle, uint dist, CritterFindType findType) ExcludeInSingleplayer`

  ...  
  param fromHx ...  
  param fromHy ...  
  param toHx ...  
  param toHy ...  
  param angle ...  
  param dist ...  
  param findType ...  
  return ...

* `Critter[] GetCrittersWithBlockInPath(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy, float angle, uint dist, CritterFindType findType, uint16& preBlockHx, uint16& preBlockHy, uint16& blockHx, uint16& blockHy) ExcludeInSingleplayer`

  ...  
  param fromHx ...  
  param fromHy ...  
  param toHx ...  
  param toHy ...  
  param angle ...  
  param dist ...  
  param findType ...  
  param preBlockHx ...  
  param preBlockHy ...  
  param blockHx ...  
  param blockHy ...  
  return ...

* `void GetHexInPath(uint16 fromHx, uint16 fromHy, uint16& toHx, uint16& toHy, float angle, uint dist) ExcludeInSingleplayer`

  ...  
  param fromHx ...  
  param fromHy ...  
  param toHx ...  
  param toHy ...  
  param angle ...  
  param dist ...

* `uint8[] GetPath(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy, uint cut) ExcludeInSingleplayer`

  ...  
  param fromHx ...  
  param fromHy ...  
  param toHx ...  
  param toHy ...  
  param cut ...  
  return ...

* `uint8[] GetPath(Critter cr, uint16 toHx, uint16 toHy, uint cut) ExcludeInSingleplayer`

  ...  
  param cr ...  
  param toHx ...  
  param toHy ...  
  param cut ...  
  return ...

* `uint GetPathLength(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy, uint cut) ExcludeInSingleplayer`

  ...  
  param fromHx ...  
  param fromHy ...  
  param toHx ...  
  param toHy ...  
  param cut ...  
  return ...

* `uint GetPathLength(Critter cr, uint16 toHx, uint16 toHy, uint cut) ExcludeInSingleplayer`

  ...  
  param cr ...  
  param toHx ...  
  param toHy ...  
  param cut ...  
  return ...

* `void MoveScreenToHex(uint16 hx, uint16 hy, uint speed, bool canStop)`

  ...  
  param hx ...  
  param hy ...  
  param speed ...  
  param canStop ...

* `void MoveScreenOffset(int ox, int oy, uint speed, bool canStop)`

  ...  
  param ox ...  
  param oy ...  
  param speed ...  
  param canStop ...

* `void LockScreenScroll(Critter cr, bool softLock, bool unlockIfSame)`

  ...  
  param cr ...  
  param softLock ...  
  param unlockIfSame ...

* `bool MoveHexByDir(uint16& hx, uint16& hy, uint8 dir, uint steps) ExcludeInSingleplayer`

  ...  
  param hx ...  
  param hy ...  
  param dir ...  
  param steps ...  
  return ...

* `Item GetTile(uint16 hx, uint16 hy, bool roof)`

  ...  
  param hx ...  
  param hy ...  
  param roof ...  
  return ...

* `Item GetTile(uint16 hx, uint16 hy, bool roof, uint8 layer)`

  ...  
  param hx ...  
  param hy ...  
  param roof ...  
  param layer ...  
  return ...

* `Item[] GetTiles(uint16 hx, uint16 hy, bool roof)`

  ...  
  param hx ...  
  param hy ...  
  param roof ...  
  return ...

* `void RedrawMap()`

  ...

* `void ChangeZoom(float targetZoom)`

  ...  
  param targetZoom ...

* `bool GetHexScreenPos(uint16 hx, uint16 hy, int& x, int& y)`

  ...  
  param hx ...  
  param hy ...  
  param x ...  
  param y ...  
  return ...

* `bool GetHexAtScreenPos(int x, int y, uint16& hx, uint16& hy)`

  ...  
  param x ...  
  param y ...  
  param hx ...  
  param hy ...  
  return ...

* `bool GetHexAtScreenPos(int x, int y, uint16& hx, uint16& hy, int& ox, int& oy)`

  ...  
  param x ...  
  param y ...  
  param hx ...  
  param hy ...  
  param ox ...  
  param oy ...  
  return ...

* `Item GetItemAtScreenPos(int x, int y)`

  ...  
  param x ...  
  param y ...  
  return ...

* `Critter GetCritterAtScreenPos(int x, int y)`

  ...  
  param x ...  
  param y ...  
  return ...

* `Critter GetCritterAtScreenPos(int x, int y, int extraRange)`

  ...  
  param x ...  
  param y ...  
  param extraRange  
  return ...

* `Entity GetEntityAtScreenPos(int x, int y)`

  ...  
  param x ...  
  param y ...  
  return ...

* `bool IsMapHexPassed(uint16 hx, uint16 hy)`

  ...  
  param hx ...  
  param hy ...  
  return ...

* `bool IsMapHexShooted(uint16 hx, uint16 hy)`

  ...  
  param hx ...  
  param hy ...  
  return ...

* `void SetShootBorders(bool enabled)`

  ...  
  param enabled ...

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

  ...

* `PrivateServer ident[] MapIds ReadOnly`

  ...

* `PrivateServer hstring[] MapProtos ReadOnly`

  ...

* `PrivateServer hstring[] MapEntrances ReadOnly`

  ...

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

  ...

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
  param initFunc ...

* `void SetupScriptEx(hstring initFunc)`

  ...  
  param initFunc ...

* `uint GetMapCount()`

  ...  
  return ...

* `Map GetMap(hstring mapPid)`

  ...  
  param mapPid ...  
  return ...

* `Map GetMapByIndex(uint index)`

  ...  
  param index ...  
  return ...

* `Map[] GetMaps()`

  ...  
  return ...

* `void GetEntrance(uint entranceIndex, uint& mapIndex, hstring& entrance)`

  ...  
  param entranceIndex ...  
  param mapIndex ...  
  param entrance ...  
  return ...

* `uint GetEntrances(int[]& mapsIndex, hstring[]& entrances)`

  ...  
  param mapsIndex ...  
  param entrances ...  
  return ...

* `void Regenerate()`

  ...  
  return ...

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

  ...

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

  ...

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

  - `Alive = 0x01`

  - `Dead = 0x02`

  - `Players = 0x10`

  - `Npc = 0x20`

  - `AlivePlayers = 0x11`

  - `DeadPlayers = 0x12`

  - `AliveNpc = 0x21`

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

  ...

  - `None = 0`

  - `Left = 1`

  - `Right = 2`

  - `Top = 4`

  - `Bottom = 8`

* `DockStyle`

  ...

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

  ...

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

  ...

  - `NoPref = 0`

  - `Always = 1`

  - `Sometimes = 2`

  - `BeSure = 3`

  - `BeCareful = 4`

  - `BeAbsSure = 5`

* `AttackWho`

  ...

  - `WhoAttackMe = 0`

  - `Strongest = 1`

  - `Weakest = 2`

  - `Whomever = 3`

  - `Closest = 4`

* `BestWeap`

  ...

  - `NoPref = 0`

  - `Never = 1`

  - `Random = 2`

  - `Unarmed = 3`

  - `RangedOvMelee = 4`

  - `MeleeOvRanged = 5`

  - `UnarmOvThrown = 6`

* `ChemUse`

  ...

  - `Clean = 0`

  - `Sometimes = 1`

  - `StimsHurtLo = 2`

  - `StimsHurtHi = 3`

  - `Anytime = 4`

  - `Always = 5`

* `Disposition`

  ...

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

  ...

  - `None = 0`

  - `Crippled = 1`

  - `Blind = 2`

  - `CripArms = 3`

* `RunAway`

  ...

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

  ...

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

  ...

  - `InventoryMain = 0`

  - `InventorySpecial = 1`

  - `InventoryStats = 2`

  - `InventoryResist = 3`

* `ItemLookTypes`

  ...

  - `Default = 0`

  - `OnlyName = 1`

  - `Map = 2`

  - `Barter = 3`

  - `Inventory = 4`

  - `WmCar = 5`

* `CritterLookTypes`

  ...

  - `OnlyName = 0`

  - `LookShort = 1`

  - `LookFull = 2`

* `Fonts`

  ...

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

  ...

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

  ...

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

  ...

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

  ...

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

  ...

  - `Male = 0`

  - `Female = 1`

  - `It = 2`

* `ItemPerks`

  ...

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

  ...

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

  ...

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

  ...

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

  ...

  - `NukaCola = 0`

  - `Buffout = 1`

  - `Mentats = 2`

  - `Psycho = 3`

  - `Radaway = 4`

  - `Jet = 5`

  - `Tragic = 6`

* `KarmaLevel`

  ...

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

  ...

  - `Unknown = 0`

  - `Idolized = 1`

  - `Liked = 2`

  - `Accepted = 3`

  - `Neutral = 4`

  - `Antipathy = 5`

  - `Hated = 6`

  - `Vilified = 7`

* `EScores`

  ...

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

  ...

  - `None = 0`

  - `MainInfo = 100`

  - `SermonDead = 101`

  - `SermonCharacter = 102`

  - `SermonNasty = 103`

  - `SermonBehavior = 104`

  - `MythNeutral = 105`

* `TransferTypes`

  ...

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

  ...

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

  - `AttackDistanceHint = 47`

  - `TalkDistance = 48`

  - `MaxTalkers = 49`

  - `DialogId = 50`

  - `Lexems = 51`

  - `KnownLocations = 52`

  - `InSneakMode = 53`

  - `DeadDrawNoFlatten = 54`

  - `NameColor = 55`

  - `ContourColor = 56`

  - `ArroyoRaydersAttackedId = 57`

  - `BehemothOwner = 58`

  - `BehemothRadio = 59`

  - `BehemothLastComand = 60`

  - `BehemothOrderType = 61`

  - `BehemothLastOrder = 62`

  - `BehemothParam_1 = 63`

  - `BehemothParam_2 = 64`

  - `BehemothLastReport = 65`

  - `BHHubHoloRemembered = 66`

  - `BHUranDiscount = 67`

  - `BBMsgPage = 68`

  - `BBSelectedMsg = 69`

  - `KlamAldoBusy = 70`

  - `KlamAldoListenId = 71`

  - `KlamAldoReaderId = 72`

  - `BBMsgCount = 73`

  - `CaravanCrvId = 74`

  - `VCDeadPatrollers = 75`

  - `ReddWadeCaravanEscort = 76`

  - `ReddSavinelCaravanEscort = 77`

  - `ReddStanCaravanEscort = 78`

  - `NcrReddingCaravanEscort = 79`

  - `BHKitCaravanEscort = 80`

  - `VCShrimPatrol = 81`

  - `ArroyoSelmaCaravanEscort = 82`

  - `ArroyoGayzumCaravanEscort = 83`

  - `ArroyoLaumerCaravanEscort = 84`

  - `ModAurelianoCaravanEscort = 85`

  - `CommonCrvResetCounter = 86`

  - `ReddCrvResetCounter = 87`

  - `NcrCrvResetCounter = 88`

  - `BHCrvResetCounter = 89`

  - `ArroyoCrvResetCounter = 90`

  - `CaravanReaction = 91`

  - `CaravanNervosityLvl = 92`

  - `CaravanIdleCount = 93`

  - `LastSelectedCaravan = 94`

  - `ApRegenerationTick = 95`

  - `ApRegenerationTime = 96`

  - `CollectorTimeNextSearch = 97`

  - `CompRiddleMapId = 98`

  - `CompRiddleHexX = 99`

  - `CompRiddleHexY = 100`

  - `KnockoutAp = 101`

  - `WaitEndTick = 102`

  - `ActionAnimKnockoutEnd = 103`

  - `NcrBusterLostCStatus = 104`

  - `QDappoLostRobotHexNum = 105`

  - `BankMoney = 106`

  - `DenHubBank5 = 107`

  - `DenHubGuard5 = 108`

  - `DenPoormanItemId = 109`

  - `DenVirginCount = 110`

  - `DenVirginIsHome = 111`

  - `UniqTimeout = 112`

  - `Loyality = 113`

  - `NpcStory = 114`

  - `NameMemNpcPlayer = 115`

  - `NameMemPlayerNpc = 116`

  - `TradeWas = 117`

  - `DenKliffBlessWas = 118`

  - `DenVirginiaSexWas = 119`

  - `NcrPlayerTalkPoliceman = 120`

  - `SFLoPanPayed = 121`

  - `ChanceOneFromTwo = 122`

  - `ChanceOneFromThree = 123`

  - `ChanceOneFromFive = 124`

  - `CurrentDialogNumber = 125`

  - `LastDialogBoxShownTick = 126`

  - `DrugEffects = 127`

  - `DoughnutsCounter = 128`

  - `LastElectronicLocked = 129`

  - `EliTimeNextSing = 130`

  - `EnemyStack = 131`

  - `IsNoEnemyStack = 132`

  - `EnergyBarierTerminalHx = 133`

  - `EnergyBarierTerminalHy = 134`

  - `EnergyBarierNetNum = 135`

  - `EnergyBarierHackBonus = 136`

  - `EnergyBarierHitBonus = 137`

  - `FighterPatternCanGenStim = 138`

  - `FighterPatternAllyAssistRadius = 139`

  - `FighterPatternAssistAlliesNum = 140`

  - `FighterPatternMustHealLvl = 141`

  - `FighterPatternLocalAlarmDeads = 142`

  - `FighterPatternGlobalAlarmDeads = 143`

  - `FighterQuestMinHp = 144`

  - `FighterQuestOnlyHandCombat = 145`

  - `FighterQuestTeamIdOld = 146`

  - `FighterQuestTeamIdFight = 147`

  - `FighterQuestPlayerId = 148`

  - `FighterQuestFightPriority = 149`

  - `FighterQuestVarNum = 150`

  - `FixboyPowerArmor = 151`

  - `ModLourenceVenomedratRecipe = 152`

  - `ModLourenceTNTRatRecipe = 153`

  - `NavEmpRocketRecipe = 154`

  - `FixboyDefault = 155`

  - `SFRecipeSsupersledge = 156`

  - `SFRecipePlasmagrenades = 157`

  - `Fixboy700NitroExpress = 158`

  - `FixboyAmmoPressOperator = 159`

  - `RacingCheckPoints = 160`

  - `RacingCheckpointLocId = 161`

  - `GERacingCritterHx = 162`

  - `GERacingCritterHy = 163`

  - `GERacingCritterDir = 164`

  - `GERacingNpcRole = 165`

  - `GERacingOpeningPhrases = 166`

  - `GEReplExplodeTank = 167`

  - `GEReplNopasaran = 168`

  - `GEReplFindstation = 169`

  - `GEReplNotifictions = 170`

  - `GEReplEntryZombie = 171`

  - `GEReplLastOrder = 172`

  - `GEReplIsAddedAttackPlane = 173`

  - `HellMineTimeoutEnd = 174`

  - `HostileLQIsStoped = 175`

  - `HostileLQData = 176`

  - `SFAhs7Escort = 177`

  - `SFHonomerPlayerId = 178`

  - `SFEscortLocation = 179`

  - `SFLabFailed = 180`

  - `QHubLabIsDialogRun = 181`

  - `BarterLourensRats1 = 182`

  - `ModLourenceRatsFlute = 183`

  - `BarterLourensRatBodycount = 184`

  - `ModHoughRatsFluteTimeout = 185`

  - `ModLourenceToxinTimeout = 186`

  - `ModLourenceRatsFluteCounter = 187`

  - `ModLourenceLureActive = 188`

  - `GuardedItemSkill = 189`

  - `V13DclawEggs = 190`

  - `KlamTorrCowboy = 191`

  - `KlamCowboyCountGav = 192`

  - `KlamCowboyMobHx = 193`

  - `KlamCowboyMobHy = 194`

  - `KlamDantonBramin = 195`

  - `KlamJosallDanton = 196`

  - `KlamKuklachev = 197`

  - `KlamSmilyGecko = 198`

  - `KlamSmilyCurrentHp = 199`

  - `KlamSmilyCountKills = 200`

  - `KlamSmilyHealing = 201`

  - `LimitedBarterData = 202`

  - `IsGeck = 203`

  - `StealExpCount = 204`

  - `FirstAidCount = 205`

  - `MainQuest = 206`

  - `GCityCitizen = 207`

  - `MapGeckCityTraderSkillBarter = 208`

  - `MapKlamathRobotTimeNextSay = 209`

  - `ModJoeGiantWasp = 210`

  - `TribSulikRaid = 211`

  - `TribRaiderKillCount = 212`

  - `NCRElizeSlavers = 213`

  - `MapPrimalTribeRaiderHx = 214`

  - `MapPrimalTribeRaiderHy = 215`

  - `SFRonKillBeasts = 216`

  - `SFRonFindbodies = 217`

  - `SFTankerCentaurNoticed = 218`

  - `SFTankerFloaterNoticed = 219`

  - `MapSFTankerBicycleId = 220`

  - `MirelurkCombatCurStage = 221`

  - `MirelurkCombatTimeNextStage = 222`

  - `MirelurkCombatLastBrokenBag = 223`

  - `MirelurkCombatDestroyingItem = 224`

  - `MobAttackedId = 225`

  - `MobFury = 226`

  - `MobFear = 227`

  - `MobMaxFear = 228`

  - `ModVampireFarmLocation = 229`

  - `MonologueData = 230`

  - `NavHenryEmpTest = 231`

  - `NavEmpTestedCritter = 232`

  - `NavarroTimeOutScan = 233`

  - `NavarroChipUsedId = 234`

  - `NcrAlexHoloFindStatus = 235`

  - `NCRFelixFindBrahmin = 236`

  - `NCRHubBook = 237`

  - `NCRFelixSaveBrahmin = 238`

  - `NCRHubBookAccess1 = 239`

  - `NCRHubBookAccess2 = 240`

  - `NCRHubBookAccess3 = 241`

  - `NCRHubBookAccess4 = 242`

  - `NCRHubBookAccess5 = 243`

  - `NCRHubBookAccess6 = 244`

  - `NCRHubBookAccess7 = 245`

  - `NCRHubBookQuestTimeout = 246`

  - `NcrCommonBeggarInvokeId = 247`

  - `NcrCommonBeggarPhraseNum = 248`

  - `NcrCommonBeggarHideMoneyInvocation = 249`

  - `NcrCommonBrahminId = 250`

  - `QNcrElizeInvasion = 251`

  - `NCRKarlsonSon = 252`

  - `NcrSonCatcherId = 253`

  - `NcrSonMovesCounter = 254`

  - `NcrMichealMessageNum = 255`

  - `MailDelivery = 256`

  - `NcrMailRecieverId = 257`

  - `NcrMailTimeout = 258`

  - `NcrRatchBuggy = 259`

  - `NcrShaimanProtest = 260`

  - `NcrShaimanStringNum = 261`

  - `NcrSiegeTerminate = 262`

  - `NcrSiegeKillsCounter = 263`

  - `NcrSmitVsVestinStatus = 264`

  - `NcrSmitStringNum = 265`

  - `NcrSmitGateStringNum = 266`

  - `NcrSmitPlayerId = 267`

  - `NcrSmitIdleCount = 268`

  - `NcrWestinMapPidTo = 269`

  - `NcrWestinHexNumTo = 270`

  - `NcrWestinEveryEveningInvokeId = 271`

  - `NcrWestinEveryMorningInvokeId = 272`

  - `LastBagRefreshedTime = 273`

  - `LastNpcDialog = 274`

  - `NpcDialogStringNum = 275`

  - `Planes = 276`

  - `NpcRevengeNpcHxHy = 277`

  - `NpcRevengeCountWait = 278`

  - `NRWriKidnap = 279`

  - `NRSalvatoreKill = 280`

  - `NRWriKidnapNotifyTime = 281`

  - `NRKidnapKillsCounter = 282`

  - `QNrWriKidnapInvokeId = 283`

  - `NukeStock = 284`

  - `NukeRestockTime = 285`

  - `PatternSniperCountRunning = 286`

  - `PetOwnerId = 287`

  - `PetLifeTime = 288`

  - `IsGenerated = 289`

  - `PokerWins = 290`

  - `PokerNumOfNpc = 291`

  - `PokerWincash = 292`

  - `PokerFraud = 293`

  - `PokerManywins = 294`

  - `PokerData = 295`

  - `QWarehouse = 296`

  - `QWarehouseSub1 = 297`

  - `QWarehouseSub2 = 298`

  - `WarehouseDataId = 299`

  - `WarehouseQuestData = 300`

  - `WarehouseOther = 301`

  - `RatGrenadeProtoId = 302`

  - `RatGrenadeOwnerId = 303`

  - `ReddMineNuggets = 304`

  - `ReddMarionWan = 305`

  - `ReddQWinamingoKills = 306`

  - `ReddQWinamingoHealing = 307`

  - `ReddDoctorPoisoned = 308`

  - `ReddRooneyCemetery = 309`

  - `CanRepairWeapons = 310`

  - `CanRepairWeaponsSpecial = 311`

  - `CanRepairArmor = 312`

  - `CanRepairArmorSpecial = 313`

  - `RepairCompleteTime = 314`

  - `RepairItemPid = 315`

  - `ReplicationTime = 316`

  - `HellVisits = 317`

  - `ReplBankIsCanEnter = 318`

  - `ReplBankeIsAttackGagPlayer = 319`

  - `ReplHellTurretHack = 320`

  - `TerminalPlayerId = 321`

  - `TerminalDialogId = 322`

  - `ModFarrelAmmiak = 323`

  - `RouletteCroupierNum = 324`

  - `RouletteBetCoord1 = 325`

  - `RouletteBetCoord2 = 326`

  - `RouletteBetCoord3 = 327`

  - `RouletteBetSize = 328`

  - `RouletteBetType = 329`

  - `RouletteData = 330`

  - `CanSendSay = 331`

  - `Scores = 332`

  - `SEAndroidMonologEnd = 333`

  - `SETalkingHeadStringNum = 334`

  - `SETeleportEatId = 335`

  - `SFAhs7HubJudgement = 336`

  - `SFLoPanBlackmailSum = 337`

  - `SFHububJudgementLocId = 338`

  - `SFHubJudgementKills = 339`

  - `SfMercMaster = 340`

  - `SFCommonOneWeekInvokeId = 341`

  - `SFCommonFightPlayerId = 342`

  - `ClickCounter = 343`

  - `SFInvasionMirelurkKills = 344`

  - `BHRocketBase = 345`

  - `NcrElizeSlvrsHunting = 346`

  - `NcrElizeSlvrsHuntingStatus = 347`

  - `NcrSantiagoSpyMission = 348`

  - `QSpyMissonStringNum = 349`

  - `TimeoutBattle = 350`

  - `TimeoutTransfer = 351`

  - `WalkSpeedBase = 352`

  - `WalkSpeed = 353`

  - `IsNoMove = 354`

  - `IsNoMoveBase = 355`

  - `IsNoRun = 356`

  - `IsNoRunBase = 357`

  - `Strength = 358`

  - `StrengthBase = 359`

  - `Perception = 360`

  - `PerceptionBase = 361`

  - `Endurance = 362`

  - `EnduranceBase = 363`

  - `Charisma = 364`

  - `CharismaBase = 365`

  - `Intellect = 366`

  - `IntellectBase = 367`

  - `Agility = 368`

  - `AgilityBase = 369`

  - `Luck = 370`

  - `LuckBase = 371`

  - `ArmorClass = 372`

  - `CurrentHp = 373`

  - `MaxLife = 374`

  - `MaxLifeBase = 375`

  - `ActionPointsBase = 376`

  - `ArmorClassBase = 377`

  - `MeleeDamage = 378`

  - `MeleeDamageBase = 379`

  - `IsOverweight = 380`

  - `CarryWeight = 381`

  - `CarryWeightBase = 382`

  - `Sequence = 383`

  - `SequenceBase = 384`

  - `HealingRate = 385`

  - `HealingRateBase = 386`

  - `CriticalChance = 387`

  - `CriticalChanceBase = 388`

  - `MaxCritical = 389`

  - `MaxCriticalBase = 390`

  - `Toxic = 391`

  - `Radioactive = 392`

  - `KillExperience = 393`

  - `BodyType = 394`

  - `LocomotionType = 395`

  - `DamageType = 396`

  - `Age = 397`

  - `Gender = 398`

  - `PoisoningLevel = 399`

  - `RadiationLevel = 400`

  - `UnspentSkillPoints = 401`

  - `UnspentPerks = 402`

  - `Karma = 403`

  - `ReplicationMoney = 404`

  - `ReplicationCount = 405`

  - `ReplicationCost = 406`

  - `RateObject = 407`

  - `BonusLook = 408`

  - `NpcRole = 409`

  - `AiId = 410`

  - `TeamId = 411`

  - `NextCrType = 412`

  - `DeadBlockerId = 413`

  - `CurrentArmorPerk = 414`

  - `NextReplicationMap = 415`

  - `NextReplicationEntry = 416`

  - `PlayerKarma = 417`

  - `ArmorPerk = 418`

  - `LastStealCrId = 419`

  - `StealCount = 420`

  - `GlobalMapMoveCounter = 421`

  - `Experience = 422`

  - `MaxMoveApBase = 423`

  - `AnimType = 424`

  - `IsNoUnarmed = 425`

  - `KnownLocProtoId = 426`

  - `IsNoHome = 427`

  - `HomeMapId = 428`

  - `HomeMapPid = 429`

  - `HomeHexX = 430`

  - `HomeHexY = 431`

  - `HomeDir = 432`

  - `IsNoTalk = 433`

  - `MapLeaveHexX = 434`

  - `MapLeaveHexY = 435`

  - `KnownLockerId = 436`

  - `SpecialSkillPickOnGround = 437`

  - `SpecialSkillLootCritter = 438`

  - `FollowLeaderId = 439`

  - `LastSendEntrancesLocId = 440`

  - `LastSendEntrancesTick = 441`

  - `CrTypeAliasBase = 442`

  - `CrTypeAlias = 443`

  - `ModelNameBase = 444`

  - `IsNoArmor = 445`

  - `Anims = 446`

  - `IsNoAim = 447`

  - `Kills = 448`

  - `KillMen = 449`

  - `KillWomen = 450`

  - `KillAlien = 451`

  - `KillChildren = 452`

  - `KillFloater = 453`

  - `KillRat = 454`

  - `KillCentaur = 455`

  - `ReputationDen = 456`

  - `ReputationKlamath = 457`

  - `ReputationModoc = 458`

  - `ReputationVaultCity = 459`

  - `ReputationGecko = 460`

  - `ReputationBrokenHills = 461`

  - `ReputationNewReno = 462`

  - `ReputationSierra = 463`

  - `ReputationVault15 = 464`

  - `ReputationNCR = 465`

  - `ReputationCathedral = 466`

  - `ReputationSAD = 467`

  - `ReputationRedding = 468`

  - `ReputationSF = 469`

  - `ReputationNavarro = 470`

  - `ReputationArroyo = 471`

  - `ReputationPrimalTribe = 472`

  - `ReputationRangers = 473`

  - `ReputationVault13 = 474`

  - `ReputationSacramento = 475`

  - `Addictions = 476`

  - `IsAddicted = 477`

  - `IsJetAddicted = 478`

  - `IsBuffoutAddicted = 479`

  - `IsMentatsAddicted = 480`

  - `IsPsychoAddicted = 481`

  - `IsRadawayAddicted = 482`

  - `DamageResistance = 483`

  - `NormalResistance = 484`

  - `PoisonResistance = 485`

  - `RadiationResistance = 486`

  - `ExplodeResistance = 487`

  - `NormalResistanceBase = 488`

  - `LaserResistanceBase = 489`

  - `FireResistanceBase = 490`

  - `PlasmaResistanceBase = 491`

  - `ElectricityResistanceBase = 492`

  - `EmpResistanceBase = 493`

  - `ExplodeResistanceBase = 494`

  - `PoisonResistanceBase = 495`

  - `RadiationResistanceBase = 496`

  - `DamageThreshold = 497`

  - `NormalThresholdBase = 498`

  - `LaserThresholdBase = 499`

  - `FireThresholdBase = 500`

  - `PlasmaThresholdBase = 501`

  - `ElectricityThresholdBase = 502`

  - `EmpThresholdBase = 503`

  - `ExplodeThresholdBase = 504`

  - `PoisonThresholdBase = 505`

  - `RadiationThresholdBase = 506`

  - `IsPoisoned = 507`

  - `IsRadiated = 508`

  - `IsInjured = 509`

  - `IsDamagedEye = 510`

  - `IsDamagedRightArm = 511`

  - `IsDamagedLeftArm = 512`

  - `IsDamagedRightLeg = 513`

  - `IsDamagedLeftLeg = 514`

  - `Var0 = 515`

  - `Var1 = 516`

  - `Var2 = 517`

  - `Var3 = 518`

  - `Var4 = 519`

  - `Var5 = 520`

  - `Var6 = 521`

  - `Var7 = 522`

  - `Var8 = 523`

  - `Var9 = 524`

  - `SkillSmallGuns = 525`

  - `SkillBigGuns = 526`

  - `SkillEnergyWeapons = 527`

  - `SkillUnarmed = 528`

  - `SkillMeleeWeapons = 529`

  - `SkillThrowing = 530`

  - `SkillFirstAid = 531`

  - `SkillDoctor = 532`

  - `SkillSneak = 533`

  - `SkillLockpick = 534`

  - `SkillSteal = 535`

  - `SkillTraps = 536`

  - `SkillScience = 537`

  - `SkillRepair = 538`

  - `SkillSpeech = 539`

  - `SkillBarter = 540`

  - `SkillGambling = 541`

  - `SkillOutdoorsman = 542`

  - `TagSkills = 543`

  - `TagSkill1 = 544`

  - `TagSkill2 = 545`

  - `TagSkill3 = 546`

  - `PerkBookworm = 547`

  - `PerkAwareness = 548`

  - `PerkBonusHthAttacks = 549`

  - `PerkBonusHthDamage = 550`

  - `PerkBonusRangedDamage = 551`

  - `PerkBonusRateOfFire = 552`

  - `PerkEarlierSequence = 553`

  - `PerkFasterHealing = 554`

  - `PerkMoreCriticals = 555`

  - `PerkNightVision = 556`

  - `PerkRadResistance = 557`

  - `PerkToughness = 558`

  - `PerkStrongBack = 559`

  - `PerkSharpshooter = 560`

  - `PerkSurvivalist = 561`

  - `PerkEducated = 562`

  - `PerkHealer = 563`

  - `PerkFortuneFinder = 564`

  - `PerkBetterCriticals = 565`

  - `PerkEmpathy = 566`

  - `PerkSlayer = 567`

  - `PerkSniper = 568`

  - `PerkSilentDeath = 569`

  - `PerkActionBoy = 570`

  - `PerkMentalBlock = 571`

  - `PerkLifegiver = 572`

  - `PerkDodger = 573`

  - `PerkSnakeater = 574`

  - `PerkMrFixit = 575`

  - `PerkMedic = 576`

  - `PerkMasterThief = 577`

  - `PerkSpeaker = 578`

  - `PerkHeaveHo = 579`

  - `PerkFriendlyFoe = 580`

  - `PerkPickpocket = 581`

  - `PerkGhost = 582`

  - `PerkCultOfPersonality = 583`

  - `PerkScrounger = 584`

  - `PerkExplorer = 585`

  - `PerkFlowerChild = 586`

  - `PerkPathfinder = 587`

  - `PerkAnimalFriend = 588`

  - `PerkScout = 589`

  - `PerkMysteriousStranger = 590`

  - `PerkRanger = 591`

  - `PerkSmoothTalker = 592`

  - `PerkSwiftLearner = 593`

  - `PerkTag = 594`

  - `PerkMutate = 595`

  - `PerkAdrenalineRush = 596`

  - `PerkCautiousNature = 597`

  - `PerkComprehension = 598`

  - `PerkDemolitionExpert = 599`

  - `PerkGambler = 600`

  - `PerkGainStrength = 601`

  - `PerkGainPerception = 602`

  - `PerkGainEndurance = 603`

  - `PerkGainCharisma = 604`

  - `PerkGainIntelligence = 605`

  - `PerkGainAgility = 606`

  - `PerkGainLuck = 607`

  - `PerkHarmless = 608`

  - `PerkHereAndNow = 609`

  - `PerkHthEvade = 610`

  - `PerkKamaSutraMaster = 611`

  - `PerkKarmaBeacon = 612`

  - `PerkLightStep = 613`

  - `PerkLivingAnatomy = 614`

  - `PerkMagneticPersonality = 615`

  - `PerkNegotiator = 616`

  - `PerkPackRat = 617`

  - `PerkPyromaniac = 618`

  - `PerkQuickRecovery = 619`

  - `PerkSalesman = 620`

  - `PerkStonewall = 621`

  - `PerkThief = 622`

  - `PerkWeaponHandling = 623`

  - `PerkVaultCityTraining = 624`

  - `PerkExpertExcrement = 625`

  - `PerkTerminator = 626`

  - `PerkGeckoSkinning = 627`

  - `PerkVaultCityInoculations = 628`

  - `PerkDermalImpact = 629`

  - `PerkDermalImpactEnh = 630`

  - `PerkPhoenixImplants = 631`

  - `PerkPhoenixImplantsEnh = 632`

  - `PerkNcrPerception = 633`

  - `PerkNcrEndurance = 634`

  - `PerkNcrBarter = 635`

  - `PerkNcrRepair = 636`

  - `PerkVampireAccuracy = 637`

  - `PerkVampireRegeneration = 638`

  - `PerkQuickPockets = 639`

  - `PerkMasterTrader = 640`

  - `PerkSilentRunning = 641`

  - `PerkBonusMove = 642`

  - `KarmaPerkBerserker = 643`

  - `KarmaPerkChampion = 644`

  - `KarmaPerkChildkiller = 645`

  - `KarmaPerkSexpert = 646`

  - `KarmaPerkPrizefighter = 647`

  - `KarmaPerkGigolo = 648`

  - `KarmaPerkGraveDigger = 649`

  - `KarmaPerkMarried = 650`

  - `KarmaPerkPornStar = 651`

  - `KarmaPerkSlaver = 652`

  - `KarmaPerkVirginWastes = 653`

  - `KarmaPerkManSalvatore = 654`

  - `KarmaPerkManBishop = 655`

  - `KarmaPerkManMordino = 656`

  - `KarmaPerkManWright = 657`

  - `KarmaPerkSeparated = 658`

  - `KarmaPerkPedobear = 659`

  - `KarmaPerkVcGuardsman = 660`

  - `IsTraitFastMetabolism = 661`

  - `IsTraitBruiser = 662`

  - `IsTraitSmallFrame = 663`

  - `IsTraitOneHander = 664`

  - `IsTraitFinesse = 665`

  - `IsTraitKamikaze = 666`

  - `IsTraitHeavyHanded = 667`

  - `IsTraitFastShot = 668`

  - `IsTraitBloodyMess = 669`

  - `IsTraitJinxed = 670`

  - `IsTraitJinxedII = 671`

  - `IsTraitGoodNatured = 672`

  - `IsTraitChemReliant = 673`

  - `IsTraitChemResistant = 674`

  - `IsTraitSexAppeal = 675`

  - `IsTraitSkilled = 676`

  - `IsTraitNightPerson = 677`

  - `TimeoutSkFirstAid = 678`

  - `TimeoutSkDoctor = 679`

  - `TimeoutSkRepair = 680`

  - `TimeoutSkScience = 681`

  - `TimeoutSkLockpick = 682`

  - `TimeoutSkSteal = 683`

  - `TimeoutSkOutdoorsman = 684`

  - `TimeoutRemoveFromGame = 685`

  - `TimeoutReplication = 686`

  - `TimeoutKarmaVoting = 687`

  - `TimeoutSneak = 688`

  - `TimeoutHealing = 689`

  - `TimeoutStealing = 690`

  - `TimeoutAggressor = 691`

  - `MercMasterId = 692`

  - `MercAlwaysRun = 693`

  - `MercCancelOnAttack = 694`

  - `MercLoseDist = 695`

  - `MercMasterDist = 696`

  - `MercType = 697`

  - `MercDefendMaster = 698`

  - `MercAssistMaster = 699`

  - `MercCancelTime = 700`

  - `MercCancelOnGlobal = 701`

  - `MercWaitForMaster = 702`

  - `ArroyoMynocDefence = 703`

  - `ArroyoCassidyLetter = 704`

  - `ArroyoMynocOil = 705`

  - `ArroyoProofOfDeath = 706`

  - `ArroyoLetterToLinnett = 707`

  - `KlamSallyFindProstitute = 708`

  - `KlamBobWater = 709`

  - `KlamFindTrappers = 710`

  - `KlamBugenLure = 711`

  - `KlamNotifyHusband = 712`

  - `KlamEidenBramin = 713`

  - `KlamSmilyModoc = 714`

  - `DenBillRacingWin = 715`

  - `DenLeannaCondom = 716`

  - `QDenAnanDoll = 717`

  - `DenAnanRedoll = 718`

  - `DenGhost = 719`

  - `DenBillRacingOpening = 720`

  - `DenCarstopJeffry = 721`

  - `DenCarstopBrahmin = 722`

  - `DenCarstopBreeder = 723`

  - `DenJoeySteal = 724`

  - `DenJaneDolg = 725`

  - `DenJanePsycho = 726`

  - `DenLaraPostal = 727`

  - `DenFlikJet = 728`

  - `DenLaraBand = 729`

  - `DenJoeyLoan = 730`

  - `DenLaraBos = 731`

  - `QDenCliffDealer = 732`

  - `DenFredStim = 733`

  - `DenJaneVodka = 734`

  - `DenMomSlut = 735`

  - `DenSmittyBatt = 736`

  - `DenJaneMeat = 737`

  - `DenJaneStim = 738`

  - `DenLaraMolotovCoctail = 739`

  - `DenLeannaBuy = 740`

  - `DenSmittyBoots = 741`

  - `DenJaneGuns = 742`

  - `DenSmittyKey = 743`

  - `DenJaneArmor = 744`

  - `DenSmittyAmmo = 745`

  - `DenJaneHunt = 746`

  - `DenJoeyKnife = 747`

  - `DenJoeyLara = 748`

  - `DenJaneRadio = 749`

  - `DenJoeyJet = 750`

  - `DenLaraTrust = 751`

  - `DenLeannaWine = 752`

  - `DenMomRadscorp = 753`

  - `DenSmittyFixit = 754`

  - `QDenLeannaThief = 755`

  - `ModJoeFarm = 756`

  - `ModHose = 757`

  - `ModBaltasGecko = 758`

  - `ModLourenceRatsColony = 759`

  - `ModLourenceFloater = 760`

  - `ModJoeVampire = 761`

  - `BHMarcusEscort = 762`

  - `BHSuperNewTechnology = 763`

  - `ReddDocRadio = 764`

  - `ReddDocRadioTroy = 765`

  - `ReddDocRadioFung = 766`

  - `ReddDocRadioHoliday = 767`

  - `ReddDocRadioJubiley = 768`

  - `ReddHubbChildkiller = 769`

  - `ReddMarionVinamingo = 770`

  - `ReddDoctorDelivery = 771`

  - `NavHenryProtoMaterials = 772`

  - `NavSoftJob = 773`

  - `NcrHatePatrol = 774`

  - `NcrSantiagaFindSpyStatus = 775`

  - `NcrBusterBrokenrifles = 776`

  - `NcrKessMedBoardStatus = 777`

  - `NcrDorotyFindHenryPapers = 778`

  - `NcrLeadSmit2Dustybar = 779`

  - `NcrKyleReddRecon = 780`

  - `NcrDuppoFindDasies = 781`

  - `NcrDappoLostC = 782`

  - `QChosen = 783`

  - `NRBarmenEscort = 784`

  - `SFAhs7ImperatorFormat = 785`

  - `SFEvaHelpWithZax = 786`

  - `SFKenliImperatorRestore = 787`

  - `SFLoPanBlackmail = 788`

  - `SFTigangRecipe = 789`

  - `SFNarcoman = 790`

  - `SFAhs7Invitations = 791`

  - `SFSlimSidnancy = 792`

  - `VCLetterToTodd = 793`

  - `VCValeryMail = 794`

  - `VCCindyLetter = 795`

  - `VCHartmannRecon = 796`

  - `VCHartmanNcrHelp = 797`

  - `VCBarmenDelivery = 798`

  - `VCCharlie = 799`

  - `VCTroyFreshBlood = 800`

  - `VCAndrewDeliveries = 801`

  - `VCBlackEscort = 802`

  - `VCHartmanFight = 803`

  - `VCLynettScareNewcomers = 804`

  - `VCHartmanRifles = 805`

  - `VCHeleneTroyBeauty = 806`

  - `TribSulikStuff = 807`

  - `TribMuscoTest = 808`

  - `TribShamanPowder = 809`

  - `TribMaiaraBook = 810`

  - `TribManotaNecklace = 811`

  - `BHDeadSaboteursCounter = 812`

  - `SpecialAndroid = 813`

  - `VCLynettRefuse = 814`

  - `DialogTimeout = 815`

  - `EncLoyalityHubologists = 816`

  - `EncLoyalityNcr = 817`

  - `EncLoyalityVCity = 818`

  - `EncLoyalityRedding = 819`

  - `EncLoyalityBroken = 820`

  - `EncLoyalityGecko = 821`

  - `EncLoyalityArroyo = 822`

  - `EncLoyalityKlamath = 823`

  - `EncLoyalityModoc = 824`

  - `EncLoyalityDen = 825`

  - `EncLoyalityReno = 826`

  - `EncLoyalityEnclave = 827`

  - `EncLoyalitySf = 828`

  - `ModLourenceToxinRecipe = 829`

  - `SFChitinArmorRecipeKnown = 830`

  - `SpyCathActive = 831`

  - `HasNotCard = 832`

  - `SexExp = 833`

  - `ScenFraction = 834`

  - `ArroyoDocHealing = 835`

  - `AtollTesla = 836`

  - `AtollMoney = 837`

  - `BHEscortNpcId = 838`

  - `ScenBosSoldier = 839`

  - `SFInvasionBadge = 840`

  - `ScenBosScriber = 841`

  - `ScenEnclaveSoldier = 842`

  - `ScenEnclaveScient = 843`

  - `DenJaneTraderFred = 844`

  - `DenJaneJobCounter = 845`

  - `DenJoeyCounter = 846`

  - `DenLaraBosCounter = 847`

  - `DenJaneTraderMom = 848`

  - `DenNarcCommMember = 849`

  - `DenJaneTraderLean = 850`

  - `EncOceanTraderFamiliar = 851`

  - `ModBaltasArmor1 = 852`

  - `GeckGaroldTrain = 853`

  - `GeckSkitrTransit = 854`

  - `KlamBaknerBeer = 855`

  - `ModBaltasArmor = 856`

  - `KlamVaccination = 857`

  - `KlamVaccinationB1 = 858`

  - `KlamVaccinationB2 = 859`

  - `KlamVaccinationB3 = 860`

  - `KlamGoldBeer = 861`

  - `KlamSallyPay = 862`

  - `ModBaltasArmor2 = 863`

  - `KlamVicFixittrash = 864`

  - `ModHoseTools = 865`

  - `ModVampireReaction = 866`

  - `NcrAlexQuestStatus = 867`

  - `NcrDustyPartyStatusChar = 868`

  - `NcrMiraTroubleStatusChar = 869`

  - `NcrBeggarTalk = 870`

  - `NcrDorothyGammaStatusChar = 871`

  - `NcrDumontBrkradioStatusChar = 872`

  - `NcrCaptainFlirtStatusChar = 873`

  - `NcrIsNightGuardAccessFranted = 874`

  - `NcrClausHistory = 875`

  - `NcrJubileyTailsStatus = 876`

  - `NcrRondoDorotyStatus = 877`

  - `NcrFergusStory = 878`

  - `NcrCaptainSmitAccessGranted = 879`

  - `NcrJubileyTailsCounter = 880`

  - `NcrBusterDorotyStatus = 881`

  - `NcrFergusSecret = 882`

  - `NcrGunterStory = 883`

  - `ScenRangerRank = 884`

  - `NcrDustyFoodDeliveryStatus = 885`

  - `NcrPlayerLeadSmit2Dustybar = 886`

  - `NcrKarlStory = 887`

  - `NcrCarlsonStory = 888`

  - `NcrKukComp = 889`

  - `NcrMicQStatus = 890`

  - `ScenRanger = 891`

  - `NcrDumontHistory = 892`

  - `NcrMicQCptnDumbCounter = 893`

  - `NcrPlayerHasMultipass = 894`

  - `NcrSmitVsVestinResult = 895`

  - `NRJukeboxSeen = 896`

  - `VCTrainigAccess = 897`

  - `NcrLennyFight = 898`

  - `NcrRatchPlayerPoints = 899`

  - `NRJesusTrain = 900`

  - `PurgSuppluysTaken = 901`

  - `NcrWestinPillsStatus = 902`

  - `NcrWestinPlayerGetPrepayment = 903`

  - `SFHubJudgementIgnatStory = 904`

  - `ReddMinesPlayerThief = 905`

  - `ReddDocMedicals = 906`

  - `NcrWestinPills = 907`

  - `SFHubbStatus = 908`

  - `SFInvasionSandbagsTaken = 909`

  - `SFInvasionSandbagsGiven = 910`

  - `SFImperatorCancelNum = 911`

  - `VCShiComputerAccess = 912`

  - `TribManotaStory = 913`

  - `VCKnowsAboutDelivery = 914`

  - `VCCitizenship = 915`

  - `VCHartmanFightStatus = 916`

  - `VCFreshBloodCounter = 917`

  - `VCForgeryWitnessInhome = 918`

  - `VCLynetOrMaclure = 919`

  - `VCMutCharleyHired = 920`

  - `VCCavesCounter = 921`

  - `VCPrisonerBulled = 922`

  - `VCLynettTalk = 923`

  - `VCPatrolCounter = 924`

  - `NpcDialogTimeWait = 925`

  - `KlamTrappersRadaway = 926`

  - `HoloInfo = 927`

  - `FavoriteItemPid = 928`

  - `IsNoFavoriteItem = 929`

  - `Level = 930`

  - `KarmaVoting = 931`

  - `IsNoPvp = 932`

  - `IsEndCombat = 933`

  - `IsDlgScriptBarter = 934`

  - `IsUnlimitedAmmo = 935`

  - `IsNoDrop = 936`

  - `IsNoLooseLimbs = 937`

  - `IsDeadAges = 938`

  - `IsNoHeal = 939`

  - `IsInvulnerable = 940`

  - `IsSpecialDead = 941`

  - `IsRangeHth = 942`

  - `IsNoKnock = 943`

  - `IsNoSupply = 944`

  - `IsNoKarmaOnKill = 945`

  - `IsBarterOnlyCash = 946`

  - `BarterCoefficient = 947`

  - `TransferType = 948`

  - `TransferContainerId = 949`

  - `IsNoBarter = 950`

  - `IsNoSteal = 951`

  - `IsNoLoot = 952`

  - `IsNoPush = 953`

  - `ItemsWeight = 954`

  - `ActionPoints = 955`

  - `CurrentAp = 956`

  - `BagId = 957`

  - `LastWeaponId = 958`

  - `LastWeaponNotFound = 959`

  - `HandsProtoItemId = 960`

  - `HandsItemMode = 961`

  - `LastWeaponUse = 962`

  - `IsNoItemGarbager = 963`

  - `TownSupplyVictimId = 964`

  - `TownSupplyHostileId = 965`

  - `TravellerRoute = 966`

  - `V13Dclaw = 967`

  - `VCAmandaHelpJoshua = 968`

  - `VCMailRemembered = 969`

  - `VCBeautyHoloRemembered = 970`

  - `VCityCommonBarkusTimeSay = 971`

  - `SquadMarchSquads = 972`

  - `SquadMarchQueue = 973`

  - `VCHartmanMarch = 974`

  - `VCHartmannClearCave = 975`

  - `VCDeadAllyCounter = 976`

  - `VCGuardRank = 977`

  - `VCReconCaveId = 978`

  - `VCGuardsmanTriggerPlayerId = 979`

  - `VCLynettArest = 980`

  - `VCLynettForgery = 981`

  - `VCLynettPrisonerId = 982`

  - `ReddingMortonBrothers = 983`

  - `SpecialEncounterBaxChurch = 984`

  - `SpecialEncounteTim = 985`

  - `RacingSneakersTrap = 986`

  - `SpecialEncounterBridge = 987`

  - `SpecialEncounterHoly1 = 988`

  - `SpecialEncounterHoly2 = 989`

  - `SpecialEncounterToxic = 990`

  - `SpecialEncounterPariah = 991`

  - `SpecialEncounterBrahmin = 992`

  - `SpecialEncounterWhale = 993`

  - `SpecialEncounterHead = 994`

  - `SpecialEncounterShuttle = 995`

  - `SpecialEncounterGuardian = 996`

  - `SpecialEncounterWoodsman = 997`

  - `SpecialEncounterUnwashed = 998`

  - `SpecialEncounterTeleport = 999`

  - `SpecialWastelandChildren = 1000`

  - `SpecialEncounterKotw = 1001`

  - `SpecialSoldierHolo = 1002`

  - `SpecialTrapperHolo = 1003`

  - `SpecialDollHolo = 1004`

  - `SpecialEncounterZergLaboratory = 1005`

  - `SpecialEncounterDoughnutWarehouse = 1006`

  - `SpecialEncounterAtomChurch = 1007`

  - `GeckoFindWoody = 1008`

  - `NcrDappoLostCCtatus = 1009`

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

  - `VCLastBarDialog = 50`

  - `WarehouseTurretActive = 51`

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
