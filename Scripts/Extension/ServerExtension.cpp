#include "Common.h"

#include "Server.h"

FO_USING_NAMESPACE();

FO_BEGIN_NAMESPACE();
///@ EngineHook
FO_SCRIPT_API void InitServerEngine(FOServer* server);
///@ ExportMethod
FO_SCRIPT_API void Server_Game_LoadImage(FOServer* server, int imageSlot, string_view imageName);
///@ ExportMethod
FO_SCRIPT_API uint Server_Game_GetImageColor(FOServer* server, int imageSlot, int x, int y);
///@ ExportMethod
FO_SCRIPT_API bool Server_Critter_IsFree(Critter* server);
///@ ExportMethod
FO_SCRIPT_API bool Server_Critter_IsBusy(Critter* server);
///@ ExportMethod
FO_SCRIPT_API void Server_Critter_Wait(Critter* server, uint ms);
FO_END_NAMESPACE();

struct ServerImage
{
    vector<uint> Data {};
    int Width {};
    int Height {};
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

void FO_NAMESPACE Server_Game_LoadImage(FOServer* server, int imageSlot, string_view imageName)
{
    FO_STACK_TRACE_ENTRY();

    auto& ext_data = GetServerExtData(server);

    if (imageSlot >= ext_data.ServerImages.size()) {
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
    const auto check_number = reader.GetUChar();

    if (check_number != 42) {
        throw ScriptException("File is not image", imageName);
    }

    const auto frames_count = reader.GetLEUShort();

    if (frames_count != 1) {
        throw ScriptException("File must contain only one frame", imageName);
    }

    [[maybe_unused]] const auto ticks = reader.GetLEUShort();

    const auto dirs = reader.GetUChar();

    if (dirs != 1) {
        throw ScriptException("File must contain only one dir", imageName);
    }

    [[maybe_unused]] const auto ox = reader.GetLEShort();
    [[maybe_unused]] const auto oy = reader.GetLEShort();

    const auto is_spr_ref = reader.GetUChar();
    FO_RUNTIME_ASSERT(is_spr_ref == 0);

    const auto width = reader.GetLEUShort();
    const auto height = reader.GetLEUShort();
    [[maybe_unused]] const auto nx = reader.GetLEShort();
    [[maybe_unused]] const auto ny = reader.GetLEShort();
    const auto* data = reader.GetCurBuf();

    reader.GoForward(static_cast<size_t>(width) * height * 4);

    const auto check_number2 = reader.GetUChar();
    FO_RUNTIME_ASSERT(check_number2 == 42);

    auto&& simg = std::make_unique<ServerImage>();
    simg->Width = width;
    simg->Height = height;
    simg->Data.resize(static_cast<size_t>(width) * height);
    std::memcpy(simg->Data.data(), data, simg->Data.size() * sizeof(uint));

    ext_data.ServerImages[imageSlot] = std::move(simg);
}

uint FO_NAMESPACE Server_Game_GetImageColor(FOServer* server, int imageSlot, int x, int y)
{
    FO_STACK_TRACE_ENTRY();

    auto& ext_data = GetServerExtData(server);

    if (imageSlot >= ext_data.ServerImages.size() || !ext_data.ServerImages[imageSlot]) {
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

void FO_NAMESPACE Server_Critter_Wait(Critter* server, uint ms)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(server, ms);
}
