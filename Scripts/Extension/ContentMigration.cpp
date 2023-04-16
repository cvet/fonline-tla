#include "Common.h"

#include "StringUtils.h"

///@ EngineHook
void ConfigSectionParseHook(const string& fname, string& section, map<string, string>& init_section_kv)
{
    UNUSED_VARIABLE(fname);
    UNUSED_VARIABLE(init_section_kv);

    if (section == "Tile") {
        section = "Item";
    }
}

///@ EngineHook
void ConfigEntryParseHook(const string& fname, const string& section, string& key, string& value)
{
    UNUSED_VARIABLE(fname);

    if (section == "Tile") {
        if (key == "PicMap") {
            key = "$Proto";
            value = "tile_" + _str(value).extractFileName().eraseFileExtension().str();
        }
        else if (key == "IsRoof") {
            key = "IsRoofTile";
        }
        else if (key == "Layer") {
            key = "TileLayer";
        }
    }
}
