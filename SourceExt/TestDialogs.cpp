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

TEST_CASE("Dialog SayScript is independent of the speech script")
{
    EngineMetadata meta {[] { }};
    DialogManager manager {meta};

    auto pack = manager.ParseDialog("say_test", R"([Dialog]
Speech 1
  Script Example::Lexemes
  SayScript Example::HandleText
  Answer 2
Speech 2
  Script Example::OtherLexemes
[Text engl]
{Name}{}{Say test}
)");

    REQUIRE(pack->SpeechesCount == 2);
    CHECK(pack->GetSpeech(0)->DlgScriptFuncName == meta.Hashes.to_hashed_string("Example::Lexemes"));
    CHECK(pack->GetSpeech(0)->SayScriptFuncName == meta.Hashes.to_hashed_string("Example::HandleText"));
    CHECK_FALSE(pack->GetSpeech(1)->SayScriptFuncName);
}

TEST_CASE("Dialog SayScript rejects malformed bindings")
{
    EngineMetadata meta {[] { }};
    DialogManager manager {meta};

    string body = GENERATE("SayScript Example::HandleText\nSpeech 1\n", "Speech 1\nSayScript\n", "Speech 1\nSayScript Example::HandleText extra\n", "Speech 1\nAnswer 2\nSayScript Example::HandleText\n", "Speech 1\nSayScript Example::First\nSayScript Example::Second\n");
    string data = string("[Dialog]\n") + body + "[Text engl]\n{Name}{}{Say test}\n";

    CHECK_THROWS_AS(manager.ParseDialog("say_test", data), DialogParseException);
}
