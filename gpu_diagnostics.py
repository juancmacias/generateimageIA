# gpu_diagnostics.py - Diagnóstico completo de GPU

import torch
import sys
import platform
import subprocess
import os

def check_pytorch_installation():
    """Verificar instalación de PyTorch"""
    print("🔍 DIAGNÓSTICO DE PYTORCH")
    print("=" * 40)
    
    print(f"🐍 Python: {sys.version}")
    print(f"🔥 PyTorch version: {torch.__version__}")
    
    # Verificar si PyTorch tiene soporte CUDA
    cuda_available = torch.cuda.is_available()
    print(f"🎮 CUDA disponible en PyTorch: {'✅ SÍ' if cuda_available else '❌ NO'}")
    
    if cuda_available:
        print(f"🔢 CUDA version en PyTorch: {torch.version.cuda}")
        print(f"🏗️  CuDNN version: {torch.backends.cudnn.version()}")
    else:
        print("⚠️  PyTorch instalado SIN soporte CUDA")
        if '+cpu' in torch.__version__:
            print("📝 Detectado: PyTorch CPU-only version")
        else:
            print("📝 Razón: Instalación sin CUDA o drivers incompatibles")

def check_nvidia_gpu():
    """Verificar GPUs NVIDIA en el sistema"""
    print(f"\n🖥️  DIAGNÓSTICO DE HARDWARE GPU")
    print("=" * 40)
    
    try:
        # Intentar ejecutar nvidia-smi
        result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,driver_version', 
                               '--format=csv,noheader,nounits'], 
                               capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ NVIDIA GPU(s) detectada(s):")
            lines = result.stdout.strip().split('\n')
            for i, line in enumerate(lines):
                parts = line.split(', ')
                if len(parts) >= 3:
                    name, memory, driver = parts[0], parts[1], parts[2]
                    print(f"   🎮 GPU {i}: {name}")
                    print(f"      🧠 VRAM: {memory} MB")
                    print(f"      🔧 Driver: {driver}")
        else:
            print("❌ No se pudo ejecutar nvidia-smi")
            print("   Posibles causas:")
            print("   - No hay GPU NVIDIA instalada")
            print("   - Drivers NVIDIA no instalados")
            print("   - GPU deshabilitada")
            
    except FileNotFoundError:
        print("❌ nvidia-smi no encontrado")
        print("   Esto indica que:")
        print("   - No hay drivers NVIDIA instalados")
        print("   - No hay GPU NVIDIA en el sistema")
        
    except subprocess.TimeoutExpired:
        print("⏱️  nvidia-smi timeout - posible problema con drivers")
        
    except Exception as e:
        print(f"❌ Error ejecutando nvidia-smi: {e}")

def check_cuda_installation():
    """Verificar instalación de CUDA en el sistema"""
    print(f"\n🛠️  DIAGNÓSTICO DE CUDA DEL SISTEMA")
    print("=" * 40)
    
    # Verificar variables de entorno CUDA
    cuda_path = os.environ.get('CUDA_PATH')
    cuda_home = os.environ.get('CUDA_HOME')
    
    if cuda_path:
        print(f"✅ CUDA_PATH encontrado: {cuda_path}")
    else:
        print("❌ CUDA_PATH no configurado")
        
    if cuda_home:
        print(f"✅ CUDA_HOME encontrado: {cuda_home}")
    else:
        print("❌ CUDA_HOME no configurado")
    
    # Intentar encontrar nvcc (compilador CUDA)
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = [line for line in result.stdout.split('\n') if 'release' in line.lower()]
            if version_line:
                print(f"✅ NVCC encontrado: {version_line[0].strip()}")
            else:
                print("✅ NVCC encontrado (versión no detectada)")
        else:
            print("❌ NVCC no funciona correctamente")
    except FileNotFoundError:
        print("❌ NVCC (compilador CUDA) no encontrado")
        print("   Esto sugiere que CUDA no está instalado en el sistema")
    except Exception as e:
        print(f"❌ Error verificando NVCC: {e}")

def provide_solutions():
    """Proporcionar soluciones basadas en el diagnóstico"""
    print(f"\n💡 SOLUCIONES RECOMENDADAS")
    print("=" * 40)
    
    pytorch_cuda = torch.cuda.is_available()
    pytorch_cpu_only = '+cpu' in torch.__version__
    
    if not pytorch_cuda:
        print("🔧 Para habilitar GPU en PyTorch:")
        print()
        
        if pytorch_cpu_only:
            print("1️⃣  REINSTALAR PYTORCH CON CUDA:")
            print("   Desinstalar versión actual:")
            print("   pip uninstall torch torchvision torchaudio")
            print()
            print("   Instalar versión con CUDA:")
            print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
            print("   (o cu121 para CUDA 12.1)")
            print()
        
        print("2️⃣  VERIFICAR DRIVERS NVIDIA:")
        print("   - Descargar desde: https://www.nvidia.com/drivers")
        print("   - Instalar la versión más reciente")
        print("   - Reiniciar el sistema")
        print()
        
        print("3️⃣  VERIFICAR COMPATIBILIDAD:")
        print("   - GPU debe ser NVIDIA (no AMD/Intel)")
        print("   - Compute Capability >= 3.5")
        print("   - Driver compatible con CUDA")
        print()
        
        print("4️⃣  INSTALAR CUDA TOOLKIT (opcional):")
        print("   - Descargar desde: https://developer.nvidia.com/cuda-downloads")
        print("   - Solo necesario para desarrollo avanzado")
    else:
        print("✅ PyTorch ya tiene soporte CUDA")
        print("   El sistema debería funcionar con GPU")

def test_pytorch_cuda():
    """Probar PyTorch con CUDA si está disponible"""
    print(f"\n🧪 PRUEBA DE PYTORCH + CUDA")
    print("=" * 40)
    
    if torch.cuda.is_available():
        try:
            # Crear tensor en GPU
            x = torch.randn(3, 3).cuda()
            y = torch.randn(3, 3).cuda()
            z = x + y
            
            print("✅ Operaciones básicas en GPU: OK")
            print(f"   Tensor creado en: {x.device}")
            print(f"   Suma realizada en: {z.device}")
            
            # Información de memoria
            allocated = torch.cuda.memory_allocated() / (1024**2)  # MB
            reserved = torch.cuda.memory_reserved() / (1024**2)   # MB
            print(f"   Memoria GPU usada: {allocated:.1f} MB")
            print(f"   Memoria GPU reservada: {reserved:.1f} MB")
            
        except Exception as e:
            print(f"❌ Error en prueba GPU: {e}")
            print("   La GPU puede no estar funcionando correctamente")
    else:
        print("❌ No se puede probar: CUDA no disponible en PyTorch")

def main():
    """Función principal de diagnóstico"""
    print("🩺 DIAGNÓSTICO COMPLETO DE GPU/CUDA")
    print("=" * 50)
    print()
    
    check_pytorch_installation()
    check_nvidia_gpu()
    check_cuda_installation()
    test_pytorch_cuda()
    provide_solutions()
    
    print(f"\n📋 RESUMEN:")
    print("=" * 40)
    
    pytorch_cuda = torch.cuda.is_available()
    pytorch_cpu = '+cpu' in torch.__version__
    
    if pytorch_cuda:
        print("🎉 ESTADO: GPU lista para usar")
        print("   Tu generador de imágenes usará GPU automáticamente")
    elif pytorch_cpu:
        print("⚠️  ESTADO: PyTorch solo CPU instalado")
        print("   Necesitas reinstalar PyTorch con soporte CUDA")
    else:
        print("❌ ESTADO: Problema con GPU/CUDA")
        print("   Revisa drivers NVIDIA y compatibilidad")

if __name__ == "__main__":
    main()
    input("\nPresiona ENTER para salir...")
