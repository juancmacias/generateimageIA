#!/usr/bin/env python3
# run_api.py - Script de acceso rápido para ejecutar la API

"""
🌐 API de Generación de Imágenes con IA
=====================================

Este script inicia la API REST que permite generar imágenes usando Stable Diffusion
a través de requests HTTP.

Endpoints principales:
- POST /generate - Generar imagen
- GET /status - Estado del sistema
- GET /image/{filename} - Descargar imagen
- GET /docs - Documentación interactiva

Uso:
    python run_api.py [--host HOST] [--port PORT] [--reload]

Ejemplos:
    python run_api.py                    # Ejecutar en localhost:8000
    python run_api.py --port 8080        # Ejecutar en puerto 8080
    python run_api.py --reload           # Modo desarrollo con auto-reload
"""

import sys
import argparse
from pathlib import Path

# Agregar directorio raíz al path
sys.path.append(str(Path(__file__).parent))

def main():
    parser = argparse.ArgumentParser(
        description="🌐 API de Generación de Imágenes con IA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python run_api.py                    # Ejecutar en localhost:8000
  python run_api.py --port 8080        # Ejecutar en puerto 8080
  python run_api.py --reload           # Modo desarrollo con auto-reload
  python run_api.py --host 0.0.0.0     # Permitir acceso externo

Una vez iniciada, la API estará disponible en:
  - Documentación: http://localhost:8000/docs
  - Endpoint principal: http://localhost:8000/generate
  - Estado del sistema: http://localhost:8000/status
        """
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host/IP donde ejecutar la API (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Puerto donde ejecutar la API (default: 8000)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Habilitar auto-reload para desarrollo"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Número de procesos worker (default: 1)"
    )
    
    args = parser.parse_args()
    
    print("🌐 GENERADOR DE IMÁGENES IA - API REST")
    print("=" * 50)
    print(f"🏠 Host: {args.host}")
    print(f"🚪 Puerto: {args.port}")
    print(f"🔄 Auto-reload: {'Sí' if args.reload else 'No'}")
    print(f"👥 Workers: {args.workers}")
    print("=" * 50)
    print(f"🔗 URL principal: http://{args.host}:{args.port}")
    print(f"📖 Documentación: http://{args.host}:{args.port}/docs")
    print(f"🩺 Estado sistema: http://{args.host}:{args.port}/status")
    print("=" * 50)
    print("💡 Presiona Ctrl+C para detener la API")
    print()
    
    try:
        from app.api import run_api
        run_api(
            host=args.host,
            port=args.port,
            reload=args.reload
        )
        
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        print("\n💡 Soluciones:")
        print("1. Instala las dependencias: pip install -r requirements.txt")
        print("2. Activa el entorno virtual si lo tienes")
        print("3. Verifica que estés en el directorio correcto")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n👋 API detenida por el usuario")
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
