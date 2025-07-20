#!/usr/bin/env python3
"""
API simplificada de generación de imágenes - Sin autenticación
Solo para pruebas iniciales
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any
import time

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports básicos
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Imports del generador
try:
    from app.image_generator import ImageGeneratorAI
    print("✅ ImageGeneratorAI importado correctamente")
except ImportError as e:
    print(f"❌ Error importando ImageGeneratorAI: {e}")
    sys.exit(1)

# Configuración de la aplicación
app = FastAPI(
    title="🎨 Generador de Imágenes IA - API Simple",
    description="API simplificada para generación de imágenes con Stable Diffusion",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancia global del generador
generator = None

# Modelos Pydantic
class ImageRequest(BaseModel):
    prompt: str = Field(..., description="Descripción de la imagen a generar", min_length=1)
    width: int = Field(default=512, ge=256, le=1024, description="Ancho de la imagen")
    height: int = Field(default=512, ge=256, le=1024, description="Alto de la imagen")
    num_inference_steps: int = Field(default=20, ge=10, le=50, description="Número de pasos de inferencia")

class ImageResponse(BaseModel):
    image_url: str
    timestamp: str
    prompt: str
    config: Dict[str, Any]
    generation_time: float

@app.on_event("startup")
async def startup_event():
    """Inicializar el generador de imágenes al iniciar la API"""
    global generator
    try:
        print("🚀 Inicializando generador de imágenes...")
        generator = ImageGeneratorAI()
        print("✅ Generador inicializado correctamente")
    except Exception as e:
        print(f"❌ Error inicializando generador: {e}")
        raise

@app.get("/")
async def root():
    """Endpoint raíz con información básica"""
    return {
        "message": "🎨 API de Generación de Imágenes IA",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Verificar el estado de la API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "generator_loaded": generator is not None,
        "cuda_available": True  # Asumimos que CUDA está disponible
    }

@app.post("/generate-image", response_model=ImageResponse)
async def generate_image(request: ImageRequest):
    """Generar una imagen basada en el prompt proporcionado"""
    if generator is None:
        raise HTTPException(status_code=503, detail="Generador no inicializado")
    
    try:
        start_time = time.time()
        
        # Configuración para la generación
        config = {
            "width": request.width,
            "height": request.height,
            "num_inference_steps": request.num_inference_steps,
            "guidance_scale": 7.5,
            "device": "cuda" if generator.device == "cuda" else "cpu"
        }
        
        # Generar la imagen
        image, generation_time = generator.generate(
            prompt=request.prompt,
            width=request.width,
            height=request.height,
            num_inference_steps=request.num_inference_steps
        )
        
        # Crear directorio de imágenes si no existe
        images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "generated_images")
        os.makedirs(images_dir, exist_ok=True)
        
        # Generar nombre de archivo único
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"imagen_{timestamp_str}.png"
        filepath = os.path.join(images_dir, filename)
        
        # Guardar la imagen
        image.save(filepath)
        
        # Crear URL relativa
        image_url = f"generated_images/{filename}"
        
        return ImageResponse(
            image_url=image_url,
            timestamp=datetime.now().isoformat(),
            prompt=request.prompt,
            config=config,
            generation_time=generation_time
        )
        
    except Exception as e:
        print(f"❌ Error generando imagen: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando imagen: {str(e)}")

@app.get("/info")
async def get_info():
    """Obtener información sobre la configuración actual"""
    if generator is None:
        return {"error": "Generador no inicializado"}
    
    return {
        "model_name": getattr(generator, 'model_name', 'stable-diffusion'),
        "device": generator.device,
        "memory_usage": generator.get_memory_info() if hasattr(generator, 'get_memory_info') else {},
        "supported_dimensions": {
            "min": {"width": 256, "height": 256},
            "max": {"width": 1024, "height": 1024},
            "recommended": {"width": 512, "height": 512}
        }
    }

if __name__ == "__main__":
    print("🎨 INICIANDO API SIMPLE DE GENERACIÓN DE IMÁGENES")
    print("=" * 60)
    print(f"🏠 Host: 127.0.0.1")
    print(f"🚪 Puerto: 8001")
    print(f"📖 Documentación: http://127.0.0.1:8001/docs")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        log_level="info"
    )
