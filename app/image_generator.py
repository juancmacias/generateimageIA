# image_generator.py - Generador de imágenes con Stable Diffusion

import os
import warnings
import time
from PIL import Image
import numpy as np
import torch

# Suprimir advertencias molestas
warnings.filterwarnings("ignore", category=UserWarning)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

try:
    from diffusers import StableDiffusionPipeline
    DIFFUSERS_AVAILABLE = True
    print("✅ Diffusers importado correctamente")
except ImportError as e:
    DIFFUSERS_AVAILABLE = False
    print(f"❌ Error importando diffusers: {e}")

class ImageGeneratorAI:
    """Generador de imágenes con Stable Diffusion optimizado para CPU y GPU"""
    
    def __init__(self):
        """Inicializar el generador"""
        if not DIFFUSERS_AVAILABLE:
            raise ImportError("Diffusers no está disponible")
        
        # Detectar y mostrar información del hardware
        self._detect_hardware()
        
        # Configurar modelo básico
        self._setup_model()
    
    def _detect_hardware(self):
        """Detectar y mostrar información detallada del hardware"""
        print("\n🔍 DETECTANDO HARDWARE DISPONIBLE")
        print("=" * 40)
        
        # Detectar dispositivo
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        if self.device == "cuda":
            # Información detallada de GPU
            gpu_count = torch.cuda.device_count()
            current_gpu = torch.cuda.current_device()
            gpu_name = torch.cuda.get_device_name(current_gpu)
            gpu_memory = torch.cuda.get_device_properties(current_gpu).total_memory
            gpu_memory_gb = gpu_memory / (1024**3)
            
            print(f"🚀 MODO: GPU ACELERADO")
            print(f"   💻 GPUs disponibles: {gpu_count}")
            print(f"   🎮 GPU actual: {gpu_name}")
            print(f"   🧠 VRAM total: {gpu_memory_gb:.1f} GB")
            
            # Memoria GPU disponible
            try:
                gpu_memory_allocated = torch.cuda.memory_allocated(current_gpu) / (1024**3)
                gpu_memory_free = gpu_memory_gb - gpu_memory_allocated
                print(f"   📊 VRAM libre: {gpu_memory_free:.1f} GB")
            except:
                print(f"   📊 VRAM libre: Calculando...")
                
            print(f"   ⚡ Velocidad esperada: RÁPIDA (~30-60s por imagen)")
            
        else:
            # Información de CPU
            print(f"🐌 MODO: CPU")
            print(f"   💻 Dispositivo: Procesador central")
            print(f"   🧠 Usando RAM del sistema")
            print(f"   ⏰ Velocidad esperada: LENTA (~5-10 min por imagen)")
            print(f"   💡 Tip: Para mayor velocidad, considera usar GPU CUDA")
        
        print(f"🔧 Dispositivo seleccionado: {self.device.upper()}")
        print("=" * 40)
    
    def _setup_model(self):
        """Configurar el modelo de Stable Diffusion con información específica del dispositivo"""
        try:
            model_id = "runwayml/stable-diffusion-v1-5"
            
            print(f"\n📦 CONFIGURANDO MODELO STABLE DIFFUSION")
            print(f"   🏷️  Modelo: {model_id}")
            print(f"   🎯 Dispositivo objetivo: {self.device.upper()}")
            print("   ⏳ Descargando/cargando modelo (primera vez puede ser lenta)...")
            
            # Configuración específica por dispositivo
            if self.device == "cuda":
                print("   🚀 Aplicando optimizaciones GPU...")
                torch_dtype = torch.float16
                print("   📊 Precisión: float16 (ahorro de memoria)")
            else:
                print("   🐌 Configurando para CPU...")
                torch_dtype = torch.float32
                print("   📊 Precisión: float32 (compatibilidad CPU)")
            
            # Configuración básica sin xformers
            self.pipe = StableDiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=torch_dtype,
                use_safetensors=True,
                safety_checker=None,
                requires_safety_checker=False
            )
            
            print("   🔄 Moviendo modelo al dispositivo...")
            self.pipe = self.pipe.to(self.device)
            
            # Optimizaciones específicas por dispositivo
            print("   ⚙️  Aplicando optimizaciones...")
            if self.device == "cuda":
                self.pipe.enable_attention_slicing()
                print("   ✅ Attention slicing activado (ahorro VRAM)")
                
                # Mostrar uso de memoria después de cargar
                try:
                    memory_used = torch.cuda.memory_allocated() / (1024**3)
                    print(f"   � VRAM usada por el modelo: {memory_used:.1f} GB")
                except:
                    pass
                    
                print("   🚀 Optimizaciones GPU completadas")
            else:
                print("   � Modo CPU configurado")
                print("   💡 El modelo usará RAM del sistema")
            
            print("✅ MODELO LISTO PARA GENERAR IMÁGENES!")
            print("=" * 40)
            
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            raise e
    
    def generate(self, prompt, width=512, height=512, num_inference_steps=20, guidance_scale=7.5):
        """Generar imagen con información detallada del proceso"""
        if not self.pipe:
            raise RuntimeError("El modelo no está inicializado")
        
        start_time = time.time()
        
        try:
            print(f"\n🎨 INICIANDO GENERACIÓN DE IMAGEN")
            print("=" * 40)
            print(f"   📝 Prompt: {prompt[:60]}{'...' if len(prompt) > 60 else ''}")
            print(f"   📏 Resolución: {width}x{height} pixels")
            print(f"   🎯 Pasos de inferencia: {num_inference_steps}")
            print(f"   🎚️  Guidance scale: {guidance_scale}")
            print(f"   💻 Dispositivo: {self.device.upper()}")
            
            # Estimación de tiempo
            if self.device == "cuda":
                estimated_time = num_inference_steps * 2  # ~2s per step on GPU
                print(f"   ⏱️  Tiempo estimado: ~{estimated_time}s")
            else:
                estimated_time = num_inference_steps * 15  # ~15s per step on CPU
                estimated_minutes = estimated_time // 60
                estimated_seconds = estimated_time % 60
                print(f"   ⏱️  Tiempo estimado: ~{estimated_minutes}m {estimated_seconds}s")
            
            print("   🚀 Iniciando generación...")
            print("=" * 40)
            
            # Configurar generador con seed fijo para reproducibilidad
            generator = torch.Generator(device=self.device).manual_seed(42) if self.device == "cuda" else torch.Generator().manual_seed(42)
            
            # Mostrar información de memoria antes de generar
            if self.device == "cuda":
                try:
                    memory_before = torch.cuda.memory_allocated() / (1024**3)
                    print(f"   📊 VRAM antes: {memory_before:.2f} GB")
                except:
                    pass
            
            # Generar imagen
            with torch.inference_mode():
                result = self.pipe(
                    prompt=prompt,
                    width=width,
                    height=height,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    generator=generator,
                    negative_prompt="blurry, low quality, distorted, ugly, bad anatomy, deformed"
                )
            
            image = result.images[0]
            generation_time = time.time() - start_time
            
            # Mostrar estadísticas finales
            print("\n🎉 GENERACIÓN COMPLETADA!")
            print("=" * 40)
            print(f"   ⏱️  Tiempo real: {generation_time:.2f}s")
            
            if self.device == "cuda":
                try:
                    memory_after = torch.cuda.memory_allocated() / (1024**3)
                    print(f"   📊 VRAM final: {memory_after:.2f} GB")
                    # Calcular velocidad
                    steps_per_second = num_inference_steps / generation_time
                    print(f"   ⚡ Velocidad: {steps_per_second:.1f} pasos/segundo")
                except:
                    pass
            else:
                steps_per_second = num_inference_steps / generation_time
                print(f"   🐌 Velocidad CPU: {steps_per_second:.2f} pasos/segundo")
            
            print(f"   💻 Procesado en: {self.device.upper()}")
            print("=" * 40)
            
            return image, generation_time
            
        except torch.cuda.OutOfMemoryError:
            print("\n⚠️  ERROR DE MEMORIA GPU")
            print("   📉 VRAM insuficiente, reduciendo resolución...")
            torch.cuda.empty_cache()
            new_width, new_height = width//2, height//2
            new_steps = max(num_inference_steps//2, 10)
            print(f"   🔄 Reintentando: {new_width}x{new_height}, {new_steps} pasos")
            return self.generate(prompt, new_width, new_height, new_steps)
            
        except Exception as e:
            print(f"\n❌ ERROR DURANTE LA GENERACIÓN:")
            print(f"   {e}")
            print(f"   💻 Dispositivo: {self.device}")
            raise e
    
    def cleanup(self):
        """Limpiar memoria con información detallada"""
        try:
            print("\n🧹 LIBERANDO RECURSOS...")
            
            if hasattr(self, 'pipe') and self.pipe:
                del self.pipe
                print("   ✅ Modelo eliminado de memoria")
                
            if self.device == "cuda" and torch.cuda.is_available():
                memory_before = torch.cuda.memory_allocated() / (1024**3)
                torch.cuda.empty_cache()
                memory_after = torch.cuda.memory_allocated() / (1024**3)
                freed = memory_before - memory_after
                print(f"   📊 VRAM liberada: {freed:.2f} GB")
                print(f"   📊 VRAM actual: {memory_after:.2f} GB")
            else:
                print("   💭 Memoria RAM del sistema liberada")
                
            print("✅ Limpieza completada")
            
        except Exception as e:
            print(f"⚠️ Error durante limpieza: {e}")
    
    def get_device_info(self):
        """Obtener información detallada del dispositivo"""
        info = {
            'device': self.device,
            'device_name': 'CPU',
            'memory_total': 'N/A',
            'memory_available': 'N/A',
            'cuda_available': torch.cuda.is_available()
        }
        
        if self.device == "cuda":
            info['device_name'] = torch.cuda.get_device_name()
            info['memory_total'] = f"{torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB"
            try:
                memory_allocated = torch.cuda.memory_allocated() / (1024**3)
                memory_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                info['memory_available'] = f"{memory_total - memory_allocated:.1f} GB"
            except:
                info['memory_available'] = "Calculando..."
        
        return info
    
    def __del__(self):
        try:
            self.cleanup()
        except:
            pass
