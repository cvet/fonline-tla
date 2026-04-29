#pragma once

#include "Common.h"

#include "EngineBase.h"
#include "TextPack.h"

FO_USING_NAMESPACE();

FO_DECLARE_EXCEPTION(DialogManagerException);
FO_DECLARE_EXCEPTION(DialogParseException);
FO_DECLARE_EXCEPTION(DialogException);

// Types
static constexpr uint8_t DR_NONE = 0;
static constexpr uint8_t DR_PROP_GLOBAL = 1;
static constexpr uint8_t DR_PROP_CRITTER = 2;
static constexpr uint8_t DR_PROP_ITEM = 4;
static constexpr uint8_t DR_PROP_LOCATION = 5;
static constexpr uint8_t DR_PROP_MAP = 6;
static constexpr uint8_t DR_ITEM = 7;
static constexpr uint8_t DR_SCRIPT = 8;
static constexpr uint8_t DR_NO_RECHECK = 9;
static constexpr uint8_t DR_OR = 10;

// Who types
static constexpr uint8_t DR_WHO_NONE = 0;
static constexpr uint8_t DR_WHO_PLAYER = 1;
static constexpr uint8_t DR_WHO_NPC = 2;

///@ ExportRefType Server RefCounted Export = Type, Who, ParamIndex, ParamHash, AnswerScriptFuncName, NoRecheck, Op, ValuesCount, Value, ValueExt0, ValueExt1, ValueExt2, ValueExt3, ValueExt4
class DialogAnswerReq : public RefCounted<DialogAnswerReq>
{
public:
    uint8_t Type {DR_NONE};
    uint8_t Who {DR_WHO_NONE};
    int32_t ParamIndex {};
    hstring ParamHash {};
    hstring AnswerScriptFuncName {};
    bool NoRecheck {};
    uint8_t Op {};
    uint8_t ValuesCount {};
    any_t Value {};
    any_t ValueExt0 {};
    any_t ValueExt1 {};
    any_t ValueExt2 {};
    any_t ValueExt3 {};
    any_t ValueExt4 {};
};

///@ ExportRefType Server RefCounted Export = Link, TextId, DemandsCount, ResultsCount, GetDemand, GetResult
class DialogAnswer : public RefCounted<DialogAnswer>
{
public:
    auto GetDemand(int32_t index) -> DialogAnswerReq*;
    auto GetResult(int32_t index) -> DialogAnswerReq*;

    int32_t Link {};
    hstring TextId {};
    int32_t DemandsCount {};
    int32_t ResultsCount {};
    vector<refcount_ptr<DialogAnswerReq>> Demands {};
    vector<refcount_ptr<DialogAnswerReq>> Results {};
};

///@ ExportRefType Server RefCounted Export = Id, TextId, DlgScriptFuncName, AnswersCount, GetAnswer
class DialogSpeech : public RefCounted<DialogSpeech>
{
public:
    auto GetAnswer(int32_t index) -> DialogAnswer*;

    int32_t Id {};
    hstring TextId {};
    hstring DlgScriptFuncName {};
    int32_t AnswersCount {};
    vector<refcount_ptr<DialogAnswer>> Answers {};
};

///@ ExportRefType Server RefCounted Export = PackId, SpeechesCount, GetSpeech
class DialogPack : public RefCounted<DialogPack>
{
public:
    auto GetSpeech(int32_t index) -> DialogSpeech*;

    hstring PackId {};
    int32_t SpeechesCount {};
    vector<refcount_ptr<DialogSpeech>> Speeches {};
    vector<pair<string, TextPack>> Texts {};
    string Comment {};
};

class DialogManager final
{
public:
    DialogManager() = delete;
    explicit DialogManager(EngineMetadata& meta);
    DialogManager(const DialogManager&) = delete;
    DialogManager(DialogManager&&) noexcept = default;
    auto operator=(const DialogManager&) = delete;
    auto operator=(DialogManager&&) noexcept = delete;
    ~DialogManager() = default;

    [[nodiscard]] auto GetDialog(hstring pack_id) -> DialogPack*;
    [[nodiscard]] auto GetDialogs() -> vector<DialogPack*>;

    void LoadFromResources(const FileSystem& resources);
    auto ParseDialog(string_view pack_name, string_view data) const -> refcount_ptr<DialogPack>;
    void AddDialog(refcount_ptr<DialogPack> pack);

private:
    [[nodiscard]] auto GetDrType(string_view str) const -> uint8_t;
    [[nodiscard]] auto CheckOper(uint8_t oper) const -> bool;

    auto LoadDemandResult(istringstream& input, bool is_demand) const -> refcount_ptr<DialogAnswerReq>;

    raw_ptr<EngineMetadata> _meta;
    map<hstring, refcount_ptr<DialogPack>> _dialogPacks {};
};
