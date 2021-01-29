
@echo off
title %~n0
cd /d "%~dp0"
python -u archive.py
