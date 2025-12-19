//      __________        ___               ______            _
//     / ____/ __ \____  / (_)___  ___     / ____/___  ____ _(_)___  ___
//    / /_  / / / / __ \/ / / __ \/ _ \   / __/ / __ \/ __ `/ / __ \/ _ `
//   / __/ / /_/ / / / / / / / / /  __/  / /___/ / / / /_/ / / / / /  __/
//  /_/    \____/_/ /_/_/_/_/ /_/\___/  /_____/_/ /_/\__, /_/_/ /_/\___/
//                                                  /____/
// FOnline Engine
// https://fonline.ru
// https://github.com/cvet/fonline
//
// MIT License
//
// Copyright (c) 2006 - 2025, Anton Tsvetinskiy aka cvet <cvet@tut.by>
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
//

#pragma once

#include "Common.h"

#include "EngineBase.h"
#include "TextPack.h"

FO_BEGIN_NAMESPACE();

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

///@ ExportRefType Server
struct DialogAnswerReq
{
    FO_SCRIPTABLE_OBJECT_BEGIN();

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

    FO_SCRIPTABLE_OBJECT_END();
};
static_assert(std::is_standard_layout_v<DialogAnswerReq>);

///@ ExportRefType Server
struct DialogAnswer
{
    FO_SCRIPTABLE_OBJECT_BEGIN();

    uint32 Link {};
    uint32 TextId {};
    int32 DemandsCount {};
    int32 ResultsCount {};

    auto GetDemand(int32 index) -> DialogAnswerReq*;
    auto GetResult(int32 index) -> DialogAnswerReq*;

    FO_SCRIPTABLE_OBJECT_END();

    unique_ptr<vector<refcount_ptr<DialogAnswerReq>>> Demands {SafeAlloc::MakeUnique<vector<refcount_ptr<DialogAnswerReq>>>()};
    unique_ptr<vector<refcount_ptr<DialogAnswerReq>>> Results {SafeAlloc::MakeUnique<vector<refcount_ptr<DialogAnswerReq>>>()};
};
static_assert(std::is_standard_layout_v<DialogAnswer>);

///@ ExportRefType Server
struct DialogSpeech
{
    FO_SCRIPTABLE_OBJECT_BEGIN();

    uint32 Id {};
    uint32 TextId {};
    hstring DlgScriptFuncName {};
    int32 AnswersCount {};

    auto GetAnswer(int32 index) -> DialogAnswer*;

    FO_SCRIPTABLE_OBJECT_END();

    unique_ptr<vector<refcount_ptr<DialogAnswer>>> Answers {SafeAlloc::MakeUnique<vector<refcount_ptr<DialogAnswer>>>()};
};
static_assert(std::is_standard_layout_v<DialogSpeech>);

///@ ExportRefType Server
struct DialogPack
{
    FO_SCRIPTABLE_OBJECT_BEGIN();

    hstring PackId {};
    int32 SpeechesCount {};

    auto GetSpeech(int32 index) -> DialogSpeech*;

    FO_SCRIPTABLE_OBJECT_END();

    unique_ptr<vector<refcount_ptr<DialogSpeech>>> Speeches {SafeAlloc::MakeUnique<vector<refcount_ptr<DialogSpeech>>>()};
    unique_ptr<vector<pair<string, TextPack>>> Texts {SafeAlloc::MakeUnique<vector<pair<string, TextPack>>>()};
    unique_ptr<string> Comment {SafeAlloc::MakeUnique<string>()};
};
static_assert(std::is_standard_layout_v<DialogPack>);

class DialogManager final
{
public:
    DialogManager() = delete;
    explicit DialogManager(EngineData& engine);
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

    raw_ptr<EngineData> _engine;
    map<hstring, refcount_ptr<DialogPack>> _dialogPacks {};
};

FO_END_NAMESPACE();
