# 🎨 Frontend - Generador de Imágenes IA

Frontend web moderno y responsive para la API de generación de imágenes con IA, desarrollado con HTML, CSS y JavaScript vanilla.

## 📋 Características

### ✨ Funcionalidades Principales
- 🔐 **Sistema de Autenticación**: Registro y login completos
- 🎨 **Generación de Imágenes**: Interfaz intuitiva para crear imágenes con IA
- 🖼️ **Galería Personal**: Visualiza y gestiona todas tus imágenes generadas
- 📱 **Diseño Responsive**: Funciona perfectamente en desktop y móvil
- 🌙 **Tema Moderno**: Interfaz limpia con soporte para modo oscuro

### 🛠️ Características Técnicas
- **Sin dependencias externas**: Solo HTML, CSS y JavaScript vanilla
- **Arquitectura modular**: Código organizado en clases y módulos
- **Gestión de estado**: LocalStorage para persistencia de datos
- **Manejo de errores**: Sistema robusto de notificaciones
- **Accesibilidad**: Cumple con estándares web modernos

## 🚀 Instalación y Uso

### 1. Estructura de Archivos

```
front/
├── index.html              # Página principal
├── css/
│   └── styles.css          # Estilos principales
└── js/
    ├── config.js           # Configuración de la app
    ├── utils.js            # Utilidades y helpers
    ├── api.js              # Cliente API
    ├── auth.js             # Gestión de autenticación
    ├── generator.js        # Generación de imágenes
    ├── gallery.js          # Galería de imágenes
    └── app.js              # Controlador principal
```

### 2. Configuración

1. **Configurar la URL de la API**:
   Edita `js/config.js` y cambia la URL base:
   ```javascript
   const CONFIG = {
       API_BASE_URL: 'http://localhost:8000', // Cambia por tu URL
       // ... resto de configuración
   };
   ```

2. **Servir los archivos**:
   - **Opción 1 - Servidor simple con Python**:
     ```bash
     cd front
     python -m http.server 3000
     ```
   
   - **Opción 2 - Servidor con Node.js**:
     ```bash
     cd front
     npx serve -p 3000
     ```
   
   - **Opción 3 - Apache/Nginx**: Coloca los archivos en el directorio web

3. **Acceder a la aplicación**:
   Abre tu navegador en `http://localhost:3000`

### 3. Configuración CORS

Asegúrate de que tu API FastAPI permita peticiones desde tu dominio frontend:

```python
# En tu archivo de API Python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Tu dominio frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🎮 Guía de Usuario

### 📝 Registro y Login

1. **Registro**:
   - Nombre completo
   - Email válido
   - Contraseña (mínimo 6 caracteres)

2. **Login**:
   - Email y contraseña
   - Genera automáticamente una nueva API key

### 🎨 Generación de Imágenes

1. **Describe tu imagen**:
   - Mínimo 10 caracteres
   - Máximo 500 caracteres
   - Sé específico y creativo

2. **Selecciona dimensiones**:
   - 512x512px (rápido)
   - 768x768px (balanced)
   - 1024x1024px (alta calidad)

3. **Genera y descarga**:
   - Haz clic en "Generar Imagen"
   - Espera la generación (1-2 minutos)
   - Descarga o guarda en galería

### 🖼️ Galería Personal

- **Visualizar**: Haz clic en cualquier imagen para vista ampliada
- **Descargar**: Botón de descarga en cada imagen
- **Eliminar**: Remover de la galería local
- **Buscar**: Filtra por texto del prompt

## ⌨️ Atajos de Teclado

| Atajo | Acción |
|-------|--------|
| `Ctrl+N` | Enfocar generación nueva |
| `Ctrl+R` | Actualizar galería |
| `Ctrl+K` | Buscar (si disponible) |
| `F1` | Mostrar ayuda |
| `ESC` | Cerrar modales |

## 🔧 Personalización

### Cambiar Colores

Edita las variables CSS en `css/styles.css`:

```css
:root {
    --primary-color: #6366f1;      /* Color principal */
    --secondary-color: #f59e0b;    /* Color secundario */
    --success-color: #10b981;      /* Color éxito */
    --error-color: #ef4444;        /* Color error */
    /* ... más variables */
}
```

### Modificar Configuración

En `js/config.js` puedes cambiar:

```javascript
const CONFIG = {
    // Timeouts
    TIMEOUTS: {
        DEFAULT: 30000,           // 30 segundos
        GENERATE_IMAGE: 120000    // 2 minutos
    },
    
    // Límites
    DEFAULT_SETTINGS: {
        MAX_STORED_IMAGES: 50     // Imágenes en galería
    },
    
    // Duración notificaciones
    TOAST_DURATION: 5000          // 5 segundos
};
```

## 📱 Responsive Design

La aplicación se adapta automáticamente a diferentes tamaños de pantalla:

- **Desktop** (>768px): Diseño completo con todas las características
- **Tablet** (768px): Layout adaptado, botones reorganizados
- **Móvil** (<480px): Interfaz optimizada para touch, elementos apilados

## 🔒 Seguridad

### Almacenamiento Local
- **API Keys**: Guardadas en localStorage (considera sessionStorage para mayor seguridad)
- **Imágenes**: Solo URLs y metadatos, no las imágenes completas

### Buenas Prácticas
```javascript
// Las API keys se envían en headers Authorization
headers: {
    'Authorization': `Bearer ${apiKey}`
}

// Validación de entrada en el frontend
Utils.validateEmail(email);  // Valida formato email
prompt.length >= 10;         // Valida longitud mínima
```

## 🐛 Resolución de Problemas

### Error "No se puede conectar con el servidor"

1. **Verificar API activa**:
   ```bash
   curl http://localhost:8000/status
   ```

2. **Verificar CORS**: Asegúrate de que la API permite tu dominio frontend

3. **Verificar URL**: Confirma la URL en `config.js`

### Error "Token inválido"

1. **Logout y Login**: Los JWT tokens expiran (30 min por defecto)
2. **Verificar API Key**: Hacer login genera nueva API key

### Error "Límite excedido"

- Verifica tu límite de uso en el perfil
- Contacta al administrador para aumentar límite

### Imágenes no cargan

1. **Verificar permisos**: API debe servir imágenes correctamente
2. **Verificar rutas**: URLs de imágenes en respuesta de API
3. **Verificar CORS**: Para descargas de imágenes

## 🚀 Despliegue en Producción

### 1. Optimización

```bash
# Minificar CSS (opcional)
npm install -g clean-css-cli
cleancss -o styles.min.css styles.css

# Minificar JS (opcional) 
npm install -g uglify-js
uglifyjs app.js -o app.min.js
```

### 2. Configuración HTTPS

Asegúrate de usar HTTPS en producción:

```javascript
// config.js para producción
const CONFIG = {
    API_BASE_URL: 'https://tu-api-dominio.com',
    // ... resto de configuración
};
```

### 3. CDN y Cache

Configura headers de cache apropiados:

```
# .htaccess para Apache
<IfModule mod_expires.c>
    ExpiresActive on
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
    ExpiresByType image/png "access plus 1 month"
</IfModule>
```

## 📞 Soporte

Para problemas o sugerencias:

1. **Revisa la consola del navegador** para errores JavaScript
2. **Verifica la pestaña Network** para errores de API
3. **Consulta los logs del servidor** FastAPI

## 🎯 Roadmap Futuro

- [ ] **Búsqueda avanzada** en galería
- [ ] **Categorías/Tags** para imágenes
- [ ] **Compartir imágenes** en redes sociales
- [ ] **Modo offline** con service workers
- [ ] **Temas personalizables**
- [ ] **Arrastrar y soltar** archivos
- [ ] **Preview en tiempo real** de parámetros

---

¡Disfruta creando imágenes increíbles con IA! 🎨✨
