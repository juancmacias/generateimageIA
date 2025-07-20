// Configuration
const CONFIG = {
    // API Base URL - Cambiar según tu configuración
    API_BASE_URL: 'http://localhost:8000',
    
    // Authentication mode - set to false to disable auth
    AUTH_ENABLED: false,
    
    // Endpoints
    ENDPOINTS: {
        REGISTER: '/auth/register',
        LOGIN: '/auth/login',
        PROFILE: '/auth/profile',
        GENERATE: '/generate',
        IMAGE: '/image',
        STATUS: '/status'
    },
    
    // Local Storage Keys
    STORAGE_KEYS: {
        API_KEY: 'api_key',
        USER_EMAIL: 'user_email',
        USER_NAME: 'user_name',
        GENERATED_IMAGES: 'generated_images'
    },
    
    // Default settings
    DEFAULT_SETTINGS: {
        IMAGE_WIDTH: 512,
        IMAGE_HEIGHT: 512,
        MAX_STORED_IMAGES: 50
    },
    
    // API timeouts (ms)
    TIMEOUTS: {
        DEFAULT: 30000, // 30 seconds
        GENERATE_IMAGE: 120000 // 2 minutes for image generation
    },
    
    // Image formats
    SUPPORTED_FORMATS: ['png', 'jpg', 'jpeg', 'webp'],
    
    // Toast notification duration (ms)
    TOAST_DURATION: 5000
};
