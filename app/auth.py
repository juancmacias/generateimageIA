# auth.py - Sistema de autenticación con Supabase

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from supabase import create_client, Client
from pydantic import BaseModel
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Configuración JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Configuración Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://nrkmnoivuebjjygkjyhm.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

# Cliente Supabase usando service_role key si está disponible
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY)

# Modelos Pydantic
class UserCreate(BaseModel):
    """Modelo para crear un usuario"""
    email: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    """Modelo para login"""
    email: str
    password: str

class UserResponse(BaseModel):
    """Respuesta con información del usuario"""
    id: str
    email: str
    full_name: Optional[str]
    api_key: str
    is_active: bool
    created_at: str
    usage_count: int
    usage_limit: int

class Token(BaseModel):
    """Token de acceso"""
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class APIKeyCreate(BaseModel):
    """Modelo para crear API key"""
    name: Optional[str] = "Default API Key"

# Funciones de utilidad
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Obtener hash de contraseña"""
    return pwd_context.hash(password)

def generate_api_key() -> str:
    """Generar API key única"""
    # Generar clave de 32 bytes y convertir a hex
    key = secrets.token_hex(32)
    # Agregar prefijo para identificar fácilmente
    return f"sk-img-{key}"

def hash_api_key(api_key: str) -> str:
    """Hash de API key para almacenamiento seguro"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crear token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verificar token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return payload
    except JWTError:
        return None

# Funciones de base de datos
async def create_user_in_db(email: str, password: str, full_name: Optional[str] = None) -> Dict[str, Any]:
    """Crear usuario en Supabase"""
    try:
        # Hash de la contraseña
        hashed_password = get_password_hash(password)
        
        # Generar API key
        api_key = generate_api_key()
        api_key_hash = hash_api_key(api_key)
        
        # Crear usuario en Supabase
        user_data = {
            "email": email,
            "password_hash": hashed_password,
            "full_name": full_name,
            "api_key_hash": api_key_hash,
            "is_active": True,
            "usage_count": 0,
            "usage_limit": 100,  # 100 generaciones por defecto
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("users").insert(user_data).execute()
        
        if result.data:
            user = result.data[0]
            # Devolver datos del usuario con API key sin hash
            user["api_key"] = api_key
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error creando usuario"
            )
            
    except Exception as e:
        logger.error(f"Error creando usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Obtener usuario por email"""
    try:
        result = supabase.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error obteniendo usuario: {e}")
        return None

async def get_user_by_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """Obtener usuario por API key"""
    try:
        api_key_hash = hash_api_key(api_key)
        result = supabase.table("users").select("*").eq("api_key_hash", api_key_hash).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error obteniendo usuario por API key: {e}")
        return None

async def update_user_usage(user_id: str) -> bool:
    """Incrementar contador de uso del usuario"""
    try:
        # Obtener usuario actual
        user_result = supabase.table("users").select("usage_count").eq("id", user_id).execute()
        if not user_result.data:
            return False
            
        current_usage = user_result.data[0]["usage_count"]
        new_usage = current_usage + 1
        
        # Actualizar contador
        result = supabase.table("users").update({
            "usage_count": new_usage,
            "last_used": datetime.utcnow().isoformat()
        }).eq("id", user_id).execute()
        
        return len(result.data) > 0
        
    except Exception as e:
        logger.error(f"Error actualizando uso del usuario: {e}")
        return False

# Funciones de autenticación
async def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Autenticar usuario"""
    user = await get_user_by_email(email)
    if not user:
        return None
    
    if not verify_password(password, user["password_hash"]):
        return None
    
    return user

async def register_user(user_data: UserCreate) -> Dict[str, Any]:
    """Registrar nuevo usuario"""
    # Verificar si el usuario ya existe
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Crear usuario
    return await create_user_in_db(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name
    )

async def login_user(user_data: UserLogin) -> Token:
    """Login de usuario"""
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"], "email": user["email"]},
        expires_delta=access_token_expires
    )
    
    # Generar nueva API key para la respuesta
    api_key = generate_api_key()
    api_key_hash = hash_api_key(api_key)
    
    # Actualizar API key en la base de datos
    supabase.table("users").update({
        "api_key_hash": api_key_hash,
        "last_login": datetime.utcnow().isoformat()
    }).eq("id", user["id"]).execute()
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user.get("full_name"),
            api_key=api_key,  # API key sin hash
            is_active=user["is_active"],
            created_at=user["created_at"],
            usage_count=user["usage_count"],
            usage_limit=user["usage_limit"]
        )
    )

# Dependencias de FastAPI
async def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Obtener usuario actual desde token JWT"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Obtener usuario desde base de datos
    try:
        result = supabase.table("users").select("*").eq("id", user_id).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado"
            )
        
        user = result.data[0]
        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario inactivo"
            )
        
        return user
        
    except Exception as e:
        logger.error(f"Error obteniendo usuario actual: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

async def get_current_user_from_api_key(api_key: str) -> Dict[str, Any]:
    """Obtener usuario actual desde API key"""
    user = await get_user_by_api_key(api_key)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida"
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    # Verificar límite de uso
    if user["usage_count"] >= user["usage_limit"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Límite de uso excedido. Límite: {user['usage_limit']}, Usado: {user['usage_count']}"
        )
    
    return user

async def verify_api_key_header(authorization: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Verificar API key desde header Authorization"""
    if not authorization:
        return None
    
    if not authorization.startswith("Bearer "):
        return None
    
    api_key = authorization.replace("Bearer ", "")
    
    # Verificar si es API key (formato: sk-img-...)
    if api_key.startswith("sk-img-"):
        try:
            return await get_current_user_from_api_key(api_key)
        except HTTPException:
            return None
    
    return None

# Función combinada para autenticación flexible
async def get_current_user_flexible(
    authorization: Optional[str] = None,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Autenticación flexible: primero intenta API key, luego JWT token
    """
    # Intentar autenticación con API key primero
    if authorization:
        user = await verify_api_key_header(authorization)
        if user:
            return user
    
    # Intentar autenticación con JWT token
    if credentials:
        try:
            return await get_current_user_from_token(credentials)
        except HTTPException:
            pass
    
    # Si ninguna autenticación funciona
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Se requiere autenticación válida (API key o token JWT)",
        headers={"WWW-Authenticate": "Bearer"},
    )
