#include "Common.h"

#include "StringUtils.h"

///@ EngineHook
FO_SCRIPT_API void ConfigSectionParseHook(const string& fname, string& section, map<string, string>& init_section_kv)
{
    UNUSED_VARIABLE(fname);
    UNUSED_VARIABLE(init_section_kv);

    if (section == "Tile") {
        section = "Item";
    }
}

///@ EngineHook
FO_SCRIPT_API void ConfigEntryParseHook(const string& fname, const string& section, string& key, string& value)
{
    UNUSED_VARIABLE(fname);

    if (section == "Tile") {
        if (key == "PicMap") {
            key = "$Proto";
            value = "tile_" + strex(value).extractFileName().eraseFileExtension().str();
        }
        else if (key == "IsRoof") {
            key = "IsRoofTile";
        }
        else if (key == "Layer") {
            key = "TileLayer";
        }
    }

    if (key == "LightColor" && value.front() != '0') {
        auto rgba = static_cast<uint>(strex(value).toInt64());
        rgba = (rgba & 0xFF000000) | ((rgba & 0xFF) << 16) | (rgba & 0xFF00) | ((rgba & 0xFF0000) >> 16);
        value = strex("0x{:x}", rgba);
    }

    if (section == "ProtoMap" || section == "Critter" || section == "Item" || section == "ProtoItem" || section == "Tile") {
        static thread_local string prev_key;
        static thread_local string prev_value;

        if (key == "HexX") {
            prev_key = key;
            prev_value = value;
            key = "Hex";
            value = strex("{} 0", value);
        }
        else if (key == "HexY") {
            value = strex("{} {}", prev_key == "HexX" ? prev_value : "0", value);
            key = "Hex";
            prev_key = "";
        }
        else if (key == "OffsetX") {
            prev_key = key;
            prev_value = value;
            key = "Offset";
            value = strex("{} 0", value);
        }
        else if (key == "OffsetY") {
            key = "Offset";
            value = strex("{} {}", prev_key == "OffsetX" ? prev_value : "0", value);
            prev_key = "";
        }
        else if (key == "Height") {
            prev_key = key;
            prev_value = value;
            key = "";
        }
        else if (key == "Width") {
            key = "Size";
            value = strex("{} {}", value, prev_value);
            prev_key = "";
        }
        else if (key == "WorkHexX") {
            prev_key = key;
            prev_value = value;
            key = "WorkHex";
            value = strex("{} 0", value);
        }
        else if (key == "WorkHexY") {
            value = strex("{} {}", prev_key == "WorkHexX" ? prev_value : "0", value);
            key = "WorkHex";
            prev_key = "";
        }
        else {
            prev_key = "";
        }
    }
}
