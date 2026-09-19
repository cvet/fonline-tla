#include "Common.h"

#include "AcmDecoder.h"
#include "AudioBaker.h"
#include "Baker.h"
#include "DialogBaker.h"

FO_USING_NAMESPACE();

FO_BEGIN_NAMESPACE
///@ EngineHook
FO_SCRIPT_API void SetupBakersHook(const_span<string> request_bakers, vector<unique_ptr<BaseBaker>>& bakers, shared_ptr<BakingContext> ctx);
FO_END_NAMESPACE

void FO_NAMESPACE SetupBakersHook(const_span<string> request_bakers, vector<unique_ptr<BaseBaker>>& bakers, shared_ptr<BakingContext> ctx)
{
    if (IsTestingInProgress) {
        return;
    }

    if (vec_exists(request_bakers, DialogBaker::NAME)) {
        bakers.emplace_back(safe_alloc::make_unique<DialogBaker>(ctx));
    }
    if (vec_exists(request_bakers, DialogTextBaker::NAME)) {
        bakers.emplace_back(safe_alloc::make_unique<DialogTextBaker>(ctx));
    }

    // Fallout sound effects and music ship as ACM, which the engine no longer decodes: the audio baker takes it as
    // one more source format and bakes it to Ogg Vorbis like any other
    for (auto& baker : bakers) {
        if (auto audio_baker = baker.dyn_cast<AudioBaker>()) {
            audio_baker->AddLoader(LoadAcmAudio, {"acm"});
        }
    }
}
