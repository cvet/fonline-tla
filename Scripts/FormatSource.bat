@ECHO off

FOR /F "tokens=*" %%G IN ('DIR /B /S .\*.fos') DO (
	ECHO Indenting file "%%G"
	"SourceTools\uncrustify.exe" -f "%%G" -c "SourceTools\uncrustify.cfg" -o indentoutput.tmp
	MOVE /Y indentoutput.tmp "%%G"
)

FOR /F "tokens=*" %%G IN ('DIR /B /S .\*.fosh') DO (
	ECHO Indenting file "%%G"
	"SourceTools\uncrustify.exe" -f "%%G" -c "SourceTools\uncrustify.cfg" -o indentoutput.tmp
	MOVE /Y indentoutput.tmp "%%G"
)
