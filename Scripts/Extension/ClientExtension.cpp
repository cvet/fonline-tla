#include "Common.h"

#include "Client.h"

///@ ExportMethod
[[maybe_unused]] bool Client_Critter_IsFree(CritterView* self)
{
    UNUSED_VARIABLE(self);

    return true;
}

///@ ExportMethod
[[maybe_unused]] bool Client_Critter_IsBusy(CritterView* self)
{
    UNUSED_VARIABLE(self);

    return false;
}

///@ ExportMethod
[[maybe_unused]] void Client_Critter_Wait(CritterView* self, uint ms)
{
    UNUSED_VARIABLE(self);
    UNUSED_VARIABLE(ms);
}
