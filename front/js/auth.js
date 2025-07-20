// Authentication Manager
class AuthManager {
    constructor() {
        this.api = new APIClient();
        this.userProfile = null;
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // Login form
        const loginForm = document.getElementById('loginFormEl');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }
        
        // Register form
        const registerForm = document.getElementById('registerFormEl');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }
        
        // Auth form switches
        const showRegister = document.getElementById('showRegister');
        const showLogin = document.getElementById('showLogin');
        
        if (showRegister) {
            showRegister.addEventListener('click', (e) => {
                e.preventDefault();
                this.showRegisterForm();
            });
        }
        
        if (showLogin) {
            showLogin.addEventListener('click', (e) => {
                e.preventDefault();
                this.showLoginForm();
            });
        }
        
        // Logout button
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }
    }
    
    // Handle login
    async handleLogin(event) {
        event.preventDefault();
        
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        
        if (!Utils.validateEmail(email)) {
            Utils.showToast('Por favor ingresa un email válido', 'error');
            return;
        }
        
        if (!password) {
            Utils.showToast('Por favor ingresa tu contraseña', 'error');
            return;
        }
        
        try {
            Utils.showLoading('Iniciando sesión...');
            
            const response = await this.api.login({ email, password });
            
            // Guardar el JWT si existe en la respuesta
            if (response.access_token) {
                Utils.setStorage(CONFIG.STORAGE_KEYS.JWT_TOKEN, response.access_token);
                window.lastJwtToken = response.access_token;
            }
            
            if (response.user && response.user.api_key) {
                // Store user data
                Utils.setStorage(CONFIG.STORAGE_KEYS.API_KEY, response.user.api_key);
                Utils.setStorage(CONFIG.STORAGE_KEYS.USER_EMAIL, response.user.email);
                Utils.setStorage(CONFIG.STORAGE_KEYS.USER_NAME, response.user.full_name);
                
                // Update UI
                this.userProfile = response.user;
                this.showAuthenticatedView();
                
                Utils.showToast('¡Bienvenido de nuevo!', 'success');
                
                // Load user profile data
                await this.loadUserProfile();
                
            } else {
                throw new Error('Respuesta inválida del servidor');
            }
            
        } catch (error) {
            console.error('Login error:', error);
            Utils.showToast(error.message || 'Error al iniciar sesión', 'error');
        } finally {
            Utils.hideLoading();
        }
    }
    
    // Handle register
    async handleRegister(event) {
        event.preventDefault();
        
        const name = document.getElementById('registerName').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        
        if (!name.trim()) {
            Utils.showToast('Por favor ingresa tu nombre', 'error');
            return;
        }
        
        if (!Utils.validateEmail(email)) {
            Utils.showToast('Por favor ingresa un email válido', 'error');
            return;
        }
        
        if (password.length < 6) {
            Utils.showToast('La contraseña debe tener al menos 6 caracteres', 'error');
            return;
        }
        
        try {
            Utils.showLoading('Creando cuenta...');
            
            const response = await this.api.register({
                email,
                password,
                full_name: name
            });
            
            // Guardar el JWT si existe en la respuesta
            if (response.access_token) {
                Utils.setStorage(CONFIG.STORAGE_KEYS.JWT_TOKEN, response.access_token);
                window.lastJwtToken = response.access_token;
            }
            
            if (response.user && response.user.api_key) {
                // Store user data
                Utils.setStorage(CONFIG.STORAGE_KEYS.API_KEY, response.user.api_key);
                Utils.setStorage(CONFIG.STORAGE_KEYS.USER_EMAIL, response.user.email);
                Utils.setStorage(CONFIG.STORAGE_KEYS.USER_NAME, response.user.full_name);
                
                // Update UI
                this.userProfile = response.user;
                this.showAuthenticatedView();
                
                Utils.showToast('¡Cuenta creada exitosamente!', 'success');
                
                // Load user profile data
                await this.loadUserProfile();
                
            } else {
                throw new Error('Respuesta inválida del servidor');
            }
            
        } catch (error) {
            console.error('Register error:', error);
            Utils.showToast(error.message || 'Error al crear la cuenta', 'error');
        } finally {
            Utils.hideLoading();
        }
    }
    
    // Load user profile
    async loadUserProfile() {
        try {
            const profile = await this.api.getProfile();
            this.userProfile = profile;
            this.updateProfileDisplay();
        } catch (error) {
            console.error('Error loading profile:', error);
        }
    }
    
    // Update profile display
    updateProfileDisplay() {
        if (!this.userProfile) return;
        
        // Update navigation
        const userEmail = document.getElementById('userEmail');
        const userUsage = document.getElementById('userUsage');
        
        if (userEmail) {
            userEmail.textContent = this.userProfile.email;
        }
        
        if (userUsage) {
            const remaining = this.userProfile.usage_limit - this.userProfile.usage_count;
            userUsage.textContent = `${remaining} restantes`;
        }
        
        // Update profile section
        const welcomeUser = document.getElementById('welcomeUser');
        const usageCount = document.getElementById('usageCount');
        const remainingUses = document.getElementById('remainingUses');
        
        if (welcomeUser) {
            const name = this.userProfile.full_name || this.userProfile.email.split('@')[0];
            welcomeUser.textContent = `Bienvenido, ${name}`;
        }
        
        if (usageCount) {
            usageCount.textContent = this.userProfile.usage_count || 0;
        }
        
        if (remainingUses) {
            const remaining = (this.userProfile.usage_limit || 100) - (this.userProfile.usage_count || 0);
            remainingUses.textContent = remaining;
        }
        // Mostrar el JWT en el campo visual y permitir copiarlo
        const userApiKey = document.getElementById('userApiKey');
        const copyApiKey = document.getElementById('copyApiKey');
        let jwtToken = '';
        // Prioridad: último token recibido en login/registro
        if (window.lastJwtToken && typeof window.lastJwtToken === 'string') {
            jwtToken = window.lastJwtToken;
        } else {
            jwtToken = Utils.getStorage(CONFIG.STORAGE_KEYS.JWT_TOKEN, '');
        }
        if (userApiKey) {
            userApiKey.value = jwtToken;
        }
        if (copyApiKey) {
            copyApiKey.onclick = () => {
                if (userApiKey && userApiKey.value) {
                    navigator.clipboard.writeText(userApiKey.value);
                    Utils.showToast('API Key copiada al portapapeles', 'success');
                }
            };
        }
    }
    
    // Show register form
    showRegisterForm() {
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');
        
        if (loginForm && registerForm) {
            loginForm.classList.add('hidden');
            registerForm.classList.remove('hidden');
        }
    }
    
    // Show login form
    showLoginForm() {
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');
        
        if (loginForm && registerForm) {
            registerForm.classList.add('hidden');
            loginForm.classList.remove('hidden');
        }
    }
    
    // Show authenticated view
    showAuthenticatedView() {
        const authSection = document.getElementById('authSection');
        const appSection = document.getElementById('appSection');
        const navAuth = document.getElementById('navAuth');
        
        if (authSection) {
            authSection.classList.add('hidden');
        }
        
        if (appSection) {
            appSection.classList.remove('hidden');
        }
        
        if (navAuth) {
            navAuth.classList.remove('hidden');
        }
        
        this.updateProfileDisplay();
    }
    
    // Show unauthenticated view
    showUnauthenticatedView() {
        const authSection = document.getElementById('authSection');
        const appSection = document.getElementById('appSection');
        const navAuth = document.getElementById('navAuth');
        
        if (authSection) {
            authSection.classList.remove('hidden');
        }
        
        if (appSection) {
            appSection.classList.add('hidden');
        }
        
        if (navAuth) {
            navAuth.classList.add('hidden');
        }
    }
    
    // Logout
    logout() {
        Utils.clearUserData();
        this.userProfile = null;
        this.showUnauthenticatedView();
        
        // Clear forms
        const loginForm = document.getElementById('loginFormEl');
        const registerForm = document.getElementById('registerFormEl');
        
        if (loginForm) {
            loginForm.reset();
        }
        
        if (registerForm) {
            registerForm.reset();
        }
        
        Utils.showToast('Sesión cerrada correctamente', 'info');
    }
    
    // Check if user is authenticated
    isAuthenticated() {
        return Utils.isLoggedIn();
    }
    
    // Get current user
    getCurrentUser() {
        return this.userProfile || Utils.getUserInfo();
    }
    
    // Initialize auth state
    async initializeAuthState() {
        // Check if auth is enabled
        if (!CONFIG.AUTH_ENABLED) {
            // Skip auth and go directly to app
            this.showAuthenticatedView();
            this.updateProfileDisplayNoAuth();
            return;
        }
        
        if (this.isAuthenticated()) {
            try {
                await this.loadUserProfile();
                this.showAuthenticatedView();
            } catch (error) {
                console.error('Error initializing auth state:', error);
                // Token might be expired, logout user
                this.logout();
            }
        } else {
            this.showUnauthenticatedView();
        }
    }
    
    // Update profile display when no auth
    updateProfileDisplayNoAuth() {
        // Update navigation
        const userEmail = document.getElementById('userEmail');
        const userUsage = document.getElementById('userUsage');
        
        if (userEmail) {
            userEmail.textContent = 'Usuario Anónimo';
        }
        
        if (userUsage) {
            userUsage.textContent = 'Sin límites';
        }
        
        // Update profile section
        const welcomeUser = document.getElementById('welcomeUser');
        const usageCount = document.getElementById('usageCount');
        const remainingUses = document.getElementById('remainingUses');
        
        if (welcomeUser) {
            welcomeUser.textContent = 'Bienvenido, Usuario Anónimo';
        }
        
        if (usageCount) {
            usageCount.textContent = '∞';
        }
        
        if (remainingUses) {
            remainingUses.textContent = '∞';
        }
    }
}
