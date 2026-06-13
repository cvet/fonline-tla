#include "Common.h"

#include "Client.h"

FO_USING_NAMESPACE();

FO_BEGIN_NAMESPACE
///@ ExportMethod
FO_SCRIPT_API string Client_Game_FormatTags(ClientEngine* client, string_view text, string_view textArgs);
///@ ExportMethod
FO_SCRIPT_API string Client_Game_FormatTags(ClientEngine* client, string_view text, string_view textArgs, FO_NULLABLE CritterView* talker);
///@ ExportMethod
FO_SCRIPT_API bool Client_Critter_IsFree(CritterView* self);
///@ ExportMethod
FO_SCRIPT_API bool Client_Critter_IsBusy(CritterView* self);
///@ ExportMethod
FO_SCRIPT_API void Client_Critter_Wait(CritterView* self, int32_t ms);
FO_END_NAMESPACE

static auto ResolveTextArg(string_view name, string_view text_args) -> string;

static auto HasFemaleSexTag(const CritterView* cr) -> bool
{
    if (cr == nullptr) {
        return false;
    }

    const auto* sex_tag_female = cr->GetProperties().GetRegistrator()->FindProperty("SexTagFemale");
    return sex_tag_female != nullptr && cr->GetProperties().GetValue<bool>(sex_tag_female);
}

static auto FormatTags(ClientEngine* client, string_view text, string_view text_args, CritterView* talker) -> string
{
    FO_STACK_TRACE_ENTRY();

    auto new_text = string(text);

    vector<string> dialogs;
    string tag;

    CritterView* chosen = client->GetChosen();

    for (size_t i = 0; i < new_text.length();) {
        switch (new_text[i]) {
        case '#': {
            new_text[i] = '\n';
        } break;
        case '$': {
            const auto tag_begin = i;
            auto tag_end = i + 1;

            while (tag_end < new_text.length() && (std::isalnum(static_cast<unsigned char>(new_text[tag_end])) != 0 || new_text[tag_end] == '_')) {
                tag_end++;
            }

            if (tag_end == i + 1) {
                break;
            }

            new_text.replace(tag_begin, tag_end - tag_begin, "@arg " + new_text.substr(tag_begin + 1, tag_end - tag_begin - 1) + "@");
            continue;
        }
        case '@': {
            if (i + 1 < new_text.length() && new_text[i + 1] == '@') {
                dialogs.push_back(new_text.substr(0, i));
                new_text.erase(0, i + 2);
                i = 0;
                continue;
            }

            tag = strex(new_text.substr(i + 1)).substring_until('@');
            new_text.erase(i, tag.length() + 2);

            if (tag.empty()) {
                break;
            }

            // Inline color tags are handled by the font renderer, not here — pass them through untouched
            if (tag == "color" || (tag.size() >= 6 && tag.compare(0, 6, "color ") == 0)) {
                new_text.insert(i, "@" + tag + "@");
                i += tag.length() + 2;
                continue;
            }

            // Player name
            if (strex(tag).compare_ignore_case("pname")) {
                tag = chosen != nullptr ? chosen->GetName() : "";
            }
            // Npc name
            else if (strex(tag).compare_ignore_case("nname")) {
                tag = talker != nullptr ? talker->GetName() : "";
            }
            // Sex
            else if (strex(tag).compare_ignore_case("sex")) {
                if (i < new_text.length() && new_text[i] == '|') {
                    const auto male_begin = i + 1;
                    const auto male_end = new_text.find('|', male_begin);

                    if (male_end != string::npos) {
                        auto female_begin = male_end + 1;
                        if (female_begin < new_text.length() && new_text[female_begin] == '|') {
                            female_begin++;
                        }

                        const auto female_end = new_text.find('|', female_begin);
                        if (female_end != string::npos) {
                            const auto male_text = string(new_text.substr(male_begin, male_end - male_begin));
                            const auto female_text = string(new_text.substr(female_begin, female_end - female_begin));
                            new_text.replace(i, female_end - i + 1, HasFemaleSexTag(chosen) ? female_text : male_text);
                            continue;
                        }
                    }
                }

                new_text.insert(i, "");
                continue;
            }
            // Random
            else if (strex(tag).compare_ignore_case("rnd")) {
                auto first = new_text.find_first_of('|', i);
                auto last = new_text.find_last_of('|', i);
                auto rnd = strex(new_text.substr(first, last - first + 1)).split('|');
                new_text.erase(first, last - first + 1);

                if (!rnd.empty()) {
                    new_text.insert(first, rnd[client->Random(0, numeric_cast<int32_t>(rnd.size()) - 1)]);
                }
            }
            // Text argument
            else if (tag.length() > 4 && tag[0] == 'a' && tag[1] == 'r' && tag[2] == 'g' && tag[3] == ' ') {
                tag = ResolveTextArg(tag.substr(4), text_args);
            }
            // Text pack
            else if (tag.length() > 5 && tag[0] == 't' && tag[1] == 'e' && tag[2] == 'x' && tag[3] == 't' && tag[4] == ' ') {
                tag = tag.substr(5);
                tag = strex(tag).erase('(').erase(')');

                istringstream itag(tag);
                string pack_name_str;
                string key_name;

                if (itag >> pack_name_str >> key_name) {
                    const auto text_key = TextPackKey::FromPack(client->Hashes, pack_name_str, key_name);
                    const auto& text_pack = client->GetCurLang();

                    if (text_pack.GetStrCount(text_key) == 0) {
                        tag = key_name;
                    }
                    else {
                        tag = text_pack.GetStr(text_key);
                    }
                }
                else {
                    tag = "";
                }
            }
            // Script
            else if (tag.length() > 7 && tag[0] == 's' && tag[1] == 'c' && tag[2] == 'r' && tag[3] == 'i' && tag[4] == 'p' && tag[5] == 't' && tag[6] == ' ') {
                string func_name = strex(tag.substr(7)).substring_until('$');

                if (!client->CallFunc<string, string>(client->Hashes.ToHashedString(func_name), string(text_args), tag)) {
                    tag = "";
                }
            }
            else {
                tag = "";
            }

            new_text.insert(i, tag);
            continue;
        }
        default:
            break;
        }

        ++i;
    }

    dialogs.push_back(new_text);
    new_text = dialogs[client->Random(0, numeric_cast<int32_t>(dialogs.size()) - 1)];

    return new_text;
}

static auto ResolveTextArg(string_view name, string_view text_args) -> string
{
    FO_STACK_TRACE_ENTRY();

    size_t pos = 0;

    while (pos < text_args.length()) {
        const size_t next_entry = text_args.find('|', pos);
        const string_view entry = next_entry == string_view::npos ? text_args.substr(pos) : text_args.substr(pos, next_entry - pos);
        const size_t colon = entry.find(':');

        if (colon != string_view::npos && strex(entry.substr(0, colon)).trim() == name) {
            return string(strex(entry.substr(colon + 1)).trim());
        }

        if (next_entry == string_view::npos) {
            break;
        }

        pos = next_entry + 1;
    }

    return "";
}

string FO_NAMESPACE Client_Game_FormatTags(ClientEngine* client, string_view text, string_view textArgs)
{
    FO_STACK_TRACE_ENTRY();

    return FormatTags(client, text, textArgs, nullptr);
}

string FO_NAMESPACE Client_Game_FormatTags(ClientEngine* client, string_view text, string_view textArgs, CritterView* talker)
{
    FO_STACK_TRACE_ENTRY();

    return FormatTags(client, text, textArgs, talker);
}

bool FO_NAMESPACE Client_Critter_IsFree(CritterView* self)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(self);
    return true;
}

bool FO_NAMESPACE Client_Critter_IsBusy(CritterView* self)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(self);
    return false;
}

void FO_NAMESPACE Client_Critter_Wait(CritterView* self, int32_t ms)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(self, ms);
}
