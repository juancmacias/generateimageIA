// Image Gallery Manager
class ImageGallery {
    constructor() {
        this.api = new APIClient();
        this.images = [];
        this.currentModal = null;
        this.initializeEventListeners();
        this.loadGallery();
    }
    
    initializeEventListeners() {
        // Refresh gallery button
        const refreshButton = document.getElementById('refreshGallery');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => this.refreshGallery());
        }
        
        // Modal close events
        const imageModal = document.getElementById('imageModal');
        if (imageModal) {
            imageModal.addEventListener('click', (e) => {
                if (e.target === imageModal) {
                    this.closeModal();
                }
            });
            
            const modalClose = imageModal.querySelector('.modal-close');
            if (modalClose) {
                modalClose.addEventListener('click', () => this.closeModal());
            }
        }
        
        // ESC key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.currentModal) {
                this.closeModal();
            }
        });
    }
    
    // Load gallery from local storage
    loadGallery() {
        this.images = Utils.getStorage(CONFIG.STORAGE_KEYS.GENERATED_IMAGES, []);
        this.renderGallery();
    }
    
    // Refresh gallery
    refreshGallery() {
        const refreshButton = document.getElementById('refreshGallery');
        if (refreshButton) {
            const originalHTML = refreshButton.innerHTML;
            refreshButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Actualizando';
            refreshButton.disabled = true;
            
            setTimeout(() => {
                this.loadGallery();
                refreshButton.innerHTML = originalHTML;
                refreshButton.disabled = false;
                Utils.showToast('Galería actualizada', 'info');
            }, 500);
        } else {
            this.loadGallery();
        }
    }
    
    // Render gallery
    renderGallery() {
        const gallery = document.getElementById('imageGallery');
        if (!gallery) return;
        
        if (this.images.length === 0) {
            gallery.innerHTML = `
                <div class="gallery-empty">
                    <i class="fas fa-images"></i>
                    <p>Aún no has generado ninguna imagen</p>
                    <p>¡Crea tu primera imagen arriba!</p>
                </div>
            `;
            return;
        }
        
        gallery.innerHTML = this.images.map((image, index) => 
            this.createImageCard(image, index)
        ).join('');
        
        // Add event listeners to gallery items
        this.addGalleryEventListeners();
    }
    
    // Create image card HTML
    createImageCard(image, index) {
        const truncatedPrompt = Utils.truncateText(image.prompt, 80);
        const formattedDate = Utils.formatDate(image.timestamp);
        const imageUrl = this.api.getImageUrl(image.filename);
        
        return `
            <div class="gallery-item" data-index="${index}">
                <img src="${imageUrl}" alt="${Utils.escapeHtml(image.prompt)}" loading="lazy">
                <div class="gallery-item-info">
                    <div class="gallery-item-prompt">${Utils.escapeHtml(truncatedPrompt)}</div>
                    <div class="gallery-item-date">${formattedDate}</div>
                    <div class="gallery-item-actions">
                        <button class="btn btn-outline btn-small gallery-view" data-index="${index}">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-secondary btn-small gallery-download" data-index="${index}">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="btn btn-outline btn-small gallery-delete" data-index="${index}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Add event listeners to gallery items
    addGalleryEventListeners() {
        const gallery = document.getElementById('imageGallery');
        if (!gallery) return;
        
        // View image
        gallery.addEventListener('click', (e) => {
            const viewBtn = e.target.closest('.gallery-view');
            if (viewBtn) {
                const index = parseInt(viewBtn.dataset.index);
                this.viewImage(index);
                return;
            }
            
            // Download image
            const downloadBtn = e.target.closest('.gallery-download');
            if (downloadBtn) {
                const index = parseInt(downloadBtn.dataset.index);
                this.downloadImage(index);
                return;
            }
            
            // Delete image
            const deleteBtn = e.target.closest('.gallery-delete');
            if (deleteBtn) {
                const index = parseInt(deleteBtn.dataset.index);
                this.deleteImage(index);
                return;
            }
            
            // Click on image itself
            const galleryItem = e.target.closest('.gallery-item');
            if (galleryItem && e.target.tagName === 'IMG') {
                const index = parseInt(galleryItem.dataset.index);
                this.viewImage(index);
            }
        });
    }
    
    // View image in modal
    viewImage(index) {
        const image = this.images[index];
        if (!image) return;
        
        const modal = document.getElementById('imageModal');
        const modalImage = document.getElementById('modalImage');
        const modalPrompt = document.getElementById('modalPrompt');
        const modalDownload = document.getElementById('modalDownload');
        
        if (modal && modalImage && modalPrompt) {
            const imageUrl = this.api.getImageUrl(image.filename);
            
            modalImage.src = imageUrl;
            modalImage.alt = image.prompt;
            modalPrompt.textContent = image.prompt;
            
            modal.classList.remove('hidden');
            this.currentModal = index;
            
            // Update download button
            if (modalDownload) {
                modalDownload.onclick = () => {
                    this.downloadImage(index);
                    this.closeModal();
                };
            }
        }
    }
    
    // Download image
    async downloadImage(index) {
        const image = this.images[index];
        if (!image) return;
        
        try {
            Utils.showLoading('Descargando imagen...');
            
            const imageUrl = this.api.getImageUrl(image.filename);
            const filename = image.filename || Utils.generateFilename(image.prompt);
            
            // Create download link
            const link = document.createElement('a');
            link.href = imageUrl;
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
    
    // Delete image from gallery
    deleteImage(index) {
        const image = this.images[index];
        if (!image) return;
        
        const confirmation = confirm('¿Estás seguro de que quieres eliminar esta imagen de la galería?');
        if (!confirmation) return;
        
        try {
            // Remove from array
            this.images.splice(index, 1);
            
            // Update local storage
            Utils.setStorage(CONFIG.STORAGE_KEYS.GENERATED_IMAGES, this.images);
            
            // Re-render gallery
            this.renderGallery();
            
            Utils.showToast('Imagen eliminada de la galería', 'info');
            
        } catch (error) {
            console.error('Delete error:', error);
            Utils.showToast('Error al eliminar la imagen', 'error');
        }
    }
    
    // Close modal
    closeModal() {
        const modal = document.getElementById('imageModal');
        if (modal) {
            modal.classList.add('hidden');
        }
        this.currentModal = null;
    }
    
    // Add new image to gallery
    addImage(imageData) {
        const newImage = {
            id: Utils.generateId(),
            prompt: imageData.prompt,
            image_url: imageData.image_url,
            filename: imageData.filename,
            width: imageData.width,
            height: imageData.height,
            timestamp: imageData.timestamp || new Date().toISOString(),
            usage_count: imageData.usage_count
        };
        
        // Add to beginning of array
        this.images.unshift(newImage);
        
        // Limit stored images
        if (this.images.length > CONFIG.DEFAULT_SETTINGS.MAX_STORED_IMAGES) {
            this.images = this.images.slice(0, CONFIG.DEFAULT_SETTINGS.MAX_STORED_IMAGES);
        }
        
        // Update local storage
        Utils.setStorage(CONFIG.STORAGE_KEYS.GENERATED_IMAGES, this.images);
        
        // Re-render gallery
        this.renderGallery();
    }
    
    // Clear all images
    clearGallery() {
        const confirmation = confirm('¿Estás seguro de que quieres limpiar toda la galería?');
        if (!confirmation) return;
        
        this.images = [];
        Utils.setStorage(CONFIG.STORAGE_KEYS.GENERATED_IMAGES, []);
        this.renderGallery();
        
        Utils.showToast('Galería limpiada', 'info');
    }
    
    // Get gallery statistics
    getStatistics() {
        return {
            totalImages: this.images.length,
            oldestImage: this.images.length > 0 ? this.images[this.images.length - 1].timestamp : null,
            newestImage: this.images.length > 0 ? this.images[0].timestamp : null,
            totalPrompts: this.images.length,
            uniquePrompts: new Set(this.images.map(img => img.prompt)).size
        };
    }
    
    // Search images by prompt
    searchImages(query) {
        if (!query.trim()) {
            this.renderGallery();
            return;
        }
        
        const filteredImages = this.images.filter(image => 
            image.prompt.toLowerCase().includes(query.toLowerCase())
        );
        
        this.renderFilteredGallery(filteredImages, query);
    }
    
    // Render filtered gallery
    renderFilteredGallery(filteredImages, query) {
        const gallery = document.getElementById('imageGallery');
        if (!gallery) return;
        
        if (filteredImages.length === 0) {
            gallery.innerHTML = `
                <div class="gallery-empty">
                    <i class="fas fa-search"></i>
                    <p>No se encontraron imágenes para "${Utils.escapeHtml(query)}"</p>
                    <p>Intenta con otros términos de búsqueda</p>
                </div>
            `;
            return;
        }
        
        gallery.innerHTML = filteredImages.map((image, index) => {
            // Find original index for event handlers
            const originalIndex = this.images.findIndex(img => img.id === image.id);
            return this.createImageCard(image, originalIndex);
        }).join('');
        
        // Add event listeners
        this.addGalleryEventListeners();
    }
    
    // Export gallery data
    exportGallery() {
        try {
            const data = {
                images: this.images,
                exported_at: new Date().toISOString(),
                version: '1.0'
            };
            
            const blob = new Blob([JSON.stringify(data, null, 2)], { 
                type: 'application/json' 
            });
            
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `image_gallery_${new Date().toISOString().split('T')[0]}.json`;
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            URL.revokeObjectURL(url);
            
            Utils.showToast('Galería exportada', 'success');
            
        } catch (error) {
            console.error('Export error:', error);
            Utils.showToast('Error al exportar la galería', 'error');
        }
    }
}
