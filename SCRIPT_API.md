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

* `any CursorData (client only)`

  ...

* `CursorType DraggableCursor (client only)`

  ...

* `bool MsgboxInvert (client only)`

  ...

* `uint CombatMessagesType (client only)`

  ...

* `uint GlobalMapGroupMaxCount = 6`

  Макс размер группы

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

* `bool ForceBakering = false`

  ...

* `string BakeOutput = `

  ...

* `string[] BakeResourceEntries = `

  ...

* `string[] BakeContentEntries = `

  ...

* `string[] BakeExtraFileExtensions = fopts, fofnt, bmfc, fnt, acm, ogg, wav, ogv, json, ini, lfspine`

  Todo: move resource files control (include/exclude/pack rules) to cmake


### Critter

  ...

* `const bool[] CritterSlotEnabled = true, true, true`

  ...

* `const bool[] CritterSlotSendData = true, false, true`

  ...

* `const bool[] CritterSlotMultiItem = true, false, false`

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


## Game entity

  ...

* `Target: Server/Client`
* `Built-in: Yes`
* `Singleton: Yes`
* `Has proto: No`
* `Has statics: No`
* `Has abstract: No`

### Game properties

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

* `PrivateServer int8 KlamTrappersRadaway`

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

* `OnCritterCheckMoveItem(Critter cr, Item item, CritterItemSlot toSlot)`

  ...

* `OnCritterMoveItem(Critter cr, Item item, CritterItemSlot fromSlot)`

  ...

* `OnCritterTalk(Critter cr, Critter playerCr, bool begin, uint talkers)`

  ...

* `OnCritterBarter(Critter cr, Critter playerCr, bool begin, uint barterCount)`

  ...

* `OnCritterGetAttackDistantion(Critter cr, AbstractItem item, uint8 itemMode, uint& dist)`

  ...

* `OnItemInit(Item item, bool firstTime)`

  ...

* `OnItemFinish(Item item)`

  ...

* `OnItemCheckMove(Item item, uint count, Entity from, Entity to)`

  ...

* `OnStaticItemWalk(StaticItem item, Critter cr, bool isIn, uint8 dir)`

  ...

* `OnItemStackChanged(Item item, int countDiff)`

  ...

* `OnCritterPickItem(Critter cr, Item item)`

  ...

* `OnCritterPickScenery(Critter cr, StaticItem scenery)`

  ...

* `OnCritterRespawn(Critter critter)`

  ...

* `OnCritterKnockout(Critter critter)`

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

* `OnCritterCheckMoveItemEx(Critter cr, Item item, CritterItemSlot toSlot)`

  ...

* `OnItemCheckMoveEx(Item cr, uint count, Entity from, Entity to)`

  ...

* `OnCritterGetUseApCost(Critter cr, AbstractItem item, uint8 itemMode, uint& apCost)`

  ...

* `OnCritterGetAttackDistantionEx(Critter cr, AbstractItem item, uint8 itemMode, uint& dist)`

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

* `OnItemInvAllIn()`

  ...

* `OnItemInvIn(Item item)`

  ...

* `OnItemInvChanged(Item item, Item oldItem)`

  ...

* `OnItemInvOut(Item item)`

  ...

* `OnMapLoad()`

  ...

* `OnMapUnload()`

  ...

* `OnReceiveItems(Item[] items, int param)`

  ...

* `OnMapMessage(string& text, uint16& hexX, uint16& hexY, ucolor& color, uint& delay)`

  ...

* `OnInMessage(string text, int& sayType, ident crId, uint& delay)`

  ...

* `OnOutMessage(string& text, int& sayType)`

  ...

* `OnMessageBox(int type, string text)`

  ...

* `OnItemCheckMove(Item item, uint count, Entity from, Entity to)`

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

* `OnCritterCheckMoveItem(Critter cr, Item item, CritterItemSlot toSlot)`

  ...

* `OnCritterGetAttackDistantion(Critter cr, AbstractItem item, uint8 itemMode, uint& dist)`

  ...

* `OnScreenSizeChanged()`

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

* `OnCritterCheckMoveItemEx(Critter cr, Item item, CritterItemSlot toSlot)`

  ...

* `OnItemCheckMoveEx(Item cr, uint count, Entity from, Entity to)`

  ...

* `OnCritterGetUseApCost(Critter cr, AbstractItem item, uint8 itemMode, uint& apCost)`

  ...

* `OnCritterGetAttackDistantionEx(Critter cr, AbstractItem item, uint8 itemMode, uint& dist)`

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

* `uint DecodeUTF8(string text, uint& length)`

  ...  
  param text ...  
  param length ...  
  return ...

* `string EncodeUTF8(uint ucs)`

  ...  
  param ucs ...  
  return ...

* `string SHA1(string text)`

  ...  
  param text ...  
  return ...

* `string SHA2(string text)`

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

* `void MoveItem(Item item, uint count, Critter toCr)`

  ...  
  param item ...  
  param count ...  
  param toCr ...

* `void MoveItem(Item item, uint count, Critter toCr, bool skipChecks)`

  ...  
  param item ...  
  param count ...  
  param toCr ...  
  param skipChecks ...

* `void MoveItem(Item item, uint count, Map toMap, uint16 toHx, uint16 toHy)`

  ...  
  param item ...  
  param count ...  
  param toMap ...  
  param toHx ...  
  param toHy ...

* `void MoveItem(Item item, uint count, Map toMap, uint16 toHx, uint16 toHy, bool skipChecks)`

  ...  
  param item ...  
  param count ...  
  param toMap ...  
  param toHx ...  
  param toHy ...  
  param skipChecks ...

* `void MoveItem(Item item, uint count, Item toCont, ContainerItemStack stackId)`

  ...  
  param item ...  
  param count ...  
  param toCont ...  
  param stackId ...

* `void MoveItem(Item item, uint count, Item toCont, ContainerItemStack stackId, bool skipChecks)`

  ...  
  param item ...  
  param count ...  
  param toCont ...  
  param stackId ...  
  param skipChecks ...

* `void MoveItems(Item[] items, Critter toCr)`

  ...  
  param items ...  
  param toCr ...

* `void MoveItems(Item[] items, Critter toCr, bool skipChecks)`

  ...  
  param items ...  
  param toCr ...  
  param skipChecks ...

* `void MoveItems(Item[] items, Map toMap, uint16 toHx, uint16 toHy)`

  ...  
  param items ...  
  param toMap ...  
  param toHx ...  
  param toHy ...

* `void MoveItems(Item[] items, Map toMap, uint16 toHx, uint16 toHy, bool skipChecks)`

  ...  
  param items ...  
  param toMap ...  
  param toHx ...  
  param toHy ...  
  param skipChecks ...

* `void MoveItems(Item[] items, Item toCont, ContainerItemStack stackId)`

  ...  
  param items ...  
  param toCont ...  
  param stackId ...

* `void MoveItems(Item[] items, Item toCont, ContainerItemStack stackId, bool skipChecks)`

  ...  
  param items ...  
  param toCont ...  
  param stackId ...  
  param skipChecks ...

* `void DeleteItem(Item item)`

  ...  
  param item ...

* `void DeleteItem(Item item, uint count)`

  ...  
  param item ...  
  param count ...

* `void DeleteItem(ident itemId)`

  ...  
  param itemId ...

* `void DeleteItem(ident itemId, uint count)`

  ...  
  param itemId ...  
  param count ...

* `void DeleteItems(Item[] items)`

  ...  
  param items ...

* `void DeleteItems(ident[] itemIds)`

  ...  
  param itemIds ...

* `void DeleteCritter(Critter cr)`

  ...  
  param cr ...

* `void DeleteCritter(ident crId)`

  ...  
  param crId ...

* `void DeleteCritters(Critter[] critters)`

  ...  
  param critters ...

* `void DeleteCritters(ident[] critterIds)`

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

* `void EvaluateGameTime(tick_t fullSecond, uint16& year, uint16& month, uint16& day, uint16& dayOfWeek, uint16& hour, uint16& minute, uint16& second)`

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

* `void DeleteLocation(Location loc)`

  ...  
  param loc ...

* `void DeleteLocation(ident locId)`

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

* `void EraseTextListener(int sayType, string firstStr, int parameter)`

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

* `bool CallStaticItemFunction(Critter cr, StaticItem staticItem, Item usedItem, int param)`

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
  param imageSlot ...  
  param imageName ...

* `uint GetImageColor(int imageSlot, int x, int y)`

  ...  
  param imageSlot ...  
  param x ...  
  param y ...  
  return ...

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

* `Critter GetCritter(ident critterId) ExcludeInSingleplayer`

  ...  
  param critterId ...  
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

* `void EvaluateGameTime(tick_t fullSecond, uint16& year, uint16& month, uint16& day, uint16& dayOfWeek, uint16& hour, uint16& minute, uint16& second) ExcludeInSingleplayer`

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

* `PrivateServer hstring InitScript ScriptFuncType = ItemInit`

  ...

* `PrivateServer hstring SceneryScript ScriptFuncType = ItemScenery`

  ...

* `PrivateServer hstring TriggerScript ScriptFuncType = ItemTrigger`

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

* `Public hstring PicMap Resource`

  ...

* `Public hstring PicInv Resource`

  ...

* `Public bool Opened`

  ...

* `Public int16 OffsetX`

  ...

* `Public int16 OffsetY`

  ...

* `PrivateCommon float FlyEffectSpeed ReadOnly`

  ...

* `PrivateCommon bool Stackable ReadOnly`

  ...

* `PrivateCommon bool GroundLevel ReadOnly`

  ...

* `PrivateCommon CornerType Corner ReadOnly`

  ...

* `PrivateCommon uint Weight ReadOnly`

  ...

* `PrivateCommon uint Volume ReadOnly`

  ...

* `PrivateCommon bool DisableEgg ReadOnly`

  ...

* `PrivateCommon int8 DrawOrderOffsetHexY ReadOnly`

  ...

* `PrivateCommon uint8[] BlockLines ReadOnly`

  ...

* `PrivateCommon bool IsStatic ReadOnly`

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

* `PrivateCommon bool IsCanOpen ReadOnly`

  ...

* `PrivateCommon bool IsScrollBlock ReadOnly`

  ...

* `PrivateServer bool IsHidden`

  ...

* `PrivateClient bool HideSprite`

  ...

* `PrivateCommon bool AlwaysHideSprite ReadOnly`

  ...

* `PrivateCommon bool IsHiddenInStatic ReadOnly`

  ...

* `PrivateCommon bool IsFlat ReadOnly`

  ...

* `Public bool IsNoBlock`

  ...

* `Public bool IsShootThru`

  ...

* `Public bool IsLightThru`

  ...

* `Public bool IsAlwaysView`

  ...

* `Public bool IsBadItem`

  ...

* `Public bool IsNoHighlight`

  ...

* `Public bool IsShowAnim`

  ...

* `Public bool IsShowAnimExt`

  ...

* `Public bool IsLight`

  ...

* `Public bool IsGeck ReadOnly`

  ...

* `Public bool IsTrap`

  ...

* `Public bool IsTrigger`

  ...

* `Public bool IsNoLightInfluence`

  ...

* `Public bool IsGag`

  ...

* `Public bool IsColorize`

  ...

* `Public bool IsColorizeInv`

  ...

* `Public bool IsCanTalk`

  ...

* `Public bool IsRadio`

  ...

* `Public string Lexems`

  ...

* `PublicModifiable int16 SortValue`

  ...

* `Public int8 LightIntensity`

  ...

* `Public uint8 LightDistance`

  ...

* `Public uint8 LightFlags`

  ...

* `Public ucolor LightColor`

  ...

* `Public uint Count`

  ...

* `Protected int16 TrapValue`

  ...

* `Protected uint16 RadioChannel`

  ...

* `Protected uint16 RadioFlags`

  ...

* `Protected uint8 RadioBroadcastSend`

  ...

* `Protected uint8 RadioBroadcastRecv`

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

* `PrivateServer int[] SceneryParams`

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

* `OnCritterDrop(Critter critter)`

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

* `Item[] GetInnerItems() ExcludeInSingleplayer`

  ...  
  return ...

* `uint8 GetAlpha()`

  ...  
  return ...

## Critter entity

  ...

* `Target: Server/Client`
* `Built-in: Yes`
* `Singleton: No`
* `Has proto: Yes`
* `Has statics: No`
* `Has abstract: No`

### Critter properties

* `PrivateServer hstring InitScript ScriptFuncType = CritterInit`

  ...

* `PrivateClient string CustomName`

  ...

* `Public hstring ModelName`

  ...

* `Protected uint Multihex ReadOnly`

  ...

* `PrivateServer ident MapId ReadOnly`

  ...

* `Protected uint16 WorldX`

  ...

* `Protected uint16 WorldY`

  ...

* `PrivateServer uint GlobalMapTripId ReadOnly Temporary`

  ...

* `PrivateServer ident LastMapId ReadOnly`

  ...

* `PrivateServer hstring LastMapPid ReadOnly`

  ...

* `PrivateServer ident LastLocationId ReadOnly`

  ...

* `PrivateServer hstring LastLocationPid ReadOnly`

  ...

* `PrivateServer uint16 MapLeaveHexX ReadOnly`

  ...

* `PrivateServer uint16 MapLeaveHexY ReadOnly`

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

* `PrivateCommon CritterCondition Condition ReadOnly`

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

* `PrivateClient int16 NameOffset`

  ...

* `PrivateServer uint8[] GlobalMapFog ReadOnly`

  ...

* `VirtualPrivateServer uint SneakCoefficient`

  ...

* `VirtualProtected uint LookDistance`

  ...

* `Protected int ReplicationTime`

  ...

* `Public uint TalkDistance`

  ...

* `Public int ScaleFactor`

  ...

* `Public int CurrentHp`

  ...

* `PrivateServer uint MaxTalkers`

  ...

* `Public hstring DialogId`

  ...

* `Public string Lexems`

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

* `PrivateServer ident[] KnownLocations`

  ...

* `PrivateServer uint ShowCritterDist1`

  ...

* `PrivateServer uint ShowCritterDist2`

  ...

* `PrivateServer uint ShowCritterDist3`

  ...

* `Protected hstring[] KnownLocProtoId`

  ...

* `PrivateClient int[] ModelLayers Temporary`

  ...

* `Protected bool IsHide`

  ...

* `Protected bool IsNoHome`

  ...

* `Protected bool IsGeck`

  ...

* `Protected bool IsNoUnarmed`

  ...

* `Public bool IsNoTalk`

  ...

* `Public bool IsNoFlatten`

  ...

* `PrivateClient ucolor NameColor`

  ...

* `PrivateClient ucolor ContourColor`

  ...

* `PrivateServer any[] TE_Identifier ReadOnly`

  ...

* `PrivateServer tick_t[] TE_FireTime ReadOnly`

  ...

* `PrivateServer hstring[] TE_FuncName ReadOnly`

  ...

* `PrivateServer uint[] TE_Rate ReadOnly`

  ...

* `VirtualPrivateClient bool IsSexTagFemale`

  ...

* `VirtualPrivateClient bool IsModelInCombatMode`

  ...

* `PrivateServer uint IdlePeriod Temporary`

  ...

* `PrivateCommon bool IsControlledByPlayer ReadOnly Temporary`

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

* `OnDropItem(Item item)`

  ...

* `OnSomeCritterDropItem(Critter fromCr, Item item)`

  ...

* `OnSomeCritterMoveItem(Critter fromCr, Item item, uint8 itemMode)`

  ...

* `OnNpcPlaneBegin(int planeId, int reason, Critter someCr, Item someItem)`

  ...

* `OnNpcPlaneEnd(int planeId, int reason, Critter someCr, Item someItem)`

  ...

* `OnNpcPlaneRun(int planeId, int reason, any& result0, any& result1, any& result2)`

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

* `void DeleteItem(hstring pid)`

  ...  
  param pid ...

* `void DeleteItem(hstring pid, uint count)`

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

* `void UnsetKnownLocation(ident locId)`

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

* `void SendItems(Item[] items, int param)`

  ...  
  param items ...  
  param param ...

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

* `void ResetMovingState()`

  ...

* `void ResetMovingState(ident& gagId)`

  ...  
  param gagId ...

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

* `void EraseTimeEvent(uint index)`

  ...  
  param index ...

* `uint EraseTimeEvents(any identifier)`

  ...  
  param identifier ...  
  return ...

* `uint EraseTimeEvents(any[] identifiers)`

  ...  
  param identifiers ...  
  return ...

* `tick_t GetPlayerOfflineTime()`

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

* `PrivateServer hstring InitScript ScriptFuncType = MapInit`

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

* `PrivateClient string FileDir ReadOnly Temporary`

  ...

* `PrivateCommon uint16 Width ReadOnly`

  ...

* `PrivateCommon uint16 Height ReadOnly`

  ...

* `PrivateClient uint16 WorkHexX ReadOnly`

  ...

* `PrivateClient uint16 WorkHexY ReadOnly`

  ...

* `PrivateServer ident LocId ReadOnly`

  ...

* `PrivateServer uint LocMapIndex ReadOnly`

  ...

* `PrivateServer ident[] CritterIds ReadOnly`

  ...

* `PrivateServer ident[] ItemIds ReadOnly`

  ...

* `PrivateCommon uint8 RainCapacity`

  ...

* `PrivateCommon int CurDayTime`

  ...

* `PrivateCommon int[] DayTime`

  ...

* `PrivateCommon uint8[] DayColor`

  ...

* `PrivateServer bool IsNoLogOut`

  ...

* `PrivateClient float SpritesZoom ReadOnly`

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

* `Critter[] GetCrittersWhoViewPath(uint16 fromHx, uint16 fromHy, uint16 toHx, uint16 toHy, CritterFindType findType)`

  ...  
  param fromHx ...  
  param fromHy ...  
  param toHx ...  
  param toHy ...  
  param findType ...  
  return ...

* `Critter[] GetCrittersSeeing(Critter[] critters, bool lookOnThem, CritterFindType findType)`

  ...  
  param critters ...  
  param lookOnThem ...  
  param findType ...  
  return ...

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

## Location entity

  ...

* `Target: Server/Client`
* `Built-in: Yes`
* `Singleton: No`
* `Has proto: Yes`
* `Has statics: No`
* `Has abstract: No`

### Location properties

* `PrivateServer hstring InitScript ScriptFuncType = LocationInit`

  ...

* `PrivateServer ident[] MapIds ReadOnly`

  ...

* `PrivateServer hstring[] MapProtos ReadOnly`

  ...

* `PrivateServer hstring[] MapEntrances ReadOnly`

  ...

* `PrivateServer hstring[] Automaps ReadOnly`

  ...

* `PrivateServer bool AutoGarbage`

  ...

* `PrivateServer bool GeckVisible`

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

* `PrivateServer bool ToGarbage`

  ...

* `PrivateServer ucolor Color`

  ...

* `PrivateServer bool IsEncounter`

  ...

* `PrivateServer bool GECachesCacheChecked`

  ...

* `PrivateServer uint8 RacingCheckpointNumber Max = 14`

  ...

* `PrivateServer ident StorehouseContId`

  ...

* `PrivateServer uint MaxPlayers`

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

  - `PropogateException = 3`

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

  - `Locations = 4`

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

  - `KnockFront = 91`

  - `KnockBack = 92`

  - `StandupBack = 38`

  - `StandupFront = 30`

  - `Pickup = 21`

  - `Use = 22`

  - `DodgeEmpty = 14`

  - `Punch = 17`

  - `Kick = 18`

  - `ThrowEmpty = 19`

  - `Run = 20`

  - `DeadFront = 101`

  - `DeadBack = 102`

  - `DeadBloodySingle = 104`

  - `DeadBurn = 105`

  - `DeadBloodyBurst = 106`

  - `DeadBurst = 107`

  - `DeadPulse = 108`

  - `DeadLaser = 109`

  - `DeadBurn2 = 110`

  - `DeadPulseDust = 111`

  - `DeadExplode = 112`

  - `DeadFused = 113`

  - `DeadBurnRun = 114`

  - `DeadFront2 = 115`

  - `DeadBack2 = 116`

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

  - `Year = 0`

  - `Month = 1`

  - `Day = 2`

  - `Hour = 3`

  - `Minute = 4`

  - `Second = 5`

  - `TimeMultiplier = 6`

  - `LastEntityId = 7`

  - `LastDeferredCallId = 8`

  - `HistoryRecordsId = 9`

  - `LastGlobalMapTripId = 10`

  - `ArroyoMynocTimeout = 11`

  - `BaseSierraRule = 12`

  - `BaseMariposaRule = 13`

  - `BaseCathedralRule = 14`

  - `BaseSierraOrg = 15`

  - `BaseMariposaOrg = 16`

  - `BaseCathedralOrg = 17`

  - `BaseSierraTimeEventId = 18`

  - `BaseMariposaTimeEventId = 19`

  - `BaseCathedralTimeEventId = 20`

  - `BaseEnclaveScore = 21`

  - `BaseBosScore = 22`

  - `BulletinBoard = 23`

  - `DenGhostIsDead = 24`

  - `DenVirginIsAway = 25`

  - `GameEventManagerData = 26`

  - `GameEventData = 27`

  - `RacingWinnersFound = 28`

  - `RacingWinner = 29`

  - `LastGlobalMapTrip = 30`

  - `EndingV13DclawGenocide = 31`

  - `KlamCowboy = 32`

  - `KlamCowboyLevel = 33`

  - `KlamSmilyGeckoLocation = 34`

  - `KlamSmilyGeckoTimeout = 35`

  - `TribRaid = 36`

  - `PrimalTribeQuestPlayers = 37`

  - `MobWaveData = 38`

  - `NCRRanchBrahminIll = 39`

  - `NcrDustyOneHourInvokeId = 40`

  - `NcrDustyOneWeekInvokeId = 41`

  - `NCRDustyPartyStatusGlobal = 42`

  - `NCRDustyRotgutCounter = 43`

  - `NCRDustyBeerGammaCounter = 44`

  - `NCRInvasion = 45`

  - `NCRKessStageGlobal = 46`

  - `NcrSmitPosition = 47`

  - `NcrSmitGateGuardAccessGranted = 48`

  - `NcrWestinPositionGlobal = 49`

  - `RegProperties = 50`

  - `ReddMarionWanLocation = 51`

  - `ReddMarionWanTimeout = 52`

  - `ReddJohnsonBroadcast = 53`

  - `PermanentDeath = 54`

  - `BestScores = 55`

  - `BestScoreCritterIds = 56`

  - `BestScoreValues = 57`

  - `SFZax366StatusGlobal = 58`

  - `SFDevinHired = 59`

  - `MissilesCanada = 60`

  - `MissilesKishinev = 61`

  - `MissilesBaku = 62`

  - `MissilesTokio = 63`

  - `MissilesEburg = 64`

  - `MissilesVladik = 65`

  - `MissilesRay = 66`

  - `MissilesFukusima = 67`

  - `BestEScores = 68`

  - `ArroyoRaidersCount = 69`

  - `ArroyoLastDefenceGroup = 70`

  - `ArroyoMynocMap = 71`

  - `EncOceanTraderAlive = 72`

  - `GameEventCaches = 73`

  - `RacingEvent = 74`

  - `GEReplStationStatus = 75`

  - `NCRSiegeCampsNum = 76`

  - `SFBosArmourCounter = 77`

  - `SFInvasionStatus = 78`

  - `DenLeannaThief = 79`

  - `DenCliffDealer = 80`

  - `DenAnanDollUse = 81`

  - `KlamSmilyGeckoCounter = 82`

  - `KlamTrappersRadaway = 83`

  - `EndingArroyoTodd = 84`

  - `EndingV13DclawRevival = 85`

  - `GeckSkitrHired = 86`

  - `NRBbarmenHired = 87`

  - `NcrIsCurfewActive = 88`

  - `NcrMicGuaranteeCounter = 89`

  - `SFImperatorMemory = 90`

  - `GCityGeckSold = 91`

  - `VCBlackHired = 92`

  - `EndingV13DclawSaved = 93`

  - `VCHartmanMarchStatus = 94`

  - `RaidersDead = 95`

* `PlayerProperty`

  ...

  - `Invalid = 0xFFFF`

  - `ControlledCritterId = 0`

  - `LastControlledCritterId = 1`

  - `Password = 2`

  - `ConnectionIp = 3`

  - `ConnectionPort = 4`

  - `MainCritterId = 5`

* `ItemProperty`

  ...

  - `Invalid = 0xFFFF`

  - `InitScript = 0`

  - `SceneryScript = 1`

  - `TriggerScript = 2`

  - `Ownership = 3`

  - `MapId = 4`

  - `HexX = 5`

  - `HexY = 6`

  - `CritterId = 7`

  - `CritterSlot = 8`

  - `ContainerId = 9`

  - `ContainerStack = 10`

  - `InnerItemIds = 11`

  - `PicMap = 12`

  - `PicInv = 13`

  - `Opened = 14`

  - `OffsetX = 15`

  - `OffsetY = 16`

  - `FlyEffectSpeed = 17`

  - `Stackable = 18`

  - `GroundLevel = 19`

  - `Corner = 20`

  - `Weight = 21`

  - `Volume = 22`

  - `DisableEgg = 23`

  - `DrawOrderOffsetHexY = 24`

  - `BlockLines = 25`

  - `IsStatic = 26`

  - `IsScenery = 27`

  - `IsWall = 28`

  - `IsTile = 29`

  - `IsRoofTile = 30`

  - `TileLayer = 31`

  - `IsCanOpen = 32`

  - `IsScrollBlock = 33`

  - `IsHidden = 34`

  - `HideSprite = 35`

  - `AlwaysHideSprite = 36`

  - `IsHiddenInStatic = 37`

  - `IsFlat = 38`

  - `IsNoBlock = 39`

  - `IsShootThru = 40`

  - `IsLightThru = 41`

  - `IsAlwaysView = 42`

  - `IsBadItem = 43`

  - `IsNoHighlight = 44`

  - `IsShowAnim = 45`

  - `IsShowAnimExt = 46`

  - `IsLight = 47`

  - `IsGeck = 48`

  - `IsTrap = 49`

  - `IsTrigger = 50`

  - `IsNoLightInfluence = 51`

  - `IsGag = 52`

  - `IsColorize = 53`

  - `IsColorizeInv = 54`

  - `IsCanTalk = 55`

  - `IsRadio = 56`

  - `Lexems = 57`

  - `SortValue = 58`

  - `LightIntensity = 59`

  - `LightDistance = 60`

  - `LightFlags = 61`

  - `LightColor = 62`

  - `Count = 63`

  - `TrapValue = 64`

  - `RadioChannel = 65`

  - `RadioFlags = 66`

  - `RadioBroadcastSend = 67`

  - `RadioBroadcastRecv = 68`

  - `CarIsBioEngine = 69`

  - `CarIsNoLockpick = 70`

  - `CaravanCabLeaderId = 71`

  - `ELockCloseAtSeconds = 72`

  - `ELockCode = 73`

  - `ExplodeInvokeId = 74`

  - `ExplodeSwitcherExplodeId = 75`

  - `ExplodeOwnerId = 76`

  - `ExplodeBonusDamage = 77`

  - `ExplodeBonusRadius = 78`

  - `ExplodeTimeRespawnMine = 79`

  - `GECachesNumParameters = 80`

  - `GeigerEnabled = 81`

  - `GeigerCapacity = 82`

  - `GeigerTimeEvent = 83`

  - `QHunterCountFluteUse = 84`

  - `DoorAutoCloseTime = 85`

  - `DoorAutoDialog = 86`

  - `LockerId = 87`

  - `LockerComplexity = 88`

  - `Locker_Locked = 89`

  - `Locker_Jammed = 90`

  - `Locker_Broken = 91`

  - `Locker_NoOpen = 92`

  - `Locker_IsElectro = 93`

  - `Door_NoBlockMove = 94`

  - `Door_NoBlockShoot = 95`

  - `Door_NoBlockLight = 96`

  - `Container_Volume = 97`

  - `Container_Changeble = 98`

  - `Container_CannotPickUp = 99`

  - `Door_IsMultyHex = 100`

  - `Door_MultyHexLine1 = 101`

  - `Door_MultyHexLine2 = 102`

  - `Door_BlockerIds = 103`

  - `NavarroCountUseScaner = 104`

  - `NCRPostmanLocPidStart = 105`

  - `NCRPostmanLocPidRec = 106`

  - `NCRPostmanMapPidRec = 107`

  - `NCRPostmanNpcDidRec = 108`

  - `NCRPostmanPlayerID = 109`

  - `PetId = 110`

  - `PetProto = 111`

  - `PosterSNWall = 112`

  - `PosterEWWall = 113`

  - `RatGrenadeInvokeId = 114`

  - `ReddGatesGoodList = 115`

  - `ReddGatesBadList = 116`

  - `RespawnItemMode = 117`

  - `RespawnItemRespTime = 118`

  - `RespawnItemVarNum = 119`

  - `SeAndroidRadioListened = 120`

  - `SeAndroidVarNum = 121`

  - `SmokeGrenadeOwnerId = 122`

  - `Mode = 123`

  - `AnimHide0 = 124`

  - `AnimHide1 = 125`

  - `AnimShow0 = 126`

  - `AnimShow1 = 127`

  - `AnimStay0 = 128`

  - `AnimStay1 = 129`

  - `AnimWaitBase = 130`

  - `AnimWaitRndMax = 131`

  - `AnimWaitRndMin = 132`

  - `Armor_CrTypeMale = 133`

  - `Armor_CrTypeFemale = 134`

  - `Armor_AC = 135`

  - `Armor_Perk = 136`

  - `Armor_DRNormal = 137`

  - `Armor_DRLaser = 138`

  - `Armor_DRFire = 139`

  - `Armor_DRPlasma = 140`

  - `Armor_DRElectr = 141`

  - `Armor_DREmp = 142`

  - `Armor_DRExplode = 143`

  - `Armor_DTNormal = 144`

  - `Armor_DTLaser = 145`

  - `Armor_DTFire = 146`

  - `Armor_DTPlasma = 147`

  - `Armor_DTElectr = 148`

  - `Armor_DTEmp = 149`

  - `Armor_DTExplode = 150`

  - `Weapon_IsUnarmed = 151`

  - `Weapon_UnarmedTree = 152`

  - `Weapon_UnarmedPriority = 153`

  - `Weapon_UnarmedMinAgility = 154`

  - `Weapon_UnarmedMinUnarmed = 155`

  - `Weapon_UnarmedMinLevel = 156`

  - `Weapon_MaxAmmoCount = 157`

  - `Weapon_Caliber = 158`

  - `Weapon_DefaultAmmoPid = 159`

  - `Weapon_StateAnim = 160`

  - `Weapon_MinStrength = 161`

  - `Weapon_Perk = 162`

  - `Weapon_IsTwoHanded = 163`

  - `Weapon_ActiveUses = 164`

  - `Weapon_Skill_0 = 165`

  - `Weapon_Skill_1 = 166`

  - `Weapon_Skill_2 = 167`

  - `Weapon_PicUse_0 = 168`

  - `Weapon_PicUse_1 = 169`

  - `Weapon_PicUse_2 = 170`

  - `Weapon_MaxDist_0 = 171`

  - `Weapon_MaxDist_1 = 172`

  - `Weapon_MaxDist_2 = 173`

  - `Weapon_Round_0 = 174`

  - `Weapon_Round_1 = 175`

  - `Weapon_Round_2 = 176`

  - `Weapon_ApCost_0 = 177`

  - `Weapon_ApCost_1 = 178`

  - `Weapon_ApCost_2 = 179`

  - `Weapon_Aim_0 = 180`

  - `Weapon_Aim_1 = 181`

  - `Weapon_Aim_2 = 182`

  - `Weapon_SoundId_0 = 183`

  - `Weapon_SoundId_1 = 184`

  - `Weapon_SoundId_2 = 185`

  - `Weapon_DmgType_0 = 186`

  - `Weapon_DmgType_1 = 187`

  - `Weapon_DmgType_2 = 188`

  - `Weapon_ActionAnim_0 = 189`

  - `Weapon_ActionAnim_1 = 190`

  - `Weapon_ActionAnim_2 = 191`

  - `Weapon_DmgMin_0 = 192`

  - `Weapon_DmgMin_1 = 193`

  - `Weapon_DmgMin_2 = 194`

  - `Weapon_DmgMax_0 = 195`

  - `Weapon_DmgMax_1 = 196`

  - `Weapon_DmgMax_2 = 197`

  - `Weapon_Remove_0 = 198`

  - `Weapon_Remove_1 = 199`

  - `Weapon_Remove_2 = 200`

  - `Weapon_Effect_0 = 201`

  - `Weapon_Effect_1 = 202`

  - `Weapon_Effect_2 = 203`

  - `Weapon_ReloadAp = 204`

  - `Weapon_UnarmedCriticalBonus = 205`

  - `Weapon_CriticalFailture = 206`

  - `Weapon_UnarmedArmorPiercing = 207`

  - `Ammo_Caliber = 208`

  - `Ammo_AcMod = 209`

  - `Ammo_DrMod = 210`

  - `Ammo_DmgMult = 211`

  - `Ammo_DmgDiv = 212`

  - `Car_Speed = 213`

  - `Car_Passability = 214`

  - `Car_DeteriorationRate = 215`

  - `Car_CrittersCapacity = 216`

  - `Car_TankVolume = 217`

  - `Car_MaxDeterioration = 218`

  - `Car_FuelConsumption = 219`

  - `Car_Entrance = 220`

  - `Car_MovementType = 221`

  - `Deteriorable = 222`

  - `IsBroken = 223`

  - `BrokenEternal = 224`

  - `BrokenLowBroken = 225`

  - `BrokenNormBroken = 226`

  - `BrokenHighBroken = 227`

  - `BrokenNotresc = 228`

  - `BrokenService = 229`

  - `BrokenServiceExt = 230`

  - `BrokenCount = 231`

  - `Deterioration = 232`

  - `LockerCondition = 233`

  - `IsLockpick = 234`

  - `Lockpick_Points = 235`

  - `Lockpick_IsElectro = 236`

  - `IsHolodisk = 237`

  - `HolodiskNum = 238`

  - `IsNoLoot = 239`

  - `IsNoSteal = 240`

  - `Val0 = 241`

  - `Val1 = 242`

  - `Val2 = 243`

  - `Val3 = 244`

  - `Val4 = 245`

  - `Val5 = 246`

  - `Val6 = 247`

  - `Val7 = 248`

  - `Val8 = 249`

  - `Val9 = 250`

  - `ScriptModule = 251`

  - `ScriptFunc = 252`

  - `BrokenFlags = 253`

  - `Cost = 254`

  - `SoundId = 255`

  - `Material = 256`

  - `AmmoPid = 257`

  - `AmmoCount = 258`

  - `Info = 259`

  - `IsCanUseOnSmth = 260`

  - `IsCanUse = 261`

  - `IsCanPickUp = 262`

  - `LastUsedTime = 263`

  - `IsQuestItem = 264`

  - `Indicator = 265`

  - `IndicatorMax = 266`

  - `Charge = 267`

  - `IsCanLook = 268`

  - `IsWallTransEnd = 269`

  - `IsHasTimer = 270`

  - `IsBigGun = 271`

  - `IsMultiHex = 272`

  - `ChildPid_0 = 273`

  - `ChildPid_1 = 274`

  - `ChildPid_2 = 275`

  - `ChildPid_3 = 276`

  - `ChildPid_4 = 277`

  - `ChildLines_0 = 278`

  - `ChildLines_1 = 279`

  - `ChildLines_2 = 280`

  - `ChildLines_3 = 281`

  - `ChildLines_4 = 282`

  - `Type = 283`

  - `TriggerNum = 284`

  - `Container_MagicHandsGrnd = 285`

  - `Grid_Type = 286`

  - `Grid_ToMap = 287`

  - `Grid_ToMapEntry = 288`

  - `Grid_ToMapDir = 289`

  - `SceneryParams = 290`

  - `V13GorisEggPlayerId = 291`

  - `VCityCommonIsMail = 292`

  - `VCityCommonMailOwnerId = 293`

* `CritterProperty`

  ...

  - `Invalid = 0xFFFF`

  - `InitScript = 0`

  - `CustomName = 1`

  - `ModelName = 2`

  - `Multihex = 3`

  - `MapId = 4`

  - `WorldX = 5`

  - `WorldY = 6`

  - `GlobalMapTripId = 7`

  - `LastMapId = 8`

  - `LastMapPid = 9`

  - `LastLocationId = 10`

  - `LastLocationPid = 11`

  - `MapLeaveHexX = 12`

  - `MapLeaveHexY = 13`

  - `HexX = 14`

  - `HexY = 15`

  - `HexOffsX = 16`

  - `HexOffsY = 17`

  - `Dir = 18`

  - `DirAngle = 19`

  - `ItemIds = 20`

  - `Condition = 21`

  - `AliveStateAnim = 22`

  - `KnockoutStateAnim = 23`

  - `DeadStateAnim = 24`

  - `AliveActionAnim = 25`

  - `KnockoutActionAnim = 26`

  - `DeadActionAnim = 27`

  - `NameOffset = 28`

  - `GlobalMapFog = 29`

  - `SneakCoefficient = 30`

  - `LookDistance = 31`

  - `ReplicationTime = 32`

  - `TalkDistance = 33`

  - `ScaleFactor = 34`

  - `CurrentHp = 35`

  - `MaxTalkers = 36`

  - `DialogId = 37`

  - `Lexems = 38`

  - `HomeMapId = 39`

  - `HomeMapPid = 40`

  - `HomeHexX = 41`

  - `HomeHexY = 42`

  - `HomeDir = 43`

  - `KnownLocations = 44`

  - `ShowCritterDist1 = 45`

  - `ShowCritterDist2 = 46`

  - `ShowCritterDist3 = 47`

  - `KnownLocProtoId = 48`

  - `ModelLayers = 49`

  - `IsHide = 50`

  - `IsNoHome = 51`

  - `IsGeck = 52`

  - `IsNoUnarmed = 53`

  - `IsNoTalk = 54`

  - `IsNoFlatten = 55`

  - `NameColor = 56`

  - `ContourColor = 57`

  - `TE_Identifier = 58`

  - `TE_FireTime = 59`

  - `TE_FuncName = 60`

  - `TE_Rate = 61`

  - `IsSexTagFemale = 62`

  - `IsModelInCombatMode = 63`

  - `IdlePeriod = 64`

  - `IsControlledByPlayer = 65`

  - `IsChosen = 66`

  - `IsPlayerOffline = 67`

  - `IsAttached = 68`

  - `AttachMaster = 69`

  - `HideSprite = 70`

  - `ArroyoRaydersAttackedId = 71`

  - `BehemothOwner = 72`

  - `BehemothRadio = 73`

  - `BehemothLastComand = 74`

  - `BehemothOrderType = 75`

  - `BehemothLastOrder = 76`

  - `BehemothParam_1 = 77`

  - `BehemothParam_2 = 78`

  - `BehemothLastReport = 79`

  - `BHHubHoloRemembered = 80`

  - `BHUranDiscount = 81`

  - `BBMsgPage = 82`

  - `BBSelectedMsg = 83`

  - `KlamAldoBusy = 84`

  - `KlamAldoListenId = 85`

  - `KlamAldoReaderId = 86`

  - `BBMsgCount = 87`

  - `CaravanCrvId = 88`

  - `VCDeadPatrollers = 89`

  - `ReddWadeCaravanEscort = 90`

  - `ReddSavinelCaravanEscort = 91`

  - `ReddStanCaravanEscort = 92`

  - `NcrReddingCaravanEscort = 93`

  - `BHKitCaravanEscort = 94`

  - `VCShrimPatrol = 95`

  - `ArroyoSelmaCaravanEscort = 96`

  - `ArroyoGayzumCaravanEscort = 97`

  - `ArroyoLaumerCaravanEscort = 98`

  - `ModAurelianoCaravanEscort = 99`

  - `CommonCrvResetCounter = 100`

  - `ReddCrvResetCounter = 101`

  - `NcrCrvResetCounter = 102`

  - `BHCrvResetCounter = 103`

  - `ArroyoCrvResetCounter = 104`

  - `CaravanReaction = 105`

  - `CaravanNervosityLvl = 106`

  - `CaravanIdleCount = 107`

  - `LastSelectedCaravan = 108`

  - `ApRegenerationTick = 109`

  - `ApRegenerationTime = 110`

  - `CollectorTimeNextSearch = 111`

  - `CompRiddleMapId = 112`

  - `CompRiddleHexX = 113`

  - `CompRiddleHexY = 114`

  - `KnockoutAp = 115`

  - `ActionAnimKnockoutEnd = 116`

  - `NcrBusterLostCStatus = 117`

  - `QDappoLostRobotHexNum = 118`

  - `BankMoney = 119`

  - `DenHubBank5 = 120`

  - `DenHubGuard5 = 121`

  - `DenPoormanItemId = 122`

  - `DenVirginCount = 123`

  - `DenVirginIsHome = 124`

  - `UniqTimeout = 125`

  - `Loyality = 126`

  - `NpcStory = 127`

  - `NameMemNpcPlayer = 128`

  - `NameMemPlayerNpc = 129`

  - `TradeWas = 130`

  - `DenKliffBlessWas = 131`

  - `DenVirginiaSexWas = 132`

  - `NcrPlayerTalkPoliceman = 133`

  - `SFLoPanPayed = 134`

  - `ChanceOneFromTwo = 135`

  - `ChanceOneFromThree = 136`

  - `ChanceOneFromFive = 137`

  - `DrugEffects = 138`

  - `DoughnutsCounter = 139`

  - `LastElectronicLocked = 140`

  - `EliTimeNextSing = 141`

  - `EnemyStack = 142`

  - `IsNoEnemyStack = 143`

  - `EnergyBarierTerminalHx = 144`

  - `EnergyBarierTerminalHy = 145`

  - `EnergyBarierNetNum = 146`

  - `EnergyBarierHackBonus = 147`

  - `EnergyBarierHitBonus = 148`

  - `FighterPatternCanGenStim = 149`

  - `FighterPatternAllyAssistRadius = 150`

  - `FighterPatternAssistAlliesNum = 151`

  - `FighterPatternMustHealLvl = 152`

  - `FighterPatternLocalAlarmDeads = 153`

  - `FighterPatternGlobalAlarmDeads = 154`

  - `FighterQuestMinHp = 155`

  - `FighterQuestOnlyHandCombat = 156`

  - `FighterQuestTeamIdOld = 157`

  - `FighterQuestTeamIdFight = 158`

  - `FighterQuestPlayerId = 159`

  - `FighterQuestFightPriority = 160`

  - `FighterQuestVarNum = 161`

  - `FixboyPowerArmor = 162`

  - `ModLourenceVenomedratRecipe = 163`

  - `ModLourenceTNTRatRecipe = 164`

  - `NavEmpRocketRecipe = 165`

  - `FixboyDefault = 166`

  - `SFRecipeSsupersledge = 167`

  - `SFRecipePlasmagrenades = 168`

  - `Fixboy700NitroExpress = 169`

  - `FixboyAmmoPressOperator = 170`

  - `RacingCheckPoints = 171`

  - `RacingCheckpointLocId = 172`

  - `GERacingCritterHx = 173`

  - `GERacingCritterHy = 174`

  - `GERacingCritterDir = 175`

  - `GERacingNpcRole = 176`

  - `GERacingOpeningPhrases = 177`

  - `GEReplExplodeTank = 178`

  - `GEReplNopasaran = 179`

  - `GEReplFindstation = 180`

  - `GEReplNotifictions = 181`

  - `GEReplEntryZombie = 182`

  - `GEReplLastOrder = 183`

  - `GEReplIsAddedAttackPlane = 184`

  - `HellMineTimeoutEnd = 185`

  - `HostileLQIsStoped = 186`

  - `HostileLQData = 187`

  - `SFAhs7Escort = 188`

  - `SFHonomerPlayerId = 189`

  - `SFEscortLocation = 190`

  - `SFLabFailed = 191`

  - `QHubLabIsDialogRun = 192`

  - `BarterLourensRats1 = 193`

  - `ModLourenceRatsFlute = 194`

  - `BarterLourensRatBodycount = 195`

  - `ModHoughRatsFluteTimeout = 196`

  - `ModLourenceToxinTimeout = 197`

  - `ModLourenceRatsFluteCounter = 198`

  - `ModLourenceLureActive = 199`

  - `GuardedItemSkill = 200`

  - `V13DclawEggs = 201`

  - `KlamTorrCowboy = 202`

  - `KlamCowboyCountGav = 203`

  - `KlamCowboyMobHx = 204`

  - `KlamCowboyMobHy = 205`

  - `KlamDantonBramin = 206`

  - `KlamJosallDanton = 207`

  - `KlamKuklachev = 208`

  - `KlamSmilyGecko = 209`

  - `KlamSmilyCurrentHp = 210`

  - `KlamSmilyCountKills = 211`

  - `KlamSmilyHealing = 212`

  - `LimitedBarterData = 213`

  - `StealExpCount = 214`

  - `FirstAidCount = 215`

  - `MainQuest = 216`

  - `GCityCitizen = 217`

  - `MapGeckCityTraderSkillBarter = 218`

  - `MapKlamathRobotTimeNextSay = 219`

  - `ModJoeGiantWasp = 220`

  - `TribSulikRaid = 221`

  - `TribRaiderKillCount = 222`

  - `NCRElizeSlavers = 223`

  - `MapPrimalTribeRaiderHx = 224`

  - `MapPrimalTribeRaiderHy = 225`

  - `SFRonKillBeasts = 226`

  - `SFRonFindbodies = 227`

  - `SFTankerCentaurNoticed = 228`

  - `SFTankerFloaterNoticed = 229`

  - `MapSFTankerBicycleId = 230`

  - `MirelurkCombatCurStage = 231`

  - `MirelurkCombatTimeNextStage = 232`

  - `MirelurkCombatLastBrokenBag = 233`

  - `MirelurkCombatDestroyingItem = 234`

  - `MobAttackedId = 235`

  - `MobFury = 236`

  - `MobFear = 237`

  - `MobMaxFear = 238`

  - `ModVampireFarmLocation = 239`

  - `MonologueData = 240`

  - `NavHenryEmpTest = 241`

  - `NavEmpTestedCritter = 242`

  - `NavarroTimeOutScan = 243`

  - `NavarroChipUsedId = 244`

  - `NcrAlexHoloFindStatus = 245`

  - `NCRFelixFindBrahmin = 246`

  - `NCRHubBook = 247`

  - `NCRFelixSaveBrahmin = 248`

  - `NCRHubBookAccess1 = 249`

  - `NCRHubBookAccess2 = 250`

  - `NCRHubBookAccess3 = 251`

  - `NCRHubBookAccess4 = 252`

  - `NCRHubBookAccess5 = 253`

  - `NCRHubBookAccess6 = 254`

  - `NCRHubBookAccess7 = 255`

  - `NCRHubBookQuestTimeout = 256`

  - `NcrCommonBeggarInvokeId = 257`

  - `NcrCommonBeggarPhraseNum = 258`

  - `NcrCommonBeggarHideMoneyInvocation = 259`

  - `NcrCommonBrahminId = 260`

  - `QNcrElizeInvasion = 261`

  - `NCRKarlsonSon = 262`

  - `NcrSonCatcherId = 263`

  - `NcrSonMovesCounter = 264`

  - `NcrMichealMessageNum = 265`

  - `MailDelivery = 266`

  - `NcrMailRecieverId = 267`

  - `NcrMailTimeout = 268`

  - `NcrRatchBuggy = 269`

  - `NcrShaimanProtest = 270`

  - `NcrShaimanStringNum = 271`

  - `NcrSiegeTerminate = 272`

  - `NcrSiegeKillsCounter = 273`

  - `NcrSmitVsVestinStatus = 274`

  - `NcrSmitStringNum = 275`

  - `NcrSmitGateStringNum = 276`

  - `NcrSmitPlayerId = 277`

  - `NcrSmitIdleCount = 278`

  - `NcrWestinMapPidTo = 279`

  - `NcrWestinHexNumTo = 280`

  - `NcrWestinEveryEveningInvokeId = 281`

  - `NcrWestinEveryMorningInvokeId = 282`

  - `LastBagRefreshedTime = 283`

  - `LastNpcDialog = 284`

  - `NpcDialogStringNum = 285`

  - `Planes = 286`

  - `NpcRevengeNpcHxHy = 287`

  - `NpcRevengeCountWait = 288`

  - `NRWriKidnap = 289`

  - `NRSalvatoreKill = 290`

  - `NRWriKidnapNotifyTime = 291`

  - `NRKidnapKillsCounter = 292`

  - `QNrWriKidnapInvokeId = 293`

  - `NukeStock = 294`

  - `NukeRestockTime = 295`

  - `PatternSniperCountRunning = 296`

  - `PetOwnerId = 297`

  - `PetLifeTime = 298`

  - `IsGenerated = 299`

  - `PokerWins = 300`

  - `PokerNumOfNpc = 301`

  - `PokerWincash = 302`

  - `PokerFraud = 303`

  - `PokerManywins = 304`

  - `PokerData = 305`

  - `QWarehouse = 306`

  - `QWarehouseSub1 = 307`

  - `QWarehouseSub2 = 308`

  - `WarehouseDataId = 309`

  - `WarehouseQuestData = 310`

  - `WarehouseOther = 311`

  - `RatGrenadeProtoId = 312`

  - `RatGrenadeOwnerId = 313`

  - `ReddMineNuggets = 314`

  - `ReddMarionWan = 315`

  - `ReddQWinamingoKills = 316`

  - `ReddQWinamingoHealing = 317`

  - `ReddDoctorPoisoned = 318`

  - `ReddRooneyCemetery = 319`

  - `CanRepairWeapons = 320`

  - `CanRepairWeaponsSpecial = 321`

  - `CanRepairArmor = 322`

  - `CanRepairArmorSpecial = 323`

  - `RepairCompleteTime = 324`

  - `RepairItemPid = 325`

  - `HellVisits = 326`

  - `ReplBankIsCanEnter = 327`

  - `ReplBankeIsAttackGagPlayer = 328`

  - `ReplHellTurretHack = 329`

  - `TerminalPlayerId = 330`

  - `TerminalDialogId = 331`

  - `ModFarrelAmmiak = 332`

  - `RouletteCroupierNum = 333`

  - `RouletteBetCoord1 = 334`

  - `RouletteBetCoord2 = 335`

  - `RouletteBetCoord3 = 336`

  - `RouletteBetSize = 337`

  - `RouletteBetType = 338`

  - `RouletteData = 339`

  - `CanSendSay = 340`

  - `Scores = 341`

  - `SEAndroidMonologEnd = 342`

  - `SETalkingHeadStringNum = 343`

  - `SETeleportEatId = 344`

  - `SFAhs7HubJudgement = 345`

  - `SFLoPanBlackmailSum = 346`

  - `SFHububJudgementLocId = 347`

  - `SFHubJudgementKills = 348`

  - `SfMercMaster = 349`

  - `SFCommonOneWeekInvokeId = 350`

  - `SFCommonFightPlayerId = 351`

  - `ClickCounter = 352`

  - `SFInvasionMirelurkKills = 353`

  - `BHRocketBase = 354`

  - `NcrElizeSlvrsHunting = 355`

  - `NcrElizeSlvrsHuntingStatus = 356`

  - `NcrSantiagoSpyMission = 357`

  - `QSpyMissonStringNum = 358`

  - `TimeoutBattle = 359`

  - `TimeoutTransfer = 360`

  - `WalkSpeedBase = 361`

  - `WalkSpeed = 362`

  - `IsNoMove = 363`

  - `IsNoMoveBase = 364`

  - `IsNoRun = 365`

  - `IsNoRunBase = 366`

  - `Strength = 367`

  - `StrengthBase = 368`

  - `Perception = 369`

  - `PerceptionBase = 370`

  - `Endurance = 371`

  - `EnduranceBase = 372`

  - `Charisma = 373`

  - `CharismaBase = 374`

  - `Intellect = 375`

  - `IntellectBase = 376`

  - `Agility = 377`

  - `AgilityBase = 378`

  - `Luck = 379`

  - `LuckBase = 380`

  - `ArmorClass = 381`

  - `MaxLife = 382`

  - `MaxLifeBase = 383`

  - `ActionPointsBase = 384`

  - `ArmorClassBase = 385`

  - `MeleeDamage = 386`

  - `MeleeDamageBase = 387`

  - `IsOverweight = 388`

  - `CarryWeight = 389`

  - `CarryWeightBase = 390`

  - `Sequence = 391`

  - `SequenceBase = 392`

  - `HealingRate = 393`

  - `HealingRateBase = 394`

  - `CriticalChance = 395`

  - `CriticalChanceBase = 396`

  - `MaxCritical = 397`

  - `MaxCriticalBase = 398`

  - `Toxic = 399`

  - `Radioactive = 400`

  - `KillExperience = 401`

  - `BodyType = 402`

  - `LocomotionType = 403`

  - `DamageType = 404`

  - `Age = 405`

  - `Gender = 406`

  - `PoisoningLevel = 407`

  - `RadiationLevel = 408`

  - `UnspentSkillPoints = 409`

  - `UnspentPerks = 410`

  - `Karma = 411`

  - `ReplicationMoney = 412`

  - `ReplicationCount = 413`

  - `ReplicationCost = 414`

  - `RateObject = 415`

  - `BonusLook = 416`

  - `NpcRole = 417`

  - `AiId = 418`

  - `TeamId = 419`

  - `NextCrType = 420`

  - `DeadBlockerId = 421`

  - `CurrentArmorPerk = 422`

  - `NextReplicationMap = 423`

  - `NextReplicationEntry = 424`

  - `PlayerKarma = 425`

  - `ArmorPerk = 426`

  - `LastStealCrId = 427`

  - `StealCount = 428`

  - `GlobalMapMoveCounter = 429`

  - `Experience = 430`

  - `MaxMoveApBase = 431`

  - `AnimType = 432`

  - `FollowLeaderId = 433`

  - `LastSendEntrancesLocId = 434`

  - `LastSendEntrancesTick = 435`

  - `CrTypeAliasBase = 436`

  - `CrTypeAlias = 437`

  - `ModelNameBase = 438`

  - `IsNoArmor = 439`

  - `Anims = 440`

  - `IsNoAim = 441`

  - `Kills = 442`

  - `KillMen = 443`

  - `KillWomen = 444`

  - `KillAlien = 445`

  - `KillChildren = 446`

  - `KillFloater = 447`

  - `KillRat = 448`

  - `KillCentaur = 449`

  - `ReputationDen = 450`

  - `ReputationKlamath = 451`

  - `ReputationModoc = 452`

  - `ReputationVaultCity = 453`

  - `ReputationGecko = 454`

  - `ReputationBrokenHills = 455`

  - `ReputationNewReno = 456`

  - `ReputationSierra = 457`

  - `ReputationVault15 = 458`

  - `ReputationNCR = 459`

  - `ReputationCathedral = 460`

  - `ReputationSAD = 461`

  - `ReputationRedding = 462`

  - `ReputationSF = 463`

  - `ReputationNavarro = 464`

  - `ReputationArroyo = 465`

  - `ReputationPrimalTribe = 466`

  - `ReputationRangers = 467`

  - `ReputationVault13 = 468`

  - `ReputationSacramento = 469`

  - `Addictions = 470`

  - `IsAddicted = 471`

  - `IsJetAddicted = 472`

  - `IsBuffoutAddicted = 473`

  - `IsMentatsAddicted = 474`

  - `IsPsychoAddicted = 475`

  - `IsRadawayAddicted = 476`

  - `DamageResistance = 477`

  - `NormalResistance = 478`

  - `PoisonResistance = 479`

  - `RadiationResistance = 480`

  - `ExplodeResistance = 481`

  - `NormalResistanceBase = 482`

  - `LaserResistanceBase = 483`

  - `FireResistanceBase = 484`

  - `PlasmaResistanceBase = 485`

  - `ElectricityResistanceBase = 486`

  - `EmpResistanceBase = 487`

  - `ExplodeResistanceBase = 488`

  - `PoisonResistanceBase = 489`

  - `RadiationResistanceBase = 490`

  - `DamageThreshold = 491`

  - `NormalThresholdBase = 492`

  - `LaserThresholdBase = 493`

  - `FireThresholdBase = 494`

  - `PlasmaThresholdBase = 495`

  - `ElectricityThresholdBase = 496`

  - `EmpThresholdBase = 497`

  - `ExplodeThresholdBase = 498`

  - `PoisonThresholdBase = 499`

  - `RadiationThresholdBase = 500`

  - `IsPoisoned = 501`

  - `IsRadiated = 502`

  - `IsInjured = 503`

  - `IsDamagedEye = 504`

  - `IsDamagedRightArm = 505`

  - `IsDamagedLeftArm = 506`

  - `IsDamagedRightLeg = 507`

  - `IsDamagedLeftLeg = 508`

  - `Var0 = 509`

  - `Var1 = 510`

  - `Var2 = 511`

  - `Var3 = 512`

  - `Var4 = 513`

  - `Var5 = 514`

  - `Var6 = 515`

  - `Var7 = 516`

  - `Var8 = 517`

  - `Var9 = 518`

  - `SkillSmallGuns = 519`

  - `SkillBigGuns = 520`

  - `SkillEnergyWeapons = 521`

  - `SkillUnarmed = 522`

  - `SkillMeleeWeapons = 523`

  - `SkillThrowing = 524`

  - `SkillFirstAid = 525`

  - `SkillDoctor = 526`

  - `SkillSneak = 527`

  - `SkillLockpick = 528`

  - `SkillSteal = 529`

  - `SkillTraps = 530`

  - `SkillScience = 531`

  - `SkillRepair = 532`

  - `SkillSpeech = 533`

  - `SkillBarter = 534`

  - `SkillGambling = 535`

  - `SkillOutdoorsman = 536`

  - `TagSkills = 537`

  - `TagSkill1 = 538`

  - `TagSkill2 = 539`

  - `TagSkill3 = 540`

  - `PerkBookworm = 541`

  - `PerkAwareness = 542`

  - `PerkBonusHthAttacks = 543`

  - `PerkBonusHthDamage = 544`

  - `PerkBonusRangedDamage = 545`

  - `PerkBonusRateOfFire = 546`

  - `PerkEarlierSequence = 547`

  - `PerkFasterHealing = 548`

  - `PerkMoreCriticals = 549`

  - `PerkNightVision = 550`

  - `PerkRadResistance = 551`

  - `PerkToughness = 552`

  - `PerkStrongBack = 553`

  - `PerkSharpshooter = 554`

  - `PerkSurvivalist = 555`

  - `PerkEducated = 556`

  - `PerkHealer = 557`

  - `PerkFortuneFinder = 558`

  - `PerkBetterCriticals = 559`

  - `PerkEmpathy = 560`

  - `PerkSlayer = 561`

  - `PerkSniper = 562`

  - `PerkSilentDeath = 563`

  - `PerkActionBoy = 564`

  - `PerkMentalBlock = 565`

  - `PerkLifegiver = 566`

  - `PerkDodger = 567`

  - `PerkSnakeater = 568`

  - `PerkMrFixit = 569`

  - `PerkMedic = 570`

  - `PerkMasterThief = 571`

  - `PerkSpeaker = 572`

  - `PerkHeaveHo = 573`

  - `PerkFriendlyFoe = 574`

  - `PerkPickpocket = 575`

  - `PerkGhost = 576`

  - `PerkCultOfPersonality = 577`

  - `PerkScrounger = 578`

  - `PerkExplorer = 579`

  - `PerkFlowerChild = 580`

  - `PerkPathfinder = 581`

  - `PerkAnimalFriend = 582`

  - `PerkScout = 583`

  - `PerkMysteriousStranger = 584`

  - `PerkRanger = 585`

  - `PerkSmoothTalker = 586`

  - `PerkSwiftLearner = 587`

  - `PerkTag = 588`

  - `PerkMutate = 589`

  - `PerkAdrenalineRush = 590`

  - `PerkCautiousNature = 591`

  - `PerkComprehension = 592`

  - `PerkDemolitionExpert = 593`

  - `PerkGambler = 594`

  - `PerkGainStrength = 595`

  - `PerkGainPerception = 596`

  - `PerkGainEndurance = 597`

  - `PerkGainCharisma = 598`

  - `PerkGainIntelligence = 599`

  - `PerkGainAgility = 600`

  - `PerkGainLuck = 601`

  - `PerkHarmless = 602`

  - `PerkHereAndNow = 603`

  - `PerkHthEvade = 604`

  - `PerkKamaSutraMaster = 605`

  - `PerkKarmaBeacon = 606`

  - `PerkLightStep = 607`

  - `PerkLivingAnatomy = 608`

  - `PerkMagneticPersonality = 609`

  - `PerkNegotiator = 610`

  - `PerkPackRat = 611`

  - `PerkPyromaniac = 612`

  - `PerkQuickRecovery = 613`

  - `PerkSalesman = 614`

  - `PerkStonewall = 615`

  - `PerkThief = 616`

  - `PerkWeaponHandling = 617`

  - `PerkVaultCityTraining = 618`

  - `PerkExpertExcrement = 619`

  - `PerkTerminator = 620`

  - `PerkGeckoSkinning = 621`

  - `PerkVaultCityInoculations = 622`

  - `PerkDermalImpact = 623`

  - `PerkDermalImpactEnh = 624`

  - `PerkPhoenixImplants = 625`

  - `PerkPhoenixImplantsEnh = 626`

  - `PerkNcrPerception = 627`

  - `PerkNcrEndurance = 628`

  - `PerkNcrBarter = 629`

  - `PerkNcrRepair = 630`

  - `PerkVampireAccuracy = 631`

  - `PerkVampireRegeneration = 632`

  - `PerkQuickPockets = 633`

  - `PerkMasterTrader = 634`

  - `PerkSilentRunning = 635`

  - `PerkBonusMove = 636`

  - `KarmaPerkBerserker = 637`

  - `KarmaPerkChampion = 638`

  - `KarmaPerkChildkiller = 639`

  - `KarmaPerkSexpert = 640`

  - `KarmaPerkPrizefighter = 641`

  - `KarmaPerkGigolo = 642`

  - `KarmaPerkGraveDigger = 643`

  - `KarmaPerkMarried = 644`

  - `KarmaPerkPornStar = 645`

  - `KarmaPerkSlaver = 646`

  - `KarmaPerkVirginWastes = 647`

  - `KarmaPerkManSalvatore = 648`

  - `KarmaPerkManBishop = 649`

  - `KarmaPerkManMordino = 650`

  - `KarmaPerkManWright = 651`

  - `KarmaPerkSeparated = 652`

  - `KarmaPerkPedobear = 653`

  - `KarmaPerkVcGuardsman = 654`

  - `IsTraitFastMetabolism = 655`

  - `IsTraitBruiser = 656`

  - `IsTraitSmallFrame = 657`

  - `IsTraitOneHander = 658`

  - `IsTraitFinesse = 659`

  - `IsTraitKamikaze = 660`

  - `IsTraitHeavyHanded = 661`

  - `IsTraitFastShot = 662`

  - `IsTraitBloodyMess = 663`

  - `IsTraitJinxed = 664`

  - `IsTraitJinxedII = 665`

  - `IsTraitGoodNatured = 666`

  - `IsTraitChemReliant = 667`

  - `IsTraitChemResistant = 668`

  - `IsTraitSexAppeal = 669`

  - `IsTraitSkilled = 670`

  - `IsTraitNightPerson = 671`

  - `TimeoutSkFirstAid = 672`

  - `TimeoutSkDoctor = 673`

  - `TimeoutSkRepair = 674`

  - `TimeoutSkScience = 675`

  - `TimeoutSkLockpick = 676`

  - `TimeoutSkSteal = 677`

  - `TimeoutSkOutdoorsman = 678`

  - `TimeoutRemoveFromGame = 679`

  - `TimeoutReplication = 680`

  - `TimeoutKarmaVoting = 681`

  - `TimeoutSneak = 682`

  - `TimeoutHealing = 683`

  - `TimeoutStealing = 684`

  - `TimeoutAggressor = 685`

  - `MercMasterId = 686`

  - `MercAlwaysRun = 687`

  - `MercCancelOnAttack = 688`

  - `MercLoseDist = 689`

  - `MercMasterDist = 690`

  - `MercType = 691`

  - `MercDefendMaster = 692`

  - `MercAssistMaster = 693`

  - `MercCancelTime = 694`

  - `MercCancelOnGlobal = 695`

  - `MercWaitForMaster = 696`

  - `ArroyoMynocDefence = 697`

  - `ArroyoCassidyLetter = 698`

  - `ArroyoMynocOil = 699`

  - `ArroyoProofOfDeath = 700`

  - `ArroyoLetterToLinnett = 701`

  - `KlamSallyFindProstitute = 702`

  - `KlamBobWater = 703`

  - `KlamFindTrappers = 704`

  - `KlamBugenLure = 705`

  - `KlamNotifyHusband = 706`

  - `KlamEidenBramin = 707`

  - `KlamSmilyModoc = 708`

  - `DenBillRacingWin = 709`

  - `DenLeannaCondom = 710`

  - `QDenAnanDoll = 711`

  - `DenAnanRedoll = 712`

  - `DenGhost = 713`

  - `DenBillRacingOpening = 714`

  - `DenCarstopJeffry = 715`

  - `DenCarstopBrahmin = 716`

  - `DenCarstopBreeder = 717`

  - `DenJoeySteal = 718`

  - `DenJaneDolg = 719`

  - `DenJanePsycho = 720`

  - `DenLaraPostal = 721`

  - `DenFlikJet = 722`

  - `DenLaraBand = 723`

  - `DenJoeyLoan = 724`

  - `DenLaraBos = 725`

  - `QDenCliffDealer = 726`

  - `DenFredStim = 727`

  - `DenJaneVodka = 728`

  - `DenMomSlut = 729`

  - `DenSmittyBatt = 730`

  - `DenJaneMeat = 731`

  - `DenJaneStim = 732`

  - `DenLaraMolotovCoctail = 733`

  - `DenLeannaBuy = 734`

  - `DenSmittyBoots = 735`

  - `DenJaneGuns = 736`

  - `DenSmittyKey = 737`

  - `DenJaneArmor = 738`

  - `DenSmittyAmmo = 739`

  - `DenJaneHunt = 740`

  - `DenJoeyKnife = 741`

  - `DenJoeyLara = 742`

  - `DenJaneRadio = 743`

  - `DenJoeyJet = 744`

  - `DenLaraTrust = 745`

  - `DenLeannaWine = 746`

  - `DenMomRadscorp = 747`

  - `DenSmittyFixit = 748`

  - `QDenLeannaThief = 749`

  - `ModJoeFarm = 750`

  - `ModHose = 751`

  - `ModBaltasGecko = 752`

  - `ModLourenceRatsColony = 753`

  - `ModLourenceFloater = 754`

  - `ModJoeVampire = 755`

  - `BHMarcusEscort = 756`

  - `BHSuperNewTechnology = 757`

  - `ReddDocRadio = 758`

  - `ReddDocRadioTroy = 759`

  - `ReddDocRadioFung = 760`

  - `ReddDocRadioHoliday = 761`

  - `ReddDocRadioJubiley = 762`

  - `ReddHubbChildkiller = 763`

  - `ReddMarionVinamingo = 764`

  - `ReddDoctorDelivery = 765`

  - `NavHenryProtoMaterials = 766`

  - `NavSoftJob = 767`

  - `NcrHatePatrol = 768`

  - `NcrSantiagaFindSpyStatus = 769`

  - `NcrBusterBrokenrifles = 770`

  - `NcrKessMedBoardStatus = 771`

  - `NcrDorotyFindHenryPapers = 772`

  - `NcrLeadSmit2Dustybar = 773`

  - `NcrKyleReddRecon = 774`

  - `NcrDuppoFindDasies = 775`

  - `NcrDappoLostC = 776`

  - `QChosen = 777`

  - `NRBarmenEscort = 778`

  - `SFAhs7ImperatorFormat = 779`

  - `SFEvaHelpWithZax = 780`

  - `SFKenliImperatorRestore = 781`

  - `SFLoPanBlackmail = 782`

  - `SFTigangRecipe = 783`

  - `SFNarcoman = 784`

  - `SFAhs7Invitations = 785`

  - `SFSlimSidnancy = 786`

  - `VCLetterToTodd = 787`

  - `VCValeryMail = 788`

  - `VCCindyLetter = 789`

  - `VCHartmannRecon = 790`

  - `VCHartmanNcrHelp = 791`

  - `VCBarmenDelivery = 792`

  - `VCCharlie = 793`

  - `VCTroyFreshBlood = 794`

  - `VCAndrewDeliveries = 795`

  - `VCBlackEscort = 796`

  - `VCHartmanFight = 797`

  - `VCLynettScareNewcomers = 798`

  - `VCHartmanRifles = 799`

  - `VCHeleneTroyBeauty = 800`

  - `TribSulikStuff = 801`

  - `TribMuscoTest = 802`

  - `TribShamanPowder = 803`

  - `TribMaiaraBook = 804`

  - `TribManotaNecklace = 805`

  - `BHDeadSaboteursCounter = 806`

  - `SpecialAndroid = 807`

  - `VCLynettRefuse = 808`

  - `DialogTimeout = 809`

  - `EncLoyalityHubologists = 810`

  - `EncLoyalityNcr = 811`

  - `EncLoyalityVCity = 812`

  - `EncLoyalityRedding = 813`

  - `EncLoyalityBroken = 814`

  - `EncLoyalityGecko = 815`

  - `EncLoyalityArroyo = 816`

  - `EncLoyalityKlamath = 817`

  - `EncLoyalityModoc = 818`

  - `EncLoyalityDen = 819`

  - `EncLoyalityReno = 820`

  - `EncLoyalityEnclave = 821`

  - `EncLoyalitySf = 822`

  - `ModLourenceToxinRecipe = 823`

  - `SFChitinArmorRecipeKnown = 824`

  - `SpyCathActive = 825`

  - `HasNotCard = 826`

  - `SexExp = 827`

  - `ScenFraction = 828`

  - `ArroyoDocHealing = 829`

  - `AtollTesla = 830`

  - `AtollMoney = 831`

  - `BHEscortNpcId = 832`

  - `ScenBosSoldier = 833`

  - `SFInvasionBadge = 834`

  - `ScenBosScriber = 835`

  - `ScenEnclaveSoldier = 836`

  - `ScenEnclaveScient = 837`

  - `DenJaneTraderFred = 838`

  - `DenJaneJobCounter = 839`

  - `DenJoeyCounter = 840`

  - `DenLaraBosCounter = 841`

  - `DenJaneTraderMom = 842`

  - `DenNarcCommMember = 843`

  - `DenJaneTraderLean = 844`

  - `EncOceanTraderFamiliar = 845`

  - `ModBaltasArmor1 = 846`

  - `GeckGaroldTrain = 847`

  - `GeckSkitrTransit = 848`

  - `KlamBaknerBeer = 849`

  - `ModBaltasArmor = 850`

  - `KlamVaccination = 851`

  - `KlamVaccinationB1 = 852`

  - `KlamVaccinationB2 = 853`

  - `KlamVaccinationB3 = 854`

  - `KlamGoldBeer = 855`

  - `KlamSallyPay = 856`

  - `ModBaltasArmor2 = 857`

  - `KlamVicFixittrash = 858`

  - `ModHoseTools = 859`

  - `ModVampireReaction = 860`

  - `NcrAlexQuestStatus = 861`

  - `NcrDustyPartyStatusChar = 862`

  - `NcrMiraTroubleStatusChar = 863`

  - `NcrBeggarTalk = 864`

  - `NcrDorothyGammaStatusChar = 865`

  - `NcrDumontBrkradioStatusChar = 866`

  - `NcrCaptainFlirtStatusChar = 867`

  - `NcrIsNightGuardAccessFranted = 868`

  - `NcrClausHistory = 869`

  - `NcrJubileyTailsStatus = 870`

  - `NcrRondoDorotyStatus = 871`

  - `NcrFergusStory = 872`

  - `NcrCaptainSmitAccessGranted = 873`

  - `NcrJubileyTailsCounter = 874`

  - `NcrBusterDorotyStatus = 875`

  - `NcrFergusSecret = 876`

  - `NcrGunterStory = 877`

  - `ScenRangerRank = 878`

  - `NcrDustyFoodDeliveryStatus = 879`

  - `NcrPlayerLeadSmit2Dustybar = 880`

  - `NcrKarlStory = 881`

  - `NcrCarlsonStory = 882`

  - `NcrKukComp = 883`

  - `NcrMicQStatus = 884`

  - `ScenRanger = 885`

  - `NcrDumontHistory = 886`

  - `NcrMicQCptnDumbCounter = 887`

  - `NcrPlayerHasMultipass = 888`

  - `NcrSmitVsVestinResult = 889`

  - `NRJukeboxSeen = 890`

  - `VCTrainigAccess = 891`

  - `NcrLennyFight = 892`

  - `NcrRatchPlayerPoints = 893`

  - `NRJesusTrain = 894`

  - `PurgSuppluysTaken = 895`

  - `NcrWestinPillsStatus = 896`

  - `NcrWestinPlayerGetPrepayment = 897`

  - `SFHubJudgementIgnatStory = 898`

  - `ReddMinesPlayerThief = 899`

  - `ReddDocMedicals = 900`

  - `NcrWestinPills = 901`

  - `SFHubbStatus = 902`

  - `SFInvasionSandbagsTaken = 903`

  - `SFInvasionSandbagsGiven = 904`

  - `SFImperatorCancelNum = 905`

  - `VCShiComputerAccess = 906`

  - `TribManotaStory = 907`

  - `VCKnowsAboutDelivery = 908`

  - `VCCitizenship = 909`

  - `VCHartmanFightStatus = 910`

  - `VCFreshBloodCounter = 911`

  - `VCForgeryWitnessInhome = 912`

  - `VCLynetOrMaclure = 913`

  - `VCMutCharleyHired = 914`

  - `VCCavesCounter = 915`

  - `VCPrisonerBulled = 916`

  - `VCLynettTalk = 917`

  - `VCPatrolCounter = 918`

  - `NpcDialogTimeWait = 919`

  - `HoloInfo = 920`

  - `FavoriteItemPid = 921`

  - `IsNoFavoriteItem = 922`

  - `Level = 923`

  - `KarmaVoting = 924`

  - `IsNoPvp = 925`

  - `IsEndCombat = 926`

  - `IsDlgScriptBarter = 927`

  - `IsUnlimitedAmmo = 928`

  - `IsNoDrop = 929`

  - `IsNoLooseLimbs = 930`

  - `IsDeadAges = 931`

  - `IsNoHeal = 932`

  - `IsInvulnerable = 933`

  - `IsSpecialDead = 934`

  - `IsRangeHth = 935`

  - `IsNoKnock = 936`

  - `IsNoSupply = 937`

  - `IsNoKarmaOnKill = 938`

  - `IsBarterOnlyCash = 939`

  - `BarterCoefficient = 940`

  - `TransferType = 941`

  - `TransferContainerId = 942`

  - `IsNoBarter = 943`

  - `IsNoSteal = 944`

  - `IsNoLoot = 945`

  - `IsNoPush = 946`

  - `ItemsWeight = 947`

  - `ActionPoints = 948`

  - `CurrentAp = 949`

  - `BagId = 950`

  - `LastWeaponId = 951`

  - `LastWeaponNotFound = 952`

  - `HandsProtoItemId = 953`

  - `HandsItemMode = 954`

  - `LastWeaponUse = 955`

  - `IsNoItemGarbager = 956`

  - `TownSupplyVictimId = 957`

  - `TownSupplyHostileId = 958`

  - `TravellerRoute = 959`

  - `V13Dclaw = 960`

  - `VCAmandaHelpJoshua = 961`

  - `VCMailRemembered = 962`

  - `VCBeautyHoloRemembered = 963`

  - `VCityCommonBarkusTimeSay = 964`

  - `SquadMarchSquads = 965`

  - `SquadMarchQueue = 966`

  - `VCHartmanMarch = 967`

  - `VCHartmannClearCave = 968`

  - `VCDeadAllyCounter = 969`

  - `VCGuardRank = 970`

  - `VCReconCaveId = 971`

  - `VCGuardsmanTriggerPlayerId = 972`

  - `VCLynettArest = 973`

  - `VCLynettForgery = 974`

  - `VCLynettPrisonerId = 975`

  - `ReddingMortonBrothers = 976`

  - `SpecialEncounterBaxChurch = 977`

  - `SpecialEncounteTim = 978`

  - `RacingSneakersTrap = 979`

  - `SpecialEncounterBridge = 980`

  - `SpecialEncounterHoly1 = 981`

  - `SpecialEncounterHoly2 = 982`

  - `SpecialEncounterToxic = 983`

  - `SpecialEncounterPariah = 984`

  - `SpecialEncounterBrahmin = 985`

  - `SpecialEncounterWhale = 986`

  - `SpecialEncounterHead = 987`

  - `SpecialEncounterShuttle = 988`

  - `SpecialEncounterGuardian = 989`

  - `SpecialEncounterWoodsman = 990`

  - `SpecialEncounterUnwashed = 991`

  - `SpecialEncounterTeleport = 992`

  - `SpecialWastelandChildren = 993`

  - `SpecialEncounterKotw = 994`

  - `SpecialSoldierHolo = 995`

  - `SpecialTrapperHolo = 996`

  - `SpecialDollHolo = 997`

  - `SpecialEncounterZergLaboratory = 998`

  - `SpecialEncounterDoughnutWarehouse = 999`

  - `SpecialEncounterAtomChurch = 1000`

  - `GeckoFindWoody = 1001`

  - `NcrDappoLostCCtatus = 1002`

* `MapProperty`

  ...

  - `Invalid = 0xFFFF`

  - `InitScript = 0`

  - `LoopTime1 = 1`

  - `LoopTime2 = 2`

  - `LoopTime3 = 3`

  - `LoopTime4 = 4`

  - `LoopTime5 = 5`

  - `FileDir = 6`

  - `Width = 7`

  - `Height = 8`

  - `WorkHexX = 9`

  - `WorkHexY = 10`

  - `LocId = 11`

  - `LocMapIndex = 12`

  - `CritterIds = 13`

  - `ItemIds = 14`

  - `RainCapacity = 15`

  - `CurDayTime = 16`

  - `DayTime = 17`

  - `DayColor = 18`

  - `IsNoLogOut = 19`

  - `SpritesZoom = 20`

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

  - `MapCoastRainUp = 38`

  - `GeckCityDoor = 39`

  - `GeckCityCharges = 40`

  - `GeckCityTimeBroken = 41`

  - `MapRadiationMinDose = 42`

  - `MapRadiationMaxDose = 43`

  - `NcrMichaelCritterId = 44`

  - `NcrSiegeComplexity = 45`

  - `IsNoPvPMap = 46`

  - `NpcRevengeData = 47`

  - `ResourcesData = 48`

  - `VCLastBarDialog = 49`

  - `WarehouseTurretActive = 50`

* `LocationProperty`

  ...

  - `Invalid = 0xFFFF`

  - `InitScript = 0`

  - `MapIds = 1`

  - `MapProtos = 2`

  - `MapEntrances = 3`

  - `Automaps = 4`

  - `AutoGarbage = 5`

  - `GeckVisible = 6`

  - `EntranceScript = 7`

  - `WorldX = 8`

  - `WorldY = 9`

  - `Radius = 10`

  - `Hidden = 11`

  - `ToGarbage = 12`

  - `Color = 13`

  - `IsEncounter = 14`

  - `GECachesCacheChecked = 15`

  - `RacingCheckpointNumber = 16`

  - `StorehouseContId = 17`

  - `MaxPlayers = 18`

  - `GeckCityMembers = 19`

  - `GeckCityLeader = 20`

  - `LocModVampireFarmQuesterId = 21`

  - `LocDefendersHostile = 22`

  - `NRWriGuardDead = 23`

  - `NRKidnapAllMarodeursDead = 24`

  - `LastLootTransfer = 25`

  - `SeAndroidPlayerIn = 26`

  - `SeAndroidPlayerId = 27`

  - `SeAndroidMinesTriggered = 28`

  - `SeAndroidTFounded = 29`

  - `SeAndroidLFounded = 30`

  - `SeAndroidDFounded = 31`

  - `SeAndroidRFounded = 32`

  - `SeAndroidPFounded = 33`

  - `SeAndroidCFounded = 34`

  - `SiloMissileLaunched = 35`
