@echo off
echo 🚀 INSTALADOR AUTOMATICO - Generador de Imagenes IA
echo ===================================================
echo.

echo 📋 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Instala Python 3.10+ primero
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

echo 🔨 Creando entorno virtual...
if exist .venv (
    echo ⚠️  Entorno virtual ya existe, continuando...
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ Error creando entorno virtual
        pause
        exit /b 1
    )
    echo ✅ Entorno virtual creado
)
echo.

echo 📦 Instalando dependencias básicas...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error instalando dependencias básicas
    pause
    exit /b 1
)
echo ✅ Dependencias básicas instaladas
echo.

echo 🎮 Instalando PyTorch con soporte GPU...
.venv\Scripts\python.exe -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
if errorlevel 1 (
    echo ❌ Error instalando PyTorch GPU
    echo 💡 Instalando versión CPU como respaldo...
    .venv\Scripts\python.exe -m pip install torch torchvision torchaudio
)
echo ✅ PyTorch instalado
echo.

echo 🩺 Verificando instalación GPU...
.venv\Scripts\python.exe utils\gpu_diagnostics.py
echo.

echo 🎉 ¡INSTALACION COMPLETADA!
echo ===========================
echo 📚 Para usar el generador:
echo    • Generar imagen: python generate_image.py
echo    • Ver ejemplos: python run_examples.py
echo    • Verificar GPU: python check_gpu.py
echo.
echo 📖 Consulta README.md para más información
echo.
pause
