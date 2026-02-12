@echo off
echo Scripts formatting
cd "%~dp0" && "Tools/clang-format-20.exe" --verbose -i Scripts/*.fos Scripts/Json/*.fos Scripts/Extension/*.cpp
