#include "Common.h"

FO_USING_NAMESPACE();

FO_BEGIN_NAMESPACE
///@ EngineHook
FO_SCRIPT_API auto ConfigSectionParseHook(string_view fname, string_view section, string& out_section, map<string, string>& init_section_kv) -> bool;
///@ EngineHook
FO_SCRIPT_API auto ConfigEntryParseHook(string_view fname, string_view section, string_view key, string_view value, string& out_key, string& out_value) -> bool;
FO_END_NAMESPACE

auto FO_NAMESPACE ConfigSectionParseHook(string_view fname, string_view section, string& out_section, map<string, string>& init_section_kv) -> bool
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(fname, init_section_kv);

    if (section == "Tile") {
        out_section = "Item";
        return true;
    }

    return false;
}

auto FO_NAMESPACE ConfigEntryParseHook(string_view fname, string_view section, string_view key, string_view value, string& out_key, string& out_value) -> bool
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(fname);

    out_key = string(key);
    out_value = string(value);
    auto changed = false;

    if (section == "Tile") {
        if (key == "PicMap") {
            out_key = "$Proto";
            out_value = "tile_" + strex(value).extract_file_name().erase_file_extension().str();
            changed = true;
        }
        else if (key == "IsRoof") {
            out_key = "IsRoofTile";
            changed = true;
        }
        else if (key == "Layer") {
            out_key = "TileLayer";
            changed = true;
        }
    }

    if (section == "ProtoMap" || section == "Critter" || section == "Item" || section == "ProtoItem" || section == "Tile") {
        static thread_local string prev_key;
        static thread_local string prev_value;

        if (key == "HexX") {
            prev_key = string(key);
            prev_value = string(value);
            out_key = "Hex";
            out_value = strex("{} 0", value);
            changed = true;
        }
        else if (key == "HexY") {
            out_value = strex("{} {}", prev_key == "HexX" ? prev_value : "0", value);
            out_key = "Hex";
            prev_key = "";
            changed = true;
        }
        else if (key == "OffsetX") {
            prev_key = string(key);
            prev_value = string(value);
            out_key = "Offset";
            out_value = strex("{} 0", value);
            changed = true;
        }
        else if (key == "OffsetY") {
            out_key = "Offset";
            out_value = strex("{} {}", prev_key == "OffsetX" ? prev_value : "0", value);
            prev_key = "";
            changed = true;
        }
        else if (key == "Height") {
            prev_key = string(key);
            prev_value = string(value);
            out_key.clear();
            changed = true;
        }
        else if (key == "Width") {
            out_key = "Size";
            out_value = strex("{} {}", value, prev_value);
            prev_key = "";
            changed = true;
        }
        else if (key == "WorkHexX") {
            prev_key = string(key);
            prev_value = string(value);
            out_key = "WorkHex";
            out_value = strex("{} 0", value);
            changed = true;
        }
        else if (key == "WorkHexY") {
            out_value = strex("{} {}", prev_key == "WorkHexX" ? prev_value : "0", value);
            out_key = "WorkHex";
            prev_key = "";
            changed = true;
        }
        else {
            prev_key = "";
        }
    }

    return changed;
}
