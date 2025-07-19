#!/usr/bin/env python3
"""
ℹ️ Información del Sistema - Script de Acceso Rápido
==================================================
Script para mostrar información completa del sistema.
"""

import sys
import os
import subprocess

def main():
    """Ejecutar información del sistema con entorno virtual"""
    # Obtener rutas
    current_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(current_dir, '.venv', 'Scripts', 'python.exe')
    system_script = os.path.join(current_dir, 'utils', 'system_info.py')
    
    # Verificar que existe el entorno virtual
    if not os.path.exists(venv_python):
        print("❌ Error: Entorno virtual no encontrado")
        print("💡 Ejecuta: python -m venv .venv && .venv\\Scripts\\activate && pip install -r requirements.txt")
        return 1
    
    # Ejecutar con el Python del entorno virtual
    try:
        subprocess.run([venv_python, system_script], check=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando información del sistema: {e}")
        return 1
    except FileNotFoundError:
        print("❌ Error: No se encontró el script de información del sistema")
        return 1

if __name__ == "__main__":
    sys.exit(main())
