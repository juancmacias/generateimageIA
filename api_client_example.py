# api_client_example.py - Ejemplo de cliente para la API de generación de imágenes

"""
📱 Cliente de Ejemplo para la API de Generación de Imágenes
==========================================================

Este script demuestra cómo usar la API de generación de imágenes
desde un cliente Python usando requests.

Funcionalidades:
- Verificar estado del sistema
- Generar imágenes con diferentes parámetros
- Descargar imágenes generadas
- Listar imágenes disponibles

Uso:
    python api_client_example.py
"""

import requests
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

class ImageGeneratorClient:
    """Cliente para interactuar con la API de generación de imágenes"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Inicializar cliente
        
        Args:
            base_url: URL base de la API (ej: http://localhost:8000)
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def check_api_status(self) -> bool:
        """Verificar si la API está disponible"""
        try:
            response = self.session.get(f"{self.base_url}/")
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema"""
        try:
            response = self.session.get(f"{self.base_url}/status")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
    
    def generate_image(
        self,
        prompt: str,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5
    ) -> Dict[str, Any]:
        """
        Generar una imagen
        
        Args:
            prompt: Descripción de la imagen
            width: Ancho en píxeles
            height: Alto en píxeles
            num_inference_steps: Pasos de inferencia
            guidance_scale: Escala de guidance
            
        Returns:
            Diccionario con la respuesta de la API
        """
        data = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale
        }
        
        try:
            print(f"🎨 Generando imagen: '{prompt}'...")
            print(f"   📏 Dimensiones: {width}x{height}")
            print(f"   🎯 Pasos: {num_inference_steps}")
            
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/generate",
                json=data,
                timeout=300  # 5 minutos timeout
            )
            response.raise_for_status()
            
            result = response.json()
            total_time = time.time() - start_time
            
            print(f"   ⏱️ Tiempo total: {total_time:.2f}s")
            
            return result
            
        except requests.RequestException as e:
            return {"error": str(e), "success": False}
    
    def download_image(self, filename: str, save_path: Optional[str] = None) -> bool:
        """
        Descargar una imagen generada
        
        Args:
            filename: Nombre del archivo de imagen
            save_path: Ruta donde guardar (opcional)
            
        Returns:
            True si se descargó exitosamente
        """
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
    
    def list_images(self) -> Dict[str, Any]:
        """Listar todas las imágenes disponibles"""
        try:
            response = self.session.get(f"{self.base_url}/images/list")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
    
    def cleanup_resources(self) -> Dict[str, Any]:
        """Limpiar recursos del servidor"""
        try:
            response = self.session.delete(f"{self.base_url}/cleanup")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

def demo_basic_usage():
    """Demostración básica de uso de la API"""
    print("🚀 DEMO: Cliente API de Generación de Imágenes")
    print("=" * 50)
    
    # Crear cliente
    client = ImageGeneratorClient()
    
    # 1. Verificar que la API está disponible
    print("🔍 Verificando disponibilidad de la API...")
    if not client.check_api_status():
        print("❌ La API no está disponible.")
        print("💡 Asegúrate de ejecutar: python run_api.py")
        return
    
    print("✅ API disponible")
    
    # 2. Obtener estado del sistema
    print("\n🩺 Verificando estado del sistema...")
    status = client.get_system_status()
    if "error" in status:
        print(f"❌ Error obteniendo estado: {status['error']}")
    else:
        print(f"   🖥️  GPU disponible: {'Sí' if status['gpu_available'] else 'No'}")
        print(f"   📱 Dispositivo: {status['device_name']}")
        print(f"   📊 Memoria: {status['memory_info']}")
        print(f"   🧠 Modelo cargado: {'Sí' if status['model_loaded'] else 'No'}")
    
    # 3. Generar imagen de ejemplo
    print("\n🎨 Generando imagen de ejemplo...")
    result = client.generate_image(
        prompt="a beautiful cat flying through space among stars and galaxies",
        width=512,
        height=512,
        num_inference_steps=20,
        guidance_scale=7.5
    )
    
    if result.get("success"):
        print(f"✅ Imagen generada exitosamente!")
        print(f"   📁 Archivo: {result['filename']}")
        print(f"   🔗 URL: {client.base_url}{result['image_url']}")
        print(f"   ⏱️ Tiempo generación: {result['generation_time']:.2f}s")
        
        # 4. Descargar la imagen generada
        if input("\n📥 ¿Descargar imagen? (y/N): ").lower() == 'y':
            client.download_image(result['filename'])
            
    else:
        print(f"❌ Error generando imagen: {result.get('message', 'Error desconocido')}")
    
    # 5. Listar imágenes disponibles
    print("\n📚 Listando imágenes disponibles...")
    images_list = client.list_images()
    if "error" in images_list:
        print(f"❌ Error listando imágenes: {images_list['error']}")
    else:
        print(f"   📊 Total de imágenes: {images_list['count']}")
        for img in images_list['images'][:3]:  # Mostrar solo las primeras 3
            print(f"   📄 {img['filename']} ({img['size']} bytes)")

def demo_batch_generation():
    """Demostración de generación en lote"""
    print("\n🔄 DEMO: Generación en Lote")
    print("=" * 30)
    
    client = ImageGeneratorClient()
    
    prompts = [
        "a peaceful forest with morning sunlight",
        "a modern city skyline at night with neon lights",
        "a vintage car on a desert road"
    ]
    
    results = []
    for i, prompt in enumerate(prompts, 1):
        print(f"\n{i}/{len(prompts)} - Generando: {prompt}")
        result = client.generate_image(
            prompt=prompt,
            width=256,  # Resolución menor para velocidad
            height=256,
            num_inference_steps=15
        )
        results.append(result)
        
        if result.get("success"):
            print(f"   ✅ Completado en {result['generation_time']:.1f}s")
        else:
            print(f"   ❌ Error: {result.get('message', 'Desconocido')}")
    
    successful = [r for r in results if r.get("success")]
    print(f"\n📊 Resumen: {len(successful)}/{len(prompts)} imágenes generadas exitosamente")

def interactive_mode():
    """Modo interactivo para generar imágenes personalizadas"""
    print("\n🎮 MODO INTERACTIVO")
    print("=" * 20)
    print("Genera imágenes personalizadas. Escribe 'quit' para salir.")
    
    client = ImageGeneratorClient()
    
    if not client.check_api_status():
        print("❌ API no disponible")
        return
    
    while True:
        print("\n" + "="*40)
        prompt = input("📝 Describe la imagen que quieres generar: ").strip()
        
        if prompt.lower() in ['quit', 'exit', 'salir']:
            break
            
        if not prompt:
            continue
        
        # Configuración opcional
        print("\n⚙️ Configuración (presiona Enter para usar valores por defecto)")
        
        try:
            width = input(f"   📐 Ancho [512]: ").strip()
            width = int(width) if width else 512
            
            height = input(f"   📏 Alto [512]: ").strip()
            height = int(height) if height else 512
            
            steps = input(f"   🎯 Pasos de inferencia [20]: ").strip()
            steps = int(steps) if steps else 20
            
            guidance = input(f"   🎚️ Guidance scale [7.5]: ").strip()
            guidance = float(guidance) if guidance else 7.5
            
        except ValueError:
            print("⚠️ Valor inválido, usando valores por defecto")
            width, height, steps, guidance = 512, 512, 20, 7.5
        
        # Generar imagen
        result = client.generate_image(prompt, width, height, steps, guidance)
        
        if result.get("success"):
            print(f"\n🎉 ¡Imagen generada!")
            print(f"   🔗 URL: {client.base_url}{result['image_url']}")
            
            if input("   📥 ¿Descargar? (y/N): ").lower() == 'y':
                client.download_image(result['filename'])
        else:
            print(f"\n❌ Error: {result.get('message', 'Desconocido')}")

def main():
    """Función principal"""
    print("🎨 CLIENTE API - GENERADOR DE IMÁGENES IA")
    print("=" * 50)
    print("Opciones:")
    print("1. Demo básico")
    print("2. Generación en lote")
    print("3. Modo interactivo")
    print("4. Solo verificar estado")
    print("=" * 50)
    
    choice = input("Selecciona una opción (1-4) [1]: ").strip()
    
    if choice == "2":
        demo_batch_generation()
    elif choice == "3":
        interactive_mode()
    elif choice == "4":
        client = ImageGeneratorClient()
        status = client.get_system_status()
        print(f"\n🩺 Estado del sistema:")
        print(json.dumps(status, indent=2, ensure_ascii=False))
    else:
        demo_basic_usage()
    
    print("\n👋 ¡Gracias por usar el Generador de Imágenes IA!")

if __name__ == "__main__":
    main()
