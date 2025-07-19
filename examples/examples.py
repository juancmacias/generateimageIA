# examples.py - Ejemplos de diferentes tipos de imágenes

import os
import sys
from datetime import datetime

# Agregar el directorio app al path para importar el generador
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(os.path.dirname(current_dir), 'app')
sys.path.insert(0, app_dir)

from image_generator import ImageGeneratorAI

def generate_example_images():
    """Generar varios ejemplos de imágenes"""
    
    # Lista de prompts de ejemplo
    examples = [
        {
            "name": "paisaje_fantastico",
            "prompt": "a magical floating island in the sky with waterfalls, rainbow bridges, fantasy art, detailed, colorful",
            "description": "Paisaje fantástico con islas flotantes"
        },
        {
            "name": "robot_futurista", 
            "prompt": "a sleek humanoid robot in a futuristic laboratory, metallic surface, blue lights, sci-fi concept art",
            "description": "Robot futurista en laboratorio"
        },
        {
            "name": "bosque_mistico",
            "prompt": "an enchanted forest with glowing mushrooms and fairy lights, misty atmosphere, magical creatures",
            "description": "Bosque místico con luces mágicas"
        },
        {
            "name": "ciudad_cyberpunk",
            "prompt": "cyberpunk cityscape at night, neon signs, rain reflections, dark atmosphere, futuristic architecture",
            "description": "Ciudad cyberpunk nocturna"
        }
    ]
    
    print("🎨 Generador de Imágenes - Ejemplos Variados")
    print("=" * 50)
    print(f"Se generarán {len(examples)} imágenes de ejemplo")
    print("Cada una tomará varios minutos...")
    print()
    
    try:
        # Inicializar generador
        generator = ImageGeneratorAI()
        
        # Crear directorio de ejemplos
        examples_dir = "example_images"
        os.makedirs(examples_dir, exist_ok=True)
        
        for i, example in enumerate(examples, 1):
            print(f"📸 Generando imagen {i}/{len(examples)}: {example['description']}")
            
            # Generar imagen
            image, generation_time = generator.generate(
                prompt=example['prompt'],
                width=512,
                height=512,
                num_inference_steps=20,
                guidance_scale=7.5
            )
            
            # Guardar imagen
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{example['name']}_{timestamp}.png"
            filepath = os.path.join(examples_dir, filename)
            
            image.save(filepath, format='PNG', optimize=True)
            
            print(f"   ✅ Guardado como: {filename}")
            print(f"   ⏱️  Tiempo: {generation_time:.1f}s")
            print()
        
        print("🎉 ¡Todos los ejemplos generados exitosamente!")
        print(f"📁 Revisa la carpeta: {examples_dir}/")
        
        # Limpiar
        generator.cleanup()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

def generate_single_custom():
    """Permitir al usuario ingresar un prompt personalizado"""
    
    print("🎨 Generador Personalizado")
    print("=" * 30)
    
    # Solicitar prompt al usuario
    prompt = input("Describe la imagen que quieres generar: ").strip()
    
    if not prompt:
        print("❌ No se ingresó ningún prompt")
        return 1
    
    try:
        # Generar
        generator = ImageGeneratorAI()
        
        print(f"\n🎨 Generando: {prompt}")
        image, generation_time = generator.generate(
            prompt=prompt,
            width=512,
            height=512,
            num_inference_steps=25,
            guidance_scale=7.5
        )
        
        # Guardar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"custom_image_{timestamp}.png"
        filepath = os.path.join("generated_images", filename)
        
        os.makedirs("generated_images", exist_ok=True)
        image.save(filepath, format='PNG', optimize=True)
        
        print(f"\n✅ Imagen guardada: {filename}")
        
        generator.cleanup()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

def main():
    """Función principal con menú de opciones"""
    
    print("🎨 GENERADOR DE IMÁGENES CON IA")
    print("=" * 35)
    print("1. Generar ejemplos variados (4 imágenes)")
    print("2. Generar imagen personalizada")
    print("3. Salir")
    print()
    
    try:
        choice = input("Elige una opción (1-3): ").strip()
        
        if choice == "1":
            return generate_example_images()
        elif choice == "2":
            return generate_single_custom()
        elif choice == "3":
            print("👋 ¡Hasta luego!")
            return 0
        else:
            print("❌ Opción no válida")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Operación cancelada por el usuario")
        return 1
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    
    if exit_code == 0:
        input("\nPresiona ENTER para salir...")
    
    sys.exit(exit_code)
