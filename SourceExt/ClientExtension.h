#pragma once

#include "Common.h"

#include "Client.h"

FO_USING_NAMESPACE();

struct AiControlClientData;

struct ClientExtData
{
    int32_t EmbeddedClientIndex {};
    unique_del_nptr<AiControlClientData> AiControl {};
};

inline auto GetClientExtData(ptr<ClientEngine> client) -> ClientExtData&
{
    return *reinterpret_cast<ClientExtData*>(client->UserData.get());
}
