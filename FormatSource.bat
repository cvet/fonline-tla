@echo off

FOR /F "tokens=*" %%G IN ('DIR /B /S .\*.fos') DO (
echo Indenting file "%%G"
"FOnlineSDK\Server\Modules\_SourceTools\uncrustify.exe" -f "%%G" -c "FOnlineSDK\Server\Modules\_SourceTools\uncrustify.cfg" -o indentoutput.tmp
move /Y indentoutput.tmp "%%G"
)

FOR /F "tokens=*" %%G IN ('DIR /B /S .\*.fosh') DO (
echo Indenting file "%%G"
"FOnlineSDK\Server\Modules\_SourceTools\uncrustify.exe" -f "%%G" -c "FOnlineSDK\Server\Modules\_SourceTools\uncrustify.cfg" -o indentoutput.tmp
move /Y indentoutput.tmp "%%G"
)
