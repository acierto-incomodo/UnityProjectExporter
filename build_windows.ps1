Write-Host "Instalando dependencias..." -ForegroundColor Cyan
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error al instalar dependencias." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`nCompilando ejecutable con PyInstaller..." -ForegroundColor Cyan
pyinstaller --noconsole --onefile --name "UnityZipExporter" exportador_unity.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error al compilar con PyInstaller." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`n¡Listo! El ejecutable está en la carpeta dist\UnityZipExporter.exe" -ForegroundColor Green
