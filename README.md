# 🎨 Generador de Imágenes con IA

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-green.svg)
![CUDA](https://img.shields.io/badge/CUDA-11.8%2B-brightgreen.svg)
![GPU](https://img.shields.io/badge/GPU-NVIDIA-76B900.svg)

Un potente generador de imágenes con Inteligencia Artificial que utiliza **Stable Diffusion** con aceleración **GPU** para crear imágenes de alta calidad de forma rápida y eficiente.

## 📋 Características Principales

- 🚀 **Aceleración GPU** con NVIDIA CUDA
- 🎯 **Stable Diffusion v1.5** - Estado del arte en generación de imágenes
- ⚡ **Optimizaciones avanzadas** para máximo rendimiento
- 🧠 **Gestión inteligente de memoria** VRAM
- 🛠️ **Diagnósticos completos** de hardware
- 📊 **Interfaz detallada** con estadísticas en tiempo real
- 🎨 **Múltiples ejemplos** predefinidos

## 🏗️ Estructura del Proyecto

```
imagenes_IA/
├── 📁 app/                   # Aplicación principal
│   ├── image_generator.py    # Motor de generación IA
│   ├── main.py               # Script del gato espacial
│   └── __init__.py           # Configuración del paquete
│
├── 📁 utils/                  # Herramientas y diagnósticos
│   ├── gpu_diagnostics.py    # Diagnóstico GPU/CUDA
│   ├── system_info.py        # Información del sistema
│   └── __init__.py           # Configuración del paquete
│
├── 📁 examples/              # Ejemplos y demos
│   ├── examples.py           # Múltiples ejemplos
│   └── __init__.py           # Configuración del paquete
│
├── 📁 generated_images/      # Imágenes generadas
├── 📁 .venv/                 # Entorno virtual Python
│
├── 🚀 generate_image.py      # Script acceso rápido - Generar imagen
├── 🩺 check_gpu.py          # Script acceso rápido - Comprobar GPU
├── 📚 run_examples.py       # Script acceso rápido - Ejecutar ejemplos
├── ℹ️  system_check.py       # Script acceso rápido - Info sistema
│
├── requirements.txt          # Dependencias
├── README.md                # Esta documentación
└── .gitignore               # Archivos ignorados por Git
```

## ⚙️ Requisitos del Sistema

### 🖥️ Hardware Recomendado
- **GPU NVIDIA** con 4GB+ VRAM (GTX 1060, RTX 2060 o superior)
- **RAM**: 8GB+ (16GB recomendado)
- **Almacenamiento**: 10GB+ espacio libre
- **Sistema**: Windows 10/11, Linux, macOS

### 🔧 Software
- **Python 3.10+**
- **NVIDIA Driver 475+** (para GPU)
- **Git** (para clonar repositorio)

## 🚀 Instalación

### 🎯 Instalación Automática (Recomendada)

#### En Windows:
```bash
# Ejecutar instalador automático
install.bat
```

#### En Linux/macOS:
```bash
# Hacer ejecutable y correr
chmod +x install.sh
./install.sh
```

### 🔧 Instalación Manual

#### 1️⃣ Clonar el Repositorio
```bash
git clone https://github.com/usuario/imagenes_IA.git
cd imagenes_IA
```

#### 2️⃣ Crear Entorno Virtual
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# En Windows:
.venv\Scripts\activate

# En Linux/macOS:
source .venv/bin/activate
```

#### 3️⃣ Instalar Dependencias
```bash
# Instalar dependencias básicas
pip install -r requirements.txt

# Para GPU NVIDIA con CUDA 11.8:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### 4️⃣ Verificar Instalación
```bash
# Verificar GPU
python check_gpu.py

# Probar todos los componentes
python test_system.py
```

**Resultado esperado con GPU:**
```
🎉 ESTADO: GPU lista para usar
   Tu generador de imágenes usará GPU automáticamente
```

## 🎮 Uso Rápido

### 🖼️ Generar Imagen del Gato Espacial
```bash
python generate_image.py
```
Genera una imagen de un gato volando en el espacio estelar.

### 📚 Ejecutar Ejemplos Interactivos
```bash
python run_examples.py
```
Menú interactivo con múltiples ejemplos predefinidos.

### 🩺 Diagnóstico Completo del Sistema
```bash
python check_gpu.py
```
Verifica GPU, CUDA, PyTorch y compatibilidad.

### ℹ️ Información del Sistema
```bash
python system_check.py
```
Muestra información detallada del hardware.

### 🧪 Probar Todos los Componentes
```bash
python test_system.py
```
Ejecuta una suite completa de tests para verificar que todo funciona.

## 📝 Uso Avanzado

### Generar Imagen Personalizada
```python
from app.image_generator import ImageGeneratorAI

# Crear generador
generator = ImageGeneratorAI()

# Generar imagen
image, tiempo = generator.generate(
    prompt="a beautiful landscape with mountains and sunset",
    width=512,
    height=512,
    num_inference_steps=20,
    guidance_scale=7.5
)

# Guardar imagen
image.save("mi_imagen.png")
```

### Verificar Estado GPU
```python
from utils.gpu_diagnostics import check_gpu_status

status = check_gpu_status()
print(f"GPU disponible: {status['gpu_available']}")
print(f"Dispositivo: {status['device_name']}")
```

## 🎯 Ejemplos de Prompts

| Categoría | Prompt | Tiempo GPU | Resultado |
|-----------|--------|------------|-----------|
| **Naturaleza** | `beautiful mountain landscape at sunset` | ~30s | 🏔️ Paisaje montañoso |
| **Animales** | `majestic lion in african savanna` | ~35s | 🦁 León en sabana |
| **Ciencia Ficción** | `futuristic city with flying cars` | ~40s | 🚗 Ciudad futurista |
| **Arte** | `abstract colorful painting, digital art` | ~25s | 🎨 Arte abstracto |
| **Espacio** | `astronaut floating in deep space, stars` | ~30s | 👨‍🚀 Astronauta |

## 📊 Rendimiento

### Con GPU NVIDIA GTX 960M (4GB VRAM):
- ⚡ **Imagen 512x512**: ~45 segundos
- 🧠 **VRAM utilizada**: ~2.0GB
- 🚀 **Aceleración vs CPU**: 4x más rápido

### Con CPU (Fallback):
- ⏳ **Imagen 512x512**: ~180 segundos
- 💾 **RAM utilizada**: ~4GB
- 🐌 **Recomendado solo sin GPU**

## 🛠️ Solución de Problemas

### ❌ "CUDA no disponible"
```bash
# Verificar driver NVIDIA
nvidia-smi

# Reinstalar PyTorch con CUDA
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### ❌ "Memoria VRAM insuficiente"
- Reducir resolución: `width=256, height=256`
- Reducir pasos: `num_inference_steps=10`
- Cerrar otras aplicaciones que usen GPU

### ❌ "Modelo no se descarga"
```bash
# Limpiar cache
pip cache purge

# Verificar conexión internet
# Ejecutar diagnóstico
python check_gpu.py
```

## 🔧 Configuración Avanzada

### Optimización para GPU con poca VRAM (<4GB):
```python
generator = ImageGeneratorAI(
    enable_attention_slicing=True,  # Reduce uso VRAM
    enable_cpu_offload=True,        # Offload a CPU cuando necesario
    use_half_precision=True         # Usar float16
)
```

### Generación en lotes:
```python
# Generar múltiples imágenes
prompts = ["cat in space", "dog on beach", "bird in forest"]
for prompt in prompts:
    image, _ = generator.generate(prompt)
    image.save(f"{prompt.replace(' ', '_')}.png")
```

## 📚 Dependencias Principales

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `torch` | 2.7.1+cu118 | Framework ML con CUDA |
| `diffusers` | 0.31.0+ | Modelos Stable Diffusion |
| `transformers` | 4.48.0+ | Procesamiento de texto |
| `accelerate` | 1.2.1+ | Optimizaciones GPU |
| `pillow` | 11.3.0+ | Procesamiento de imágenes |

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea tu rama feature: `git checkout -b feature/AmazingFeature`
3. Commit tus cambios: `git commit -m 'Add some AmazingFeature'`
4. Push a la rama: `git push origin feature/AmazingFeature`
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👨‍💻 Autor

**Curso IA F5**
- 📧 Email: curso@ia-f5.com
- 🌐 Website: [ia-f5.com](https://ia-f5.com)

## 🙏 Agradecimientos

- [Stability AI](https://stability.ai/) por Stable Diffusion
- [Hugging Face](https://huggingface.co/) por la librería Diffusers
- [PyTorch](https://pytorch.org/) por el framework de ML
- Comunidad open source por las contribuciones

---

<div align="center">

**⭐ Si este proyecto te ha sido útil, ¡dale una estrella! ⭐**

</div>
