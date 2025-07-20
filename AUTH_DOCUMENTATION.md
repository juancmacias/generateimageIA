# 🔐 Sistema de Autenticación - Documentación

## 📋 Resumen

El sistema de autenticación con Supabase permite registrar usuarios, manejar API keys, aplicar límites de uso y mantener un registro completo de todas las generaciones. Es completamente **compatible con la API anterior**.

## 🚀 Configuración Inicial

### 1. Configurar Supabase

#### Crear proyecto en Supabase:
1. Ve a [supabase.com](https://supabase.com)
2. Crea una nueva cuenta o inicia sesión
3. Crea un nuevo proyecto
4. Obtén la URL y las claves de tu proyecto

#### Configurar base de datos:
1. Ve a SQL Editor en Supabase
2. Ejecuta el script `database/setup_database.sql`
3. Esto creará todas las tablas necesarias

### 2. Configurar Variables de Entorno

Edita el archivo `.env` con tus datos reales:

```env
# Configuración de Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=tu_supabase_service_role_key

# Clave secreta JWT (cambiar en producción)
JWT_SECRET_KEY=una_clave_muy_segura_de_al_menos_32_caracteres

# Habilitar autenticación
AUTH_ENABLED=true
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

## 🎮 Uso de la API

### Modo Compatible (Sin Autenticación)

La API funciona **exactamente igual** que antes si deshabilitas la autenticación:

```bash
# Ejecutar sin autenticación
python run_api_with_auth.py --no-auth
```

Todos los endpoints existentes funcionan igual:
- `POST /generate` - Generar imagen
- `GET /status` - Estado del sistema  
- `GET /image/{filename}` - Descargar imagen

### Modo con Autenticación

```bash
# Ejecutar con autenticación
python run_api_with_auth.py
```

## 🔐 Endpoints de Autenticación

### POST /auth/register
Registrar un nuevo usuario.

**Request:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "contraseña_segura",
  "full_name": "Nombre Completo (opcional)"
}
```

**Response:**
```json
{
  "access_token": "jwt_token_aqui",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "uuid_del_usuario",
    "email": "usuario@ejemplo.com",
    "full_name": "Nombre Completo",
    "api_key": "sk-img-api_key_completa",
    "is_active": true,
    "created_at": "2025-07-19T12:00:00Z",
    "usage_count": 0,
    "usage_limit": 100
  }
}
```

### POST /auth/login
Iniciar sesión (genera nueva API key).

**Request:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "contraseña_segura"
}
```

**Response:** (igual que register)

### GET /auth/profile
Obtener perfil del usuario (requiere autenticación).

**Headers:**
```
Authorization: Bearer tu_jwt_token
# O
Authorization: Bearer tu_api_key
```

**Response:**
```json
{
  "user_id": "uuid_del_usuario",
  "email": "usuario@ejemplo.com", 
  "usage_count": 5,
  "usage_limit": 100,
  "remaining_uses": 95,
  "created_at": "2025-07-19T12:00:00Z"
}
```

## 🎨 Generar Imágenes con Autenticación

### Opción 1: Con API Key (Recomendado)

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Authorization: Bearer sk-img-tu_api_key_aqui" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "beautiful landscape with mountains",
    "width": 512,
    "height": 512
  }'
```

### Opción 2: Con JWT Token

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Authorization: Bearer tu_jwt_token_aqui" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "beautiful landscape with mountains",
    "width": 512,
    "height": 512
  }'
```

### Opción 3: Sin Autenticación (si AUTH_ENABLED=false)

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "beautiful landscape with mountains",
    "width": 512,
    "height": 512
  }'
```

## 🐍 Cliente Python con Autenticación

### Ejemplo básico:

```python
import requests

# 1. Registrar usuario
register_data = {
    "email": "mi@email.com",
    "password": "mi_contraseña",
    "full_name": "Mi Nombre"
}

response = requests.post("http://localhost:8000/auth/register", json=register_data)
result = response.json()

api_key = result["user"]["api_key"]
print(f"Tu API key: {api_key}")

# 2. Generar imagen con API key
headers = {"Authorization": f"Bearer {api_key}"}
image_data = {
    "prompt": "a beautiful cat in space",
    "width": 512,
    "height": 512
}

response = requests.post("http://localhost:8000/generate", json=image_data, headers=headers)
result = response.json()

print(f"Imagen generada: {result['image_url']}")
print(f"Uso actualizado: {result['usage_count']}")
```

### Cliente completo con manejo de errores:

```python
python auth_client_example.py
```

## 🌍 Frontend JavaScript/React

### Ejemplo con fetch:

```javascript
class ImageGeneratorAuth {
  constructor() {
    this.apiKey = localStorage.getItem('api_key');
    this.baseURL = 'http://localhost:8000';
  }

  async register(email, password, fullName) {
    const response = await fetch(`${this.baseURL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, full_name: fullName })
    });
    
    const result = await response.json();
    if (result.user) {
      this.apiKey = result.user.api_key;
      localStorage.setItem('api_key', this.apiKey);
    }
    return result;
  }

  async generateImage(prompt, options = {}) {
    if (!this.apiKey) throw new Error('No API key. Please login first.');
    
    const response = await fetch(`${this.baseURL}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify({ prompt, ...options })
    });
    
    return response.json();
  }

  async getProfile() {
    const response = await fetch(`${this.baseURL}/auth/profile`, {
      headers: { 'Authorization': `Bearer ${this.apiKey}` }
    });
    return response.json();
  }
}

// Uso
const generator = new ImageGeneratorAuth();

// Registrar usuario
await generator.register('mi@email.com', 'contraseña', 'Mi Nombre');

// Generar imagen
const result = await generator.generateImage('beautiful sunset over mountains');
console.log('Imagen:', result.image_url);

// Ver perfil
const profile = await generator.getProfile();
console.log('Usos restantes:', profile.remaining_uses);
```

## 📊 Límites y Uso

### Límites por defecto:
- **Usuarios nuevos**: 100 generaciones
- **Rate limiting**: 10 requests por minuto (configurable)

### Verificar uso:
```bash
# Ver perfil
curl -H "Authorization: Bearer tu_api_key" \
  http://localhost:8000/auth/profile

# Ver estadísticas detalladas
curl -H "Authorization: Bearer tu_api_key" \
  http://localhost:8000/auth/stats
```

### Respuesta cuando se excede límite:
```json
{
  "success": false,
  "message": "Límite de uso excedido. Límite: 100, Usado: 100"
}
```

## 🛠️ Administración

### Modificar límites de usuario (en Supabase):

```sql
-- Aumentar límite de usuario específico
UPDATE users 
SET usage_limit = 500 
WHERE email = 'usuario@ejemplo.com';

-- Ver estadísticas generales
SELECT * FROM get_usage_stats();

-- Limpiar generaciones antiguas (>30 días)
SELECT cleanup_old_generations(30);
```

### Ver logs de generaciones:

```sql
-- Últimas 10 generaciones
SELECT u.email, ig.prompt, ig.created_at, ig.generation_time, ig.success
FROM image_generations ig
JOIN users u ON ig.user_id = u.id
ORDER BY ig.created_at DESC
LIMIT 10;

-- Estadísticas por usuario
SELECT * FROM user_stats;
```

## 🔒 Seguridad

### Configuración de producción:

```env
# Usar clave JWT muy segura (32+ caracteres)
JWT_SECRET_KEY=clave_super_secreta_de_produccion_muy_larga

# Configurar CORS correctamente
CORS_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com

# Usar HTTPS en producción
ENVIRONMENT=production
DEBUG=false
```

### Buenas prácticas:

1. **API Keys**: Rotar regularmente (login genera nueva key)
2. **JWT Tokens**: Expiran automáticamente (30 min por defecto)
3. **HTTPS**: Obligatorio en producción
4. **Rate Limiting**: Configurar según necesidades
5. **Monitoreo**: Revisar logs regularmente

## 🚨 Resolución de Problemas

### Error "La autenticación no está habilitada":
```bash
# Verificar .env
AUTH_ENABLED=true

# Reiniciar API
python run_api_with_auth.py
```

### Error de conexión a Supabase:
1. Verificar SUPABASE_URL y SUPABASE_KEY en .env
2. Verificar que las tablas existan (ejecutar setup_database.sql)
3. Verificar conexión a internet

### Error "Token inválido":
- Los JWT tokens expiran (30 min)
- Hacer login nuevamente para obtener nuevo token
- O usar API key (no expira hasta nuevo login)

### Error "API key inválida":
- Hacer login para generar nueva API key
- La API key cambia en cada login por seguridad

## 📈 Monitoreo y Estadísticas

### Dashboard básico en Supabase:

1. Ve a tu proyecto Supabase
2. Sección "Database" > "Tables"
3. Tabla `users` - ver usuarios registrados
4. Tabla `image_generations` - ver todas las generaciones
5. Vista `user_stats` - estadísticas agregadas

### Métricas importantes:

```sql
-- Usuarios activos por día
SELECT DATE(created_at) as date, COUNT(*) as new_users
FROM users 
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date;

-- Generaciones por día
SELECT DATE(created_at) as date, 
       COUNT(*) as total,
       COUNT(CASE WHEN success THEN 1 END) as successful
FROM image_generations 
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date;

-- Top prompts
SELECT prompt, COUNT(*) as usage_count
FROM image_generations 
WHERE success = true
GROUP BY prompt
ORDER BY usage_count DESC
LIMIT 10;
```

## 🤝 Compatibilidad

### Con API anterior:
- ✅ Todos los endpoints existentes funcionan igual
- ✅ Mismas respuestas y formatos  
- ✅ Cliente anterior funciona sin cambios
- ✅ Se puede deshabilitar autenticación completamente

### Migración gradual:
1. Implementar con `AUTH_ENABLED=false` (sin cambios)
2. Configurar Supabase y cambiar a `AUTH_ENABLED=true`
3. Los clientes existentes siguen funcionando
4. Los nuevos clientes pueden usar autenticación

---

💡 **Tip:** Usa la documentación interactiva en `/docs` para probar todos los endpoints directamente desde el navegador.
