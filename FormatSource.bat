@echo off

FOR /F "tokens=*" %%G IN ('DIR /B /S .\*.fos') DO (
echo Indenting file "%%G"
"Fonline\Binaries\SourceTools\uncrustify.exe" -f "%%G" -c "Fonline\Binaries\SourceTools\uncrustify.cfg" -o indentoutput.tmp
move /Y indentoutput.tmp "%%G"
)

FOR /F "tokens=*" %%G IN ('DIR /B /S .\*.fosh') DO (
echo Indenting file "%%G"
"Fonline\Binaries\SourceTools\uncrustify.exe" -f "%%G" -c "Fonline\Binaries\SourceTools\uncrustify.cfg" -o indentoutput.tmp
move /Y indentoutput.tmp "%%G"
)
