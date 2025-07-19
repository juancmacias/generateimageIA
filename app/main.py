# main.py - Script principal para generar gato espacial

import os
import sys
from datetime import datetime
from image_generator import ImageGeneratorAI

def main():
    """Función principal para generar gato espacial"""
    print("🚀 GENERADOR DE IMÁGENES CON IA")
    print("🐱 Proyecto: Gato Volador Espacial")
    print("=" * 50)
    
    try:
        # Crear generador y mostrar información de hardware
        generator = ImageGeneratorAI()
        
        # Mostrar información del dispositivo
        device_info = generator.get_device_info()
        print(f"\n💻 INFORMACIÓN DEL SISTEMA:")
        print(f"   🔧 Dispositivo: {device_info['device_name']}")
        print(f"   🧠 Memoria: {device_info['memory_total']}")
        if device_info['cuda_available']:
            print(f"   📊 CUDA disponible: ✅")
        else:
            print(f"   📊 CUDA disponible: ❌")
        
        # Prompt mejorado para el gato espacial
        prompt = ("a majestic cat flying gracefully through a brilliant starfield in deep space, "
                 "colorful nebulae in background, cinematic digital art, high resolution, "
                 "detailed fur, glowing stars, cosmic atmosphere, professional artwork")
        
        # Generar imagen
        image, generation_time = generator.generate(
            prompt=prompt,
            width=512,
            height=512,
            num_inference_steps=10,
            guidance_scale=7.5
        )
        
        # Crear directorio de salida
        output_dir = "generated_images"
        os.makedirs(output_dir, exist_ok=True)
        
        # Guardar imagen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gato_espacial_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        
        image.save(filepath, format='PNG', optimize=True)
        
        # Calcular estadísticas de rendimiento
        file_size = os.path.getsize(filepath) / (1024*1024)  # MB
        pixels_generated = image.size[0] * image.size[1]
        pixels_per_second = pixels_generated / generation_time
        
        # Mostrar resultados detallados
        print(f"\n🎉 ¡IMAGEN GENERADA EXITOSAMENTE!")
        print("=" * 50)
        print(f"📁 Archivo: {filename}")
        print(f"📍 Ubicación: {os.path.abspath(filepath)}")
        print(f"📏 Resolución: {image.size[0]}x{image.size[1]} pixels ({pixels_generated:,} total)")
        print(f"📦 Tamaño: {file_size:.2f} MB")
        print(f"⏱️  Tiempo: {generation_time:.2f} segundos")
        print(f"⚡ Velocidad: {pixels_per_second:,.0f} pixels/segundo")
        print(f"💻 Hardware: {device_info['device_name']}")
        
        # Mostrar rendimiento según dispositivo
        if device_info['device'] == 'cuda':
            print(f"🚀 Modo GPU - Excelente velocidad!")
        else:
            print(f"� Modo CPU - Considera usar GPU para mayor velocidad")
        
        print(f"\n🎯 ¡Tu gato espacial está listo!")
        print(f"   👀 Abre: {output_dir}/{filename}")
        
        # Limpiar recursos
        generator.cleanup()
        
        return 0
        
    except ImportError as e:
        print(f"\n❌ ERROR DE DEPENDENCIAS:")
        print(f"   {e}")
        print("\n💡 SOLUCIÓN:")
        print("   Verifica que todas las dependencias estén instaladas:")
        print("   pip install torch diffusers transformers pillow")
        return 1
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE GENERACIÓN:")
        print(f"   {e}")
        print("\n💡 POSIBLES SOLUCIONES:")
        print("   1. Verifica conexión a internet (para descargar modelos)")
        print("   2. Asegúrate de tener suficiente memoria RAM/GPU")
        print("   3. Intenta cerrar otros programas pesados")
        return 1

if __name__ == "__main__":
    exit_code = main()
    
    if exit_code == 0:
        print("\n🌟 ¡Gracias por usar el generador de imágenes!")
        input("   Presiona ENTER para salir...")
    
    sys.exit(exit_code)
