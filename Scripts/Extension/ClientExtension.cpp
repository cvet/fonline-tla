#include "Common.h"

#include "Client.h"

FO_USING_NAMESPACE();

FO_BEGIN_NAMESPACE();
///@ ExportMethod
[[maybe_unused]] bool Client_Critter_IsFree(CritterView* self);
///@ ExportMethod
[[maybe_unused]] bool Client_Critter_IsBusy(CritterView* self);
///@ ExportMethod
[[maybe_unused]] void Client_Critter_Wait(CritterView* self, int32 ms);
FO_END_NAMESPACE();

bool FO_NAMESPACE Client_Critter_IsFree(CritterView* self)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(self);
    return true;
}

bool FO_NAMESPACE Client_Critter_IsBusy(CritterView* self)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(self);
    return false;
}

void FO_NAMESPACE Client_Critter_Wait(CritterView* self, int32 ms)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(self, ms);
}
