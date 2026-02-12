#include "Common.h"

#include "Baker.h"
#include "DialogBaker.h"

FO_USING_NAMESPACE();

FO_BEGIN_NAMESPACE
///@ EngineHook
FO_SCRIPT_API void SetupBakersHook(const_span<string> request_bakers, vector<unique_ptr<BaseBaker>>& bakers, shared_ptr<BakingContext> ctx);
FO_END_NAMESPACE

void FO_NAMESPACE SetupBakersHook(const_span<string> request_bakers, vector<unique_ptr<BaseBaker>>& bakers, shared_ptr<BakingContext> ctx)
{
    if (vec_exists(request_bakers, DialogBaker::NAME)) {
        bakers.emplace_back(SafeAlloc::MakeUnique<DialogBaker>(ctx));
    }
    if (vec_exists(request_bakers, DialogTextBaker::NAME)) {
        bakers.emplace_back(SafeAlloc::MakeUnique<DialogTextBaker>(ctx));
    }
}
