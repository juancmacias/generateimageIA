# api_with_auth.py - API REST con autenticación integrada (mantiene compatibilidad)

import os
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, status, Depends, Header
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

# Cargar variables de entorno primero
load_dotenv()

from .image_generator import ImageGeneratorAI

# Configuración de autenticación
AUTH_ENABLED = os.getenv("AUTH_ENABLED", "false").lower() == "true"

# Importaciones condicionales para autenticación
if AUTH_ENABLED:
    try:
        from .auth import (
            UserCreate, UserLogin, Token, APIKeyCreate,
            register_user, login_user, get_current_user_flexible,
            update_user_usage, supabase
        )
        print("✅ Módulo de autenticación cargado correctamente")
    except Exception as e:
        print(f"⚠️ Error cargando autenticación: {e}")
        print("🔄 Deshabilitando autenticación automáticamente")
        AUTH_ENABLED = False
else:
    print("ℹ️ Autenticación deshabilitada por configuración")

# Modelos básicos que siempre están disponibles (crear aquí los que faltan si es necesario)
if not AUTH_ENABLED:
    # Crear modelos dummy para mantener compatibilidad
    class UserCreate(BaseModel):
        email: str
        password: str
        full_name: Optional[str] = None
    
    class UserLogin(BaseModel):
        email: str
        password: str
    
    class Token(BaseModel):
        access_token: str
        token_type: str = "bearer"
        api_key: Optional[str] = None

# Configuración
BASE_DIR = Path(__file__).parent.parent
GENERATED_IMAGES_DIR = BASE_DIR / "generated_images"
GENERATED_IMAGES_DIR.mkdir(exist_ok=True)

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

# Modelos Pydantic para la API (mantienen compatibilidad)
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
    user_id: Optional[str] = None  # Nuevo: ID del usuario (si está autenticado)
    usage_count: Optional[int] = None  # Nuevo: contador de uso

class SystemStatusResponse(BaseModel):
    """Modelo para la respuesta del estado del sistema"""
    gpu_available: bool
    device_name: str
    memory_info: dict
    model_loaded: bool
    auth_enabled: bool = AUTH_ENABLED  # Nuevo: indica si la autenticación está habilitada

class UserStatsResponse(BaseModel):
    """Respuesta con estadísticas del usuario"""
    user_id: str
    email: str
    usage_count: int
    usage_limit: int
    remaining_uses: int
    created_at: str

# Crear aplicación FastAPI
app = FastAPI(
    title=os.getenv("API_TITLE", "Generador de Imágenes IA API"),
    description="API REST para generar imágenes usando Stable Diffusion con GPU/CPU. Incluye sistema opcional de autenticación.",
    version=os.getenv("API_VERSION", "2.0.0"),
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales para el generador
generator = None
model_loading = False

def initialize_generator():
    """Inicializar el generador de imágenes de forma lazy (sin cambios)"""
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

def generate_filename(prompt: str, user_id: Optional[str] = None) -> str:
    """Generar nombre único para el archivo de imagen"""
    # Limpiar prompt para nombre de archivo
    clean_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
    clean_prompt = clean_prompt.replace(' ', '_').lower()
    
    # Agregar timestamp y UUID para garantizar unicidad
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    
    # Agregar user_id si está disponible (para organización)
    if user_id:
        return f"{clean_prompt}_{user_id[:8]}_{timestamp}_{unique_id}.png"
    else:
        return f"{clean_prompt}_{timestamp}_{unique_id}.png"

async def log_generation(
    user_id: Optional[str],
    request: ImageGenerationRequest,
    filename: str,
    generation_time: float,
    device: str,
    success: bool = True,
    error_message: Optional[str] = None
):
    """Registrar generación en la base de datos (si el usuario está autenticado)"""
    if not user_id or not AUTH_ENABLED:
        return
    
    try:
        # Solo intentar registrar si Supabase está disponible
        if 'supabase' in globals():
            log_data = {
                "user_id": user_id,
                "prompt": request.prompt,
                "width": request.width,
                "height": request.height,
                "num_inference_steps": request.num_inference_steps,
                "guidance_scale": float(request.guidance_scale),
                "generation_time": float(generation_time),
                "filename": filename,
                "device": device,
                "success": success,
                "error_message": error_message
            }
            
            supabase.table("image_generations").insert(log_data).execute()
        
    except Exception as e:
        print(f"⚠️ Error registrando generación: {e}")

# Dependencia opcional de autenticación
async def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Obtener usuario si está autenticado, None si no (mantiene compatibilidad)"""
    if not AUTH_ENABLED or not authorization:
        return None
    
    try:
        if 'get_current_user_flexible' in globals():
            return await get_current_user_flexible(authorization=authorization)
        else:
            return None
    except HTTPException:
        return None
    except Exception as e:
        print(f"⚠️ Error en autenticación opcional: {e}")
        return None

async def get_required_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Requiere autenticación obligatoriamente"""
    if not AUTH_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La autenticación no está habilitada en este servidor"
        )
    
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación. Proporciona un token JWT o API key en el header Authorization"
        )
    
    if 'get_current_user_flexible' in globals():
        return await get_current_user_flexible(authorization=authorization)
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sistema de autenticación no disponible"
        )

# Endpoints existentes (mantienen compatibilidad total)
@app.get("/", response_model=dict)
async def root():
    """Endpoint raíz con información básica de la API"""
    return {
        "message": "API de Generación de Imágenes con IA",
        "version": "2.0.0",
        "status": "active",
        "auth_enabled": AUTH_ENABLED,
        "endpoints": {
            "generate": "/generate - Generar imagen (POST)",
            "status": "/status - Estado del sistema (GET)",
            "image": "/image/{filename} - Descargar imagen (GET)",
            "docs": "/docs - Documentación interactiva (GET)",
            # Nuevos endpoints de autenticación
            "register": "/auth/register - Registrar usuario (POST)" if AUTH_ENABLED else None,
            "login": "/auth/login - Iniciar sesión (POST)" if AUTH_ENABLED else None,
            "profile": "/auth/profile - Perfil del usuario (GET)" if AUTH_ENABLED else None,
        }
    }

@app.get("/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Obtener estado del sistema y GPU (sin cambios + info de auth)"""
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
            model_loaded=generator is not None,
            auth_enabled=AUTH_ENABLED
        )
        
    except Exception as e:
        return SystemStatusResponse(
            gpu_available=False,
            device_name="Error",
            memory_info={"error": str(e)},
            model_loaded=False,
            auth_enabled=AUTH_ENABLED
        )

@app.post("/generate", response_model=ImageGenerationResponse)
async def generate_image(
    request: ImageGenerationRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Generar una imagen basada en el prompt proporcionado
    
    COMPATIBILIDAD TOTAL: Funciona sin autenticación (modo público) y con autenticación.
    Si hay autenticación, registra uso y aplica límites.
    """
    start_time = time.time()
    user_id = user["id"] if user else None
    
    try:
        # Si hay autenticación habilitada y usuario autenticado, verificar límites
        if AUTH_ENABLED and user:
            if user["usage_count"] >= user["usage_limit"]:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Límite de generaciones excedido. Límite: {user['usage_limit']}, Usado: {user['usage_count']}"
                )
        
        # Inicializar generador si no existe
        gen = initialize_generator()
        
        print(f"\n🎨 Nueva solicitud de generación:")
        print(f"   📝 Prompt: {request.prompt}")
        print(f"   📏 Dimensiones: {request.width}x{request.height}")
        print(f"   🎯 Pasos: {request.num_inference_steps}")
        print(f"   🎚️ Guidance: {request.guidance_scale}")
        if user:
            print(f"   👤 Usuario: {user['email']} (Uso: {user['usage_count']}/{user['usage_limit']})")
        else:
            print(f"   👤 Usuario: Anónimo")
        
        # Generar imagen
        image, generation_time = gen.generate(
            prompt=request.prompt,
            width=request.width,
            height=request.height,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale
        )
        
        # Generar nombre único para el archivo
        filename = generate_filename(request.prompt, user_id)
        file_path = GENERATED_IMAGES_DIR / filename
        
        # Guardar imagen
        image.save(file_path, "PNG", quality=95)
        
        # Actualizar contador de uso si hay usuario autenticado
        if AUTH_ENABLED and user and 'update_user_usage' in globals():
            await update_user_usage(user["id"])
        
        # Registrar generación
        await log_generation(
            user_id=user_id,
            request=request,
            filename=filename,
            generation_time=generation_time,
            device=gen.device,
            success=True
        )
        
        # Construir URL de la imagen
        image_url = f"/image/{filename}"
        
        total_time = time.time() - start_time
        
        print(f"✅ Imagen generada exitosamente:")
        print(f"   📁 Archivo: {filename}")
        print(f"   ⏱️ Tiempo total: {total_time:.2f}s")
        print(f"   🔗 URL: {image_url}")
        
        response_data = {
            "success": True,
            "message": "Imagen generada exitosamente",
            "image_url": image_url,
            "filename": filename,
            "generation_time": generation_time,
            "parameters": {
                "prompt": request.prompt,
                "width": request.width,
                "height": request.height,
                "num_inference_steps": request.num_inference_steps,
                "guidance_scale": request.guidance_scale,
                "device": gen.device
            }
        }
        
        # Agregar información del usuario si está autenticado
        if user:
            response_data["user_id"] = user["id"]
            response_data["usage_count"] = user["usage_count"] + 1
        
        return ImageGenerationResponse(**response_data)
        
    except HTTPException:
        # Re-lanzar HTTPException sin modificar
        raise
        
    except Exception as e:
        error_msg = f"Error generando imagen: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Registrar error si hay usuario
        await log_generation(
            user_id=user_id,
            request=request,
            filename="",
            generation_time=time.time() - start_time,
            device=gen.device if 'gen' in locals() else "unknown",
            success=False,
            error_message=str(e)
        )
        
        return ImageGenerationResponse(
            success=False,
            message=error_msg,
            generation_time=time.time() - start_time,
            user_id=user_id,
            usage_count=user["usage_count"] if user else None
        )

# Los siguientes endpoints mantienen compatibilidad total (sin cambios)
@app.get("/image/{filename}")
async def get_image(filename: str):
    """Descargar una imagen generada por nombre de archivo (sin cambios)"""
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
    """Listar todas las imágenes generadas disponibles (sin cambios)"""
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
    """Limpiar recursos del generador para liberar memoria (sin cambios)"""
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

# ENDPOINTS DE AUTENTICACIÓN (solo disponibles si AUTH_ENABLED = True)
if AUTH_ENABLED and 'register_user' in globals():
    @app.post("/auth/register", response_model=Token)
    async def register(user_data: UserCreate):
        """
        Registrar un nuevo usuario
        
        Devuelve token JWT y API key para usar la API
        """
        try:
            user = await register_user(user_data)
            login_data = UserLogin(email=user_data.email, password=user_data.password)
            return await login_user(login_data)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error registrando usuario: {str(e)}"
            )

    @app.post("/auth/login", response_model=Token)
    async def login(user_data: UserLogin):
        """
        Iniciar sesión con email y contraseña
        
        Devuelve token JWT y nueva API key
        """
        return await login_user(user_data)

    @app.get("/auth/profile", response_model=UserStatsResponse)
    async def get_profile(user: Dict[str, Any] = Depends(get_required_user)):
        """
        Obtener perfil y estadísticas del usuario actual
        
        Requiere autenticación con JWT token o API key
        """
        return UserStatsResponse(
            user_id=user["id"],
            email=user["email"],
            usage_count=user["usage_count"],
            usage_limit=user["usage_limit"],
            remaining_uses=max(0, user["usage_limit"] - user["usage_count"]),
            created_at=user["created_at"]
        )

    @app.get("/auth/stats")
    async def get_user_detailed_stats(user: Dict[str, Any] = Depends(get_required_user)):
        """
        Obtener estadísticas detalladas del usuario
        """
        try:
            # Obtener estadísticas de generaciones
            stats = supabase.table("image_generations").select("*").eq("user_id", user["id"]).execute()
            
            generations = stats.data
            total_generations = len(generations)
            successful = len([g for g in generations if g["success"]])
            failed = total_generations - successful
            
            avg_time = 0
            if successful > 0:
                times = [g["generation_time"] for g in generations if g["success"] and g["generation_time"]]
                avg_time = sum(times) / len(times) if times else 0
            
            return {
                "user_info": {
                    "id": user["id"],
                    "email": user["email"],
                    "full_name": user.get("full_name"),
                    "created_at": user["created_at"]
                },
                "usage": {
                    "usage_count": user["usage_count"],
                    "usage_limit": user["usage_limit"],
                    "remaining": max(0, user["usage_limit"] - user["usage_count"])
                },
                "statistics": {
                    "total_generations": total_generations,
                    "successful_generations": successful,
                    "failed_generations": failed,
                    "success_rate": (successful / total_generations * 100) if total_generations > 0 else 0,
                    "average_generation_time": round(avg_time, 2)
                }
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error obteniendo estadísticas: {str(e)}"
            )
else:
    # Endpoints dummy cuando la autenticación está deshabilitada
    @app.post("/auth/register")
    async def register_disabled():
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="La autenticación no está habilitada en este servidor"
        )
    
    @app.post("/auth/login")
    async def login_disabled():
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="La autenticación no está habilitada en este servidor"
        )
    
    @app.get("/auth/profile")
    async def profile_disabled():
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="La autenticación no está habilitada en este servidor"
        )
    
    @app.get("/auth/stats")
    async def stats_disabled():
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="La autenticación no está habilitada en este servidor"
        )

# Eventos de la aplicación (sin cambios + log de auth)
@app.on_event("startup")
async def startup_event():
    """Evento ejecutado al iniciar la aplicación"""
    print("\n🚀 INICIANDO API DE GENERACIÓN DE IMÁGENES v2.0")
    print("=" * 60)
    print(f"📁 Directorio de imágenes: {GENERATED_IMAGES_DIR}")
    print(f"🔐 Autenticación: {'Habilitada' if AUTH_ENABLED else 'Deshabilitada'}")
    print("=" * 60)

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
    print(f"🔐 Autenticación: {'Habilitada' if AUTH_ENABLED else 'Deshabilitada'}")
    
    uvicorn.run(
        "app.api_with_auth:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    run_api(reload=True)
