#include "Common.h"

#include "Client.h"

FO_USING_NAMESPACE();

FO_BEGIN_NAMESPACE();
///@ ExportMethod
FO_SCRIPT_API string Client_Game_FormatTags(FOClient* client, string_view text, string_view lexems);
///@ ExportMethod
FO_SCRIPT_API string Client_Game_FormatTags(FOClient* client, string_view text, string_view lexems, CritterView* talker);
///@ ExportMethod
FO_SCRIPT_API bool Client_Critter_IsFree(CritterView* self);
///@ ExportMethod
FO_SCRIPT_API bool Client_Critter_IsBusy(CritterView* self);
///@ ExportMethod
FO_SCRIPT_API void Client_Critter_Wait(CritterView* self, int32 ms);
FO_END_NAMESPACE();

static auto FormatTags(FOClient* client, string_view text, string_view lexems, CritterView* talker) -> string;

string FO_NAMESPACE Client_Game_FormatTags(FOClient* client, string_view text, string_view lexems)
{
    FO_STACK_TRACE_ENTRY();

    return FormatTags(client, text, lexems, nullptr);
}

string FO_NAMESPACE Client_Game_FormatTags(FOClient* client, string_view text, string_view lexems, CritterView* talker)
{
    FO_STACK_TRACE_ENTRY();

    return FormatTags(client, text, lexems, talker);
}

string FormatTags(FOClient* client, string_view text, string_view lexems, CritterView* talker)
{
    FO_STACK_TRACE_ENTRY();

    auto new_text = string(text);

    vector<string> dialogs;
    auto sex = 0;
    auto sex_tags = false;
    string tag;

    CritterView* chosen = client->GetChosen();

    for (size_t i = 0; i < new_text.length();) {
        switch (new_text[i]) {
        case '#': {
            new_text[i] = '\n';
        } break;
        case '|': {
            if (sex_tags) {
                tag = strex(new_text.substr(i + 1)).substringUntil('|');
                new_text.erase(i, tag.length() + 2);

                if (sex != 0) {
                    if (sex == 1) {
                        new_text.insert(i, tag);
                    }

                    sex--;
                }
                continue;
            }
        } break;
        case '@': {
            if (new_text[i + 1] == '@') {
                dialogs.push_back(new_text.substr(0, i));
                new_text.erase(0, i + 2);
                i = 0;
                continue;
            }

            tag = strex(new_text.substr(i + 1)).substringUntil('@');
            new_text.erase(i, tag.length() + 2);

            if (tag.empty()) {
                break;
            }

            // Player name
            if (strex(tag).compareIgnoreCase("pname")) {
                tag = chosen != nullptr ? chosen->GetName() : "";
            }
            // Npc name
            else if (strex(tag).compareIgnoreCase("nname")) {
                tag = talker != nullptr ? talker->GetName() : "";
            }
            // Sex
            else if (strex(tag).compareIgnoreCase("sex")) {
                sex = chosen != nullptr && chosen->GetSexTagFemale() ? 2 : 1;
                sex_tags = true;
                continue;
            }
            // Random
            else if (strex(tag).compareIgnoreCase("rnd")) {
                auto first = new_text.find_first_of('|', i);
                auto last = new_text.find_last_of('|', i);
                auto rnd = strex(new_text.substr(first, last - first + 1)).split('|');
                new_text.erase(first, last - first + 1);

                if (!rnd.empty()) {
                    new_text.insert(first, rnd[GenericUtils::Random(0, numeric_cast<int32>(rnd.size()) - 1)]);
                }
            }
            // Lexems
            else if (tag.length() > 4 && tag[0] == 'l' && tag[1] == 'e' && tag[2] == 'x' && tag[3] == ' ') {
                auto lex = "$" + tag.substr(4);
                auto pos = lexems.find(lex);

                if (pos != string::npos) {
                    pos += lex.length();
                    tag = strex(lexems.substr(pos)).substringUntil('$').trim();
                }
                else {
                    tag = "<lexem not found>";
                }
            }
            // Text pack
            else if (tag.length() > 5 && tag[0] == 't' && tag[1] == 'e' && tag[2] == 'x' && tag[3] == 't' && tag[4] == ' ') {
                tag = tag.substr(5);
                tag = strex(tag).erase('(').erase(')');

                istringstream itag(tag);
                string pack_name_str;
                uint32 str_num = 0;

                if (itag >> pack_name_str >> str_num) {
                    bool failed = false;
                    const auto pack_name = client->GetCurLang().ResolveTextPackName(pack_name_str, &failed);
                    const auto& text_pack = client->GetCurLang().GetTextPack(pack_name);

                    if (failed) {
                        tag = "<text tag, invalid pack name>";
                    }
                    else if (text_pack.GetStrCount(str_num) == 0) {
                        tag = strex("<text tag, string {} not found>", str_num);
                    }
                    else {
                        tag = text_pack.GetStr(str_num);
                    }
                }
                else {
                    tag = "<text tag parse fail>";
                }
            }
            // Script
            else if (tag.length() > 7 && tag[0] == 's' && tag[1] == 'c' && tag[2] == 'r' && tag[3] == 'i' && tag[4] == 'p' && tag[5] == 't' && tag[6] == ' ') {
                string func_name = strex(tag.substr(7)).substringUntil('$');

                if (!client->ScriptSys.CallFunc<string, string>(client->Hashes.ToHashedString(func_name), string(lexems), tag)) {
                    tag = "<script function not found>";
                }
            }
            // Error
            else {
                tag = "<error>";
            }

            new_text.insert(i, tag);
        }
            continue;
        default:
            break;
        }

        ++i;
    }

    dialogs.push_back(new_text);
    new_text = dialogs[GenericUtils::Random(0, numeric_cast<int32>(dialogs.size()) - 1)];

    return new_text;
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

void FO_NAMESPACE Client_Critter_Wait(CritterView* self, int32 ms)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(self, ms);
}
