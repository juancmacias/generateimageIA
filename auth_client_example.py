# auth_client_example.py - Cliente de ejemplo con autenticación

"""
🔐 Cliente con Autenticación para la API de Generación de Imágenes
================================================================

Este script demuestra cómo usar la nueva API con sistema de autenticación.
Muestra registro, login, generación con API key y manejo de límites.

Características:
- Registro de nuevo usuario
- Login y obtención de tokens
- Generación con API key
- Monitoreo de uso y límites
- Manejo de errores de autenticación

Uso:
    python auth_client_example.py
"""

import requests
import json
import time
from typing import Dict, Any, Optional
from pathlib import Path

class AuthImageGeneratorClient:
    """Cliente autenticado para la API de generación de imágenes"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Inicializar cliente autenticado
        
        Args:
            base_url: URL base de la API
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.token = None
        self.api_key = None
        self.user_info = None
    
    def check_auth_status(self) -> Dict[str, Any]:
        """Verificar si la API tiene autenticación habilitada"""
        try:
            response = self.session.get(f"{self.base_url}/status")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
    
    def register(self, email: str, password: str, full_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Registrar nuevo usuario
        
        Args:
            email: Email del usuario
            password: Contraseña
            full_name: Nombre completo (opcional)
        """
        data = {
            "email": email,
            "password": password
        }
        
        if full_name:
            data["full_name"] = full_name
        
        try:
            print(f"📝 Registrando usuario: {email}")
            response = self.session.post(f"{self.base_url}/auth/register", json=data)
            response.raise_for_status()
            
            result = response.json()
            
            # Guardar información de autenticación
            self.token = result["access_token"]
            self.api_key = result["user"]["api_key"]
            self.user_info = result["user"]
            
            # Configurar headers de autenticación
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            
            print(f"✅ Usuario registrado exitosamente!")
            print(f"   📧 Email: {result['user']['email']}")
            print(f"   🔑 API Key: {self.api_key[:16]}...")
            print(f"   📊 Límite de uso: {result['user']['usage_limit']}")
            
            return result
            
        except requests.RequestException as e:
            error_detail = "Error desconocido"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_detail = error_data.get('detail', str(e))
                except:
                    error_detail = str(e)
            
            print(f"❌ Error en registro: {error_detail}")
            return {"error": error_detail, "success": False}
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Iniciar sesión
        
        Args:
            email: Email del usuario
            password: Contraseña
        """
        data = {
            "email": email,
            "password": password
        }
        
        try:
            print(f"🔐 Iniciando sesión: {email}")
            response = self.session.post(f"{self.base_url}/auth/login", json=data)
            response.raise_for_status()
            
            result = response.json()
            
            # Guardar información de autenticación
            self.token = result["access_token"]
            self.api_key = result["user"]["api_key"]
            self.user_info = result["user"]
            
            # Configurar headers de autenticación
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            
            print(f"✅ Sesión iniciada exitosamente!")
            print(f"   📧 Email: {result['user']['email']}")
            print(f"   🔑 Nueva API Key: {self.api_key[:16]}...")
            print(f"   📊 Uso actual: {result['user']['usage_count']}/{result['user']['usage_limit']}")
            
            return result
            
        except requests.RequestException as e:
            error_detail = "Error desconocido"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_detail = error_data.get('detail', str(e))
                except:
                    error_detail = str(e)
            
            print(f"❌ Error en login: {error_detail}")
            return {"error": error_detail, "success": False}
    
    def get_profile(self) -> Dict[str, Any]:
        """Obtener perfil del usuario actual"""
        try:
            response = self.session.get(f"{self.base_url}/auth/profile")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas detalladas del usuario"""
        try:
            response = self.session.get(f"{self.base_url}/auth/stats")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
    
    def generate_with_api_key(
        self,
        prompt: str,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5
    ) -> Dict[str, Any]:
        """
        Generar imagen usando API key (más eficiente que token JWT)
        """
        if not self.api_key:
            return {"error": "No hay API key disponible. Inicia sesión primero.", "success": False}
        
        # Crear sesión temporal solo con API key
        temp_session = requests.Session()
        temp_session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        
        data = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale
        }
        
        try:
            print(f"🎨 Generando imagen con API key: '{prompt}'...")
            print(f"   📏 Dimensiones: {width}x{height}")
            print(f"   🎯 Pasos: {num_inference_steps}")
            
            start_time = time.time()
            response = temp_session.post(
                f"{self.base_url}/generate",
                json=data,
                timeout=300  # 5 minutos timeout
            )
            response.raise_for_status()
            
            result = response.json()
            total_time = time.time() - start_time
            
            if result.get("success"):
                print(f"   ✅ Generación exitosa en {total_time:.2f}s")
                print(f"   📁 Archivo: {result['filename']}")
                if result.get("usage_count"):
                    print(f"   📊 Uso actualizado: {result['usage_count']}")
            else:
                print(f"   ❌ Error: {result.get('message', 'Error desconocido')}")
            
            return result
            
        except requests.RequestException as e:
            error_detail = "Error desconocido"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_detail = error_data.get('detail', str(e))
                except:
                    error_detail = str(e)
            
            print(f"❌ Error generando imagen: {error_detail}")
            return {"error": error_detail, "success": False}
    
    def generate_with_token(
        self,
        prompt: str,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5
    ) -> Dict[str, Any]:
        """
        Generar imagen usando token JWT
        """
        if not self.token:
            return {"error": "No hay token disponible. Inicia sesión primero.", "success": False}
        
        data = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale
        }
        
        try:
            print(f"🎨 Generando imagen con JWT: '{prompt}'...")
            
            response = self.session.post(f"{self.base_url}/generate", json=data, timeout=300)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            return {"error": str(e), "success": False}
    
    def download_image(self, filename: str, save_path: Optional[str] = None) -> bool:
        """Descargar imagen generada"""
        try:
            response = self.session.get(f"{self.base_url}/image/{filename}")
            response.raise_for_status()
            
            if save_path is None:
                save_path = f"downloaded_{filename}"
            
            Path(save_path).write_bytes(response.content)
            print(f"📥 Imagen descargada: {save_path}")
            return True
            
        except requests.RequestException as e:
            print(f"❌ Error descargando imagen: {e}")
            return False

def demo_authentication():
    """Demo completo del sistema de autenticación"""
    print("🔐 DEMO: Sistema de Autenticación")
    print("=" * 40)
    
    client = AuthImageGeneratorClient()
    
    # 1. Verificar estado de la API
    print("🔍 Verificando estado de la API...")
    status = client.check_auth_status()
    if not status.get("auth_enabled"):
        print("⚠️ La autenticación no está habilitada en la API.")
        print("💡 Para habilitar, configura AUTH_ENABLED=true en .env")
        return
    
    print("✅ Autenticación habilitada")
    
    # 2. Registrar usuario (o intentar login si ya existe)
    email = input("\n📧 Ingresa tu email: ").strip()
    password = input("🔒 Ingresa tu contraseña: ").strip()
    full_name = input("👤 Ingresa tu nombre (opcional): ").strip() or None
    
    # Intentar registro primero
    register_result = client.register(email, password, full_name)
    
    if not register_result.get("success", True):
        if "ya está registrado" in str(register_result.get("error", "")):
            print("\n💡 Usuario ya existe, intentando login...")
            login_result = client.login(email, password)
            if not login_result.get("success", True):
                print("❌ Error en login. Terminando demo.")
                return
        else:
            print("❌ Error en registro. Terminando demo.")
            return
    
    # 3. Mostrar perfil
    print("\n👤 Obteniendo perfil...")
    profile = client.get_profile()
    if "error" not in profile:
        print(f"   📧 Email: {profile['email']}")
        print(f"   📊 Uso: {profile['usage_count']}/{profile['usage_limit']}")
        print(f"   🆓 Restantes: {profile['remaining_uses']}")
    
    # 4. Mostrar estadísticas detalladas
    print("\n📊 Estadísticas detalladas...")
    stats = client.get_stats()
    if "error" not in stats:
        print(f"   📈 Total generaciones: {stats['statistics']['total_generations']}")
        print(f"   ✅ Exitosas: {stats['statistics']['successful_generations']}")
        print(f"   📉 Tasa éxito: {stats['statistics']['success_rate']:.1f}%")
    
    # 5. Generar imagen con API key
    print("\n🎨 Generando imagen con API key...")
    result = client.generate_with_api_key(
        prompt="a beautiful cat astronaut floating in space among colorful nebulas",
        width=256,  # Resolución pequeña para demo
        height=256,
        num_inference_steps=15
    )
    
    if result.get("success"):
        print(f"🎉 ¡Imagen generada exitosamente!")
        
        # Descargar imagen
        if input("📥 ¿Descargar imagen? (y/N): ").lower() == 'y':
            client.download_image(result['filename'])
    
    # 6. Mostrar perfil actualizado
    print("\n📊 Perfil actualizado:")
    updated_profile = client.get_profile()
    if "error" not in updated_profile:
        print(f"   📊 Uso: {updated_profile['usage_count']}/{updated_profile['usage_limit']}")
        print(f"   🆓 Restantes: {updated_profile['remaining_uses']}")

def demo_api_key_only():
    """Demo usando solo API key (sin registro interactivo)"""
    print("\n🔑 DEMO: Uso solo con API key")
    print("=" * 30)
    
    api_key = input("Ingresa tu API key: ").strip()
    if not api_key:
        print("❌ API key requerida")
        return
    
    client = AuthImageGeneratorClient()
    client.api_key = api_key
    
    # Generar imagen
    result = client.generate_with_api_key(
        "a magical forest with glowing mushrooms and fireflies",
        width=512,
        height=512
    )
    
    if result.get("success"):
        print("🎉 Imagen generada con API key exitosamente!")
        if input("📥 ¿Descargar? (y/N): ").lower() == 'y':
            client.download_image(result['filename'])

def main():
    """Función principal"""
    print("🔐 CLIENTE AUTENTICADO - GENERADOR DE IMÁGENES IA")
    print("=" * 55)
    print("Opciones:")
    print("1. Demo completo con registro/login")
    print("2. Usar solo API key existente")
    print("3. Verificar estado de la API")
    print("=" * 55)
    
    choice = input("Selecciona una opción (1-3) [1]: ").strip()
    
    if choice == "2":
        demo_api_key_only()
    elif choice == "3":
        client = AuthImageGeneratorClient()
        status = client.check_auth_status()
        print("\n🩺 Estado de la API:")
        print(json.dumps(status, indent=2, ensure_ascii=False))
    else:
        demo_authentication()
    
    print("\n👋 ¡Gracias por probar el sistema de autenticación!")

if __name__ == "__main__":
    main()
