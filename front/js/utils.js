// Utility functions
class Utils {
    // Show/hide loading overlay
    static showLoading(message = 'Procesando...') {
        const overlay = document.getElementById('loadingOverlay');
        const spinner = overlay.querySelector('.loading-spinner p');
        spinner.textContent = message;
        overlay.classList.remove('hidden');
    }
    
    static hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.classList.add('hidden');
    }
    
    // Toast notifications
    static showToast(message, type = 'info', duration = CONFIG.TOAST_DURATION) {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const iconMap = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        toast.innerHTML = `
            <i class="${iconMap[type] || iconMap.info}"></i>
            <span class="toast-message">${message}</span>
        `;
        
        container.appendChild(toast);
        
        // Auto remove
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (toast.parentNode) {
                    container.removeChild(toast);
                }
            }, 300);
        }, duration);
        
        // Click to dismiss
        toast.addEventListener('click', () => {
            container.removeChild(toast);
        });
    }
    
    // Format date
    static formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    // Generate filename
    static generateFilename(prompt, extension = 'png') {
        const cleanPrompt = prompt
            .toLowerCase()
            .replace(/[^a-z0-9\s]/g, '')
            .replace(/\s+/g, '_')
            .substring(0, 50);
        
        const timestamp = new Date().toISOString().replace(/[:.]/g, '').slice(0, -5);
        return `${cleanPrompt}_${timestamp}.${extension}`;
    }
    
    // Download file
    static downloadFile(url, filename) {
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    // Validate email
    static validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    // Truncate text
    static truncateText(text, maxLength = 100) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
    
    // Local Storage helpers
    static setStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Error saving to localStorage:', error);
        }
    }
    
    static getStorage(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Error reading from localStorage:', error);
            return defaultValue;
        }
    }
    
    static removeStorage(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Error removing from localStorage:', error);
        }
    }
    
    // Debounce function
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    // Copy to clipboard
    static async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            Utils.showToast('Copiado al portapapeles', 'success');
        } catch (error) {
            console.error('Error copying to clipboard:', error);
            Utils.showToast('Error al copiar al portapapeles', 'error');
        }
    }
    
    // Check if user is logged in
    static isLoggedIn() {
        return !!Utils.getStorage(CONFIG.STORAGE_KEYS.API_KEY);
    }
    
    // Get user info
    static getUserInfo() {
        return {
            apiKey: Utils.getStorage(CONFIG.STORAGE_KEYS.API_KEY),
            email: Utils.getStorage(CONFIG.STORAGE_KEYS.USER_EMAIL),
            name: Utils.getStorage(CONFIG.STORAGE_KEYS.USER_NAME)
        };
    }
    
    // Clear user data
    static clearUserData() {
        Utils.removeStorage(CONFIG.STORAGE_KEYS.API_KEY);
        Utils.removeStorage(CONFIG.STORAGE_KEYS.USER_EMAIL);
        Utils.removeStorage(CONFIG.STORAGE_KEYS.USER_NAME);
    }
    
    // Format file size
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Generate random ID
    static generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
    
    // Escape HTML
    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Load image with fallback
    static loadImage(src) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(img);
            img.onerror = () => reject(new Error(`Failed to load image: ${src}`));
            img.src = src;
        });
    }
    
    // Check if mobile device
    static isMobileDevice() {
        return window.innerWidth <= 768;
    }
    
    // Smooth scroll to element
    static scrollToElement(element, offset = 0) {
        const elementPosition = element.offsetTop - offset;
        window.scrollTo({
            top: elementPosition,
            behavior: 'smooth'
        });
    }
    
    // Add CSS animation classes
    static addAnimationClass(element, className, duration = 300) {
        element.classList.add(className);
        setTimeout(() => {
            element.classList.remove(className);
        }, duration);
    }
}

// Event delegation helper
class EventDelegate {
    constructor(container) {
        this.container = container;
        this.events = new Map();
    }
    
    on(selector, eventType, handler) {
        const key = `${selector}:${eventType}`;
        if (!this.events.has(key)) {
            this.events.set(key, new Set());
            
            this.container.addEventListener(eventType, (event) => {
                const target = event.target.closest(selector);
                if (target) {
                    const handlers = this.events.get(key);
                    handlers.forEach(handler => handler(event, target));
                }
            });
        }
        
        this.events.get(key).add(handler);
    }
    
    off(selector, eventType, handler) {
        const key = `${selector}:${eventType}`;
        if (this.events.has(key)) {
            this.events.get(key).delete(handler);
        }
    }
}

// Form validation helper
class FormValidator {
    constructor(form) {
        this.form = form;
        this.rules = new Map();
        this.errors = new Map();
    }
    
    addRule(fieldName, validator, message) {
        if (!this.rules.has(fieldName)) {
            this.rules.set(fieldName, []);
        }
        this.rules.get(fieldName).push({ validator, message });
        return this;
    }
    
    validate() {
        this.errors.clear();
        
        this.rules.forEach((rules, fieldName) => {
            const field = this.form.querySelector(`[name="${fieldName}"]`);
            if (!field) return;
            
            const value = field.value.trim();
            
            rules.forEach(({ validator, message }) => {
                if (!validator(value, field)) {
                    if (!this.errors.has(fieldName)) {
                        this.errors.set(fieldName, []);
                    }
                    this.errors.get(fieldName).push(message);
                }
            });
        });
        
        return this.errors.size === 0;
    }
    
    getErrors() {
        return this.errors;
    }
    
    showErrors() {
        this.errors.forEach((messages, fieldName) => {
            const field = this.form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                field.classList.add('error');
                // You can add error message display logic here
            }
        });
    }
    
    clearErrors() {
        this.form.querySelectorAll('.error').forEach(field => {
            field.classList.remove('error');
        });
    }
}
