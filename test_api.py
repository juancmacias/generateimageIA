#!/usr/bin/env python3
"""
Script de prueba para la API de generación de imágenes
"""
import requests
import json
from datetime import datetime

def test_basic_image_generation():
    """Prueba básica de generación de imagen"""
    # URL de la API (ajusta si es necesario)
    base_url = "http://127.0.0.1:8001"
    
    # Parámetros para la generación de imagen
    request_data = {
        "prompt": "Un gato espacial con traje de astronauta flotando entre estrellas",
        "width": 512,
        "height": 512,
        "num_inference_steps": 20
    }
    
    print(f"🚀 Iniciando prueba de generación de imagen...")
    print(f"📝 Prompt: {request_data['prompt']}")
    print(f"📐 Dimensiones: {request_data['width']}x{request_data['height']}")
    print(f"🔄 Pasos de inferencia: {request_data['num_inference_steps']}")
    print("-" * 60)
    
    try:
        # Realizar la solicitud
        print("⏳ Enviando solicitud a la API...")
        response = requests.post(
            f"{base_url}/generate",
            json=request_data,
            timeout=180  # 3 minutos
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ ¡Imagen generada exitosamente!")
                print(f"🔗 URL de la imagen: {result['image_url']}")
                print(f"📅 Timestamp: {datetime.now().isoformat()}")
                print(f"⚡ Tiempo de generación: {result['generation_time']:.2f} segundos")
                print(f"🎯 Prompt usado: {request_data['prompt']}")
                print(f"📊 Configuración: {result['parameters']}")
                return result
            else:
                print(f"❌ Error en la generación: {result['message']}")
                return None
        else:
            print(f"❌ Error en la API: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout: La solicitud tomó demasiado tiempo")
        return None
    except requests.exceptions.ConnectionError:
        print("🔌 Error de conexión: ¿Está la API ejecutándose en http://127.0.0.1:8001?")
        return None
    except Exception as e:
        print(f"💥 Error inesperado: {e}")
        return None

def test_api_health():
    """Prueba el endpoint de estado de la API"""
    try:
        response = requests.get("http://127.0.0.1:8001/status")
        if response.status_code == 200:
            result = response.json()
            print("💚 API está funcionando correctamente")
            print(f"📊 Estado: {result}")
            return True
        else:
            print(f"❌ Problema con la API: {response.status_code}")
            return False
    except Exception as e:
        print(f"💥 Error conectando con la API: {e}")
        return False

if __name__ == "__main__":
    print("🎨 PRUEBA DE API DE GENERACIÓN DE IMÁGENES")
    print("=" * 60)
    
    # Verificar que la API esté disponible
    if test_api_health():
        print("\n🖼️ PROBANDO GENERACIÓN DE IMAGEN")
        print("=" * 60)
        result = test_basic_image_generation()
        
        if result:
            print("\n🎉 ¡PRUEBA EXITOSA!")
            print("Puedes encontrar tu imagen generada en la carpeta 'generated_images'")
        else:
            print("\n😞 La prueba falló")
    else:
        print("\n❌ No se puede conectar con la API")
        print("Asegúrate de que esté ejecutándose en http://127.0.0.1:8001")
