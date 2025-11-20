#include "Common.h"

#include "Server.h"

FO_USING_NAMESPACE();

FO_BEGIN_NAMESPACE();
///@ EngineHook
FO_SCRIPT_API void InitServerEngine(FOServer* server);
///@ ExportMethod
FO_SCRIPT_API void Server_Game_LoadImage(FOServer* server, int32 imageSlot, string_view imageName);
///@ ExportMethod
FO_SCRIPT_API ucolor Server_Game_GetImageColor(FOServer* server, int32 imageSlot, int32 x, int32 y);
///@ ExportMethod
FO_SCRIPT_API bool Server_Critter_IsFree(Critter* server);
///@ ExportMethod
FO_SCRIPT_API bool Server_Critter_IsBusy(Critter* server);
///@ ExportMethod
FO_SCRIPT_API void Server_Critter_Wait(Critter* server, int32 ms);
FO_END_NAMESPACE();

struct ServerImage
{
    vector<ucolor> Data {};
    int32 Width {};
    int32 Height {};
};

struct ServerExtData
{
    vector<unique_ptr<ServerImage>> ServerImages {};
};

static auto GetServerExtData(FOServer* server) -> ServerExtData&
{
    return *reinterpret_cast<ServerExtData*>(server->UserData.get());
}

void FO_NAMESPACE InitServerEngine(FOServer* server)
{
    FO_STACK_TRACE_ENTRY();

    server->UserData = unique_del_ptr<uint8>(reinterpret_cast<uint8*>(SafeAlloc::MakeRaw<ServerExtData>()), [](const uint8* ptr) {
        const auto* ext_data_ptr = reinterpret_cast<const ServerExtData*>(ptr);
        delete ext_data_ptr;
    });
}

void FO_NAMESPACE Server_Game_LoadImage(FOServer* server, int32 imageSlot, string_view imageName)
{
    FO_STACK_TRACE_ENTRY();

    auto& ext_data = GetServerExtData(server);

    if (imageSlot < 0 || imageSlot >= static_cast<int32>(ext_data.ServerImages.size())) {
        ext_data.ServerImages.resize(imageSlot + 1);
    }
    if (ext_data.ServerImages[imageSlot]) {
        ext_data.ServerImages[imageSlot] = nullptr;
    }

    if (imageName.empty()) {
        return;
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

    [[maybe_unused]] const auto ox = reader.GetLEUInt16();
    [[maybe_unused]] const auto oy = reader.GetLEUInt16();

    const auto is_spr_ref = reader.GetUInt8();
    FO_RUNTIME_ASSERT(is_spr_ref == 0);

    const auto width = reader.GetLEUInt16();
    const auto height = reader.GetLEUInt16();
    [[maybe_unused]] const auto nx = reader.GetLEUInt16();
    [[maybe_unused]] const auto ny = reader.GetLEUInt16();
    const auto* data = reader.GetCurBuf();

    reader.GoForward(static_cast<size_t>(width) * height * 4);

    const auto check_number2 = reader.GetUInt8();
    FO_RUNTIME_ASSERT(check_number2 == 42);

    auto&& simg = std::make_unique<ServerImage>();
    simg->Width = width;
    simg->Height = height;
    simg->Data.resize(static_cast<size_t>(width) * height);
    std::memcpy(simg->Data.data(), data, simg->Data.size() * sizeof(ucolor));

    ext_data.ServerImages[imageSlot] = std::move(simg);
}

ucolor FO_NAMESPACE Server_Game_GetImageColor(FOServer* server, int32 imageSlot, int32 x, int32 y)
{
    FO_STACK_TRACE_ENTRY();

    auto& ext_data = GetServerExtData(server);

    if (imageSlot < 0 || imageSlot >= static_cast<int32>(ext_data.ServerImages.size()) || !ext_data.ServerImages[imageSlot]) {
        throw ScriptException("Image not loaded");
    }

    auto&& simg = ext_data.ServerImages[imageSlot];

    if (x < 0 || y < 0 || x >= simg->Width || y >= simg->Height) {
        throw ScriptException("Invalid coords arg");
    }

    const auto result = simg->Data[y * simg->Width + x];
    return result;
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

void FO_NAMESPACE Server_Critter_Wait(Critter* server, int32 ms)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(server, ms);
}
