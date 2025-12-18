#include "Common.h"

#include "Baker.h"
#include "DialogBaker.h"

FO_USING_NAMESPACE();

FO_BEGIN_NAMESPACE();
///@ EngineHook
FO_SCRIPT_API void SetupBakersHook(vector<unique_ptr<BaseBaker>>& bakers, BakerData& baker_data);
FO_END_NAMESPACE();

void FO_NAMESPACE SetupBakersHook(vector<unique_ptr<BaseBaker>>& bakers, BakerData& baker_data)
{
    bakers.emplace_back(SafeAlloc::MakeUnique<DialogBaker>(baker_data));
    bakers.emplace_back(SafeAlloc::MakeUnique<DialogTextBaker>(baker_data));
}
