#pragma once

#include "Client.h"
#include "Common.h"

FO_USING_NAMESPACE();

struct AiControlClientData;

struct ClientExtData
{
    int32_t EmbeddedClientIndex {};
    unique_del_ptr<AiControlClientData> AiControl {};
};

inline auto GetClientExtData(ClientEngine* client) -> ClientExtData&
{
    return *reinterpret_cast<ClientExtData*>(client->UserData.get());
}
