#!/usr/bin/env python3
"""
📚 Ejemplos Interactivos - Script de Acceso Rápido
=================================================
Script para ejecutar ejemplos y demos del generador de imágenes.
"""

import sys
import os
import subprocess

def main():
    """Ejecutar ejemplos con entorno virtual"""
    # Obtener rutas
    current_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(current_dir, '.venv', 'Scripts', 'python.exe')
    examples_script = os.path.join(current_dir, 'examples', 'examples.py')
    
    # Verificar que existe el entorno virtual
    if not os.path.exists(venv_python):
        print("❌ Error: Entorno virtual no encontrado")
        print("💡 Ejecuta: python -m venv .venv && .venv\\Scripts\\activate && pip install -r requirements.txt")
        return 1
    
    # Ejecutar con el Python del entorno virtual
    try:
        subprocess.run([venv_python, examples_script], check=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando ejemplos: {e}")
        return 1
    except FileNotFoundError:
        print("❌ Error: No se encontró el script de ejemplos")
        return 1

if __name__ == "__main__":
    sys.exit(main())
