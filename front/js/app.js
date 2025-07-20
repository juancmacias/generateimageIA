// Main Application Controller
class App {
    constructor() {
        this.authManager = null;
        this.imageGenerator = null;
        this.imageGallery = null;
        this.isInitialized = false;
        
        this.initialize();
    }
    
    async initialize() {
        try {
            // Wait for DOM to be fully loaded
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.initializeApp());
            } else {
                this.initializeApp();
            }
            
        } catch (error) {
            console.error('App initialization error:', error);
            Utils.showToast('Error al inicializar la aplicación', 'error');
        }
    }
    
    async initializeApp() {
        try {
            Utils.showLoading('Iniciando aplicación...');
            
            // Initialize managers
            this.authManager = new AuthManager();
            this.imageGenerator = new ImageGenerator();
            this.imageGallery = new ImageGallery();
            
            // Make gallery available globally for cross-component communication
            window.imageGallery = this.imageGallery;
            
            // Initialize auth state
            await this.authManager.initializeAuthState();
            
            // Set up global event listeners
            this.setupGlobalEventListeners();
            
            // Check API status
            await this.checkAPIStatus();
            
            this.isInitialized = true;
            
            Utils.showToast('¡Aplicación lista!', 'success');
            
        } catch (error) {
            console.error('App initialization error:', error);
            Utils.showToast('Error al conectar con el servidor', 'warning');
        } finally {
            Utils.hideLoading();
        }
    }
    
    setupGlobalEventListeners() {
        // Handle window resize
        window.addEventListener('resize', Utils.debounce(() => {
            this.handleWindowResize();
        }, 250));
        
        // Handle online/offline status
        window.addEventListener('online', () => {
            Utils.showToast('Conexión restaurada', 'success');
        });
        
        window.addEventListener('offline', () => {
            Utils.showToast('Conexión perdida', 'warning');
        });
        
        // Handle beforeunload (warn about unsaved changes)
        window.addEventListener('beforeunload', (e) => {
            if (this.imageGenerator && this.imageGenerator.isGenerating) {
                e.preventDefault();
                e.returnValue = '¿Estás seguro? Se está generando una imagen.';
                return e.returnValue;
            }
        });
        
        // Handle visibility change (pause/resume activities)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.handleAppPause();
            } else {
                this.handleAppResume();
            }
        });
        
        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleGlobalKeyboard(e);
        });
        
        // Handle errors
        window.addEventListener('error', (e) => {
            console.error('Global error:', e.error);
            Utils.showToast('Se produjo un error inesperado', 'error');
        });
        
        window.addEventListener('unhandledrejection', (e) => {
            console.error('Unhandled promise rejection:', e.reason);
            Utils.showToast('Error de conexión', 'error');
        });
    }
    
    async checkAPIStatus() {
        try {
            const api = new APIClient();
            const status = await api.getStatus();
            
            if (status && status.status === 'ok') {
                console.log('API Status:', status);
                return true;
            } else {
                throw new Error('API not responding correctly');
            }
            
        } catch (error) {
            console.warn('API Status check failed:', error);
            Utils.showToast('No se pudo conectar con el servidor', 'warning');
            return false;
        }
    }
    
    handleWindowResize() {
        // Handle responsive adjustments
        const isMobile = Utils.isMobileDevice();
        document.body.classList.toggle('mobile-device', isMobile);
        
        // Notify components about resize
        if (this.imageGallery) {
            // Gallery might need to adjust layout
            this.imageGallery.renderGallery();
        }
    }
    
    handleAppPause() {
        // App is hidden/minimized
        console.log('App paused');
    }
    
    handleAppResume() {
        // App is visible again
        console.log('App resumed');
        
        // Check if user is still authenticated
        if (this.authManager && this.authManager.isAuthenticated()) {
            // Refresh user profile to check for any changes
            this.authManager.loadUserProfile().catch(error => {
                console.error('Error refreshing profile:', error);
            });
        }
    }
    
    handleGlobalKeyboard(event) {
        // Don't interfere with form inputs
        if (event.target.tagName === 'INPUT' || 
            event.target.tagName === 'TEXTAREA' || 
            event.target.contentEditable === 'true') {
            return;
        }
        
        // Global shortcuts
        switch (event.key) {
            case 'Escape':
                // Close any open modals
                const modals = document.querySelectorAll('.modal:not(.hidden)');
                modals.forEach(modal => {
                    modal.classList.add('hidden');
                });
                break;
                
            case 'F1':
                event.preventDefault();
                this.showHelp();
                break;
                
            case 'F5':
                // Allow normal F5 refresh, but warn if generating
                if (this.imageGenerator && this.imageGenerator.isGenerating) {
                    event.preventDefault();
                    const confirm = window.confirm('¿Estás seguro? Se está generando una imagen.');
                    if (confirm) {
                        window.location.reload();
                    }
                }
                break;
        }
        
        // Ctrl/Cmd shortcuts
        if (event.ctrlKey || event.metaKey) {
            switch (event.key) {
                case 'k':
                    event.preventDefault();
                    this.focusSearch();
                    break;
                    
                case 'n':
                    event.preventDefault();
                    this.focusNewGeneration();
                    break;
                    
                case 'r':
                    event.preventDefault();
                    this.refreshGallery();
                    break;
            }
        }
    }
    
    focusSearch() {
        // Focus search if it exists (could be added later)
        const searchInput = document.querySelector('input[type="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    focusNewGeneration() {
        const promptText = document.getElementById('promptText');
        if (promptText && !promptText.closest('.hidden')) {
            promptText.focus();
        }
    }
    
    refreshGallery() {
        if (this.imageGallery) {
            this.imageGallery.refreshGallery();
        }
    }
    
    showHelp() {
        const helpText = `
🎨 Generador de Imágenes IA - Ayuda

Atajos de teclado:
• Ctrl+N - Crear nueva imagen
• Ctrl+R - Actualizar galería  
• Ctrl+K - Buscar (si disponible)
• F1 - Mostrar ayuda
• ESC - Cerrar modales

Uso:
1. Regístrate o inicia sesión
2. Describe la imagen que quieres generar
3. Selecciona el tamaño deseado
4. Haz clic en "Generar Imagen"
5. Descarga o guarda tus imágenes

¡Disfruta creando!
        `;
        
        alert(helpText);
    }
    
    // Public methods for external access
    getAuthManager() {
        return this.authManager;
    }
    
    getImageGenerator() {
        return this.imageGenerator;
    }
    
    getImageGallery() {
        return this.imageGallery;
    }
    
    isReady() {
        return this.isInitialized;
    }
    
    // Utility method to restart app
    async restart() {
        try {
            Utils.showLoading('Reiniciando aplicación...');
            
            // Clear any ongoing processes
            if (this.imageGenerator) {
                this.imageGenerator.clearCurrentGeneration();
            }
            
            // Reinitialize
            await this.initializeApp();
            
        } catch (error) {
            console.error('App restart error:', error);
            Utils.showToast('Error al reiniciar la aplicación', 'error');
        }
    }
}

// Initialize app when script loads
let app;

// Ensure single app instance
if (!window.imageGenApp) {
    window.imageGenApp = new App();
    app = window.imageGenApp;
} else {
    app = window.imageGenApp;
}

// Export for debugging
if (typeof module !== 'undefined' && module.exports) {
    module.exports = App;
}
