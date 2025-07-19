# system_info.py - Información detallada del sistema para IA

import torch
import sys
import platform
import psutil
from image_generator import SimpleImageGenerator

def show_system_info():
    """Mostrar información completa del sistema"""
    
    print("🖥️  INFORMACIÓN COMPLETA DEL SISTEMA")
    print("=" * 50)
    
    # Información básica del sistema
    print("📋 SISTEMA OPERATIVO:")
    print(f"   🖥️  OS: {platform.system()} {platform.release()}")
    print(f"   🏗️  Arquitectura: {platform.architecture()[0]}")
    print(f"   🐍 Python: {sys.version.split()[0]}")
    print(f"   🔥 PyTorch: {torch.__version__}")
    
    # Información de CPU
    print(f"\n💻 PROCESADOR:")
    print(f"   🧠 CPU: {platform.processor()}")
    print(f"   🔢 Cores: {psutil.cpu_count(logical=False)} físicos, {psutil.cpu_count(logical=True)} lógicos")
    print(f"   📊 Uso actual: {psutil.cpu_percent()}%")
    
    # Información de memoria RAM
    memory = psutil.virtual_memory()
    print(f"\n🧠 MEMORIA RAM:")
    print(f"   📊 Total: {memory.total / (1024**3):.1f} GB")
    print(f"   ✅ Disponible: {memory.available / (1024**3):.1f} GB")
    print(f"   📈 Uso: {memory.percent}%")
    
    # Información de GPU/CUDA
    print(f"\n🎮 ACELERACIÓN GPU:")
    if torch.cuda.is_available():
        print("   ✅ CUDA disponible: SÍ")
        print(f"   🔢 GPUs detectadas: {torch.cuda.device_count()}")
        
        for i in range(torch.cuda.device_count()):
            gpu_props = torch.cuda.get_device_properties(i)
            print(f"\n   🎯 GPU {i}: {gpu_props.name}")
            print(f"      🧠 VRAM: {gpu_props.total_memory / (1024**3):.1f} GB")
            print(f"      ⚡ Compute Capability: {gpu_props.major}.{gpu_props.minor}")
            
            try:
                memory_allocated = torch.cuda.memory_allocated(i) / (1024**3)
                memory_reserved = torch.cuda.memory_reserved(i) / (1024**3)
                memory_free = (gpu_props.total_memory / (1024**3)) - memory_reserved
                print(f"      📊 VRAM libre: {memory_free:.1f} GB")
                print(f"      📈 VRAM usada: {memory_allocated:.1f} GB")
            except:
                print(f"      📊 Estado: Disponible")
    else:
        print("   ❌ CUDA disponible: NO")
        print("   💡 Razones posibles:")
        print("      - No hay GPU NVIDIA instalada")
        print("      - Drivers NVIDIA desactualizados")
        print("      - PyTorch instalado sin soporte CUDA")
    
    # Recomendaciones de rendimiento
    print(f"\n⚡ RECOMENDACIONES DE RENDIMIENTO:")
    
    if torch.cuda.is_available():
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        if gpu_memory >= 6:
            print("   🚀 EXCELENTE: GPU con suficiente VRAM")
            print("   💡 Puedes generar imágenes de hasta 1024x1024")
            print("   ⏱️  Tiempo esperado: 30-60 segundos por imagen")
        elif gpu_memory >= 4:
            print("   ✅ BUENO: GPU con VRAM moderada")
            print("   💡 Recomendado: imágenes de 512x512")
            print("   ⏱️  Tiempo esperado: 60-120 segundos por imagen")
        else:
            print("   ⚠️  LIMITADO: GPU con poca VRAM")
            print("   💡 Usar resoluciones bajas (256x256-512x512)")
            print("   ⏱️  Tiempo esperado: variable")
    else:
        ram_gb = memory.total / (1024**3)
        if ram_gb >= 16:
            print("   🐌 CPU con RAM suficiente")
            print("   💡 Funcional pero lento")
            print("   ⏱️  Tiempo esperado: 5-10 minutos por imagen")
        else:
            print("   ⚠️  RAM limitada para generación de imágenes")
            print("   💡 Cerrar otros programas antes de generar")
            print("   ⏱️  Tiempo esperado: 10-15 minutos por imagen")
    
    print("\n" + "=" * 50)
    
    # Probar inicialización del generador
    try:
        print("\n🧪 PROBANDO INICIALIZACIÓN DEL GENERADOR...")
        generator = SimpleImageGenerator()
        device_info = generator.get_device_info()
        
        print("✅ PRUEBA EXITOSA!")
        print(f"   Dispositivo configurado: {device_info['device_name']}")
        generator.cleanup()
        
    except Exception as e:
        print(f"❌ ERROR EN LA PRUEBA: {e}")
        print("💡 Verifica que las dependencias estén correctamente instaladas")

def main():
    """Función principal"""
    show_system_info()
    input("\nPresiona ENTER para salir...")

if __name__ == "__main__":
    main()
