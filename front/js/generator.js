// Image Generator Manager
class ImageGenerator {
    constructor() {
        this.api = new APIClient();
        this.isGenerating = false;
        this.currentGeneration = null;
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // Generate form
        const generateForm = document.getElementById('generateForm');
        if (generateForm) {
            generateForm.addEventListener('submit', (e) => this.handleGenerate(e));
        }
        
        // Download button
        const downloadImage = document.getElementById('downloadImage');
        if (downloadImage) {
            downloadImage.addEventListener('click', () => this.downloadCurrentImage());
        }
        
        // Generate another button
        const generateAnother = document.getElementById('generateAnother');
        if (generateAnother) {
            generateAnother.addEventListener('click', () => this.generateAnother());
        }
        
        // Image preview click (open modal)
        const generatedImage = document.getElementById('generatedImage');
        if (generatedImage) {
            generatedImage.addEventListener('click', () => this.openImageModal());
        }
    }
    
    // Handle image generation
    async handleGenerate(event) {
        event.preventDefault();
        
        if (this.isGenerating) {
            Utils.showToast('Ya se está generando una imagen', 'warning');
            return;
        }
        
        const prompt = document.getElementById('promptText').value.trim();
        const width = parseInt(document.getElementById('imageWidth').value);
        const height = parseInt(document.getElementById('imageHeight').value);
        
        if (!prompt) {
            Utils.showToast('Por favor describe la imagen que quieres generar', 'error');
            return;
        }
        
        if (prompt.length < 10) {
            Utils.showToast('La descripción debe tener al menos 10 caracteres', 'error');
            return;
        }
        
        try {
            this.isGenerating = true;
            this.updateGenerateButton(true);
            Utils.showLoading('Generando imagen...');
            
            const imageData = {
                prompt: prompt,
                width: width,
                height: height
            };
            
            const response = await this.api.generateImage(imageData);
            
            if (response.success && response.image_url) {
                // Store current generation
                this.currentGeneration = {
                    ...response,
                    prompt: prompt,
                    width: width,
                    height: height,
                    timestamp: new Date().toISOString()
                };
                
                // Show generated image
                this.showGeneratedImage(response);
                
                // Update usage count if available
                if (response.usage_count !== undefined) {
                    this.updateUsageCount(response.usage_count);
                }
                
                // Save to local storage for gallery
                this.saveImageToLocal(this.currentGeneration);
                
                Utils.showToast('¡Imagen generada exitosamente!', 'success');
                
            } else {
                throw new Error(response.message || 'Error al generar la imagen');
            }
            
        } catch (error) {
            console.error('Generation error:', error);
            Utils.showToast(error.message || 'Error al generar la imagen', 'error');
        } finally {
            this.isGenerating = false;
            this.updateGenerateButton(false);
            Utils.hideLoading();
        }
    }
    
    // Show generated image
    showGeneratedImage(response) {
        const imagePreview = document.getElementById('imagePreview');
        const generatedImage = document.getElementById('generatedImage');
        if (imagePreview && generatedImage) {
            // Usar la URL absoluta del backend para mostrar la imagen generada
            const imageUrl = this.api.getImageUrl(response.filename);
            generatedImage.src = imageUrl;
            generatedImage.alt = response.prompt || 'Imagen generada';
            imagePreview.classList.remove('hidden');
            // Scroll to preview
            Utils.scrollToElement(imagePreview, 100);
        }
    }
    
    // Update generate button state
    updateGenerateButton(isGenerating) {
        const generateButton = document.querySelector('.btn-generate');
        if (generateButton) {
            if (isGenerating) {
                generateButton.disabled = true;
                generateButton.innerHTML = `
                    <i class="fas fa-spinner fa-spin"></i>
                    Generando...
                `;
            } else {
                generateButton.disabled = false;
                generateButton.innerHTML = `
                    <i class="fas fa-magic"></i>
                    Generar Imagen
                `;
            }
        }
    }
    
    // Update usage count display
    updateUsageCount(usageCount) {
        const usageCountEl = document.getElementById('usageCount');
        const remainingUsesEl = document.getElementById('remainingUses');
        const userUsage = document.getElementById('userUsage');
        
        if (usageCountEl) {
            usageCountEl.textContent = usageCount;
        }
        
        // Assuming default limit of 100, update when we have profile data
        const limit = 100;
        const remaining = limit - usageCount;
        
        if (remainingUsesEl) {
            remainingUsesEl.textContent = remaining;
        }
        
        if (userUsage) {
            userUsage.textContent = `${remaining} restantes`;
        }
    }
    
    // Download current image
    async downloadCurrentImage() {
        if (!this.currentGeneration) {
            Utils.showToast('No hay imagen para descargar', 'error');
            return;
        }
        
        try {
            Utils.showLoading('Descargando imagen...');
            
            const filename = this.currentGeneration.filename || 
                            Utils.generateFilename(this.currentGeneration.prompt);
            
            // Create download link
            const link = document.createElement('a');
            link.href = this.currentGeneration.image_url;
            link.download = filename;
            link.target = '_blank';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            Utils.showToast('Imagen descargada', 'success');
            
        } catch (error) {
            console.error('Download error:', error);
            Utils.showToast('Error al descargar la imagen', 'error');
        } finally {
            Utils.hideLoading();
        }
    }
    
    // Generate another image (clear current and focus on form)
    generateAnother() {
        const imagePreview = document.getElementById('imagePreview');
        const promptText = document.getElementById('promptText');
        
        if (imagePreview) {
            imagePreview.classList.add('hidden');
        }
        
        if (promptText) {
            promptText.focus();
            promptText.select();
        }
        
        this.currentGeneration = null;
    }
    
    // Open image modal
    openImageModal() {
        if (!this.currentGeneration) return;
        
        const modal = document.getElementById('imageModal');
        const modalImage = document.getElementById('modalImage');
        const modalPrompt = document.getElementById('modalPrompt');
        const modalDownload = document.getElementById('modalDownload');
        
        if (modal && modalImage && modalPrompt) {
            modalImage.src = this.currentGeneration.image_url;
            modalImage.alt = this.currentGeneration.prompt;
            modalPrompt.textContent = this.currentGeneration.prompt;
            
            modal.classList.remove('hidden');
            
            // Close modal handlers
            const closeModal = () => {
                modal.classList.add('hidden');
            };
            
            modal.addEventListener('click', (e) => {
                if (e.target === modal) closeModal();
            });
            
            const modalClose = modal.querySelector('.modal-close');
            if (modalClose) {
                modalClose.onclick = closeModal;
            }
            
            // Download from modal
            if (modalDownload) {
                modalDownload.onclick = () => {
                    this.downloadCurrentImage();
                    closeModal();
                };
            }
            
            // ESC key to close
            const escapeHandler = (e) => {
                if (e.key === 'Escape') {
                    closeModal();
                    document.removeEventListener('keydown', escapeHandler);
                }
            };
            document.addEventListener('keydown', escapeHandler);
        }
    }
    
    // Save image to local storage for gallery
    saveImageToLocal(imageData) {
        try {
            let savedImages = Utils.getStorage(CONFIG.STORAGE_KEYS.GENERATED_IMAGES, []);
            
            // Add new image to beginning
            savedImages.unshift({
                id: Utils.generateId(),
                prompt: imageData.prompt,
                image_url: imageData.image_url,
                filename: imageData.filename,
                width: imageData.width,
                height: imageData.height,
                timestamp: imageData.timestamp,
                usage_count: imageData.usage_count
            });
            
            // Limit stored images
            if (savedImages.length > CONFIG.DEFAULT_SETTINGS.MAX_STORED_IMAGES) {
                savedImages = savedImages.slice(0, CONFIG.DEFAULT_SETTINGS.MAX_STORED_IMAGES);
            }
            
            Utils.setStorage(CONFIG.STORAGE_KEYS.GENERATED_IMAGES, savedImages);
            
            // Notify gallery to update
            if (window.imageGallery) {
                window.imageGallery.refreshGallery();
            }
            
        } catch (error) {
            console.error('Error saving image to local storage:', error);
        }
    }
    
    // Get current generation
    getCurrentGeneration() {
        return this.currentGeneration;
    }
    
    // Clear current generation
    clearCurrentGeneration() {
        this.currentGeneration = null;
        const imagePreview = document.getElementById('imagePreview');
        if (imagePreview) {
            imagePreview.classList.add('hidden');
        }
    }
    
    // Validate generation parameters
    validateParameters(prompt, width, height) {
        const errors = [];
        
        if (!prompt || prompt.length < 10) {
            errors.push('La descripción debe tener al menos 10 caracteres');
        }
        
        if (prompt && prompt.length > 500) {
            errors.push('La descripción no puede exceder 500 caracteres');
        }
        
        const validSizes = [256, 512, 768, 1024];
        if (!validSizes.includes(width)) {
            errors.push('Ancho inválido');
        }
        
        if (!validSizes.includes(height)) {
            errors.push('Alto inválido');
        }
        
        return errors;
    }
}
