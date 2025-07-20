# api.py - API REST para generación de imágenes con FastAPI

import os
import time
import uuid
from datetime import datetime
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from .image_generator import ImageGeneratorAI

# Configuración
BASE_DIR = Path(__file__).parent.parent
GENERATED_IMAGES_DIR = BASE_DIR / "generated_images"
GENERATED_IMAGES_DIR.mkdir(exist_ok=True)

# Modelos Pydantic para la API
class ImageGenerationRequest(BaseModel):
    """Modelo para la solicitud de generación de imagen"""
    prompt: str = Field(..., min_length=1, max_length=1000, description="Descripción de la imagen a generar")
    width: int = Field(default=512, ge=128, le=1024, description="Ancho de la imagen en píxeles")
    height: int = Field(default=512, ge=128, le=1024, description="Alto de la imagen en píxeles")
    num_inference_steps: int = Field(default=20, ge=5, le=100, description="Número de pasos de inferencia")
    guidance_scale: float = Field(default=7.5, ge=1.0, le=20.0, description="Escala de guidance")

class ImageGenerationResponse(BaseModel):
    """Modelo para la respuesta de generación de imagen"""
    success: bool
    message: str
    image_url: Optional[str] = None
    filename: Optional[str] = None
    generation_time: Optional[float] = None
    parameters: Optional[dict] = None

class SystemStatusResponse(BaseModel):
    """Modelo para la respuesta del estado del sistema"""
    gpu_available: bool
    device_name: str
    memory_info: dict
    model_loaded: bool

# Crear aplicación FastAPI
app = FastAPI(
    title="Generador de Imágenes IA API",
    description="API REST para generar imágenes usando Stable Diffusion con GPU/CPU",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para permitir requests desde frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales para el generador
generator = None
model_loading = False

def initialize_generator():
    """Inicializar el generador de imágenes de forma lazy"""
    global generator, model_loading
    
    if generator is not None:
        return generator
    
    if model_loading:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El modelo se está cargando, por favor espera un momento"
        )
    
    try:
        model_loading = True
        print("🚀 Inicializando generador de imágenes...")
        generator = ImageGeneratorAI()
        print("✅ Generador inicializado correctamente")
        return generator
        
    except Exception as e:
        print(f"❌ Error inicializando generador: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inicializando el generador: {str(e)}"
        )
    finally:
        model_loading = False

def generate_filename(prompt: str) -> str:
    """Generar nombre único para el archivo de imagen"""
    # Limpiar prompt para nombre de archivo
    clean_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
    clean_prompt = clean_prompt.replace(' ', '_').lower()
    
    # Agregar timestamp y UUID para garantizar unicidad
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    
    return f"{clean_prompt}_{timestamp}_{unique_id}.png"

@app.get("/", response_model=dict)
async def root():
    """Endpoint raíz con información básica de la API"""
    return {
        "message": "API de Generación de Imágenes con IA",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "generate": "/generate - Generar imagen (POST)",
            "status": "/status - Estado del sistema (GET)",
            "image": "/image/{filename} - Descargar imagen (GET)",
            "docs": "/docs - Documentación interactiva (GET)"
        }
    }

@app.get("/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Obtener estado del sistema y GPU"""
    try:
        # Intentar inicializar generator si no existe
        gen = initialize_generator() if generator is None else generator
        device_info = gen.get_device_info()
        
        return SystemStatusResponse(
            gpu_available=device_info["cuda_available"],
            device_name=device_info["device_name"],
            memory_info={
                "total": device_info["memory_total"],
                "available": device_info["memory_available"]
            },
            model_loaded=generator is not None
        )
        
    except Exception as e:
        return SystemStatusResponse(
            gpu_available=False,
            device_name="Error",
            memory_info={"error": str(e)},
            model_loaded=False
        )

@app.post("/generate", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest):
    """
    Generar una imagen basada en el prompt proporcionado
    
    - **prompt**: Descripción de la imagen a generar
    - **width**: Ancho en píxeles (128-1024)
    - **height**: Alto en píxeles (128-1024)
    - **num_inference_steps**: Pasos de inferencia (5-100)
    - **guidance_scale**: Escala de guidance (1.0-20.0)
    """
    start_time = time.time()
    
    try:
        # Inicializar generador si no existe
        gen = initialize_generator()
        
        print(f"\n🎨 Nueva solicitud de generación:")
        print(f"   📝 Prompt: {request.prompt}")
        print(f"   📏 Dimensiones: {request.width}x{request.height}")
        print(f"   🎯 Pasos: {request.num_inference_steps}")
        print(f"   🎚️ Guidance: {request.guidance_scale}")
        
        # Generar imagen
        image, generation_time = gen.generate(
            prompt=request.prompt,
            width=request.width,
            height=request.height,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale
        )
        
        # Generar nombre único para el archivo
        filename = generate_filename(request.prompt)
        file_path = GENERATED_IMAGES_DIR / filename
        
        # Guardar imagen
        image.save(file_path, "PNG", quality=95)
        
        # Construir URL de la imagen
        image_url = f"/image/{filename}"
        
        total_time = time.time() - start_time
        
        print(f"✅ Imagen generada exitosamente:")
        print(f"   📁 Archivo: {filename}")
        print(f"   ⏱️ Tiempo total: {total_time:.2f}s")
        print(f"   🔗 URL: {image_url}")
        
        return ImageGenerationResponse(
            success=True,
            message="Imagen generada exitosamente",
            image_url=image_url,
            filename=filename,
            generation_time=generation_time,
            parameters={
                "prompt": request.prompt,
                "width": request.width,
                "height": request.height,
                "num_inference_steps": request.num_inference_steps,
                "guidance_scale": request.guidance_scale,
                "device": gen.device
            }
        )
        
    except HTTPException:
        # Re-lanzar HTTPException sin modificar
        raise
        
    except Exception as e:
        error_msg = f"Error generando imagen: {str(e)}"
        print(f"❌ {error_msg}")
        
        return ImageGenerationResponse(
            success=False,
            message=error_msg,
            generation_time=time.time() - start_time
        )

@app.get("/image/{filename}")
async def get_image(filename: str):
    """
    Descargar una imagen generada por nombre de archivo
    
    - **filename**: Nombre del archivo de imagen (incluir extensión .png)
    """
    file_path = GENERATED_IMAGES_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imagen '{filename}' no encontrada"
        )
    
    if not file_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de archivo no válido"
        )
    
    return FileResponse(
        path=file_path,
        media_type="image/png",
        filename=filename
    )

@app.get("/images/list")
async def list_images():
    """Listar todas las imágenes generadas disponibles"""
    try:
        images = []
        for image_file in GENERATED_IMAGES_DIR.glob("*.png"):
            stat = image_file.stat()
            images.append({
                "filename": image_file.name,
                "url": f"/image/{image_file.name}",
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        # Ordenar por fecha de creación (más reciente primero)
        images.sort(key=lambda x: x["created"], reverse=True)
        
        return {
            "success": True,
            "count": len(images),
            "images": images
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listando imágenes: {str(e)}"
        )

@app.delete("/cleanup")
async def cleanup_resources():
    """Limpiar recursos del generador para liberar memoria"""
    global generator
    
    try:
        if generator is not None:
            generator.cleanup()
            generator = None
            
        return {
            "success": True,
            "message": "Recursos liberados exitosamente"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error limpiando recursos: {str(e)}"
        }

@app.on_event("startup")
async def startup_event():
    """Evento ejecutado al iniciar la aplicación"""
    print("\n🚀 INICIANDO API DE GENERACIÓN DE IMÁGENES")
    print("=" * 50)
    print(f"📁 Directorio de imágenes: {GENERATED_IMAGES_DIR}")
    print(f"🌐 Documentación disponible en: http://localhost:8000/docs")
    print("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    """Evento ejecutado al cerrar la aplicación"""
    global generator
    
    print("\n🛑 CERRANDO API...")
    
    if generator is not None:
        try:
            generator.cleanup()
            print("✅ Recursos liberados")
        except:
            print("⚠️ Error liberando recursos")
    
    print("👋 API cerrada")

def run_api(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Función para ejecutar la API"""
    print(f"\n🌐 Iniciando servidor API en http://{host}:{port}")
    print(f"📖 Documentación en http://{host}:{port}/docs")
    
    uvicorn.run(
        "app.api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    run_api(reload=True)
