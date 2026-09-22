#pragma once

#include "Common.h"

#include "AudioBaker.h"
#include "FileSystem.h"

FO_USING_NAMESPACE();

FO_DECLARE_EXCEPTION(AcmDecoderException);

// Interplay ACM, the compressed PCM that Fallout sound effects and music are stored in. Ported from the acmstrm
// unpacker the engine carried in ThirdParty/Acm until it moved audio decoding to bake time: the arithmetic is kept bit
// for bit, while the amplitude table the original kept in a global became decoder state, so files decode concurrently
class AcmDecoder final
{
public:
    explicit AcmDecoder(const_span<uint8_t> data);
    AcmDecoder(const AcmDecoder&) = delete;
    AcmDecoder(AcmDecoder&&) noexcept = delete;
    auto operator=(const AcmDecoder&) = delete;
    auto operator=(AcmDecoder&&) noexcept = delete;
    ~AcmDecoder() = default;

    [[nodiscard]] auto GetChannels() const noexcept -> int32_t { return _channels; }
    [[nodiscard]] auto GetSampleRate() const noexcept -> int32_t { return _sampleRate; }
    [[nodiscard]] auto GetSampleCount() const noexcept -> int32_t { return _sampleCount; } // All channels together

    // Decodes the whole stream into signed 16-bit samples; a decoder decodes once
    [[nodiscard]] auto Decode() -> vector<int16_t>;

private:
    [[nodiscard]] auto ReadByte() noexcept -> uint32_t;
    void PrepareBits(int32_t bits) noexcept;
    [[nodiscard]] auto GetBits(int32_t bits) noexcept -> uint32_t;
    void SkipBits(int32_t bits) noexcept;
    [[nodiscard]] auto Amplitude(int32_t index) const -> int32_t;
    [[nodiscard]] auto Cell(int32_t row, int32_t pass) -> int32_t&;

    void MakeNewValues();
    void CreateAmplitudeDictionary();
    void FillColumn(int32_t pass, int32_t ind);
    void UnpackValues();
    void TransformFirstLevel(size_t block_start, int32_t size, int32_t blocks);
    void TransformNextLevel(size_t dec_start, size_t block_start, int32_t size, int32_t blocks);

    void ZeroFill(int32_t pass);
    void LinearFill(int32_t pass, int32_t ind);
    void K1Bits3(int32_t pass);
    void K1Bits2(int32_t pass);
    void T1Bits5(int32_t pass);
    void K2Bits4(int32_t pass);
    void K2Bits3(int32_t pass);
    void T2Bits7(int32_t pass);
    void K3Bits5(int32_t pass);
    void K3Bits4(int32_t pass);
    void K4Bits5(int32_t pass);
    void K4Bits4(int32_t pass);
    void T3Bits7(int32_t pass);

    const_span<uint8_t> _data;
    size_t _dataPos {};
    uint32_t _nextBits {};
    int32_t _availBits {};

    int32_t _channels {};
    int32_t _sampleRate {};
    int32_t _sampleCount {};
    int32_t _valsToGo {};

    int32_t _packAttrs {};
    int32_t _packAttrs2 {};
    int32_t _someSize {};
    int32_t _blocks {};
    int32_t _totalBlockSize {};

    vector<int32_t> _someBuff {};
    vector<int16_t> _firstLevelDecomp {};
    vector<int32_t> _nextLevelDecomp {};
    vector<int16_t> _amplitudes {};
    size_t _valuesPos {};
    int32_t _valCount {};
    bool _decoded {};
};

// AudioBaker loader for .acm. Fallout played every sound effect as mono whatever its header claimed, and hundreds of
// the effect headers claim stereo over mono data, while music is stereo: so the channel count follows the directory
// (sound/music/ is stereo) rather than the header, exactly as the runtime decoder did when it still existed
[[nodiscard]] auto LoadAcmAudio(string_view fname, FileReader reader) -> AudioBaker::PcmAudio;
