@echo off
REM Jalankan EKSTRAK.py dan POSISI.py menggunakan call

REM Path ke python.exe
set PYTHON_EXE=C:\Anaconda\envs\Kris\.venv\Scripts\python.exe

REM Path ke folder proyek
set PROJEK_PATH=C:\Anaconda\envs\Kris\PROJEKMFY

echo ================================
echo Menjalankan EKSTRAK.py ...
echo ================================
call %PYTHON_EXE% "%PROJEK_PATH%\EKSTRAK.py"
if %ERRORLEVEL% NEQ 0 (
    echo EKSTRAK.py gagal dijalankan
    goto Selesai
)

echo.
echo ================================
echo Menjalankan POSISI.py ...
echo ================================
call %PYTHON_EXE% "%PROJEK_PATH%\POSISI.py"
if %ERRORLEVEL% NEQ 0 (
    echo POSISI.py gagal dijalankan
    goto Selesai
)

:Selesai
echo.
echo Semua skrip telah dijalankan.
pause
