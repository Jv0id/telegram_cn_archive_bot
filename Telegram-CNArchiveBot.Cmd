@Echo off
@Rem Python 3 launcher with pause at exit
SetLocal EnableDelayedExpansion
Title %~n0
CD /D "%~dp0"

Python3 archive.py
Set ExitCode=!ErrorLevel!
Echo.
If Not "!ExitCode!"=="0" (
    Echo ExitCode: !ExitCode!  1>&2
)
Pause
Exit !ExitCode!