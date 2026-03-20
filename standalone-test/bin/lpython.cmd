@echo off
setlocal

set "LPYTHON_BIN_DIR=%~dp0"
set "LPYTHON_REAL=%LPYTHON_BIN_DIR%lpython-real.exe"
if not exist "%LPYTHON_REAL%" set "LPYTHON_REAL=%LPYTHON_BIN_DIR%lpython.exe"

if not defined LPYTHON_SKIP_VSENV (
    if not defined VSCMD_VER (
        set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
        if not exist "%VSWHERE%" set "VSWHERE=%ProgramFiles%\Microsoft Visual Studio\Installer\vswhere.exe"
        if exist "%VSWHERE%" (
            for /f "usebackq delims=" %%I in (`"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -find Common7\Tools\VsDevCmd.bat`) do set "VSDEVCMD=%%I"
            if defined VSDEVCMD call "%VSDEVCMD%" -arch=x64 >nul 2>nul
        )
    )
)

"%LPYTHON_REAL%" %*
exit /b %ERRORLEVEL%
