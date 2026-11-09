#!/usr/bin/env bash
set -e

echo "Instalando dependencias..."
python3 -m pip install -r requirements.txt

echo ""
echo "Compilando ejecutable con PyInstaller..."
pyinstaller --onefile --name "UnityZipExporter" exportador_unity.py

echo ""
echo "¡Listo! El ejecutable está en la carpeta dist/UnityZipExporter"