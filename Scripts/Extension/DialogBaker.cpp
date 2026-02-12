#include "DialogBaker.h"
#include "Dialogs.h"
#include "ScriptSystem.h"
#include "TextPack.h"

FO_BEGIN_NAMESPACE

class CritterTag
{
};

DialogBaker::DialogBaker(shared_ptr<BakingContext> ctx) :
    BaseBaker(std::move(ctx))
{
    FO_STACK_TRACE_ENTRY();
}

void DialogBaker::BakeFiles(const FileCollection& files, string_view target_path) const
{
    FO_STACK_TRACE_ENTRY();

    // Collect dialog files
    vector<File> filtered_files;

    if (target_path.empty()) {
        for (const auto& file_header : files) {
            if (strex(file_header.GetPath()).get_file_extension() != "fodlg") {
                continue;
            }
            if (_context->BakeChecker && !_context->BakeChecker(file_header.GetPath(), file_header.GetWriteTime())) {
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
        if (_context->BakeChecker && !_context->BakeChecker(target_path, file.GetWriteTime())) {
            return;
        }

        filtered_files.emplace_back(std::move(file));
    }

    if (filtered_files.empty()) {
        return;
    }

    // Load dialogs
    auto server_engine = BakerServerEngine(*_context->BakedFiles);
    server_engine.MapEngineType<CritterTag>(server_engine.GetBaseType("Critter"));
    server_engine.InitSubsystems(&server_engine, *_context->BakedFiles);
    const auto dialog_mngr = DialogManager(server_engine);

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
        for (const auto& speech : dlg_pack->Speeches) {
            if (speech->DlgScriptFuncName) {
                if (!server_engine.CheckFunc<void, CritterTag*, CritterTag*, string&>(speech->DlgScriptFuncName) && //
                    !server_engine.CheckFunc<int32, CritterTag*, CritterTag*, string&>(speech->DlgScriptFuncName)) {
                    WriteLog("Dialog {} invalid start function {}", dlg_pack->PackId, speech->DlgScriptFuncName);
                    errors++;
                }
            }

            for (const auto& answer : speech->Answers) {
                for (const auto& demand : answer->Demands) {
                    if (demand->Type == DR_SCRIPT) {
                        if ((demand->ValuesCount == 0 && !server_engine.CheckFunc<bool, CritterTag*, CritterTag*>(demand->AnswerScriptFuncName)) || //
                            (demand->ValuesCount == 1 && !server_engine.CheckFunc<bool, CritterTag*, CritterTag*, int32>(demand->AnswerScriptFuncName)) || //
                            (demand->ValuesCount == 2 && !server_engine.CheckFunc<bool, CritterTag*, CritterTag*, int32, int32>(demand->AnswerScriptFuncName)) || //
                            (demand->ValuesCount == 3 && !server_engine.CheckFunc<bool, CritterTag*, CritterTag*, int32, int32, int32>(demand->AnswerScriptFuncName)) || //
                            (demand->ValuesCount == 4 && !server_engine.CheckFunc<bool, CritterTag*, CritterTag*, int32, int32, int32, int32>(demand->AnswerScriptFuncName)) || //
                            (demand->ValuesCount == 5 && !server_engine.CheckFunc<bool, CritterTag*, CritterTag*, int32, int32, int32, int32, int32>(demand->AnswerScriptFuncName))) {
                            WriteLog("Dialog {} answer demand invalid function {}", dlg_pack->PackId, demand->AnswerScriptFuncName);
                            errors++;
                        }
                    }
                }

                for (const auto& result : answer->Results) {
                    if (result->Type == DR_SCRIPT) {
                        int32 not_found_count = 0;

                        if ((result->ValuesCount == 0 && !server_engine.CheckFunc<void, CritterTag*, CritterTag*>(result->AnswerScriptFuncName)) || //
                            (result->ValuesCount == 1 && !server_engine.CheckFunc<void, CritterTag*, CritterTag*, int32>(result->AnswerScriptFuncName)) || //
                            (result->ValuesCount == 2 && !server_engine.CheckFunc<void, CritterTag*, CritterTag*, int32, int32>(result->AnswerScriptFuncName)) || //
                            (result->ValuesCount == 3 && !server_engine.CheckFunc<void, CritterTag*, CritterTag*, int32, int32, int32>(result->AnswerScriptFuncName)) || //
                            (result->ValuesCount == 4 && !server_engine.CheckFunc<void, CritterTag*, CritterTag*, int32, int32, int32, int32>(result->AnswerScriptFuncName)) || //
                            (result->ValuesCount == 5 && !server_engine.CheckFunc<void, CritterTag*, CritterTag*, int32, int32, int32, int32, int32>(result->AnswerScriptFuncName))) {
                            not_found_count++;
                        }

                        if ((result->ValuesCount == 0 && !server_engine.CheckFunc<int32, CritterTag*, CritterTag*>(result->AnswerScriptFuncName)) || //
                            (result->ValuesCount == 1 && !server_engine.CheckFunc<int32, CritterTag*, CritterTag*, int32>(result->AnswerScriptFuncName)) || //
                            (result->ValuesCount == 2 && !server_engine.CheckFunc<int32, CritterTag*, CritterTag*, int32, int32>(result->AnswerScriptFuncName)) || //
                            (result->ValuesCount == 3 && !server_engine.CheckFunc<int32, CritterTag*, CritterTag*, int32, int32, int32>(result->AnswerScriptFuncName)) || //
                            (result->ValuesCount == 4 && !server_engine.CheckFunc<int32, CritterTag*, CritterTag*, int32, int32, int32, int32>(result->AnswerScriptFuncName)) || //
                            (result->ValuesCount == 5 && !server_engine.CheckFunc<int32, CritterTag*, CritterTag*, int32, int32, int32, int32, int32>(result->AnswerScriptFuncName))) {
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
        _context->WriteData(file.GetPath(), file.GetData());
    }
}

DialogTextBaker::DialogTextBaker(shared_ptr<BakingContext> ctx) :
    BaseBaker(std::move(ctx))
{
    FO_STACK_TRACE_ENTRY();
}

void DialogTextBaker::BakeFiles(const FileCollection& files, string_view target_path) const
{
    FO_STACK_TRACE_ENTRY();

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
        for (const auto& lang_name : _context->Settings->BakeLanguages) {
            if (!_context->BakeChecker || _context->BakeChecker(strex("{}.Dialogs.{}.fotxt-bin", _context->PackName, lang_name), max_write_time)) {
                something_changed = true;
            }
        }
    }

    if (!something_changed) {
        return;
    }

    // Load dialogs
    auto server_engine = BakerServerEngine(*_context->BakedFiles);
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
        for (const auto& dlg_pack_text : dlg_pack->Texts) {
            const string lang_pack = dlg_pack_text.first;

            if (std::ranges::find_if(_context->Settings->BakeLanguages, [&](auto&& l) { return l == lang_pack; }) == _context->Settings->BakeLanguages.end()) {
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

    TextPack::FixPacks(_context->Settings->BakeLanguages, lang_packs);

    if (errors != 0) {
        throw DialogBakerException("Errors during dialogs text baking");
    }

    // Write data
    for (auto&& [lang_name, text_packs] : lang_packs) {
        auto text_pack_data = text_packs.at("Dialogs").GetBinaryData();
        _context->WriteData(strex("{}.Dialogs.{}.fotxt-bin", _context->PackName, lang_name), text_pack_data);
    }
}

FO_END_NAMESPACE
