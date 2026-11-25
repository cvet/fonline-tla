#pragma once

#include "Common.h"

#include "Client.h"

FO_USING_NAMESPACE();

struct ClientExtData
{
    int32_t EmbeddedClientIndex {};
};

inline auto GetClientExtData(ptr<ClientEngine> client) -> ClientExtData&
{
    return *reinterpret_cast<ClientExtData*>(client->UserData.get());
}
