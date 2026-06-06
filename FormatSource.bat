@echo off
echo Scripts formatting
cd "%~dp0" && py -3 Tools/Formatter/format_project.py scripts
