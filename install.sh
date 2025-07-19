#!/bin/bash

echo "🚀 INSTALADOR AUTOMATICO - Generador de Imagenes IA"
echo "==================================================="
echo

# Verificar Python
echo "📋 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no encontrado. Instala Python 3.10+ primero"
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"
echo

# Crear entorno virtual
echo "🔨 Creando entorno virtual..."
if [ -d ".venv" ]; then
    echo "⚠️  Entorno virtual ya existe, continuando..."
else
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "❌ Error creando entorno virtual"
        exit 1
    fi
    echo "✅ Entorno virtual creado"
fi
echo

# Activar entorno virtual
source .venv/bin/activate

# Instalar dependencias
echo "📦 Instalando dependencias básicas..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Error instalando dependencias básicas"
    exit 1
fi
echo "✅ Dependencias básicas instaladas"
echo

# Instalar PyTorch GPU
echo "🎮 Instalando PyTorch con soporte GPU..."
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
if [ $? -ne 0 ]; then
    echo "❌ Error instalando PyTorch GPU"
    echo "💡 Instalando versión CPU como respaldo..."
    python -m pip install torch torchvision torchaudio
fi
echo "✅ PyTorch instalado"
echo

# Verificar GPU
echo "🩺 Verificando instalación GPU..."
python utils/gpu_diagnostics.py
echo

echo "🎉 ¡INSTALACION COMPLETADA!"
echo "=========================="
echo "📚 Para usar el generador:"
echo "   • Generar imagen: python generate_image.py"
echo "   • Ver ejemplos: python run_examples.py"
echo "   • Verificar GPU: python check_gpu.py"
echo
echo "📖 Consulta README.md para más información"
echo
