#include "Common.h"

#include "Server.h"

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

///@ EngineHook
void InitServerEngine(FOServer* server)
{
    STACK_TRACE_ENTRY();

    server->UserData = unique_del_ptr<void>(new ServerExtData(), [](void* ptr) { delete static_cast<ServerExtData*>(ptr); });
}

///@ ExportMethod
[[maybe_unused]] void Server_Game_LoadImage(FOServer* self, int imageSlot, string_view imageName)
{
    STACK_TRACE_ENTRY();

    auto&& ext_data = *static_cast<ServerExtData*>(self->UserData.get());

    if (imageSlot >= ext_data.ServerImages.size()) {
        ext_data.ServerImages.resize(imageSlot + 1);
    }
    if (ext_data.ServerImages[imageSlot]) {
        ext_data.ServerImages[imageSlot] = nullptr;
    }

    if (imageName.empty()) {
        return;
    }

    auto&& file = self->Resources.ReadFile(imageName);

    if (!file) {
        throw ScriptException("File not found", imageName);
    }

    const auto check_number = file.GetUChar();

    if (check_number != 42) {
        throw ScriptException("File is not image", imageName);
    }

    const auto frames_count = file.GetLEUShort();

    if (frames_count != 1) {
        throw ScriptException("File must contain only one frame", imageName);
    }

    [[maybe_unused]] const auto ticks = file.GetLEUShort();

    const auto dirs = file.GetUChar();

    if (dirs != 1) {
        throw ScriptException("File must contain only one dir", imageName);
    }

    [[maybe_unused]] const auto ox = file.GetLEShort();
    [[maybe_unused]] const auto oy = file.GetLEShort();

    const auto is_spr_ref = file.GetUChar();
    RUNTIME_ASSERT(is_spr_ref == 0);

    const auto width = file.GetLEUShort();
    const auto height = file.GetLEUShort();
    [[maybe_unused]] const auto nx = file.GetLEShort();
    [[maybe_unused]] const auto ny = file.GetLEShort();
    const auto* data = file.GetCurBuf();

    file.GoForward(static_cast<size_t>(width) * height * 4);

    const auto check_number2 = file.GetUChar();
    RUNTIME_ASSERT(check_number2 == 42);

    auto&& simg = std::make_unique<ServerImage>();
    simg->Width = width;
    simg->Height = height;
    simg->Data.resize(static_cast<size_t>(width) * height);
    std::memcpy(simg->Data.data(), data, simg->Data.size() * sizeof(uint));

    ext_data.ServerImages[imageSlot] = std::move(simg);
}

///@ ExportMethod
[[maybe_unused]] uint Server_Game_GetImageColor(FOServer* self, int imageSlot, int x, int y)
{
    STACK_TRACE_ENTRY();

    auto&& ext_data = *static_cast<ServerExtData*>(self->UserData.get());

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

///@ ExportMethod
[[maybe_unused]] bool Server_Critter_IsFree(Critter* self)
{
    UNUSED_VARIABLE(self);

    return true;
}

///@ ExportMethod
[[maybe_unused]] bool Server_Critter_IsBusy(Critter* self)
{
    UNUSED_VARIABLE(self);

    return false;
}

///@ ExportMethod
[[maybe_unused]] void Server_Critter_Wait(Critter* self, uint ms)
{
    UNUSED_VARIABLE(self);
    UNUSED_VARIABLE(ms);
}
