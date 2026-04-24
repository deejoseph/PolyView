@echo off
setlocal

set "PROJECT_ROOT=D:\PixelSmile\celadon-lab"
set "COMFY_ROOT=D:\PixelSmile\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable"
set "COMFY_MAIN=%COMFY_ROOT%\ComfyUI\main.py"
set "PYTHON_EXE=D:\PixelSmile\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\python_embeded\python.exe"
set "PORT_UI=8080"
set "PORT_COMFY=8188"

if not exist "%PYTHON_EXE%" (
  echo Python not found:
  echo   %PYTHON_EXE%
  pause
  exit /b 1
)

if not exist "%COMFY_MAIN%" (
  echo ComfyUI main.py not found:
  echo   %COMFY_MAIN%
  pause
  exit /b 1
)

if not exist "%PROJECT_ROOT%\polyview_server.py" (
  echo polyview_server.py not found:
  echo   %PROJECT_ROOT%\polyview_server.py
  pause
  exit /b 1
)

set "COMFY_RUNNING="
set "UI_RUNNING="

netstat -ano | findstr /r /c:":%PORT_COMFY% .*LISTENING" >nul 2>nul
if not errorlevel 1 set "COMFY_RUNNING=1"

netstat -ano | findstr /r /c:":%PORT_UI% .*LISTENING" >nul 2>nul
if not errorlevel 1 set "UI_RUNNING=1"

if defined COMFY_RUNNING (
  echo [1/3] ComfyUI is already running on port %PORT_COMFY%.
) else (
  echo [1/3] Starting ComfyUI...
  start "ComfyUI" /min "%PYTHON_EXE%" -s "%COMFY_MAIN%" --windows-standalone-build --lowvram --preview-method auto --fp16-vae
  echo [2/3] Waiting for ComfyUI...
  timeout /t 8 /nobreak > nul
)

if defined UI_RUNNING (
  echo [3/3] PolyView UI server is already running on port %PORT_UI%.
) else (
  echo [3/3] Starting PolyView UI server...
  cd /d "%PROJECT_ROOT%"
  start "PolyView_Server" "%PYTHON_EXE%" "%PROJECT_ROOT%\polyview_server.py"
  timeout /t 2 /nobreak > nul
)

start "" "http://127.0.0.1:%PORT_UI%/"

echo.
echo PolyView ready.
echo ComfyUI:  http://127.0.0.1:%PORT_COMFY%/
echo PolyView: http://127.0.0.1:%PORT_UI%/
echo.
pause
