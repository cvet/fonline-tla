#include "Dialogs.h"
#include "Application.h"
#include "ConfigFile.h"
#include "FileSystem.h"

FO_BEGIN_NAMESPACE

static auto ExtractTextPackEntries(string_view str, HashResolver& hash_resolver, vector<pair<TextPackKey, string>>& entries) -> bool
{
    FO_STACK_TRACE_ENTRY();

    auto failed = false;
    auto source = string(str);
    istringstream sstr(source);
    string line;

    while (std::getline(sstr, line, '\n')) {
        TextPackKey num = 0;
        size_t offset = 0;

        for (auto i = 0; i < 3; i++) {
            const auto first = line.find('{', offset);
            auto last = line.find('}', first);

            if (first == string::npos || last == string::npos) {
                if (i == 2 && first != string::npos) {
                    string additional_line;
                    while (last == string::npos && std::getline(sstr, additional_line, '\n')) {
                        line += "\n" + additional_line;
                        last = line.find('}', first);
                    }
                }

                if (first == string::npos || last == string::npos) {
                    if (i > 0 || first != string::npos) {
                        failed = true;
                    }

                    break;
                }
            }

            auto substr = line.substr(first + 1, last - first - 1);
            offset = last + 1;

            if (i == 0 && num == 0) {
                num = strvex(substr).is_number() ? strvex(substr).to_uint32() : hash_resolver.ToHashedString(substr).as_uint32();
            }
            else if (i == 1 && num != 0) {
                num += !substr.empty() ? (strvex(substr).is_number() ? strvex(substr).to_uint32() : hash_resolver.ToHashedString(substr).as_uint32()) : 0;
            }
            else if (i == 2 && num != 0) {
                entries.emplace_back(num, std::move(substr));
            }
            else {
                failed = true;
            }
        }
    }

    return !failed;
}

static auto GetPropEnumIndex(const EngineMetadata* meta, string_view str, bool is_demand, uint8& type, bool& is_hash) -> int32
{
    FO_STACK_TRACE_ENTRY();

    const auto* prop_global = meta->GetPropertyRegistrator(GameProperties::ENTITY_TYPE_NAME)->FindProperty(str);
    const auto* prop_critter = meta->GetPropertyRegistrator(CritterProperties::ENTITY_TYPE_NAME)->FindProperty(str);
    const auto* prop_item = meta->GetPropertyRegistrator(ItemProperties::ENTITY_TYPE_NAME)->FindProperty(str);
    const auto* prop_location = meta->GetPropertyRegistrator(LocationProperties::ENTITY_TYPE_NAME)->FindProperty(str);
    const auto* prop_map = meta->GetPropertyRegistrator(MapProperties::ENTITY_TYPE_NAME)->FindProperty(str);

    auto count = 0;
    count += prop_global != nullptr ? 1 : 0;
    count += prop_critter != nullptr ? 1 : 0;
    count += prop_item != nullptr ? 1 : 0;
    count += prop_location != nullptr ? 1 : 0;
    count += prop_map != nullptr ? 1 : 0;

    if (count == 0) {
        throw DialogParseException("DR property not found in GlobalVars/Critter/Item/Location/Map", str);
    }
    if (count > 1) {
        throw DialogParseException("DR property found multiple instances in GlobalVars/Critter/Item/Location/Map", str);
    }

    const Property* prop = nullptr;

    if (prop_global != nullptr) {
        prop = prop_global;
        type = DR_PROP_GLOBAL;
    }
    else if (prop_critter != nullptr) {
        prop = prop_critter;
        type = DR_PROP_CRITTER;
    }
    else if (prop_item != nullptr) {
        prop = prop_item;
        type = DR_PROP_ITEM;
    }
    else if (prop_location != nullptr) {
        prop = prop_location;
        type = DR_PROP_LOCATION;
    }
    else if (prop_map != nullptr) {
        prop = prop_map;
        type = DR_PROP_MAP;
    }

    if (!prop->IsPlainData()) {
        throw DialogParseException("DR property is not plain data type", str);
    }
    if (prop->IsDisabled()) {
        throw DialogParseException("DR property is disabled", str);
    }
    if (!is_demand && !prop->IsMutable()) {
        throw DialogParseException("DR property is not mutable", str);
    }

    is_hash = prop->IsBaseTypeHash();
    return prop->GetRegIndex();
}

auto DialogAnswer::GetDemand(int32 index) -> DialogAnswerReq*
{
    FO_STACK_TRACE_ENTRY();

    if (index < 0 || index >= DemandsCount) {
        throw DialogException("Dialog demand index out of range", index);
    }

    return Demands.at(index).get();
}

auto DialogAnswer::GetResult(int32 index) -> DialogAnswerReq*
{
    FO_STACK_TRACE_ENTRY();

    if (index < 0 || index >= ResultsCount) {
        throw DialogException("Dialog result index out of range", index);
    }

    return Results.at(index).get();
}

auto DialogSpeech::GetAnswer(int32 index) -> DialogAnswer*
{
    FO_STACK_TRACE_ENTRY();

    if (index < 0 || index >= AnswersCount) {
        throw DialogException("Dialog answer index out of range", index);
    }

    return Answers.at(index).get();
}

auto DialogPack::GetSpeech(int32 index) -> DialogSpeech*
{
    FO_STACK_TRACE_ENTRY();

    if (index < 0 || index >= SpeechesCount) {
        throw DialogException("Dialog speech index out of range", index);
    }

    return Speeches.at(index).get();
}

DialogManager::DialogManager(EngineMetadata& meta) :
    _meta {&meta}
{
    FO_STACK_TRACE_ENTRY();
}

void DialogManager::LoadFromResources(const FileSystem& resources)
{
    FO_STACK_TRACE_ENTRY();

    size_t errors = 0;
    auto files = resources.FilterFiles("fodlg");

    for (const auto& file_header : files) {
        try {
            auto file = File::Load(file_header);
            auto pack = ParseDialog(file.GetNameNoExt(), file.GetStr());
            AddDialog(std::move(pack));
        }
        catch (const DialogParseException& ex) {
            ReportExceptionAndContinue(ex);
            errors++;
        }
    }

    if (errors != 0) {
        throw DialogManagerException("Can't load all dialogs");
    }
}

void DialogManager::AddDialog(refcount_ptr<DialogPack> pack)
{
    FO_STACK_TRACE_ENTRY();

    if (_dialogPacks.count(pack->PackId) != 0) {
        throw DialogManagerException("Dialog already added", pack->PackId);
    }

    _dialogPacks.emplace(pack->PackId, pack);
}

auto DialogManager::GetDialog(hstring pack_id) -> DialogPack*
{
    FO_STACK_TRACE_ENTRY();

    const auto it = _dialogPacks.find(pack_id);
    return it != _dialogPacks.end() ? it->second.get() : nullptr;
}

auto DialogManager::GetDialogs() -> vector<DialogPack*>
{
    FO_STACK_TRACE_ENTRY();

    vector<DialogPack*> result;

    for (auto& pack : _dialogPacks | std::views::values) {
        result.emplace_back(pack.get());
    }

    return result;
}

auto DialogManager::ParseDialog(string_view pack_name, string_view data) const -> refcount_ptr<DialogPack>
{
    FO_STACK_TRACE_ENTRY();

    auto pack = SafeAlloc::MakeRefCounted<DialogPack>();
    auto fodlg = ConfigFile(strex("{}.fodlg", pack_name), string(data), &_meta->Hashes, ConfigFileOption::CollectContent);

    pack->PackId = _meta->Hashes.ToHashedString(pack_name);
    pack->Comment = fodlg.GetSectionContent("comment");

    const auto lang_key = fodlg.GetAsStr("data", "lang");

    if (lang_key.empty()) {
        throw DialogParseException("Lang app not found", pack_name);
    }

    if (pack->PackId.as_uint32() <= 0xFFFF) {
        throw DialogParseException("Invalid hash for dialog name", pack_name);
    }

    const auto lang_apps = strvex(lang_key).split(' ');

    if (lang_apps.empty()) {
        throw DialogParseException("Lang app is empty", pack_name);
    }

    for (size_t i = 0; i < lang_apps.size(); i++) {
        const auto& lang_app = lang_apps[i];

        if (lang_app.size() != 4) {
            throw DialogParseException("Language length not equal 4", pack_name);
        }

        const auto lang_buf = fodlg.GetSectionContent(lang_app);

        if (lang_buf.empty()) {
            throw DialogParseException("One of the lang section not found", pack_name);
        }

        vector<pair<TextPackKey, string>> temp_entries;

        if (!ExtractTextPackEntries(lang_buf, _meta->Hashes, temp_entries)) {
            throw DialogParseException("Load MSG fail", pack_name);
        }

        pack->Texts.emplace_back(string(lang_app), TextPack {});

        for (auto& [str_num, raw_str] : temp_entries) {
            const uint32 new_str_num = pack->PackId.as_uint32() + (str_num < 100000000 ? str_num / 10 : str_num - 100000000 + 12000);
            string str = strex(raw_str).replace("\n\\[", "\n[");
            pack->Texts.at(i).second.AddStr(new_str_num, std::move(str));
        }
    }

    const auto dlg_buf = fodlg.GetSectionContent("dialog");

    if (dlg_buf.empty()) {
        throw DialogParseException("Dialog section not found", pack_name);
    }

    auto dlg_buf_str = string(dlg_buf);
    istringstream input(dlg_buf_str);

    string tok;
    input >> tok;

    if (tok != "&") {
        throw DialogParseException("Dialog start token not found", pack_name);
    }

    while (!input.eof()) {
        auto speech = SafeAlloc::MakeRefCounted<DialogSpeech>();

        input >> speech->Id;

        if (input.fail()) {
            throw DialogParseException("Bad dialog id number", pack_name);
        }

        uint32 text_id = 0;
        input >> text_id;

        if (input.fail()) {
            throw DialogParseException("Bad text link", pack_name);
        }

        speech->TextId = pack->PackId.as_uint32() + text_id / 10;

        string script;
        input >> script;

        if (input.fail()) {
            throw DialogParseException("Bad not answer action", pack_name);
        }
        if (script == "NOT_ANSWER_CLOSE_DIALOG" || script == "None") {
            script = "";
        }

        speech->DlgScriptFuncName = _meta->Hashes.ToHashedString(script);

        uint32 flags = 0;
        input >> flags;

        if (input.fail()) {
            throw DialogParseException("Bad flags", pack_name);
        }

        // Read answers
        input >> tok;

        if (input.fail()) {
            throw DialogParseException("Dialog corrupted", pack_name);
        }

        if (tok == "@" || tok == "&") {
            pack->SpeechesCount++;
            pack->Speeches.emplace_back(speech);

            if (tok == "@") {
                continue;
            }
            if (tok == "&") {
                break;
            }
        }

        if (tok != "#") {
            throw DialogParseException("Parse error 0", pack_name);
        }

        while (!input.eof()) {
            auto answer = SafeAlloc::MakeRefCounted<DialogAnswer>();
            input >> answer->Link;

            if (input.fail()) {
                throw DialogParseException("Bad link in answer", pack_name);
            }

            input >> text_id;

            if (input.fail()) {
                throw DialogParseException("Bad text link in answer", pack_name);
            }

            answer->TextId = pack->PackId.as_uint32() + text_id / 10;

            while (!input.eof()) {
                input >> tok;

                if (input.fail()) {
                    throw DialogParseException("Parse answer character fail", pack_name);
                }

                if (tok == "D") {
                    answer->DemandsCount++;
                    answer->Demands.emplace_back(LoadDemandResult(input, true));
                }
                else if (tok == "R") {
                    answer->ResultsCount++;
                    answer->Results.emplace_back(LoadDemandResult(input, false));
                }
                else if (tok == "*" || tok == "d" || tok == "r") {
                    throw DialogParseException("Found old token, update dialog file to actual format (resave in version 2.22)", pack_name);
                }
                else {
                    break;
                }
            }

            speech->AnswersCount++;
            speech->Answers.emplace_back(answer);

            if (tok == "@" || tok == "&") {
                break;
            }
            else if (tok != "#") {
                throw DialogParseException("Invalid answer token", pack_name);
            }
        }

        pack->SpeechesCount++;
        pack->Speeches.emplace_back(speech);

        if (tok == "&") {
            break;
        }
    }

    return pack;
}

auto DialogManager::LoadDemandResult(istringstream& input, bool is_demand) const -> refcount_ptr<DialogAnswerReq>
{
    FO_STACK_TRACE_ENTRY();

    uint8 who = DR_WHO_PLAYER;
    uint8 oper = '=';
    int32 values_count = 0;
    string svalue;
    int32 ivalue = 0;
    int32 id_index = 0;
    hstring id_hash;
    string type_str;
    string name;
    string script_name;
    bool no_recheck = false;
    int32 script_val[5] = {0, 0, 0, 0, 0};

    input >> type_str;

    if (input.fail()) {
        throw DialogParseException("Parse DR type fail");
    }

    auto type = GetDrType(type_str);

    if (type == DR_NO_RECHECK) {
        no_recheck = true;
        input >> type_str;

        if (input.fail()) {
            throw DialogParseException("Parse DR type fail2");
        }

        type = GetDrType(type_str);
    }

    switch (type) {
    case DR_PROP_CRITTER: {
        // Who
        input >> who;
        who = GetWho(who);

        if (who == DR_WHO_NONE) {
            throw DialogParseException("Invalid DR property who", who);
        }

        // Name
        input >> name;
        auto is_hash = false;
        id_index = GetPropEnumIndex(_meta.get(), name, is_demand, type, is_hash);

        // Operator
        input >> oper;

        if (!CheckOper(oper)) {
            throw DialogParseException("Invalid DR property oper", oper);
        }

        // Value
        input >> svalue;

        if (is_hash) {
            ivalue = _meta->Hashes.ToHashedString(svalue).as_int32();
        }
        else {
            ivalue = _meta->ResolveGenericValue(svalue);
        }
    } break;
    case DR_ITEM: {
        // Who
        input >> who;
        who = GetWho(who);

        if (who == DR_WHO_NONE) {
            throw DialogParseException("Invalid DR item who", who);
        }

        // Name
        input >> name;
        id_hash = _meta->Hashes.ToHashedString(name);

        // Operator
        input >> oper;

        if (!CheckOper(oper)) {
            throw DialogParseException("Invalid DR item oper", oper);
        }

        // Value
        input >> svalue;
        ivalue = _meta->ResolveGenericValue(svalue);
    } break;
    case DR_SCRIPT: {
        // Script name
        input >> script_name;

        // Values count
        input >> values_count;

        // Values
        string value_str;

        if (values_count > 0) {
            input >> value_str;
            script_val[0] = _meta->ResolveGenericValue(value_str);
        }
        if (values_count > 1) {
            input >> value_str;
            script_val[1] = _meta->ResolveGenericValue(value_str);
        }
        if (values_count > 2) {
            input >> value_str;
            script_val[2] = _meta->ResolveGenericValue(value_str);
        }
        if (values_count > 3) {
            input >> value_str;
            script_val[3] = _meta->ResolveGenericValue(value_str);
        }
        if (values_count > 4) {
            input >> value_str;
            script_val[4] = _meta->ResolveGenericValue(value_str);
        }
        if (values_count < 0 || values_count > 5) {
            throw DialogParseException("Invalid values count", values_count);
        }
    } break;
    case DR_OR:
        break;
    default:
        throw DialogParseException("Invalid DR type");
    }

    // Validate parsing
    if (input.fail()) {
        throw DialogParseException("DR parse fail");
    }

    // Fill
    auto result = SafeAlloc::MakeRefCounted<DialogAnswerReq>();
    result->Type = type;
    result->Who = who;
    result->ParamIndex = id_index;
    result->ParamHash = id_hash;
    result->AnswerScriptFuncName = _meta->Hashes.ToHashedString(script_name);
    result->Op = oper;
    result->ValuesCount = static_cast<uint8>(values_count);
    result->NoRecheck = no_recheck;
    result->Value = ivalue;
    result->ValueExt0 = script_val[0];
    result->ValueExt1 = script_val[1];
    result->ValueExt2 = script_val[2];
    result->ValueExt3 = script_val[3];
    result->ValueExt4 = script_val[4];
    return result;
}

auto DialogManager::GetDrType(string_view str) const -> uint8
{
    FO_STACK_TRACE_ENTRY();

    if (str == "Property" || str == "_param") {
        return DR_PROP_CRITTER;
    }
    if (str == "Item" || str == "_item") {
        return DR_ITEM;
    }
    if (str == "Script" || str == "_script") {
        return DR_SCRIPT;
    }
    if (str == "NoRecheck" || str == "no_recheck") {
        return DR_NO_RECHECK;
    }
    if (str == "Or" || str == "or") {
        return DR_OR;
    }
    return DR_NONE;
}

auto DialogManager::GetWho(uint8 who) const -> uint8
{
    FO_STACK_TRACE_ENTRY();

    if (who == 'P' || who == 'p') {
        return DR_WHO_PLAYER;
    }
    if (who == 'N' || who == 'n') {
        return DR_WHO_NPC;
    }
    return DR_WHO_NONE;
}

auto DialogManager::CheckOper(uint8 oper) const -> bool
{
    FO_STACK_TRACE_ENTRY();

    return oper == '>' || oper == '<' || oper == '=' || oper == '+' || oper == '-' || oper == '*' || oper == '/' || oper == '!' || oper == '}' || oper == '{';
}

FO_END_NAMESPACE
