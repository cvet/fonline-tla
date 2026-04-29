#include "Dialogs.h"
#include "Application.h"
#include "ConfigFile.h"
#include "FileSystem.h"

FO_USING_NAMESPACE();

static constexpr int32_t DIALOG_LINK_EXIT = 0;
static constexpr int32_t DIALOG_LINK_BACK = -1;
static constexpr string_view DIALOG_ANSWER_LINK_ENUM = "DialogAnswerLink";

static auto IsDialogCommentOrEmpty(string_view line) -> bool
{
    FO_STACK_TRACE_ENTRY();

    size_t start = 0;

    while (start < line.size() && std::isspace(static_cast<unsigned char>(line[start])) != 0) {
        start++;
    }

    if (start >= line.size()) {
        return true;
    }

    return line[start] == '#' || (line[start] == '/' && start + 1 < line.size() && line[start + 1] == '/');
}

static auto TryNormalizeDialogLinkValue(const EngineMetadata* meta, int64_t link, int32_t& normalized_link) -> bool
{
    FO_STACK_TRACE_ENTRY();

    if (link == DIALOG_LINK_EXIT) {
        normalized_link = DIALOG_LINK_EXIT;
        return true;
    }
    if (link == DIALOG_LINK_BACK) {
        normalized_link = DIALOG_LINK_BACK;
        return true;
    }

    if (link < -2147483648ll || link > 2147483647ll) {
        return false;
    }

    normalized_link = numeric_cast<int32_t>(link);

    if (normalized_link >= 0) {
        return true;
    }

    bool failed = false;
    const auto& value_name = meta->ResolveEnumValueName(DIALOG_ANSWER_LINK_ENUM, normalized_link, &failed);
    ignore_unused(value_name);

    if (failed) {
        return false;
    }

    return true;
}

static auto TryResolveDialogAnswerLinkCanonical(const EngineMetadata* meta, int32_t link, string& canonical) -> bool
{
    FO_STACK_TRACE_ENTRY();

    int32_t normalized_link = 0;
    if (!TryNormalizeDialogLinkValue(meta, link, normalized_link)) {
        return false;
    }

    link = normalized_link;

    switch (link) {
    case DIALOG_LINK_EXIT:
        canonical = "Exit";
        return true;
    case DIALOG_LINK_BACK:
        canonical = "Back";
        return true;
    default:
        break;
    }

    if (link >= 0) {
        canonical = std::to_string(link);
        return true;
    }

    bool failed = false;
    const auto& value_name = meta->ResolveEnumValueName(DIALOG_ANSWER_LINK_ENUM, link, &failed);
    if (failed) {
        return false;
    }

    canonical = string(value_name);
    return true;
}

static auto TryParseDialogLinkToken(const EngineMetadata* meta, string_view token, int32_t& value, string& canonical) -> bool
{
    FO_STACK_TRACE_ENTRY();

    if (strvex(token).compare_ignore_case("Exit")) {
        value = DIALOG_LINK_EXIT;
        canonical = "Exit";
        return true;
    }
    if (strvex(token).compare_ignore_case("Back")) {
        value = DIALOG_LINK_BACK;
        canonical = "Back";
        return true;
    }

    if (strvex(token).is_number()) {
        if (!TryNormalizeDialogLinkValue(meta, strvex(token).to_int64(), value)) {
            return false;
        }

        return TryResolveDialogAnswerLinkCanonical(meta, value, canonical);
    }

    string entry_name;

    const auto separator_pos = token.find("::");
    if (separator_pos != std::string_view::npos) {
        if (token.substr(0, separator_pos) != DIALOG_ANSWER_LINK_ENUM || separator_pos + 2 >= token.size()) {
            return false;
        }

        entry_name = string(token.substr(separator_pos + 2));
    }
    else {
        entry_name = string(token);
    }

    bool failed = false;
    value = meta->ResolveEnumValue(DIALOG_ANSWER_LINK_ENUM, entry_name, &failed);
    if (!failed) {
        int32_t normalized_link = 0;
        if (!TryNormalizeDialogLinkValue(meta, value, normalized_link)) {
            return false;
        }

        value = normalized_link;
        return TryResolveDialogAnswerLinkCanonical(meta, value, canonical);
    }

    return false;
}

static auto TryParseDialogAnswerToken(const EngineMetadata* meta, string_view token, int32_t& link, string& token_for_hash) -> bool
{
    FO_STACK_TRACE_ENTRY();

    string base_token = string(token);
    size_t marker_count = 0;

    while (!base_token.empty() && base_token.back() == '*') {
        marker_count++;
        base_token.pop_back();
    }

    if (base_token.empty() || !TryParseDialogLinkToken(meta, base_token, link, token_for_hash)) {
        return false;
    }

    if (!TryNormalizeDialogLinkValue(meta, link, link)) {
        return false;
    }

    token_for_hash.append(marker_count, '*');
    return true;
}

static auto StripInlineDialogComment(string_view line) -> string
{
    for (size_t i = 0; i < line.size(); i++) {
        if (line[i] == '#' && (i == 0 || std::isspace(static_cast<unsigned char>(line[i - 1])) != 0)) {
            return string(line.substr(0, i));
        }
    }

    return string(line);
}

static auto StartsWithIgnoreCase(string_view value, string_view prefix) -> bool
{
    FO_STACK_TRACE_ENTRY();

    if (value.size() < prefix.size()) {
        return false;
    }

    return strvex(value.substr(0, prefix.size())).compare_ignore_case(prefix);
}

static auto TryParseDialogTextEntryStart(string_view line, string& key1, string& key2, string& text, bool& completed) -> bool
{
    FO_STACK_TRACE_ENTRY();

    const string_view trimmed = strvex(line).trim();

    if (trimmed.empty() || trimmed.front() != '{') {
        return false;
    }

    const size_t key1_end = trimmed.find('}', 1);

    if (key1_end == string::npos || key1_end + 1 >= trimmed.size() || trimmed[key1_end + 1] != '{') {
        return false;
    }

    const size_t key2_begin = key1_end + 2;
    const size_t key2_end = trimmed.find('}', key2_begin);

    if (key2_end == string::npos || key2_end + 1 >= trimmed.size() || trimmed[key2_end + 1] != '{') {
        return false;
    }

    const size_t text_begin = key2_end + 2;

    if (text_begin > trimmed.size() - 1) {
        return false;
    }

    key1 = trimmed.substr(1, key1_end - 1);
    key2 = trimmed.substr(key2_begin, key2_end - key2_begin);
    text = trimmed.substr(text_begin);

    completed = !text.empty() && text.back() == '}';

    if (completed) {
        text.pop_back();
    }

    return true;
}

static auto CollectDialogLangSections(ConfigFile& fodlg, string_view pack_name) -> vector<string>
{
    FO_STACK_TRACE_ENTRY();

    vector<string> lang_sections;

    for (const string_view section_name : fodlg.GetSections() | std::views::keys) {
        if (StartsWithIgnoreCase(section_name, "Text") && section_name.size() >= 5 && std::isspace(static_cast<unsigned char>(section_name[4])) != 0) {
            const string_view lang = strvex(section_name.substr(5)).trim();

            if (!lang.empty()) {
                lang_sections.emplace_back(lang);
            }
        }
    }

    if (lang_sections.empty()) {
        throw DialogParseException("Text sections not found", pack_name);
    }

    return lang_sections;
}

static void LoadDialogTextSection(const EngineMetadata& meta, DialogPack* pack, string_view pack_name, const string& lang_section_name, const string& lang_buf)
{
    FO_STACK_TRACE_ENTRY();

    if (lang_section_name.size() != 4) {
        throw DialogParseException("Language length not equal 4", pack_name);
    }
    if (lang_buf.empty()) {
        throw DialogParseException("One of the lang section not found", pack_name);
    }

    TextPack temp_msg {meta.Hashes};

    if (!temp_msg.LoadFromString(lang_buf, "Dialogs")) {
        throw DialogParseException("Load MSG fail", pack_name);
    }

    pack->Texts.emplace_back(lang_section_name, TextPack {meta.Hashes});
    const size_t text_pack_index = pack->Texts.size() - 1;

    istringstream lang_lines {string(lang_buf)};
    string lang_line;
    bool collecting_multiline = false;
    string current_key1;
    string current_key2;
    string current_text;

    auto add_text_entry = [&](const string& key1, const string& key2, string text) {
        if (key1.empty()) {
            return;
        }

        text = strex(text).replace("\\n", "\n");
        pack->Texts.at(text_pack_index).second.AddStr(TextPackKey::FromParts(meta.Hashes, "Dialogs", string(pack_name), key1, key2), std::move(text));
    };

    while (std::getline(lang_lines, lang_line)) {
        if (!collecting_multiline) {
            string key1;
            string key2;
            string text;
            bool completed = false;

            if (!TryParseDialogTextEntryStart(lang_line, key1, key2, text, completed)) {
                continue;
            }

            if (completed) {
                add_text_entry(key1, key2, std::move(text));
            }
            else {
                collecting_multiline = true;
                current_key1 = std::move(key1);
                current_key2 = std::move(key2);
                current_text = std::move(text);
            }
        }
        else {
            current_text += "\n";
            current_text += lang_line;

            const string_view trimmed_line = strvex(lang_line).trim();
            if (!trimmed_line.empty() && trimmed_line.back() == '}') {
                const size_t close_pos = current_text.find_last_of('}');
                if (close_pos != string::npos) {
                    current_text.erase(close_pos, 1);
                }

                add_text_entry(current_key1, current_key2, std::move(current_text));
                collecting_multiline = false;
                current_key1.clear();
                current_key2.clear();
                current_text.clear();
            }
        }
    }

    if (collecting_multiline) {
        throw DialogParseException("Unclosed text entry in lang section", pack_name);
    }
}

static auto GetPropEnumIndex(const EngineMetadata* meta, string_view str, bool is_demand, uint8_t& type) -> int32_t
{
    FO_STACK_TRACE_ENTRY();

    const auto* prop_global = meta->GetPropertyRegistrator(GameProperties::ENTITY_TYPE_NAME)->FindProperty(str);
    const auto* prop_critter = meta->GetPropertyRegistrator(CritterProperties::ENTITY_TYPE_NAME)->FindProperty(str);
    const auto* prop_item = meta->GetPropertyRegistrator(ItemProperties::ENTITY_TYPE_NAME)->FindProperty(str);
    const auto* prop_location = meta->GetPropertyRegistrator(LocationProperties::ENTITY_TYPE_NAME)->FindProperty(str);
    const auto* prop_map = meta->GetPropertyRegistrator(MapProperties::ENTITY_TYPE_NAME)->FindProperty(str);

    int32_t count = 0;
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

    return prop->GetRegIndex();
}

auto DialogAnswer::GetDemand(int32_t index) -> DialogAnswerReq*
{
    FO_STACK_TRACE_ENTRY();

    if (index < 0 || index >= DemandsCount) {
        throw DialogException("Dialog demand index out of range", index);
    }

    return Demands.at(index).get();
}

auto DialogAnswer::GetResult(int32_t index) -> DialogAnswerReq*
{
    FO_STACK_TRACE_ENTRY();

    if (index < 0 || index >= ResultsCount) {
        throw DialogException("Dialog result index out of range", index);
    }

    return Results.at(index).get();
}

auto DialogSpeech::GetAnswer(int32_t index) -> DialogAnswer*
{
    FO_STACK_TRACE_ENTRY();

    if (index < 0 || index >= AnswersCount) {
        throw DialogException("Dialog answer index out of range", index);
    }

    return Answers.at(index).get();
}

auto DialogPack::GetSpeech(int32_t index) -> DialogSpeech*
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
    const auto files = resources.FilterFiles("fodlg");

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
    auto fodlg = ConfigFile(strex("{}.fodlg", pack_name), string(data), ConfigFileOption::CollectContent);

    pack->PackId = _meta->Hashes.ToHashedString(pack_name);

    const bool has_new_dialog = fodlg.HasSection("Dialog");

    if (!has_new_dialog) {
        throw DialogParseException("Dialog section not found", pack_name);
    }

    const string_view comment = fodlg.GetSectionContent("Comment");
    pack->Comment = comment.empty() ? fodlg.GetSectionContent("comment") : comment;
    pack->Comment = strvex(pack->Comment).trim();

    const vector<string> lang_sections = CollectDialogLangSections(fodlg, pack_name);

    for (const auto& lang_section_name : lang_sections) {
        const auto lang_section = strex("Text {}", lang_section_name);
        const string lang_buf = string(fodlg.GetSectionContent(lang_section));

        LoadDialogTextSection(*_meta, pack.operator->(), pack_name, lang_section_name, lang_buf);
    }

    const auto dlg_buf = fodlg.GetSectionContent("Dialog");

    if (dlg_buf.empty()) {
        throw DialogParseException("Dialog section not found", pack_name);
    }

    const string new_dlg_data = string(dlg_buf);

    refcount_ptr<DialogSpeech> current_speech;
    refcount_ptr<DialogAnswer> current_answer;
    bool has_speech = false;

    auto flush_answer = [&]() {
        if (current_answer != nullptr) {
            current_speech->AnswersCount++;
            current_speech->Answers.emplace_back(current_answer);
            current_answer.reset();
        }
    };

    auto flush_speech = [&]() {
        if (current_speech != nullptr) {
            flush_answer();
            pack->SpeechesCount++;
            pack->Speeches.emplace_back(current_speech);
            current_speech.reset();
        }
    };

    istringstream lines {new_dlg_data};
    string line;

    while (std::getline(lines, line)) {
        if (IsDialogCommentOrEmpty(line)) {
            continue;
        }

        const string trimmed = string(strvex(StripInlineDialogComment(line)).trim());

        if (trimmed.empty()) {
            continue;
        }

        istringstream cmd_input(trimmed);
        string command;
        cmd_input >> command;

        const size_t pos = trimmed.find_first_of(" \t");
        const string rest = pos != string::npos ? string(strvex(trimmed.substr(pos + 1)).trim()) : string {};

        if (strvex(command).compare_ignore_case("Speech")) {
            flush_speech();

            int32_t speech_id = 0;
            vector<string> args;
            string arg;

            while (cmd_input >> arg) {
                args.emplace_back(arg);
            }

            if (args.empty()) {
                throw DialogParseException("Dialog syntax: invalid Speech command", pack_name);
            }
            if (!strvex(args[0]).is_number()) {
                throw DialogParseException("Dialog syntax: invalid Speech id", pack_name);
            }

            speech_id = numeric_cast<int32_t>(strvex(args[0]).to_int64());

            if (args.size() != 1) {
                throw DialogParseException("Dialog syntax: Speech must contain only id", pack_name);
            }

            auto speech = SafeAlloc::MakeRefCounted<DialogSpeech>();
            speech->Id = speech_id;
            speech->TextId = _meta->Hashes.ToHashedString(strex("Speech {}", speech->Id));
            speech->DlgScriptFuncName = hstring {};

            current_speech = speech;
            has_speech = true;
            continue;
        }

        if (strvex(command).compare_ignore_case("Script")) {
            if (!current_speech) {
                throw DialogParseException("Dialog syntax: Script outside speech", pack_name);
            }
            if (current_answer) {
                throw DialogParseException("Dialog syntax: Script must be placed before Answer commands", pack_name);
            }

            vector<string> args;
            string arg;

            while (cmd_input >> arg) {
                args.emplace_back(arg);
            }

            if (args.size() != 1) {
                throw DialogParseException("Dialog syntax: invalid Script command", pack_name);
            }

            current_speech->DlgScriptFuncName = _meta->Hashes.ToHashedString(args[0]);
            continue;
        }

        if (strvex(command).compare_ignore_case("Answer")) {
            if (!current_speech) {
                throw DialogParseException("Dialog syntax: Answer outside speech", pack_name);
            }

            flush_answer();

            int32_t link = 0;
            vector<string> args;
            string arg;
            string answer_token_for_hash;

            while (cmd_input >> arg) {
                args.emplace_back(arg);
            }

            if (args.size() != 1 || !TryParseDialogAnswerToken(_meta.get(), args[0], link, answer_token_for_hash)) {
                throw DialogParseException("Dialog syntax: invalid Answer command", pack_name, args[0], link, answer_token_for_hash);
            }

            auto answer = SafeAlloc::MakeRefCounted<DialogAnswer>();
            answer->Link = link;
            answer->TextId = _meta->Hashes.ToHashedString(strex("Speech {} Answer {}", current_speech->Id, answer_token_for_hash));

            current_answer = answer;
            continue;
        }

        if (strvex(command).compare_ignore_case("Demand") || strvex(command).compare_ignore_case("Result")) {
            if (!current_answer) {
                throw DialogParseException("Dialog syntax: Demand/Result outside answer", pack_name);
            }
            if (rest.empty()) {
                throw DialogParseException("Dialog syntax: empty Demand/Result payload", pack_name);
            }

            const bool is_demand = strvex(command).compare_ignore_case("Demand");
            const string payload = strvex(rest).trim().str();
            istringstream dr_input(payload);
            auto req = LoadDemandResult(dr_input, is_demand);

            if (is_demand) {
                current_answer->DemandsCount++;
                current_answer->Demands.emplace_back(req);
            }
            else {
                current_answer->ResultsCount++;
                current_answer->Results.emplace_back(req);
            }

            continue;
        }

        throw DialogParseException("Dialog syntax: unknown command", pack_name);
    }

    flush_speech();

    if (!has_speech) {
        throw DialogParseException("Dialog syntax: no speech commands found", pack_name);
    }

    return pack;
}

auto DialogManager::LoadDemandResult(istringstream& input, bool is_demand) const -> refcount_ptr<DialogAnswerReq>
{
    FO_STACK_TRACE_ENTRY();

    uint8_t who = DR_WHO_PLAYER;
    uint8_t oper = '=';
    int32_t values_count = 0;
    string svalue;
    any_t value;
    int32_t id_index = 0;
    hstring id_hash;
    string type_str;
    string name;
    string script_name;
    bool no_recheck = false;
    any_t script_val[5];

    auto parse_who = [&](string_view who_token) -> uint8_t {
        if (strvex(who_token).compare_ignore_case("Player")) {
            return DR_WHO_PLAYER;
        }
        if (strvex(who_token).compare_ignore_case("Npc")) {
            return DR_WHO_NPC;
        }

        throw DialogParseException("Invalid DR who token, expected Player or Npc", who_token);
    };

    auto parse_oper = [&](string_view oper_token) -> uint8_t {
        if (oper_token == ">") {
            return '>';
        }
        if (oper_token == "<") {
            return '<';
        }
        if (oper_token == "==") {
            return '=';
        }
        if (oper_token == "!=") {
            return '!';
        }
        if (oper_token == "<=") {
            return '{';
        }
        if (oper_token == ">=") {
            return '}';
        }

        if (!is_demand) {
            if (oper_token == "+=") {
                return '+';
            }
            if (oper_token == "-=") {
                return '-';
            }
            if (oper_token == "*=") {
                return '*';
            }
            if (oper_token == "/=") {
                return '/';
            }
            if (oper_token == "=") {
                return '=';
            }
        }

        throw DialogParseException("Invalid DR operator token", oper_token);
    };

    input >> type_str;

    if (input.fail()) {
        throw DialogParseException("Parse DR type fail");
    }

    uint8_t type = GetDrType(type_str);

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
        string who_token;
        input >> who_token;
        who = parse_who(who_token);

        if (who == DR_WHO_NONE) {
            throw DialogParseException("Invalid DR property who", who);
        }

        // Name
        input >> name;
        id_index = GetPropEnumIndex(_meta.get(), name, is_demand, type);

        // Operator
        string oper_token;
        input >> oper_token;
        oper = parse_oper(oper_token);

        if (!CheckOper(oper)) {
            throw DialogParseException("Invalid DR property oper", oper);
        }

        // Value
        input >> svalue;
        value = any_t {std::move(svalue)};
    } break;
    case DR_ITEM: {
        // Who
        string who_token;
        input >> who_token;
        who = parse_who(who_token);

        if (who == DR_WHO_NONE) {
            throw DialogParseException("Invalid DR item who", who);
        }

        // Name
        input >> name;
        id_hash = _meta->Hashes.ToHashedString(name);

        // Operator
        string oper_token;
        input >> oper_token;
        oper = parse_oper(oper_token);

        if (!CheckOper(oper)) {
            throw DialogParseException("Invalid DR item oper", oper);
        }

        // Value
        input >> svalue;
        value = any_t {std::move(svalue)};
    } break;
    case DR_SCRIPT: {
        // Script name
        input >> script_name;

        if (input.fail()) {
            throw DialogParseException("Parse DR script name fail");
        }

        string value_str;
        values_count = 0;

        while (input >> value_str) {
            if (values_count >= 5) {
                throw DialogParseException("Invalid values count", values_count + 1);
            }

            script_val[values_count] = any_t {std::move(value_str)};
            values_count++;
        }

        if (input.fail() && input.eof()) {
            input.clear();
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

    string trailing_token;

    if (input >> trailing_token) {
        throw DialogParseException("DR parse fail: extra tokens after command", trailing_token);
    }

    // Fill
    auto result = SafeAlloc::MakeRefCounted<DialogAnswerReq>();
    result->Type = type;
    result->Who = who;
    result->ParamIndex = id_index;
    result->ParamHash = id_hash;
    result->AnswerScriptFuncName = _meta->Hashes.ToHashedString(script_name);
    result->Op = oper;
    result->ValuesCount = static_cast<uint8_t>(values_count);
    result->NoRecheck = no_recheck;
    result->Value = std::move(value);
    result->ValueExt0 = std::move(script_val[0]);
    result->ValueExt1 = std::move(script_val[1]);
    result->ValueExt2 = std::move(script_val[2]);
    result->ValueExt3 = std::move(script_val[3]);
    result->ValueExt4 = std::move(script_val[4]);
    return result;
}

auto DialogManager::GetDrType(string_view str) const -> uint8_t
{
    FO_STACK_TRACE_ENTRY();

    if (strvex(str).compare_ignore_case("Property")) {
        return DR_PROP_CRITTER;
    }
    if (strvex(str).compare_ignore_case("Item")) {
        return DR_ITEM;
    }
    if (strvex(str).compare_ignore_case("Script")) {
        return DR_SCRIPT;
    }
    if (strvex(str).compare_ignore_case("NoRecheck")) {
        return DR_NO_RECHECK;
    }
    if (strvex(str).compare_ignore_case("Or")) {
        return DR_OR;
    }

    return DR_NONE;
}

auto DialogManager::CheckOper(uint8_t oper) const -> bool
{
    FO_STACK_TRACE_ENTRY();

    return oper == '>' || oper == '<' || oper == '=' || oper == '+' || oper == '-' || oper == '*' || oper == '/' || oper == '!' || oper == '}' || oper == '{';
}
