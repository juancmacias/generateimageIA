// API Client
class APIClient {
    constructor() {
        this.baseURL = CONFIG.API_BASE_URL;
        this.defaultHeaders = {
            'Content-Type': 'application/json'
        };
    }
    
    // Get authorization headers
    getAuthHeaders() {
        // If auth is disabled, return default headers
        if (!CONFIG.AUTH_ENABLED) {
            return this.defaultHeaders;
        }
        
        const apiKey = Utils.getStorage(CONFIG.STORAGE_KEYS.API_KEY);
        if (apiKey) {
            return {
                ...this.defaultHeaders,
                'Authorization': `Bearer ${apiKey}`
            };
        }
        return this.defaultHeaders;
    }
    
    // Generic request method
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.defaultHeaders,
            ...options
        };
        
        // Add authorization if available and required
        if (options.requiresAuth !== false) {
            // Only add auth headers if auth is enabled
            if (CONFIG.AUTH_ENABLED) {
                config.headers = this.getAuthHeaders();
            }
        }
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || `HTTP Error: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }
    
    // Authentication methods
    async register(userData) {
        return this.request(CONFIG.ENDPOINTS.REGISTER, {
            method: 'POST',
            body: JSON.stringify(userData),
            requiresAuth: false
        });
    }
    
    async login(credentials) {
        return this.request(CONFIG.ENDPOINTS.LOGIN, {
            method: 'POST',
            body: JSON.stringify(credentials),
            requiresAuth: false
        });
    }
    
    async getProfile() {
        return this.request(CONFIG.ENDPOINTS.PROFILE, {
            method: 'GET'
        });
    }
    
    // Image generation
    async generateImage(imageData) {
        return this.request(CONFIG.ENDPOINTS.GENERATE, {
            method: 'POST',
            body: JSON.stringify(imageData)
        });
    }
    
    // Get image URL
    getImageUrl(filename) {
        return `${this.baseURL}${CONFIG.ENDPOINTS.IMAGE}/${filename}`;
    }
    
    // System status
    async getStatus() {
        return this.request(CONFIG.ENDPOINTS.STATUS, {
            method: 'GET',
            requiresAuth: false
        });
    }
    
    // Download image
    async downloadImage(filename) {
        const url = this.getImageUrl(filename);
        const response = await fetch(url, {
            headers: this.getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error('Failed to download image');
        }
        
        return response.blob();
    }
}
