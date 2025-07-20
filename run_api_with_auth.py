#!/usr/bin/env python3
# run_api_with_auth.py - Script para ejecutar la API con autenticación

"""
🔐 API de Generación de Imágenes con Autenticación
==================================================

Este script inicia la API REST con sistema completo de autenticación usando Supabase.

Características:
- Compatible con API anterior (modo sin autenticación)
- Sistema completo de usuarios con registro/login
- API keys para acceso programático
- Límites de uso por usuario
- Logging de generaciones
- Protección con JWT tokens

Uso:
    python run_api_with_auth.py [--host HOST] [--port PORT] [--reload] [--no-auth]

Ejemplos:
    python run_api_with_auth.py                    # API con autenticación
    python run_api_with_auth.py --no-auth          # API sin autenticación (compatible)
    python run_api_with_auth.py --port 8080        # Puerto personalizado
    python run_api_with_auth.py --reload           # Modo desarrollo
"""

import sys
import os
import argparse
from pathlib import Path

# Agregar directorio raíz al path
sys.path.append(str(Path(__file__).parent))

def main():
    parser = argparse.ArgumentParser(
        description="🔐 API de Generación de Imágenes con Autenticación",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python run_api_with_auth.py                    # API con autenticación
  python run_api_with_auth.py --no-auth          # API sin autenticación
  python run_api_with_auth.py --port 8080        # Puerto 8080
  python run_api_with_auth.py --reload           # Auto-reload para desarrollo

Configuración:
  - Configura las variables en el archivo .env
  - Para Supabase: SUPABASE_URL, SUPABASE_KEY
  - Para JWT: JWT_SECRET_KEY
  - AUTH_ENABLED=true/false para habilitar/deshabilitar autenticación

Endpoints disponibles:
  POST /generate                  # Generar imagen (compatible sin auth)
  GET  /status                   # Estado del sistema
  GET  /image/{filename}         # Descargar imagen
  
  POST /auth/register            # Registrar usuario (si auth habilitada)
  POST /auth/login               # Login (si auth habilitada)
  GET  /auth/profile             # Perfil del usuario (requiere auth)
  GET  /docs                     # Documentación interactiva
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
        "--no-auth",
        action="store_true",
        help="Deshabilitar autenticación (modo compatible con API anterior)"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Número de procesos worker (default: 1)"
    )
    
    args = parser.parse_args()
    
    # Configurar autenticación
    if args.no_auth:
        os.environ["AUTH_ENABLED"] = "false"
    
    # Verificar archivo .env
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("⚠️  ADVERTENCIA: No se encontró archivo .env")
        print("   Copiando .env.example a .env...")
        example_file = Path(__file__).parent / ".env.example"
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print("   ✅ Archivo .env creado desde .env.example")
            print("   📝 Configura las variables en .env antes de usar autenticación")
        else:
            print("   ❌ No se encontró .env.example")
    
    auth_status = "Deshabilitada" if args.no_auth else "Habilitada"
    
    print("🔐 GENERADOR DE IMÁGENES IA - API CON AUTENTICACIÓN")
    print("=" * 60)
    print(f"🏠 Host: {args.host}")
    print(f"🚪 Puerto: {args.port}")
    print(f"🔄 Auto-reload: {'Sí' if args.reload else 'No'}")
    print(f"👥 Workers: {args.workers}")
    print(f"🔐 Autenticación: {auth_status}")
    print("=" * 60)
    print(f"🔗 URL principal: http://{args.host}:{args.port}")
    print(f"📖 Documentación: http://{args.host}:{args.port}/docs")
    
    if not args.no_auth:
        print(f"🔐 Registro: http://{args.host}:{args.port}/auth/register")
        print(f"🔑 Login: http://{args.host}:{args.port}/auth/login")
        print("💡 Usa 'auth_client_example.py' para probar la autenticación")
    else:
        print("💡 Usa 'api_client_example.py' para probar sin autenticación")
    
    print("=" * 60)
    print("💡 Presiona Ctrl+C para detener la API")
    print()
    
    try:
        from app.api_with_auth import run_api
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
        print("\n🔧 Instalación de dependencias:")
        print("pip install fastapi uvicorn supabase python-jose[cryptography] passlib[bcrypt] python-dotenv")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n👋 API detenida por el usuario")
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
