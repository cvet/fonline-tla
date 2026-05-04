#include "Common.h"

#include "Dialogs.h"
#include "Server.h"

FO_USING_NAMESPACE();

struct ServerImage
{
    vector<ucolor> Data {};
    int32_t Width {};
    int32_t Height {};
};

struct ServerExtData
{
    int32_t LookMinimum {};
    raw_ptr<const Property> InSneakMode {};
    raw_ptr<const Property> SneakCoefficient {};
    raw_ptr<const Property> IsAlwaysView {};
    raw_ptr<const Property> IsTrap {};
    raw_ptr<const Property> TrapValue {};
    vector<unique_ptr<ServerImage>> ServerImages {};
    unique_ptr<DialogManager> DialogMngr {};
};

static constexpr int32_t TLA_SNEAK_DIVIDER = 6;

static auto GetServerExtData(ServerEngine* server) -> ServerExtData&
{
    return *reinterpret_cast<ServerExtData*>(server->UserData.get());
}

static auto GetServerExtData(const ServerEngine* server) -> const ServerExtData&
{
    return *reinterpret_cast<const ServerExtData*>(server->UserData.get());
}

FO_BEGIN_NAMESPACE
///@ EngineHook
FO_SCRIPT_API void ServerInitHook(ServerEngine* server);
///@ EngineHook
FO_SCRIPT_API CritterVisibilityMode CheckCritterVisibilityHook(const ServerEngine* server, const Map* map, const Critter* cr, const Critter* target);
///@ EngineHook
FO_SCRIPT_API bool CheckItemVisibilityHook(const ServerEngine* server, const Map* map, const Critter* cr, const Item* item);
///@ ExportMethod
FO_SCRIPT_API isize32 Server_Game_LoadImage(ServerEngine* server, uint32_t imageSlot, string_view imageName);
///@ ExportMethod
FO_SCRIPT_API ucolor Server_Game_GetImageColor(ServerEngine* server, uint32_t imageSlot, ipos32 pos);
///@ ExportMethod
FO_SCRIPT_API DialogPack* Server_Game_GetDialogPack(ServerEngine* server, hstring packId);
///@ ExportMethod
FO_SCRIPT_API string Server_Game_RunSpeechScript(ServerEngine* server, DialogSpeech* speech, Critter* cr, Critter* talker);
///@ ExportMethod
FO_SCRIPT_API bool Server_Game_DialogScriptDemand(ServerEngine* server, DialogAnswerReq* demand, Critter* master, Critter* slave);
///@ ExportMethod
FO_SCRIPT_API int32_t Server_Game_DialogScriptResult(ServerEngine* server, DialogAnswerReq* result, Critter* master, Critter* slave);
///@ ExportMethod
FO_SCRIPT_API bool Server_Critter_IsFree(Critter* server);
///@ ExportMethod
FO_SCRIPT_API bool Server_Critter_IsBusy(Critter* server);
///@ ExportMethod
FO_SCRIPT_API void Server_Critter_Wait(Critter* server, int32_t ms);
FO_END_NAMESPACE

void FO_NAMESPACE ServerInitHook(ServerEngine* server)
{
    FO_STACK_TRACE_ENTRY();

    server->UserData = unique_del_ptr<uint8_t>(reinterpret_cast<uint8_t*>(SafeAlloc::MakeRaw<ServerExtData>()), [](const uint8_t* ptr) FO_DEFERRED {
        const auto* ext_data_ptr = reinterpret_cast<const ServerExtData*>(ptr);
        delete ext_data_ptr;
    });

    if (IsTestingInProgress) {
        return;
    }

    auto& ext_data = GetServerExtData(server);

    ext_data.LookMinimum = strvex(server->Settings.GetCustomSetting("Look.LookMinimum")).to_int32();
    FO_RUNTIME_ASSERT(ext_data.LookMinimum != 0);

    const auto* cr_props = server->GetPropertyRegistrator(Critter::ENTITY_TYPE_NAME);
    ext_data.InSneakMode = cr_props->FindProperty("InSneakMode");
    FO_RUNTIME_ASSERT(ext_data.InSneakMode);
    ext_data.SneakCoefficient = cr_props->FindProperty("SneakCoefficient");
    FO_RUNTIME_ASSERT(ext_data.SneakCoefficient);

    const auto* item_props = server->GetPropertyRegistrator(Item::ENTITY_TYPE_NAME);
    ext_data.IsAlwaysView = item_props->FindProperty("IsAlwaysView");
    FO_RUNTIME_ASSERT(ext_data.IsAlwaysView);
    ext_data.IsTrap = item_props->FindProperty("IsTrap");
    FO_RUNTIME_ASSERT(ext_data.IsTrap);
    ext_data.TrapValue = item_props->FindProperty("TrapValue");
    FO_RUNTIME_ASSERT(ext_data.TrapValue);

    ext_data.DialogMngr = SafeAlloc::MakeUnique<DialogManager>(*server);
    ext_data.DialogMngr->LoadFromResources(server->Resources);
}

CritterVisibilityMode FO_NAMESPACE CheckCritterVisibilityHook(const ServerEngine* server, const Map* map, const Critter* cr, const Critter* target)
{
    FO_STACK_TRACE_ENTRY();

    if (IsTestingInProgress) {
        return GeometryHelper::GetDistance(cr->GetHex(), target->GetHex()) <= cr->GetLookDistance() ? CritterVisibilityMode::Full : CritterVisibilityMode::None;
    }

    const int32_t dist = GeometryHelper::GetDistance(cr->GetHex(), target->GetHex());
    int32_t look_dist = cr->GetLookDistance();

    if (dist > look_dist) {
        return CritterVisibilityMode::None;
    }

    const auto trace_output = server->MapMngr.TracePath(map, cr->GetHex(), target->GetHex());

    if (!trace_output.IsFullTrace) {
        return CritterVisibilityMode::None;
    }

    const auto& ext_data = GetServerExtData(server);
    const auto& target_props = target->GetProperties();

    if (target_props.GetValue<bool>(ext_data.InSneakMode.get())) {
        const int32_t sneak_penalty = target_props.GetValue<int32_t>(ext_data.SneakCoefficient.get()) / TLA_SNEAK_DIVIDER;
        look_dist = look_dist > sneak_penalty ? look_dist - sneak_penalty : 0;
    }

    look_dist = std::max(look_dist, ext_data.LookMinimum);
    return look_dist >= dist ? CritterVisibilityMode::Full : CritterVisibilityMode::None;
}

bool FO_NAMESPACE CheckItemVisibilityHook(const ServerEngine* server, const Map* map, const Critter* cr, const Item* item)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(map);

    if (IsTestingInProgress) {
        return GeometryHelper::GetDistance(cr->GetHex(), item->GetHex()) <= cr->GetLookDistance();
    }

    const auto& ext_data = GetServerExtData(server);
    const auto& props = item->GetProperties();

    if (props.GetValue<bool>(ext_data.IsAlwaysView.get())) {
        return true;
    }

    const int32_t dist = GeometryHelper::GetDistance(cr->GetHex(), item->GetHex());
    int32_t look_dist = cr->GetLookDistance();

    if (props.GetValue<bool>(ext_data.IsTrap.get())) {
        const int32_t trap_penalty = props.GetValue<int32_t>(ext_data.TrapValue.get());
        look_dist = look_dist > trap_penalty ? look_dist - trap_penalty : 0;
    }

    look_dist = std::max(look_dist, ext_data.LookMinimum);
    return look_dist >= dist;
}

isize32 FO_NAMESPACE Server_Game_LoadImage(ServerEngine* server, uint32_t imageSlot, string_view imageName)
{
    FO_STACK_TRACE_ENTRY();

    if (IsTestingInProgress) {
        ignore_unused(server, imageSlot, imageName);
        return {};
    }

    auto& ext_data = GetServerExtData(server);

    if (imageSlot >= numeric_cast<uint32_t>(ext_data.ServerImages.size())) {
        ext_data.ServerImages.resize(imageSlot + 1);
    }
    if (ext_data.ServerImages[imageSlot]) {
        ext_data.ServerImages[imageSlot] = nullptr;
    }

    if (imageName.empty()) {
        return {};
    }

    const auto file = server->Resources.ReadFile(imageName);

    if (!file) {
        throw ScriptException("File not found", imageName);
    }

    auto reader = file.GetReader();

    const auto check_number = reader.GetUInt8();

    if (check_number != 42) {
        throw ScriptException("File is not image", imageName);
    }

    const auto frames_count = reader.GetLEUInt16();

    if (frames_count != 1) {
        throw ScriptException("File must contain only one frame", imageName);
    }

    [[maybe_unused]] const auto ticks = reader.GetLEUInt16();

    const auto dirs = reader.GetUInt8();

    if (dirs != 1) {
        throw ScriptException("File must contain only one dir", imageName);
    }

    [[maybe_unused]] const auto ox = reader.GetLEInt16();
    [[maybe_unused]] const auto oy = reader.GetLEInt16();

    const auto is_spr_ref = reader.GetUInt8();
    FO_RUNTIME_ASSERT(is_spr_ref == 0);

    const auto width = reader.GetLEUInt16();
    const auto height = reader.GetLEUInt16();
    [[maybe_unused]] const auto nx = reader.GetLEInt16();
    [[maybe_unused]] const auto ny = reader.GetLEInt16();
    const auto* data = reader.GetCurBuf();

    reader.GoForward(numeric_cast<size_t>(width) * height * 4);

    const auto check_number2 = reader.GetUInt8();
    FO_RUNTIME_ASSERT(check_number2 == 42);

    auto simg = SafeAlloc::MakeUnique<ServerImage>();
    simg->Width = width;
    simg->Height = height;
    simg->Data.resize(numeric_cast<size_t>(width) * height);
    MemCopy(simg->Data.data(), data, simg->Data.size() * sizeof(ucolor));

    ext_data.ServerImages[imageSlot] = std::move(simg);

    return {width, height};
}

ucolor FO_NAMESPACE Server_Game_GetImageColor(ServerEngine* server, uint32_t imageSlot, ipos32 pos)
{
    FO_STACK_TRACE_ENTRY();

    auto& ext_data = GetServerExtData(server);

    if (imageSlot >= numeric_cast<uint32_t>(ext_data.ServerImages.size()) || !ext_data.ServerImages[imageSlot]) {
        throw ScriptException("Image not loaded");
    }

    auto& simg = ext_data.ServerImages[imageSlot];

    if (pos.x < 0 || pos.y < 0 || pos.x >= simg->Width || pos.y >= simg->Height) {
        throw ScriptException("Invalid coords arg");
    }

    const auto result = simg->Data[pos.y * simg->Width + pos.x];
    return result;
}

DialogPack* FO_NAMESPACE Server_Game_GetDialogPack(ServerEngine* server, hstring packId)
{
    FO_STACK_TRACE_ENTRY();

    auto& ext_data = GetServerExtData(server);
    auto* pack = ext_data.DialogMngr->GetDialog(packId);

    if (pack == nullptr) {
        BreakIntoDebugger();
        return nullptr;
    }

    return pack;
}

string FO_NAMESPACE Server_Game_RunSpeechScript(ServerEngine* server, DialogSpeech* speech, Critter* cr, Critter* talker)
{
    FO_STACK_TRACE_ENTRY();

    string lexems;

    if (speech->DlgScriptFuncName) {
        bool failed = false;

        if (auto func = server->FindFunc<void, Critter*, Critter*, string&>(speech->DlgScriptFuncName); func && !func.Call(cr, talker, lexems)) {
            failed = true;
        }
        if (auto func = server->FindFunc<uint32_t, Critter*, Critter*, string&>(speech->DlgScriptFuncName); func && !func.Call(cr, talker, lexems)) {
            failed = true;
        }

        if (failed) {
            return "!";
        }
    }

    return lexems;
}

bool FO_NAMESPACE Server_Game_DialogScriptDemand(ServerEngine* server, DialogAnswerReq* demand, Critter* master, Critter* slave)
{
    FO_STACK_TRACE_ENTRY();

    const auto call_demand = [server, demand, master, slave]<typename... TArgs>(const TArgs&... args) -> bool {
        auto func = server->FindFunc<bool, Critter*, Critter*, TArgs...>(demand->AnswerScriptFuncName);
        return func && func.HasAttribute("DialogDemand") && func.Call(master, slave, args...) && func.GetResult();
    };

    switch (demand->ValuesCount) {
    case 0:
        return call_demand();
    case 1:
        return call_demand(demand->ValueExt0);
    case 2:
        return call_demand(demand->ValueExt0, demand->ValueExt1);
    case 3:
        return call_demand(demand->ValueExt0, demand->ValueExt1, demand->ValueExt2);
    case 4:
        return call_demand(demand->ValueExt0, demand->ValueExt1, demand->ValueExt2, demand->ValueExt3);
    case 5:
        return call_demand(demand->ValueExt0, demand->ValueExt1, demand->ValueExt2, demand->ValueExt3, demand->ValueExt4);
    default:
        FO_UNREACHABLE_PLACE();
    }
}

int32_t FO_NAMESPACE Server_Game_DialogScriptResult(ServerEngine* server, DialogAnswerReq* result, Critter* master, Critter* slave)
{
    FO_STACK_TRACE_ENTRY();

    const auto call_result_int = [server, result, master, slave]<typename... TArgs>(const TArgs&... args) -> optional<int32_t> {
        auto func = server->FindFunc<int32_t, Critter*, Critter*, TArgs...>(result->AnswerScriptFuncName);

        if (func && func.HasAttribute("DialogResult") && func.Call(master, slave, args...)) {
            return func.GetResult();
        }

        return std::nullopt;
    };

    const auto call_result_void = [server, result, master, slave]<typename... TArgs>(const TArgs&... args) -> bool {
        auto func = server->FindFunc<void, Critter*, Critter*, TArgs...>(result->AnswerScriptFuncName);
        return func && func.HasAttribute("DialogResult") && func.Call(master, slave, args...);
    };

    switch (result->ValuesCount) {
    case 0:
        if (const auto res = call_result_int()) {
            return *res;
        }
        break;
    case 1:
        if (const auto res = call_result_int(result->ValueExt0)) {
            return *res;
        }
        break;
    case 2:
        if (const auto res = call_result_int(result->ValueExt0, result->ValueExt1)) {
            return *res;
        }
        break;
    case 3:
        if (const auto res = call_result_int(result->ValueExt0, result->ValueExt1, result->ValueExt2)) {
            return *res;
        }
        break;
    case 4:
        if (const auto res = call_result_int(result->ValueExt0, result->ValueExt1, result->ValueExt2, result->ValueExt3)) {
            return *res;
        }
        break;
    case 5:
        if (const auto res = call_result_int(result->ValueExt0, result->ValueExt1, result->ValueExt2, result->ValueExt3, result->ValueExt4)) {
            return *res;
        }
        break;
    default:
        FO_UNREACHABLE_PLACE();
    }

    switch (result->ValuesCount) {
    case 0:
        if (!call_result_void()) {
            return 0;
        }
        break;
    case 1:
        if (!call_result_void(result->ValueExt0)) {
            return 0;
        }
        break;
    case 2:
        if (!call_result_void(result->ValueExt0, result->ValueExt1)) {
            return 0;
        }
        break;
    case 3:
        if (!call_result_void(result->ValueExt0, result->ValueExt1, result->ValueExt2)) {
            return 0;
        }
        break;
    case 4:
        if (!call_result_void(result->ValueExt0, result->ValueExt1, result->ValueExt2, result->ValueExt3)) {
            return 0;
        }
        break;
    case 5:
        if (!call_result_void(result->ValueExt0, result->ValueExt1, result->ValueExt2, result->ValueExt3, result->ValueExt4)) {
            return 0;
        }
        break;
    default:
        FO_UNREACHABLE_PLACE();
    }

    return 0;
}

bool FO_NAMESPACE Server_Critter_IsFree(Critter* server)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(server);
    return true;
}

bool FO_NAMESPACE Server_Critter_IsBusy(Critter* server)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(server);
    return false;
}

void FO_NAMESPACE Server_Critter_Wait(Critter* server, int32_t ms)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(server, ms);
}
