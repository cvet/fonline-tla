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

#include "DialogBaker.h"
#include "Dialogs.h"
#include "ScriptSystem.h"
#include "TextPack.h"

FO_BEGIN_NAMESPACE();

class Critter;

DialogBaker::DialogBaker(BakerData& data) :
    BaseBaker(data)
{
    FO_STACK_TRACE_ENTRY();

    _skipBaking = !std::ranges::find_if(_settings->GetResourcePacks(), [&](auto&& pack) { return pack.Name == _resPackName; })->ServerOnly;
}

DialogBaker::~DialogBaker()
{
    FO_STACK_TRACE_ENTRY();
}

void DialogBaker::BakeFiles(const FileCollection& files, string_view target_path) const
{
    FO_STACK_TRACE_ENTRY();

    if (_skipBaking) {
        return;
    }

    // Collect dialog files
    vector<File> filtered_files;

    if (target_path.empty()) {
        for (const auto& file_header : files) {
            if (strex(file_header.GetPath()).get_file_extension() != "fodlg") {
                continue;
            }
            if (_bakeChecker && !_bakeChecker(file_header.GetPath(), file_header.GetWriteTime())) {
                continue;
            }

            filtered_files.emplace_back(File::Load(file_header));
        }
    }
    else {
        if (strex(target_path).get_file_extension() != "fodlg") {
            return;
        }

        auto file = files.FindFileByPath(target_path);

        if (!file) {
            return;
        }
        if (_bakeChecker && !_bakeChecker(target_path, file.GetWriteTime())) {
            return;
        }

        filtered_files.emplace_back(std::move(file));
    }

    if (filtered_files.empty()) {
        return;
    }

    // Load dialogs
    auto server_engine = BakerEngine(PropertiesRelationType::ServerRelative);
    const auto dialog_mngr = DialogManager(server_engine);
    const auto script_sys = BakerScriptSystem(server_engine, *_bakedFiles);

    size_t errors = 0;
    vector<refcount_ptr<DialogPack>> dialog_packs;

    for (const auto& file : filtered_files) {
        try {
            auto pack = dialog_mngr.ParseDialog(file.GetNameNoExt(), file.GetStr());
            dialog_packs.emplace_back(std::move(pack));
        }
        catch (const DialogParseException& ex) {
            WriteLog("Dialog baking error: {}", ex.what());
            errors++;
        }
    }

    // Verify
    for (const auto& dlg_pack : dialog_packs) {
        for (const auto& speech : *dlg_pack->Speeches) {
            if (speech->DlgScriptFuncName) {
                if (!script_sys.CheckFunc<void, Critter*, Critter*, string*>(speech->DlgScriptFuncName) && //
                    !script_sys.CheckFunc<int32, Critter*, Critter*, string*>(speech->DlgScriptFuncName)) {
                    //WriteLog("Dialog {} invalid start function {}", dlg_pack->PackId, speech->DlgScriptFuncName);
                    //errors++;
                }
            }

            for (const auto& answer : *speech->Answers) {
                for (const auto& demand : *answer->Demands) {
                    if (demand->Type == DR_SCRIPT) {
                        if ((demand->ValuesCount == 0 && !script_sys.CheckFunc<bool, Critter*, Critter*>(demand->AnswerScriptFuncName)) || //
                            (demand->ValuesCount == 1 && !script_sys.CheckFunc<bool, Critter*, Critter*, int32>(demand->AnswerScriptFuncName)) || //
                            (demand->ValuesCount == 2 && !script_sys.CheckFunc<bool, Critter*, Critter*, int32, int32>(demand->AnswerScriptFuncName)) || //
                            (demand->ValuesCount == 3 && !script_sys.CheckFunc<bool, Critter*, Critter*, int32, int32, int32>(demand->AnswerScriptFuncName)) || //
                            (demand->ValuesCount == 4 && !script_sys.CheckFunc<bool, Critter*, Critter*, int32, int32, int32, int32>(demand->AnswerScriptFuncName)) || //
                            (demand->ValuesCount == 5 && !script_sys.CheckFunc<bool, Critter*, Critter*, int32, int32, int32, int32, int32>(demand->AnswerScriptFuncName))) {
                            WriteLog("Dialog {} answer demand invalid function {}", dlg_pack->PackId, demand->AnswerScriptFuncName);
                            errors++;
                        }
                    }
                }

                for (const auto& result : *answer->Results) {
                    if (result->Type == DR_SCRIPT) {
                        int32 not_found_count = 0;

                        if ((result->ValuesCount == 0 && !script_sys.CheckFunc<void, Critter*, Critter*>(result->AnswerScriptFuncName)) || //
                            (result->ValuesCount == 1 && !script_sys.CheckFunc<void, Critter*, Critter*, int32>(result->AnswerScriptFuncName)) || //
                            (result->ValuesCount == 2 && !script_sys.CheckFunc<void, Critter*, Critter*, int32, int32>(result->AnswerScriptFuncName)) || //
                            (result->ValuesCount == 3 && !script_sys.CheckFunc<void, Critter*, Critter*, int32, int32, int32>(result->AnswerScriptFuncName)) || //
                            (result->ValuesCount == 4 && !script_sys.CheckFunc<void, Critter*, Critter*, int32, int32, int32, int32>(result->AnswerScriptFuncName)) || //
                            (result->ValuesCount == 5 && !script_sys.CheckFunc<void, Critter*, Critter*, int32, int32, int32, int32, int32>(result->AnswerScriptFuncName))) {
                            not_found_count++;
                        }

                        if ((result->ValuesCount == 0 && !script_sys.CheckFunc<int32, Critter*, Critter*>(result->AnswerScriptFuncName)) || //
                            (result->ValuesCount == 1 && !script_sys.CheckFunc<int32, Critter*, Critter*, int32>(result->AnswerScriptFuncName)) || //
                            (result->ValuesCount == 2 && !script_sys.CheckFunc<int32, Critter*, Critter*, int32, int32>(result->AnswerScriptFuncName)) || //
                            (result->ValuesCount == 3 && !script_sys.CheckFunc<int32, Critter*, Critter*, int32, int32, int32>(result->AnswerScriptFuncName)) || //
                            (result->ValuesCount == 4 && !script_sys.CheckFunc<int32, Critter*, Critter*, int32, int32, int32, int32>(result->AnswerScriptFuncName)) || //
                            (result->ValuesCount == 5 && !script_sys.CheckFunc<int32, Critter*, Critter*, int32, int32, int32, int32, int32>(result->AnswerScriptFuncName))) {
                            not_found_count++;
                        }

                        if (not_found_count != 1) {
                            WriteLog("Dialog {} answer result invalid function {}", dlg_pack->PackId, result->AnswerScriptFuncName);
                            errors++;
                        }
                    }
                }
            }
        }
    }

    if (errors != 0) {
        throw DialogBakerException("Errors during dialogs baking");
    }

    // Write data
    for (const auto& file : filtered_files) {
        _writeData(file.GetPath(), file.GetData());
    }
}

DialogTextBaker::DialogTextBaker(BakerData& data) :
    BaseBaker(data)
{
    FO_STACK_TRACE_ENTRY();

    _skipBaking = std::ranges::find_if(_settings->GetResourcePacks(), [&](auto&& pack) { return pack.Name == _resPackName; })->ServerOnly;
}

DialogTextBaker::~DialogTextBaker()
{
    FO_STACK_TRACE_ENTRY();
}

void DialogTextBaker::BakeFiles(const FileCollection& files, string_view target_path) const
{
    FO_STACK_TRACE_ENTRY();

    if (_skipBaking) {
        return;
    }
    if (!target_path.empty() && !strex(target_path).get_file_extension().starts_with("fotxt")) {
        return;
    }

    // Collect dialog files
    vector<File> filtered_files;
    uint64 max_write_time = 0;

    for (const auto& file_header : files) {
        if (strex(file_header.GetPath()).get_file_extension() != "fodlg") {
            continue;
        }

        max_write_time = std::max(max_write_time, file_header.GetWriteTime());
        filtered_files.emplace_back(File::Load(file_header));
    }

    bool something_changed = false;

    if (!filtered_files.empty()) {
        for (const auto& lang_name : _settings->BakeLanguages) {
            if (!_bakeChecker || _bakeChecker(strex("{}.Dialogs.{}.fotxt-bin", _resPackName, lang_name), max_write_time)) {
                something_changed = true;
            }
        }
    }

    if (!something_changed) {
        return;
    }

    // Load dialogs
    auto server_engine = BakerEngine(PropertiesRelationType::ServerRelative);
    const auto dialog_mngr = DialogManager(server_engine);

    size_t errors = 0;
    vector<refcount_ptr<DialogPack>> dialog_packs;

    for (const auto& file : filtered_files) {
        try {
            auto pack = dialog_mngr.ParseDialog(file.GetNameNoExt(), file.GetStr());
            dialog_packs.emplace_back(std::move(pack));
        }
        catch (const DialogParseException& ex) {
            WriteLog("Dialog text baking error: {}", ex.what());
            errors++;
        }
    }

    // Fill texts
    vector<pair<string, map<string, TextPack>>> lang_packs;

    for (const auto& dlg_pack : dialog_packs) {
        for (const auto& dlg_pack_text : *dlg_pack->Texts) {
            const string lang_pack = dlg_pack_text.first;

            if (std::find_if(_settings->BakeLanguages.begin(), _settings->BakeLanguages.end(), [&](auto&& l) { return l == lang_pack; }) == _settings->BakeLanguages.end()) {
                WriteLog(LogType::Warning, "Dialog {} contains unsupported language {}", dlg_pack->PackId, lang_pack);
                continue;
            }

            const auto it = std::ranges::find_if(lang_packs, [&](auto&& l) { return l.first == lang_pack; });

            if (it == lang_packs.end()) {
                auto dialogs_text_pack = map<string, TextPack>();
                dialogs_text_pack.emplace("Dialogs", dlg_pack_text.second);
                lang_packs.emplace_back(lang_pack, std::move(dialogs_text_pack));
            }
            else {
                auto& text_pack = it->second.at("Dialogs");

                if (!text_pack.CheckIntersections(dlg_pack_text.second)) {
                    text_pack.Merge(dlg_pack_text.second);
                }
                else {
                    WriteLog("Dialog {} text intersection detected", dlg_pack->PackId);
                    errors++;
                }
            }
        }
    }

    TextPack::FixPacks(_settings->BakeLanguages, lang_packs);

    if (errors != 0) {
        throw DialogBakerException("Errors during dialogs text baking");
    }

    // Write data
    for (auto&& [lang_name, text_packs] : lang_packs) {
        auto text_pack_data = text_packs.at("Dialogs").GetBinaryData();
        _writeData(strex("{}.Dialogs.{}.fotxt-bin", _resPackName, lang_name), text_pack_data);
    }
}

FO_END_NAMESPACE();
