#include "Common.h"

#include "Client.h"

///# ...
///# return ...
///@ ExportMethod
[[maybe_unused]] bool Client_Critter_IsFree(CritterView* self)
{
    return true;
}

///# ...
///# return ...
///@ ExportMethod
[[maybe_unused]] bool Client_Critter_IsBusy(CritterView* self)
{
    return false;
}

///# ...
///# param ms ...
///@ ExportMethod
[[maybe_unused]] void Client_Critter_Wait(CritterView* self, uint ms)
{
}
