# 🌐 API de Generación de Imágenes - Documentación

## 📋 Resumen

La API REST permite generar imágenes usando Stable Diffusion a través de requests HTTP. Proporciona endpoints para generar imágenes, verificar el estado del sistema, descargar imágenes y más.

## 🚀 Inicio Rápido

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar la API
```bash
python run_api.py
```

La API estará disponible en: `http://localhost:8000`

### 3. Documentación Interactiva
Visita `http://localhost:8000/docs` para la documentación interactiva de Swagger.

## 📡 Endpoints Principales

### POST /generate
Genera una imagen basada en un prompt.

**Parámetros:**
- `prompt` (string, requerido): Descripción de la imagen
- `width` (int, opcional): Ancho en píxeles (128-1024, default: 512)
- `height` (int, opcional): Alto en píxeles (128-1024, default: 512)
- `num_inference_steps` (int, opcional): Pasos de inferencia (5-100, default: 20)
- `guidance_scale` (float, opcional): Escala de guidance (1.0-20.0, default: 7.5)

**Ejemplo de request:**
```json
{
  "prompt": "a beautiful cat flying through space among stars",
  "width": 512,
  "height": 512,
  "num_inference_steps": 20,
  "guidance_scale": 7.5
}
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Imagen generada exitosamente",
  "image_url": "/image/cat_space_20250719_123456_abc123.png",
  "filename": "cat_space_20250719_123456_abc123.png",
  "generation_time": 32.45,
  "parameters": {
    "prompt": "a beautiful cat flying through space among stars",
    "width": 512,
    "height": 512,
    "num_inference_steps": 20,
    "guidance_scale": 7.5,
    "device": "cuda"
  }
}
```

### GET /status
Obtiene el estado del sistema y GPU.

**Respuesta:**
```json
{
  "gpu_available": true,
  "device_name": "NVIDIA GeForce GTX 960M",
  "memory_info": {
    "total": "4.0 GB",
    "available": "2.1 GB"
  },
  "model_loaded": true
}
```

### GET /image/{filename}
Descarga una imagen generada por nombre de archivo.

**Ejemplo:**
```
GET /image/cat_space_20250719_123456_abc123.png
```

### GET /images/list
Lista todas las imágenes generadas disponibles.

**Respuesta:**
```json
{
  "success": true,
  "count": 5,
  "images": [
    {
      "filename": "cat_space_20250719_123456_abc123.png",
      "url": "/image/cat_space_20250719_123456_abc123.png",
      "size": 892456,
      "created": "2025-07-19T12:34:56",
      "modified": "2025-07-19T12:34:56"
    }
  ]
}
```

### DELETE /cleanup
Libera los recursos del generador para ahorrar memoria.

## 💻 Uso con cURL

### Generar imagen:
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a majestic lion in african savanna",
    "width": 512,
    "height": 512,
    "num_inference_steps": 20
  }'
```

### Verificar estado:
```bash
curl "http://localhost:8000/status"
```

### Descargar imagen:
```bash
curl "http://localhost:8000/image/filename.png" --output "imagen_descargada.png"
```

## 🐍 Uso con Python

### Ejemplo básico:
```python
import requests

# Generar imagen
response = requests.post("http://localhost:8000/generate", json={
    "prompt": "beautiful landscape with mountains and sunset",
    "width": 512,
    "height": 512,
    "num_inference_steps": 20
})

result = response.json()
if result["success"]:
    print(f"Imagen generada: {result['image_url']}")
    
    # Descargar imagen
    img_response = requests.get(f"http://localhost:8000{result['image_url']}")
    with open(result["filename"], "wb") as f:
        f.write(img_response.content)
```

### Cliente completo:
```bash
python api_client_example.py
```

## 🌍 Uso con JavaScript/Fetch

```javascript
// Generar imagen
async function generateImage(prompt) {
  const response = await fetch('http://localhost:8000/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt: prompt,
      width: 512,
      height: 512,
      num_inference_steps: 20
    })
  });
  
  const result = await response.json();
  if (result.success) {
    console.log('Imagen generada:', result.image_url);
    return result;
  } else {
    console.error('Error:', result.message);
  }
}

// Usar la función
generateImage("a futuristic city with flying cars");
```

## 🔧 Configuración Avanzada

### Ejecutar en otro puerto:
```bash
python run_api.py --port 8080
```

### Permitir acceso externo:
```bash
python run_api.py --host 0.0.0.0
```

### Modo desarrollo con auto-reload:
```bash
python run_api.py --reload
```

## 📊 Parámetros de Generación

### `prompt`
- **Tipo:** string
- **Descripción:** Texto que describe la imagen a generar
- **Ejemplos:**
  - `"a beautiful cat flying through space"`
  - `"mountain landscape at sunset, digital art"`
  - `"futuristic city with neon lights, cyberpunk"`

### `width` / `height`
- **Tipo:** int
- **Rango:** 128-1024 píxeles
- **Recomendaciones:**
  - 256x256: Rápido, menor calidad
  - 512x512: Equilibrio calidad/velocidad
  - 768x768: Alta calidad, más lento

### `num_inference_steps`
- **Tipo:** int
- **Rango:** 5-100
- **Recomendaciones:**
  - 5-10: Muy rápido, calidad básica
  - 15-25: Equilibrio calidad/velocidad
  - 30-50: Alta calidad, más lento

### `guidance_scale`
- **Tipo:** float
- **Rango:** 1.0-20.0
- **Descripción:** Qué tanto debe seguir el prompt
- **Recomendaciones:**
  - 5-8: Más creativo, menos fiel al prompt
  - 7.5: Equilibrio (default)
  - 10-15: Muy fiel al prompt

## 🚨 Códigos de Error

| Código | Descripción | Solución |
|--------|-------------|----------|
| 400 | Parámetros inválidos | Verificar tipos y rangos |
| 404 | Imagen no encontrada | Verificar nombre del archivo |
| 500 | Error del servidor | Verificar logs, posible falta de memoria |
| 503 | Servicio no disponible | Modelo cargándose, esperar |

## ⚡ Optimización de Rendimiento

### Para GPU con poca VRAM (<4GB):
- Usar resoluciones menores (256x256, 384x384)
- Reducir pasos de inferencia (10-15)
- Cerrar otras aplicaciones que usen GPU

### Para CPU:
- Usar resoluciones pequeñas (256x256)
- Usar pocos pasos (5-10)
- Tener paciencia (mucho más lento)

## 🛠️ Solución de Problemas

### La API no inicia:
```bash
# Verificar dependencias
pip install -r requirements.txt

# Verificar puerto ocupado
netstat -an | findstr :8000
```

### Error "CUDA out of memory":
- Reducir `width` y `height`
- Reducir `num_inference_steps`
- Usar endpoint `/cleanup` para liberar memoria

### Modelo no se carga:
```bash
# Verificar espacio en disco
python -c "import torch; print(torch.cuda.is_available())"

# Limpiar cache
pip cache purge
```

## 📈 Monitoreo

### Logs de la API:
Los logs se muestran en la consola donde ejecutaste `run_api.py`.

### Uso de memoria:
Usar el endpoint `/status` para monitorear el uso de VRAM/RAM.

### Imágenes generadas:
Las imágenes se guardan en la carpeta `generated_images/`.

## 🔒 Seguridad

**⚠️ Importante:** Esta API está diseñada para desarrollo local. Para producción:

1. Configurar autenticación
2. Validar y sanitizar prompts
3. Implementar rate limiting
4. Usar HTTPS
5. Configurar CORS adecuadamente

## 🤝 Integración con Frontend

### React/Next.js:
```javascript
const generateImage = async (prompt) => {
  const response = await fetch('/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt })
  });
  return response.json();
};
```

### Vue.js:
```javascript
async generateImage(prompt) {
  try {
    const response = await this.$http.post('/generate', { prompt });
    return response.data;
  } catch (error) {
    console.error('Error:', error);
  }
}
```

## 📚 Recursos Adicionales

- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [Stable Diffusion Guide](https://huggingface.co/docs/diffusers/)
- [Repositorio del proyecto](https://github.com/juancmacias/generateimageIA)

---

💡 **Tip:** Usa la documentación interactiva en `/docs` para probar la API directamente desde el navegador.
