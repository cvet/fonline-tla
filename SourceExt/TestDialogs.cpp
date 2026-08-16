#include "catch_amalgamated.hpp"

#include "Dialogs.h"

TEST_CASE("Dialog script values preserve legacy generic tokens")
{
    CHECK(NormalizeDialogScriptValue("@!") == "!");
    CHECK(NormalizeDialogScriptValue("@arroyo") == "arroyo");
    CHECK(NormalizeDialogScriptValue("Content::Location::modoc") == "modoc");
    CHECK(NormalizeDialogScriptValue("Content::Map::sf_dock") == "sf_dock");
    CHECK(NormalizeDialogScriptValue("15") == "15");
    CHECK(NormalizeDialogScriptValue("true") == "true");
}

TEST_CASE("Dialog property booleans preserve integer storage spelling")
{
    CHECK(NormalizeDialogPropertyValue("true") == "1");
    CHECK(NormalizeDialogPropertyValue("false") == "0");
    CHECK(NormalizeDialogPropertyValue("TRUE") == "1");
    CHECK(NormalizeDialogPropertyValue("FALSE") == "0");
    CHECK(NormalizeDialogPropertyValue("42") == "42");
}
