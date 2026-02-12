#pragma once

#include "Common.h"

#include "EngineBase.h"
#include "TextPack.h"

FO_BEGIN_NAMESPACE

FO_DECLARE_EXCEPTION(DialogManagerException);
FO_DECLARE_EXCEPTION(DialogParseException);
FO_DECLARE_EXCEPTION(DialogException);

// Types
static constexpr uint8 DR_NONE = 0;
static constexpr uint8 DR_PROP_GLOBAL = 1;
static constexpr uint8 DR_PROP_CRITTER = 2;
static constexpr uint8 DR_PROP_ITEM = 4;
static constexpr uint8 DR_PROP_LOCATION = 5;
static constexpr uint8 DR_PROP_MAP = 6;
static constexpr uint8 DR_ITEM = 7;
static constexpr uint8 DR_SCRIPT = 8;
static constexpr uint8 DR_NO_RECHECK = 9;
static constexpr uint8 DR_OR = 10;

// Who types
static constexpr uint8 DR_WHO_NONE = 0;
static constexpr uint8 DR_WHO_PLAYER = 1;
static constexpr uint8 DR_WHO_NPC = 2;

///@ ExportRefType Server RefCounted Export = Type, Who, ParamIndex, ParamHash, AnswerScriptFuncName, NoRecheck, Op, ValuesCount, Value, ValueExt0, ValueExt1, ValueExt2, ValueExt3, ValueExt4
class DialogAnswerReq : public RefCounted<DialogAnswerReq>
{
public:
    uint8 Type {DR_NONE};
    uint8 Who {DR_WHO_NONE};
    int32 ParamIndex {};
    hstring ParamHash {};
    hstring AnswerScriptFuncName {};
    bool NoRecheck {};
    uint8 Op {};
    uint8 ValuesCount {};
    int32 Value {};
    int32 ValueExt0 {};
    int32 ValueExt1 {};
    int32 ValueExt2 {};
    int32 ValueExt3 {};
    int32 ValueExt4 {};
};

///@ ExportRefType Server RefCounted Export = Link, TextId, DemandsCount, ResultsCount, GetDemand, GetResult
class DialogAnswer : public RefCounted<DialogAnswer>
{
public:
    auto GetDemand(int32 index) -> DialogAnswerReq*;
    auto GetResult(int32 index) -> DialogAnswerReq*;

    uint32 Link {};
    uint32 TextId {};
    int32 DemandsCount {};
    int32 ResultsCount {};
    vector<refcount_ptr<DialogAnswerReq>> Demands {};
    vector<refcount_ptr<DialogAnswerReq>> Results {};
};

///@ ExportRefType Server RefCounted Export = Id, TextId, DlgScriptFuncName, AnswersCount, GetAnswer
class DialogSpeech : public RefCounted<DialogSpeech>
{
public:
    auto GetAnswer(int32 index) -> DialogAnswer*;

    uint32 Id {};
    uint32 TextId {};
    hstring DlgScriptFuncName {};
    int32 AnswersCount {};
    vector<refcount_ptr<DialogAnswer>> Answers {};
};

///@ ExportRefType Server RefCounted Export = PackId, SpeechesCount, GetSpeech
class DialogPack : public RefCounted<DialogPack>
{
public:
    auto GetSpeech(int32 index) -> DialogSpeech*;

    hstring PackId {};
    int32 SpeechesCount {};
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
    [[nodiscard]] auto GetDrType(string_view str) const -> uint8;
    [[nodiscard]] auto GetWho(uint8 who) const -> uint8;
    [[nodiscard]] auto CheckOper(uint8 oper) const -> bool;

    auto LoadDemandResult(istringstream& input, bool is_demand) const -> refcount_ptr<DialogAnswerReq>;

    raw_ptr<EngineMetadata> _meta;
    map<hstring, refcount_ptr<DialogPack>> _dialogPacks {};
};

FO_END_NAMESPACE
