@echo off
title Desinstalar VoxF9
echo.
echo ========================================
echo   DESINSTALAR VOICETYPE
echo ========================================
echo.
echo Esto eliminara:
echo   - VoxF9.exe
echo   - Modelo de voz (1.4 GB)
echo   - Acceso directo del escritorio
echo.
set /p confirm="Estas seguro? (S/N): "
if /i not "%confirm%"=="S" goto :cancel

echo.
echo [1/3] Cerrando VoxF9...
taskkill /f /im VoxF9.exe >nul 2>&1
timeout /t 2 >nul

echo [2/3] Eliminando acceso directo...
del "%USERPROFILE%\Desktop\VoxF9.lnk" 2>nul

echo [3/3] Eliminando archivos del programa...
set "FOLDER=%~dp0"

:: Auto-eliminar la carpeta (truco para eliminar mientras se ejecuta)
start /b "" cmd /c "timeout /t 2 >nul & rmdir /s /q "%FOLDER%""

echo.
echo ========================================
echo   VoxF9 desinstalado correctamente
echo ========================================
echo.
echo La ventana se cerrara automaticamente...
timeout /t 3 >nul
exit

:cancel
echo.
echo Desinstalacion cancelada.
pause
