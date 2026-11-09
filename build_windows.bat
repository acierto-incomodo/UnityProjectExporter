@echo off
echo Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error al instalar dependencias.
    pause
    exit /b %errorlevel%
)

echo.
echo Compilando ejecutable con PyInstaller...
pyinstaller --noconsole --onefile --name "UnityZipExporter" exportador_unity.py
if %errorlevel% neq 0 (
    echo Error al compilar con PyInstaller.
    pause
    exit /b %errorlevel%
)

echo.
echo ¡Listo! El ejecutable esta en la carpeta dist\UnityZipExporter.exe
pause