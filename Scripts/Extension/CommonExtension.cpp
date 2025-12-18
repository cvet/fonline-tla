#include "Common.h"

#include "EngineBase.h"

#include "sha1.h"
#include "sha2.h"

FO_USING_NAMESPACE();

FO_BEGIN_NAMESPACE();
///@ ExportMethod
FO_SCRIPT_API string Common_Game_Sha1(BaseEngine* engine, string_view text);
///@ ExportMethod
FO_SCRIPT_API string Common_Game_Sha2(BaseEngine* engine, string_view text);
FO_END_NAMESPACE();

string FO_NAMESPACE Common_Game_Sha1(BaseEngine* engine, string_view text)
{
    ignore_unused(engine);

    SHA1_CTX ctx;
    _SHA1_Init(&ctx);
    _SHA1_Update(&ctx, reinterpret_cast<const uint8*>(text.data()), text.length());
    uint8 digest[SHA1_DIGEST_SIZE];
    _SHA1_Final(&ctx, digest);

    const auto* nums = "0123456789abcdef";
    char hex_digest[SHA1_DIGEST_SIZE * 2];
    for (size_t i = 0; i < sizeof(hex_digest); i++) {
        hex_digest[i] = nums[(i % 2) != 0 ? digest[i / 2] & 0xF : digest[i / 2] >> 4];
    }

    return {hex_digest, sizeof(hex_digest)};
}

string FO_NAMESPACE Common_Game_Sha2(BaseEngine* engine, string_view text)
{
    ignore_unused(engine);

    constexpr uint32 digest_size = 32;
    uint8 digest[digest_size];
    sha256(reinterpret_cast<const uint8*>(text.data()), numeric_cast<uint32>(text.length()), digest);

    const auto* nums = "0123456789abcdef";
    char hex_digest[digest_size * 2];
    for (size_t i = 0; i < sizeof(hex_digest); i++) {
        hex_digest[i] = nums[(i % 2) != 0 ? digest[i / 2] & 0xF : digest[i / 2] >> 4];
    }
    return {hex_digest, sizeof(hex_digest)};
}
