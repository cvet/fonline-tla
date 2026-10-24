# Engine settings relevance audit

Date: 2026-10-16. Static audit of the current uncommitted Engine and TLA changes.


Historical snapshot dated 2026-10-16, not a current settings contract or fresh
acceptance. The exact uncommitted source revision of that audit is not encoded
in this report. Original source locations below are retained as code rather
than live links into an evolved Engine tree; do not treat shifted line numbers
as present-day per-claim evidence. Current settings are owned by
[Engine settings reference](../Engine/Docs/en/reference/script-api/settings.md),
`Engine/Source/Common/Settings.inc`, `TLA.fomain` and their consumers. Re-run an
owner-backed audit before acting on the old migration recommendations.

The full register is deliberately kept together for coverage review. Reading
routes by group:

[Common](#common--7) | [AngelScript](#angelscript--6) | [ManagedScript](#managedscript--20) |
[Network](#network--27) | [ServerNetwork](#servernetwork--20) | [ClientNetwork](#clientnetwork--12)
| [Audio](#audio--5) | [View](#view--12) | [Geometry](#geometry--13) | [SpriteMesh](#spritemesh--4)
| [Animation](#animation--2) | [Render](#render--46) | [Web](#web--11) | [Android](#android--11) |
[Packaging](#packaging--3) | [Timer](#timer--1) | [Baking](#baking--23) | [Critter](#critter--3) |
[CritterView](#critterview--1) | [Hex](#hex--6) | [DataBase](#database--8) | [Input](#input--2) |
[Mapper](#mapper--7) | [Client](#client--16) | [Server](#server--24)

## Result

- Removed native `View.GlobalDayColorTime` and `View.GlobalDayColor`, their TLA config entries and their entries in three Engine examples. TLA retains the exact time keys and palette in constants in `Scripts/DayColor.fos`. Nonempty map arrays retain priority independently for time keys and colors.
- `Map.SetDayColors` and the rendered `Map.GlobalDayColor` output remain generic rendering capabilities. The removed configuration setting was an input curve owned by the project.
- The remaining **290** declarations in **25** groups reconcile with the complete register below: 282 have an engine/tool consumer, 2 actively configure model bones, 2 hold mutable display state, 1 is read only by TLA, and 3 have no verified consumer.
- Findings for the other settings are migration recommendations. Conditional platform and backend capabilities remain relevant even when TLA does not enable them.

## Findings and recommended migrations

| Setting | Direct evidence | Assessment and next action |
| --- | --- | --- |
| `Geometry.MapHexLineHeight` | No full-key or short-name reads found in the examined code; declarations and configs remain. | No applying consumer was found. Candidate for removal from native API/configs with migration notes. |
| `Geometry.MapSmoothPath` | The same negative search; TLA sets `True`. | The configuration is not connected to the current smoothing code. Candidate for removal; this conclusion is static, without a separate runtime experiment. |
| `Geometry.CritterBlockHex` | The same negative search; TLA sets `True`. Current pathfinding reads the separate critter property `PathfindingObstacle`. | The setting does not control the current path consumer. Candidate for removal; project properties own the actual policy. |
| `Geometry.MapDataPrefix` | `Scripts/MoveCursor.fos:167` reads it when constructing sprite paths. No native Engine/CoreScripts/tool reader found. | Working project input, like the former day curve. Move the declaration/name into MoveCursor and preserve its configured value/resources. |
| `View.MonitorWidth`, `View.MonitorHeight` | `UpdateMonitorSettings` writes them at startup and SDL display/scale changes; no value readers found in the examined code. | Mutable runtime state belongs to the window/display owner. `AppWindow::GetDisplaySize` and script `Game.GetDisplaySize` already exist. Reconcile external consumers when removing these duplicate fields. |
| `Render.HeadBone`, `Render.LegBones` | ModelManager reads the names; ModelInformation and ModelInstance apply their joint indexes. | Active. Bone names belong to a particular skeleton; move them into model descriptions while preserving split body/legs and head rotation. Deletion alone would break a working path. |

## Method and coverage

- No engine-owned `///@ Setting` metadata declarations were found under Engine scripting sources/resources; project/example/test declarations are outside this native register.
- Declaration corpus: every `SETTING(...)` in `Engine/Source/Common/Settings.inc`; no other declaration file found under Engine/Source. Roles below come from the nearest `ExportSettings` annotation.
- Exact full keys with word boundaries were searched across `Engine/Source`, `Engine/BuildTools`, `Engine/Examples`, `Engine/Resources`, `Scripts`, `SourceExt`, `Tools`, `Gui`, `Resources/FOnline`, `Resources/Mapper`, `TLA.fomain`, and `CMakeLists.txt`.
- Declarations, generated files, Markdown/JSON models and logs are excluded as consumer evidence. Tests and configs are separate categories and do not prove active use. Canonical embedded script in `Gui/*.fogui` is included.
- The three settings without readers were additionally searched by short name, including JSON/resources. Display-event writes and the bone-binding chain were inspected separately. Locations below identify actual uses, including writes to runtime outputs; text hits alone are insufficient.
- Independent MiMo review confirmed all declaration/inventory/register rows and all eight flagged settings. Codex verified actual returned line coverage (433/433 source, 291/291 TSV, 451/451 original report) from execution events, then corrected 45 evidence links following its two minor findings.
- Scope is the current Engine/TLA corpus. Other games/private repositories, every target platform and every scripting backend were not qualified by this static audit. The independent reviewer inspected all rows and detailed consumers for flagged settings plus a sample of active entries.

## Implementation verification

- RED: four expected native assertion failures while the two keys were reserved readonly settings; clean script compilation failure for missing selection helpers before implementation.
- GREEN: authoritative `Verify :: All` passed: all native targets, 588 native cases / 729,596 assertions, 110 script cases, script/nullable validators, 156 project Python tests / 82 subtests, and formatting (zero changed files).
- Documentation: 19 focused API/translation tests passed; final Engine validation passed 412 Markdown entries. The native API model has 290 settings / 2,572 classified symbols. Contract enforcement reports 79 changes across 17 domains, 43 required dispositions, zero missing. Two stale generated EN/RU public-contract pages were found and regenerated before the final pass.
- Mapper: with both map arrays empty, the ordinary DayColor loop submitted noon RGBA `(128,128,128,255)` / capacity `0` and dawn `(18,18,53,255)` / capacity `92` to rendering. Assertions and actual screenshots passed. Client: normal registration/login reached the local game map with QA commands disabled; screenshot inspected. Both isolated runs preserved existing cache files and had no warning/error/exception/overrun diagnostics.
- Palette/time values were compared against the preserved pre-run TLA config; all values match. Register validation confirms 290 unique keys, no missing/extra/duplicate rows, and 287 source use links containing the exact key; three remaining rows explicitly have no verified consumer.
- Managed backend-specific C++ generator tests were not run: TLA has `FO_MANAGED_SCRIPTING=OFF`. No all-platform/backend runtime qualification is claimed. Local verification logs and reports are retained under ignored `Build/settings-audit-20261016/`.

## Complete register

### Common — 7

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `Common.GameName` | `string` / Common | Active | `Engine/Source/Server/Server.cpp:296` |
| `Common.GameVersion` | `string` / Common | Active | `Engine/Source/Server/Server.cpp:296` |
| `Common.UnpackagedSubConfig` | `string` / Common | Active | `Engine/Source/Frontend/ApplicationInit.cpp:281` |
| `Common.Packaged` | `bool` / Common | Active | `Engine/Source/Client/Updater.cpp:93` |
| `Common.AsyncLogWrite` | `bool` / Common | Active | `Engine/Source/Frontend/ApplicationInit.cpp:132` |
| `Common.SecretSettingTokens` | `vector<string>` / Common | Active | `Engine/Source/Common/Settings.cpp:801` |
| `Common.UserWritablePath` | `string` / Common | Active | `Engine/Source/Tools/Mapper.cpp:92` |

### AngelScript — 6

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `AngelScript.OverrunReportTime` | `int32_t` / Common | Active | `Engine/Source/Scripting/AngelScript/AngelScriptBackend.cpp:751` |
| `AngelScript.DebuggerEnabled` | `bool` / Common | Active | `Engine/Source/Scripting/AngelScript/AngelScriptBackend.cpp:216` |
| `AngelScript.DebuggerBindHost` | `string` / Common | Active | `Engine/Source/Scripting/AngelScript/AngelScriptDebugger.cpp:172` |
| `AngelScript.MutableGlobalsAllowedNamespaces` | `vector<string>` / Common | Active | `Engine/Source/Scripting/AngelScript/AngelScriptBackend.cpp:703` |
| `AngelScript.AttributedFunctionDirectCallAllowedNamespaces` | `vector<string>` / Common | Active | `Engine/Source/Scripting/AngelScript/AngelScriptBackend.cpp:425` |
| `AngelScript.ExtraDirectCallBlockingAttributes` | `vector<string>` / Common | Active | `Engine/Source/Scripting/AngelScript/AngelScriptBackend.cpp:422` |

### ManagedScript — 20

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `ManagedScript.OverrunReportTime` | `int32_t` / Common | Active | `Engine/Source/Scripting/Managed/ManagedScriptBackend.cpp:1320` |
| `ManagedScript.InteropProbeOnStart` | `bool` / Common | Active | `Engine/Source/Scripting/Managed/CoreScripts/Initializator.Probes.cs:8` |
| `ManagedScript.DeepTrackEntityWrappers` | `bool` / Common | Active | `Engine/Source/Scripting/Managed/ManagedScriptBackend.cpp:1120` |
| `ManagedScript.Assemblies` | `vector<string>` / Common | Active | `Engine/Source/Tools/ManagedScriptBaker.cpp:220` |
| `ManagedScript.ProjectName` | `string` / Common | Active | `Engine/Source/Tools/ManagedScriptBaker.cpp:227` |
| `ManagedScript.TargetFramework` | `string` / Common | Active | `Engine/Source/Tools/ManagedScriptBaker.cpp:315` |
| `ManagedScript.MsBuild` | `string` / Common | Active | `Engine/Source/Tools/ManagedScriptBaker.cpp:377` |
| `ManagedScript.Dirs` | `vector<string>` / Common | Active | `Engine/Source/Tools/ManagedScriptBaker.cpp:217` |
| `ManagedScript.GeneratedDir` | `string` / Common | Active | `Engine/Source/Tools/ManagedScriptBaker.cpp:215` |
| `ManagedScript.ExtraSources` | `vector<string>` / Common | Active | `Engine/Source/Tools/ManagedScriptBaker.cpp:291` |
| `ManagedScript.ExtraReferences` | `vector<string>` / Common | Active | `Engine/Source/Tools/ManagedScriptBaker.cpp:294` |
| `ManagedScript.Analyzers` | `vector<string>` / Common | Active | `Engine/Source/Tools/ManagedScriptBaker.cpp:2038` |
| `ManagedScript.AnalyzerPackages` | `vector<string>` / Common | Active | `Engine/Source/Tools/ManagedScriptBaker.cpp:2039` |
| `ManagedScript.AdditionalFiles` | `vector<string>` / Common | Active | `Engine/Source/Tools/ManagedScriptBaker.cpp:2040` |
| `ManagedScript.AnalysisLevel` | `string` / Common | Active | `Engine/Source/Tools/ManagedScriptBaker.cpp:2036` |
| `ManagedScript.AnalysisMode` | `string` / Common | Active | `Engine/Source/Tools/ManagedScriptBaker.cpp:2037` |
| `ManagedScript.BakerDryRun` | `bool` / Common | Active | `Engine/Source/Tools/ManagedScriptBaker.cpp:233` |
| `ManagedScript.PatchPointWeaver` | `string` / Common | Active | `Engine/Source/Tools/ManagedScriptBaker.cpp:2033` |
| `ManagedScript.ServerPatchesEnabled` | `bool` / Common | Active | `Engine/Source/Scripting/Managed/CoreScripts/ScriptPatches.cs:84` |
| `ManagedScript.ClientPatchesEnabled` | `bool` / Common | Active | `Engine/Source/Scripting/Managed/CoreScripts/ScriptPatches.cs:86` |

### Network — 27

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `Network.ServerPort` | `int32_t` / Common | Active | `Engine/Source/Client/Updater.cpp:89` |
| `Network.WebSocketPort` | `int32_t` / Common | Active | `Engine/Source/Client/NetworkClient-Sockets.cpp:90` |
| `Network.NetBufferSize` | `int32_t` / Common | Active | `Engine/Source/Server/ServerConnection.cpp:159` |
| `Network.UdpPortOffset` | `int32_t` / Common | Active | `Engine/Source/Client/NetworkClient-UdpSockets.cpp:92` |
| `Network.UdpPacketSize` | `int32_t` / Common | Active | `Engine/Source/Client/NetworkClient-UdpSockets.cpp:100` |
| `Network.UdpWindowSize` | `int32_t` / Common | Active | `Engine/Source/Client/NetworkClient-UdpSockets.cpp:211` |
| `Network.UdpResendTimeout` | `int32_t` / Common | Active | `Engine/Source/Client/NetworkClient-UdpSockets.cpp:212` |
| `Network.UdpConnectRetry` | `int32_t` / Common | Active | `Engine/Source/Client/NetworkClient-UdpSockets.cpp:213` |
| `Network.UdpConnectTimeout` | `int32_t` / Common | Active | `Engine/Source/Client/NetworkClient-UdpSockets.cpp:284` |
| `Network.UdpSendUpdateInterval` | `int32_t` / Common | Active | `Engine/Source/Server/NetworkServer-UdpSockets.cpp:276` |
| `Network.UdpRedundancy` | `int32_t` / Common | Active | `Engine/Source/Client/NetworkClient-UdpSockets.cpp:214` |
| `Network.UpdateFileMaxPortionSize` | `int32_t` / Common | Active | `Engine/Source/Server/Server.cpp:2247` |
| `Network.SecuredWebSockets` | `bool` / Common | Active | `Engine/Source/Client/NetworkClient-Sockets.cpp:92` |
| `Network.DisableTcpNagle` | `bool` / Common | Active | `Engine/Source/Client/NetworkClient-Sockets.cpp:335` |
| `Network.DisableZlibCompression` | `bool` / Common | Active | `Engine/Source/Server/ServerConnection.cpp:393` |
| `Network.DisableInterthreadCommunication` | `bool` / Common | Active | `Engine/Source/Server/Server.cpp:358` |
| `Network.ArtificalLags` | `int32_t` / Common | Active | `Engine/Source/Client/ClientConnection.cpp:401` |
| `Network.ArtificalLagsJitter` | `int32_t` / Common | Active | `Engine/Source/Client/ClientConnection.cpp:401` |
| `Network.LinkDelayWindowMs` | `int32_t` / Common | Active | `Engine/Source/Server/ServerConnection.cpp:162` |
| `Network.LinkDelayRebaseMs` | `int32_t` / Common | Active | `Engine/Source/Server/ServerConnection.cpp:162` |
| `Network.MoveLateCatchUpMinMs` | `int32_t` / Common | Active | `Engine/Source/Server/ServerConnection.cpp:162` |
| `Network.MoveLateCatchUpMaxMs` | `int32_t` / Common | Active | `Engine/Source/Server/Server.cpp:3608` |
| `Network.MovePlanJoinMaxSteps` | `int32_t` / Common | Active | `Engine/Source/Server/Server.cpp:3501` |
| `Network.MoveSyncTrace` | `bool` / Common | Active | `Engine/Source/Server/Server.cpp:3602` |
| `Network.CompatibilityVersion` | `string` / Common | Active | `Engine/Source/Client/Updater.cpp:89` |
| `Network.ForceCompatibilityVersion` | `string` / Common | Active | `Engine/Source/Common/Settings.cpp:305` |
| `Network.ForceMetadataVersion` | `string` / Common | Active | `Engine/Source/Client/Updater.cpp:560` |

### ServerNetwork — 20

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `ServerNetwork.DisableNetworking` | `bool` / Server | Active | `Engine/Source/Server/Server.cpp:363` |
| `ServerNetwork.EnableUdp` | `bool` / Server | Active | `Engine/Source/Server/Server.cpp:370` |
| `ServerNetwork.RejectUdpConnections` | `bool` / Server | Active | `Engine/Source/Server/NetworkServer-UdpSockets.cpp:112` |
| `ServerNetwork.UpdateFilesInMemory` | `bool` / Server | Active | `Engine/Source/Server/UpdaterBackend.cpp:82` |
| `ServerNetwork.ClientPingTime` | `int32_t` / Server | Active | `Engine/Source/Server/ServerConnection.cpp:318` |
| `ServerNetwork.InactivityDisconnectTime` | `int32_t` / Server | Active | `Engine/Source/Server/ServerConnection.cpp:258` |
| `ServerNetwork.LoginTimeout` | `int32_t` / Server | Active | `Engine/Source/Server/ServerConnection.cpp:263` |
| `ServerNetwork.MaxMessageSize` | `int32_t` / Server | Active | `Engine/Source/Server/ServerConnection.cpp:172` |
| `ServerNetwork.MaxBufferedInputSize` | `int32_t` / Server | Active | `Engine/Source/Server/ServerConnection.cpp:175` |
| `ServerNetwork.MaxRemoteCallPayloadSize` | `int32_t` / Server | Active | `Engine/Source/Server/Server.cpp:351` |
| `ServerNetwork.MaxMessagesPerProcessPass` | `int32_t` / Server | Active | `Engine/Source/Server/Server.cpp:2309` |
| `ServerNetwork.MaxUdpReorderAhead` | `int32_t` / Server | Active | `Engine/Source/Server/NetworkServer-UdpSockets.cpp:210` |
| `ServerNetwork.MaxConnections` | `int32_t` / Server | Active | `Engine/Source/Server/Server.cpp:2137` |
| `ServerNetwork.MaxPlayers` | `int32_t` / Server | Active | `Engine/Source/Server/Server.cpp:2137` |
| `ServerNetwork.NewConnectionRatePerSec` | `int32_t` / Server | Active | `Engine/Source/Server/Server.cpp:2111` |
| `ServerNetwork.ListenRetryTime` | `int32_t` / Server | Active | `Engine/Source/Server/Server.cpp:2075` |
| `ServerNetwork.ListenRetryDelay` | `int32_t` / Server | Active | `Engine/Source/Server/Server.cpp:2074` |
| `ServerNetwork.WssPrivateKey` | `string` / Server | Active | `Engine/Source/Server/NetworkServer-WebSockets.cpp:318` |
| `ServerNetwork.WssCertificate` | `string` / Server | Active | `Engine/Source/Server/NetworkServer-WebSockets.cpp:321` |
| `ServerNetwork.ChannelSecretKey` | `string` / Server | Active | `Engine/Source/Server/Server.cpp:355` |

### ClientNetwork — 12

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `ClientNetwork.ServerHost` | `string` / Client | Active | `Engine/Source/Client/Updater.cpp:89` |
| `ClientNetwork.WebSocketHost` | `string` / Client | Active | `Engine/Source/Client/NetworkClient-Sockets.cpp:89` |
| `ClientNetwork.PingPeriod` | `int32_t` / Client | Active | `Engine/Source/Client/ClientConnection.cpp:255` |
| `ClientNetwork.PingTimeout` | `int32_t` / Client | Active | `Engine/Source/Client/ClientConnection.cpp:208` |
| `ClientNetwork.UseUdp` | `bool` / Client | Active | `Engine/Source/Client/ClientConnection.cpp:93` |
| `ClientNetwork.ProxyType` | `int32_t` / Client | Active | `Engine/Source/Client/NetworkClient-Sockets.cpp:107` |
| `ClientNetwork.ProxyHost` | `string` / Client | Active | `Engine/Source/Client/NetworkClient-Sockets.cpp:130` |
| `ClientNetwork.ProxyPort` | `int32_t` / Client | Active | `Engine/Source/Client/NetworkClient-Sockets.cpp:130` |
| `ClientNetwork.ProxyUser` | `string` / Client | Active | `Engine/Source/Client/NetworkClient-Sockets.cpp:214` |
| `ClientNetwork.ProxyPass` | `string` / Client | Active | `Engine/Source/Client/NetworkClient-Sockets.cpp:216` |
| `ClientNetwork.DebugNet` | `bool` / Client | Active | `Engine/Source/Client/ClientConnection.cpp:230` |
| `ClientNetwork.ChannelServerKeys` | `vector<string>` / Client | Active | `Engine/Source/Client/ClientConnection.cpp:323` |

### Audio — 5

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `Audio.DisableAudio` | `bool` / Client | Active | `Engine/Source/Client/AudioManager.cpp:84` |
| `Audio.SoundVolume` | `int32_t` / Client | Active | `Engine/Source/Client/AudioManager.cpp:74` |
| `Audio.MusicVolume` | `int32_t` / Client | Active | `Engine/Source/Client/AudioManager.cpp:73` |
| `Audio.SoundFileExtensions` | `vector<string>` / Client | Active | `Engine/Source/Client/AudioManager.cpp:486` |
| `Audio.MixRate` | `int32_t` / Client | Active | `Engine/Source/Frontend/Application.cpp:428` |

### View — 12

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `View.ScreenWidth` | `int32_t` / Client | Active | `Engine/Source/Frontend/ApplicationStub.cpp:43` |
| `View.ScreenHeight` | `int32_t` / Client | Active | `Engine/Source/Frontend/ApplicationStub.cpp:43` |
| `View.MonitorWidth` | `int32_t` / Client | Runtime state: move to owner | `Engine/Source/Frontend/Application.cpp:293` |
| `View.MonitorHeight` | `int32_t` / Client | Runtime state: move to owner | `Engine/Source/Frontend/Application.cpp:294` |
| `View.HideNativeCursor` | `bool` / Client | Active | `Engine/Source/Frontend/Application.cpp:550` |
| `View.FadingDuration` | `int32_t` / Client | Active | `Engine/Source/Client/HexView.cpp:127` |
| `View.MapZoomEnabled` | `bool` / Client | Active | `Engine/Source/Client/MapView.cpp:3109` |
| `View.MapDirectDraw` | `bool` / Client | Active | `Engine/Source/Client/MapView.cpp:89` |
| `View.MapRenderTargetScale` | `float32_t` / Client | Active | `Engine/Source/Client/MapView.cpp:565` |
| `View.DisableLighting` | `bool` / Client | Active | `Engine/Source/Client/MapView.cpp:98` |
| `View.DisableFog` | `bool` / Client | Active | `Engine/Source/Client/MapView.cpp:98` |
| `View.DisableIndoorMask` | `bool` / Client | Active | `Engine/Source/Client/MapView.cpp:93` |

### Geometry — 13

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `Geometry.MapHexWidth` | `int32_t` / Common | Active | `Engine/Source/Tools/Mapper.cpp:5482` |
| `Geometry.MapHexHeight` | `int32_t` / Common | Active | `Engine/Source/Tools/Mapper.cpp:5482` |
| `Geometry.MapHexLineHeight` | `int32_t` / Common | No verified consumer | Not found; see method and findings |
| `Geometry.MapTileStep` | `int32_t` / Common | Active | `Engine/Source/Tools/Mapper.cpp:4038` |
| `Geometry.MapRoofElevation` | `int32_t` / Common | Active | `Engine/Source/Tools/Mapper.cpp:5488` |
| `Geometry.MapCameraAngle` | `float32_t` / Common | Active | `Engine/Source/Client/VisualParticles.cpp:215` |
| `Geometry.MapFreeMovement` | `bool` / Common | Active | `Engine/Source/Client/MapView.cpp:3896` |
| `Geometry.MapSmoothPath` | `bool` / Common | No verified consumer | Not found; see method and findings |
| `Geometry.MapDataPrefix` | `string` / Common | Project-owned | [Scripts/MoveCursor.fos:167](../Scripts/MoveCursor.fos#L167) |
| `Geometry.CritterBlockHex` | `bool` / Common | No verified consumer | Not found; see method and findings |
| `Geometry.MaxPathFindLength` | `int32_t` / Common | Active | `Engine/Source/Client/MapView.cpp:3891` |
| `Geometry.PathFindEnclosureProbe` | `int32_t` / Common | Active | `Engine/Source/Client/MapView.cpp:3892` |
| `Geometry.PathFindCritterDetour` | `int32_t` / Common | Active | `Engine/Source/Client/MapView.cpp:3893` |

### SpriteMesh — 4

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `SpriteMesh.Enabled` | `bool` / Common | Active | `Engine/Source/Tools/SpriteMeshing.cpp:120` |
| `SpriteMesh.AlphaThreshold` | `int32_t` / Common | Active | `Engine/Source/Tools/SpriteMeshing.cpp:115` |
| `SpriteMesh.MaxTriangles` | `int32_t` / Common | Active | `Engine/Source/Tools/SpriteMeshing.cpp:116` |
| `SpriteMesh.AreaSavingsWeight` | `float32_t` / Common | Active | `Engine/Source/Tools/SpriteMeshing.cpp:117` |

### Animation — 2

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `Animation.PreviewStateAnim` | `CritterStateAnim` / Common | Active | `Engine/Source/Tools/ModelInfoBaker.cpp:2238` |
| `Animation.PreviewActionAnim` | `CritterActionAnim` / Common | Active | `Engine/Source/Tools/ModelInfoBaker.cpp:2238` |

### Render — 46

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `Render.Animation3dSmoothTime` | `int32_t` / Common | Active | `Engine/Source/Client/ModelManager.cpp:89` |
| `Render.Animation3dFPS` | `int32_t` / Common | Active | `Engine/Source/Client/VisualParticles.cpp:102` |
| `Render.HeadBone` | `string` / Common | Active; model scope candidate | `Engine/Source/Client/ModelManager.cpp:96` |
| `Render.LegBones` | `vector<string>` / Common | Active; model scope candidate | `Engine/Source/Client/ModelManager.cpp:98` |
| `Render.ModelLayerProperties` | `vector<string>` / Common | Active | `Engine/Source/Tools/AnimationViewer.cpp:473` |
| `Render.WindowCentered` | `bool` / Common | Active | `Engine/Source/Frontend/Application.cpp:1161` |
| `Render.WindowResizable` | `bool` / Common | Active | `Engine/Source/Frontend/Application.cpp:1111` |
| `Render.HeadlessWindow` | `bool` / Common | Active | `Engine/Source/Applications/MapperApp.cpp:78` |
| `Render.NullRenderer` | `bool` / Common | Active | `Engine/Source/Tools/Mapper.cpp:176` |
| `Render.ForceOpenGL` | `bool` / Common | Active | `Engine/Source/Frontend/Application.cpp:462` |
| `Render.ForceDirect3D` | `bool` / Common | Active | `Engine/Source/Frontend/Application.cpp:469` |
| `Render.ForceMetal` | `bool` / Common | Active | `Engine/Source/Frontend/Application.cpp:476` |
| `Render.ForceVulkan` | `bool` / Common | Active | `Engine/Source/Frontend/Application.cpp:483` |
| `Render.ForceSDLGpu` | `bool` / Common | Active | `Engine/Source/Frontend/Application.cpp:489` |
| `Render.ForceGlslEsProfile` | `bool` / Common | Active | `Engine/Source/Frontend/Rendering-OpenGL.cpp:398` |
| `Render.AllowSoftwareRenderer` | `bool` / Common | Active | `Engine/Source/Frontend/Rendering-Direct3D.cpp:385` |
| `Render.SDLGpuDriver` | `string` / Common | Active | `Engine/Source/Frontend/Rendering-SDLGpu.cpp:624` |
| `Render.RenderDebug` | `bool` / Common | Active | `Engine/Source/Common/Settings.cpp:298` |
| `Render.DrawWireframe` | `bool` / Common | Active | `Engine/Source/Tools/SparkParticleEditor.cpp:367` |
| `Render.VSync` | `bool` / Common | Active | `Engine/Source/Applications/ParticleViewerApp.cpp:170` |
| `Render.AlwaysOnTop` | `bool` / Common | Active | `Engine/Source/Client/SpriteManager.cpp:107` |
| `Render.Fullscreen` | `bool` / Common | Active | `Engine/Source/Frontend/ApplicationStub.cpp:44` |
| `Render.Brightness` | `int32_t` / Common | Active | `Engine/Source/Client/SpriteManager.cpp:1081` |
| `Render.Sleep` | `int32_t` / Common | Active | `Engine/Source/Applications/ParticleViewerApp.cpp:170` |
| `Render.FixedFPS` | `int32_t` / Common | Active | `Engine/Source/Applications/ParticleViewerApp.cpp:170` |
| `Render.CritterTurnAngle` | `float32_t` / Common | Active | `Engine/Source/Client/ModelInstance.cpp:858` |
| `Render.CritterBodyTurnFactor` | `float32_t` / Common | Active | `Engine/Source/Client/ModelInstance.cpp:1413` |
| `Render.CritterHeadTurnFactor` | `float32_t` / Common | Active | `Engine/Source/Client/ModelInstance.cpp:1416` |
| `Render.ModelProjFactor` | `float32_t` / Common | Active | `Engine/Source/Tools/SparkParticleEditor.cpp:542` |
| `Render.ModelSpriteMaxTextureWidth` | `int32_t` / Common | Active | `Engine/Source/Client/ModelSprites.cpp:501` |
| `Render.ModelSpriteMaxTextureHeight` | `int32_t` / Common | Active | `Engine/Source/Client/ModelSprites.cpp:501` |
| `Render.ModelDirectDraw` | `bool` / Common | Active | `Engine/Source/Client/ModelSprites.cpp:144` |
| `Render.MapMaxElevation` | `int32_t` / Common | Active | `Engine/Source/Client/MapView.cpp:112` |
| `Render.EggEllipseWidthExt` | `int32_t` / Common | Active | `Engine/Source/Client/MapView.cpp:2477` |
| `Render.EggEllipseHeightExt` | `int32_t` / Common | Active | `Engine/Source/Client/MapView.cpp:2478` |
| `Render.EggTransparencyTransitionFactor` | `float32_t` / Common | Active | `Engine/Source/Client/SpriteManager.cpp:705` |
| `Render.AtlasLinearFiltration` | `bool` / Common | Active | `Engine/Source/Client/TextureAtlas.cpp:503` |
| `Render.DefaultParticleDrawWidth` | `int32_t` / Common | Active | `Engine/Source/Client/VisualParticles.cpp:207` |
| `Render.DefaultParticleDrawHeight` | `int32_t` / Common | Active | `Engine/Source/Client/VisualParticles.cpp:207` |
| `Render.RecreateClientOnError` | `bool` / Common | Active | `Engine/Source/Applications/ClientLib.cpp:336` |
| `Render.ImGuiColorStyle` | `string` / Common | Active | `Engine/Source/Frontend/Application.cpp:641` |
| `Render.ImGuiDefaultEffect` | `string` / Common | Active | `Engine/Source/Client/EffectManager.cpp:189` |
| `Render.ImGuiFontTextureSize` | `int32_t` / Common | Active | `Engine/Source/Frontend/Application.cpp:674` |
| `Render.SpriteHitValue` | `int32_t` / Common | Active | `Engine/Source/Client/SpriteManager.h:209` |
| `Render.CritterStubSpriteName` | `string` / Common | Active | `Engine/Source/Client/ResourceManager.cpp:82` |
| `Render.ItemStubSpriteName` | `string` / Common | Active | `Engine/Source/Client/ResourceManager.cpp:94` |

### Web — 11

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `Web.AutoResize` | `bool` / Client | Active | `Engine/Source/Common/WebRelated.cpp:368` |
| `Web.LoadingImage` | `string` / Client | Active | `Engine/BuildTools/package.py:1952` |
| `Web.BackgroundColor` | `string` / Client | Active | `Engine/BuildTools/package.py:1953` |
| `Web.ScreenHeightPercent` | `int32_t` / Client | Active | `Engine/Source/Common/WebRelated.cpp:437` |
| `Web.AspectFactor` | `float32_t` / Client | Active | `Engine/Source/Common/WebRelated.cpp:441` |
| `Web.HorizontalPosFactor` | `float32_t` / Client | Active | `Engine/Source/Common/WebRelated.cpp:492` |
| `Web.VerticalPosFactor` | `float32_t` / Client | Active | `Engine/Source/Common/WebRelated.cpp:493` |
| `Web.MinWidth` | `int32_t` / Client | Active | `Engine/Source/Common/WebRelated.cpp:432` |
| `Web.MinHeight` | `int32_t` / Client | Active | `Engine/Source/Common/WebRelated.cpp:433` |
| `Web.MaxWidth` | `int32_t` / Client | Active | `Engine/Source/Common/WebRelated.cpp:434` |
| `Web.MaxHeight` | `int32_t` / Client | Active | `Engine/Source/Common/WebRelated.cpp:435` |

### Android — 11

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `Android.PackageName` | `string` / Server | Active | `Engine/BuildTools/package.py:2115` |
| `Android.VersionCode` | `int32_t` / Server | Active | `Engine/BuildTools/package.py:2116` |
| `Android.MinSdk` | `int32_t` / Server | Active | `Engine/BuildTools/package.py:2118` |
| `Android.TargetSdk` | `int32_t` / Server | Active | `Engine/BuildTools/package.py:2119` |
| `Android.CompileSdk` | `int32_t` / Server | Active | `Engine/BuildTools/package.py:2120` |
| `Android.ScreenOrientation` | `string` / Server | Active | `Engine/BuildTools/package.py:2121` |
| `Android.Icon` | `string` / Server | Active | `Engine/BuildTools/package.py:2055` |
| `Android.Keystore` | `string` / Server | Active | `Engine/BuildTools/package.py:2122` |
| `Android.KeystorePassword` | `string` / Server | Active | `Engine/BuildTools/package.py:2123` |
| `Android.KeyAlias` | `string` / Server | Active | `Engine/BuildTools/package.py:2124` |
| `Android.KeyPassword` | `string` / Server | Active | `Engine/BuildTools/package.py:2125` |

### Packaging — 3

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `Packaging.CodeSigningHook` | `string` / Server | Active | `Engine/BuildTools/package.py:2233` |
| `Packaging.AppIcon` | `string` / Server | Active | `Engine/BuildTools/package.py:2364` |
| `Packaging.MsiUpgradeCode` | `string` / Server | Active | `Engine/BuildTools/package.py:2357` |

### Timer — 1

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `Timer.DeltaTimeCap` | `int32_t` / Common | Active | `Engine/Source/Common/Timer.cpp:120` |

### Baking — 23

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `Baking.ForceBaking` | `bool` / Common | Active | `Engine/Source/Tools/BakingReport.cpp:54` |
| `Baking.SingleThreadBaking` | `bool` / Common | Active | `Engine/Source/Tools/ModelInfoBaker.cpp:2109` |
| `Baking.IgnoreMissingBakerWarning` | `bool` / Common | Active | `Engine/Source/Frontend/ApplicationInit.cpp:425` |
| `Baking.PrebakeOnStartup` | `bool` / Common | Active | `Engine/Source/Frontend/ApplicationInit.cpp:146` |
| `Baking.IgnoreInputDirs` | `vector<string>` / Common | Active | `Engine/Source/Common/Settings.cpp:317` |
| `Baking.PreciseModelBounds` | `bool` / Common | Active | `Engine/Source/Tools/ModelInfoBaker.cpp:1787` |
| `Baking.ModelAttachmentMinExtent` | `float32_t` / Common | Active | `Engine/Source/Tools/ModelInfoBaker.cpp:1170` |
| `Baking.ModelAttachmentMaxExtent` | `float32_t` / Common | Active | `Engine/Source/Tools/ModelInfoBaker.cpp:1167` |
| `Baking.RawCopyFileExtensions` | `vector<string>` / Common | Active | `Engine/Source/Tools/RawCopyBaker.cpp:58` |
| `Baking.AudioVorbisQuality` | `float32_t` / Common | Active | `Engine/Source/Tools/AudioBaker.cpp:90` |
| `Baking.Direct3DLevel9Shaders` | `bool` / Common | Active | `Engine/Source/Tools/EffectBaker.cpp:458` |
| `Baking.ProtoFileExtensions` | `vector<string>` / Common | Active | `Engine/Source/Tools/ProtoTextBaker.cpp:69` |
| `Baking.AllowRepeatedProtoParents` | `bool` / Common | Active | `Engine/Source/Tools/ProtoTextBaker.cpp:185` |
| `Baking.BakeLanguages` | `vector<string>` / Common | Active | `Engine/Source/Tools/TextBaker.cpp:43` |
| `Baking.BakeOutput` | `string` / Common | Active | `Engine/Source/Tools/ProtoBaker.cpp:101` |
| `Baking.ServerResources` | `string` / Common | Active | `Engine/Source/Server/UpdaterBackend.cpp:214` |
| `Baking.ClientResources` | `string` / Common | Active | `Engine/Source/Server/UpdaterBackend.cpp:109` |
| `Baking.PlatformBinaries` | `string` / Common | Active | `Engine/Source/Server/UpdaterBackend.cpp:123` |
| `Baking.CacheResources` | `string` / Common | Active | `Engine/Source/Tools/ProtoBaker.cpp:101` |
| `Baking.ResourcePackCompressLevel` | `int32_t` / Common | Active | `Engine/BuildTools/package.py:940` |
| `Baking.ResourcePackMinCompressGain` | `int32_t` / Common | Active | `Engine/BuildTools/package.py:943` |
| `Baking.BundleCompressLevel` | `int32_t` / Common | Active | `Engine/BuildTools/package.py:944` |
| `Baking.BootstrapGameSettings` | `vector<string>` / Common | Active | `Engine/Source/Tools/ConfigBaker.cpp:104` |

### Critter — 3

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `Critter.CritterSlotEnabled` | `vector<bool>` / Server | Active | `Engine/Source/Tools/Mapper.cpp:2033` |
| `Critter.CritterSlotSendData` | `vector<bool>` / Server | Active | `Engine/Source/Server/Item.cpp:281` |
| `Critter.CritterSlotMultiItem` | `vector<bool>` / Server | Active | `Engine/Source/Scripting/ServerCritterScriptMethods.cpp:617` |

### CritterView — 1

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `CritterView.NameOffset` | `int32_t` / Client | Active | `Engine/Source/Tools/AnimationViewer.cpp:800` |

### Hex — 6

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `Hex.ScrollFixedDt` | `int32_t` / Client | Active | `Engine/Source/Client/MapView.cpp:540` |
| `Hex.ScrollSpeed` | `int32_t` / Client | Active | `Engine/Source/Client/MapView.cpp:3099` |
| `Hex.ZoomSpeed` | `int32_t` / Client | Active | `Engine/Source/Client/MapView.cpp:3143` |
| `Hex.FullscreenMouseScroll` | `bool` / Client | Active | `Engine/Source/Tools/Mapper.cpp:95` |
| `Hex.WindowedMouseScroll` | `bool` / Client | Active | `Engine/Source/Tools/Mapper.cpp:96` |
| `Hex.ScrollBlockSize` | `int32_t` / Client | Active | `Engine/Source/Client/MapView.cpp:2220` |

### DataBase — 8

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `DataBase.OpLogEnabled` | `bool` / Server | Active | `Engine/Source/Server/DataBase.cpp:225` |
| `DataBase.OpLogPath` | `string` / Server | Active | `Engine/Source/Server/DataBase.cpp:275` |
| `DataBase.ReconnectRetryPeriod` | `int32_t` / Server | Active | `Engine/Source/Server/DataBase.cpp:228` |
| `DataBase.PanicOpLogSizeThreshold` | `int32_t` / Server | Active | `Engine/Source/Server/DataBase.cpp:226` |
| `DataBase.PanicShutdownTimeout` | `int32_t` / Server | Active | `Engine/Source/Server/DataBase.cpp:227` |
| `DataBase.JsonIndent` | `int32_t` / Server | Active | `Engine/Source/Server/DataBase-Json.cpp:58` |
| `DataBase.MongoEscapeChar` | `string` / Server | Active | `Engine/Source/Server/DataBase-Mongo.cpp:68` |
| `DataBase.CustomCollections` | `vector<string>` / Server | Active | `Engine/Source/Server/Server.cpp:391` |

### Input — 2

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `Input.DisableGamepad` | `bool` / Client | Active | `Engine/Source/Frontend/Application.cpp:386` |
| `Input.ConsoleHistorySize` | `int32_t` / Client | Active | `Engine/Source/Tools/Mapper.cpp:189` |

### Mapper — 7

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `Mapper.StartMap` | `string` / Client | Active | `Engine/Source/Tools/Mapper.cpp:157` |
| `Mapper.StartHexX` | `int32_t` / Client | Active | `Engine/Source/Tools/Mapper.cpp:161` |
| `Mapper.StartHexY` | `int32_t` / Client | Active | `Engine/Source/Tools/Mapper.cpp:161` |
| `Mapper.ParticlePreviewEffect` | `string` / Client | Active | `Engine/Source/Tools/ParticleEditor.cpp:119` |
| `Mapper.ParticlePreviewSeed` | `int32_t` / Client | Active | `Engine/Source/Tools/ParticleEditor.cpp:125` |
| `Mapper.ParticlePreviewScale` | `float32_t` / Client | Active | `Engine/Source/Tools/ParticleEditor.cpp:126` |
| `Mapper.ParticlePreviewPrewarm` | `bool` / Client | Active | `Engine/Source/Tools/ParticleEditor.cpp:127` |

### Client — 16

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `Client.UpdaterInfoDelay` | `int32_t` / Client | Active | `Engine/Source/Client/Updater.cpp:233` |
| `Client.UpdaterInfoPos` | `int32_t` / Client | Active | `Engine/Source/Client/Updater.cpp:236` |
| `Client.DefaultSplash` | `string` / Client | Active | `Engine/Source/Client/Updater.cpp:108` |
| `Client.DefaultSplashPack` | `string` / Client | Active | `Engine/Source/Client/Updater.cpp:105` |
| `Client.ClientPropertiesPackData` | `bool` / Client | Active | `Engine/Source/Client/ClientEntity.cpp:40` |
| `Client.ForceEmbeddedRuntime` | `bool` / Client | Active | `Engine/Source/Applications/ClientApp.cpp:596` |
| `Client.Language` | `string` / Client | Active | `Engine/Source/Tools/Mapper.cpp:99` |
| `Client.DirectMoveTraceSteps` | `int32_t` / Client | Active | `Engine/Source/Client/Client.cpp:3178` |
| `Client.DirectMoveExtendAheadSteps` | `int32_t` / Client | Active | `Engine/Source/Client/Client.cpp:3168` |
| `Client.DirectMoveLeaseSteps` | `int32_t` / Client | Active | `Engine/Source/Client/Client.cpp:3159` |
| `Client.DirectMoveLeaseRenewSteps` | `int32_t` / Client | Active | `Engine/Source/Client/Client.cpp:3158` |
| `Client.DirectMoveRetargetMinMs` | `int32_t` / Client | Active | `Engine/Source/Client/Client.cpp:3095` |
| `Client.DirectMoveRetargetImmediateAngle` | `int32_t` / Client | Active | `Engine/Source/Client/Client.cpp:3094` |
| `Client.DirectMoveSlide` | `bool` / Client | Active | `Engine/Source/Client/Client.cpp:3228` |
| `Client.MoveCatchUpRate` | `float32_t` / Client | Active | `Engine/Source/Client/CritterHexView.cpp:693` |
| `Client.MoveCatchUpSmoothMaxMs` | `int32_t` / Client | Active | `Engine/Source/Client/Client.cpp:1603` |

### Server — 24

| Key | Type / role | Assessment | Verified use location |
| --- | --- | --- | --- |
| `Server.DbStorage` | `string` / Server | Active | `Engine/Source/Server/Server.cpp:448` |
| `Server.ServerPropertiesPackData` | `bool` / Server | Active | `Engine/Source/Server/ServerEntity.cpp:40` |
| `Server.NoStart` | `bool` / Server | Active | `Engine/Source/Applications/ServerApp.cpp:173` |
| `Server.AutoStartClientOnServer` | `int32_t` / Server | Active | `Engine/Source/Applications/ServerHeadlessApp.cpp:69` |
| `Server.ServerWidth` | `int32_t` / Server | Active | `Engine/Source/Applications/ServerApp.cpp:77` |
| `Server.ServerHeight` | `int32_t` / Server | Active | `Engine/Source/Applications/ServerApp.cpp:77` |
| `Server.CollapseLogOnStart` | `bool` / Server | Active | `Engine/Source/Applications/ServerApp.cpp:518` |
| `Server.MaxServerLogLines` | `int32_t` / Server | Active | `Engine/Source/Applications/ServerApp.cpp:102` |
| `Server.LockMaxWaitTime` | `int32_t` / Server | Active | `Engine/Source/Server/Server.cpp:1549` |
| `Server.WorkerThreads` | `int32_t` / Server | Active | `Engine/Source/Server/Server.cpp:677` |
| `Server.SingleThreadedLogic` | `bool` / Server | Active | `Engine/Source/Server/Server.cpp:677` |
| `Server.WriteHealthFile` | `bool` / Server | Active | `Engine/Source/Server/Server.cpp:261` |
| `Server.ProtoMapGridType` | `string` / Server | Active | `Engine/Source/Server/StaticMap.cpp:199` |
| `Server.MapInstanceGridType` | `string` / Server | Active | `Engine/Source/Server/MapManager.cpp:58` |
| `Server.EntityStartId` | `int64_t` / Server | Active | `Engine/Source/Server/EntityManager.cpp:334` |
| `Server.EntityIdReserveBatch` | `int64_t` / Server | Active | `Engine/Source/Server/EntityManager.cpp:1495` |
| `Server.SyncPeriodMs` | `int32_t` / Server | Active | `Engine/Source/Server/Server.cpp:836` |
| `Server.FrameTimePeriodNs` | `int32_t` / Server | Active | `Engine/Source/Server/Server.cpp:843` |
| `Server.ConnectionProcessPeriodMs` | `int32_t` / Server | Active | `Engine/Source/Server/Server.cpp:910` |
| `Server.CritterMovingPeriodMs` | `int32_t` / Server | Active | `Engine/Source/Server/Server.cpp:3922` |
| `Server.MoveBridgeReportHexes` | `int32_t` / Server | Active | `Engine/Source/Server/Server.cpp:3528` |
| `Server.MoveFinishCatchUpMaxMs` | `int32_t` / Server | Active | `Engine/Source/Server/Server.cpp:3922` |
| `Server.HealthFilePeriodMs` | `int32_t` / Server | Active | `Engine/Source/Server/Server.cpp:287` |
| `Server.ShutdownGraceMs` | `int32_t` / Server | Active | `Engine/Source/Server/Server.cpp:1142` |
