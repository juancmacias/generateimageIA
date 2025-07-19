"""
🛠️ Utilidades del Sistema
========================
Herramientas de diagnóstico, información del sistema 
y utilidades para optimización GPU/CUDA.
"""

__version__ = "1.0.0"

# Importaciones principales
try:
    from .gpu_diagnostics import check_gpu_status
    from .system_info import get_system_info
    
    __all__ = ["check_gpu_status", "get_system_info"]
except ImportError:
    # Si hay problemas de importación, continúa sin errores
    __all__ = []
