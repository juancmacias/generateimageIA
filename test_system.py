#!/usr/bin/env python3
"""
🧪 Test Suite - Generador de Imágenes IA
========================================
Script para probar todas las funcionalidades del sistema.
"""

import sys
import os
import subprocess
import time

def print_header(title):
    """Imprimir encabezado decorado"""
    print(f"\n{'='*50}")
    print(f"🧪 {title}")
    print(f"{'='*50}")

def run_test(test_name, command, timeout=30):
    """Ejecutar un test individual"""
    print(f"\n🔍 Probando: {test_name}")
    print(f"📝 Comando: {command}")
    
    try:
        # Ejecutar comando
        start_time = time.time()
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        end_time = time.time()
        
        # Mostrar resultados
        if result.returncode == 0:
            print(f"✅ {test_name}: EXITOSO ({end_time - start_time:.1f}s)")
            return True
        else:
            print(f"❌ {test_name}: FALLO")
            if result.stderr:
                print(f"📋 Error: {result.stderr[:200]}...")
            return False
    
    except subprocess.TimeoutExpired:
        print(f"⏰ {test_name}: TIMEOUT ({timeout}s)")
        return False
    except Exception as e:
        print(f"💥 {test_name}: ERROR - {e}")
        return False

def main():
    """Ejecutar suite completa de tests"""
    print_header("SUITE DE TESTS - GENERADOR IA")
    
    # Cambiar al directorio del proyecto
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    
    # Tests a ejecutar
    tests = [
        ("Entorno Virtual", ".venv\\Scripts\\python.exe --version", 5),
        ("Importar PyTorch", ".venv\\Scripts\\python.exe -c \"import torch; print(f'PyTorch {torch.__version__}')\"", 15),
        ("Importar Diffusers", ".venv\\Scripts\\python.exe -c \"import diffusers; print(f'Diffusers {diffusers.__version__}')\"", 15),
        ("Verificar CUDA", ".venv\\Scripts\\python.exe -c \"import torch; print(f'CUDA: {torch.cuda.is_available()}')\"", 15),
        ("Diagnóstico GPU", "python check_gpu.py", 60),
        ("Información Sistema", "python system_check.py", 30),
    ]
    
    # Ejecutar tests
    passed = 0
    total = len(tests)
    
    for test_name, command, timeout in tests:
        if run_test(test_name, command, timeout):
            passed += 1
    
    # Mostrar resumen
    print_header("RESUMEN DE TESTS")
    print(f"📊 Tests ejecutados: {total}")
    print(f"✅ Tests exitosos: {passed}")
    print(f"❌ Tests fallidos: {total - passed}")
    print(f"📈 Tasa de éxito: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print(f"\n🎉 ¡TODOS LOS TESTS PASARON!")
        print(f"🚀 El sistema está listo para usar")
        print(f"\n📚 Comandos disponibles:")
        print(f"   • python generate_image.py  - Generar imagen")
        print(f"   • python run_examples.py    - Ver ejemplos")
        print(f"   • python check_gpu.py       - Verificar GPU")
        return 0
    else:
        print(f"\n⚠️  ALGUNOS TESTS FALLARON")
        print(f"💡 Revisa la instalación con: install.bat")
        return 1

if __name__ == "__main__":
    sys.exit(main())
