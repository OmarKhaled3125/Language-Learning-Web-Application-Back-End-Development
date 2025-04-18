// Image Upload Component
class ImageUpload {
    constructor(dropZoneId, inputId, previewId) {
        this.dropZone = document.getElementById(dropZoneId);
        this.input = document.getElementById(inputId);
        this.preview = document.getElementById(previewId);
        
        if (!this.dropZone || !this.input || !this.preview) return;
        
        this.initialize();
    }
    
    initialize() {
        this.setupDragAndDrop();
        this.setupClickHandler();
        this.setupImagePreview();
    }
    
    setupDragAndDrop() {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, this.preventDefaults.bind(this), false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, this.highlight.bind(this), false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, this.unhighlight.bind(this), false);
        });
        
        this.dropZone.addEventListener('drop', this.handleDrop.bind(this), false);
    }
    
    setupClickHandler() {
        this.dropZone.addEventListener('click', () => {
            this.input.click();
        });
    }
    
    setupImagePreview() {
        this.input.addEventListener('change', () => {
            const file = this.input.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    this.preview.src = e.target.result;
                    this.preview.parentElement.hidden = false;
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    highlight() {
        this.dropZone.classList.add('dragover');
    }
    
    unhighlight() {
        this.dropZone.classList.remove('dragover');
    }
    
    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        this.input.files = files;
        const event = new Event('change');
        this.input.dispatchEvent(event);
    }
}

// Modal Component
class Modal {
    constructor(modalId) {
        this.modal = document.getElementById(modalId);
        this.instance = null;
        
        if (!this.modal) return;
        
        this.initialize();
    }
    
    initialize() {
        this.instance = new bootstrap.Modal(this.modal);
    }
    
    show() {
        if (this.instance) {
            this.instance.show();
        }
    }
    
    hide() {
        if (this.instance) {
            this.instance.hide();
        }
    }
    
    dispose() {
        if (this.instance) {
            this.instance.dispose();
        }
    }
}

// Alert Component
class Alert {
    constructor(message, type = 'success', duration = 5000) {
        this.message = message;
        this.type = type;
        this.duration = duration;
        this.alert = null;
        
        this.show();
    }
    
    show() {
        this.alert = document.createElement('div');
        this.alert.className = `alert alert-${this.type} alert-dismissible fade show`;
        this.alert.role = 'alert';
        
        this.alert.innerHTML = `
            ${this.message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.querySelector('.main-content').prepend(this.alert);
        
        if (this.duration > 0) {
            setTimeout(() => {
                this.hide();
            }, this.duration);
        }
    }
    
    hide() {
        if (this.alert) {
            const bsAlert = new bootstrap.Alert(this.alert);
            bsAlert.close();
        }
    }
}

// Table Component
class Table {
    constructor(tableId, options = {}) {
        this.table = document.getElementById(tableId);
        this.options = {
            sortable: options.sortable || false,
            searchable: options.searchable || false,
            pagination: options.pagination || false,
            ...options
        };
        
        if (!this.table) return;
        
        this.initialize();
    }
    
    initialize() {
        if (this.options.sortable) {
            this.setupSorting();
        }
        
        if (this.options.searchable) {
            this.setupSearch();
        }
        
        if (this.options.pagination) {
            this.setupPagination();
        }
    }
    
    setupSorting() {
        const headers = this.table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                this.sortTable(header.dataset.sort);
            });
        });
    }
    
    setupSearch() {
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.className = 'form-control mb-3';
        searchInput.placeholder = 'Search...';
        
        this.table.parentElement.insertBefore(searchInput, this.table);
        
        searchInput.addEventListener('input', (e) => {
            this.filterTable(e.target.value);
        });
    }
    
    setupPagination() {
        // Implementation depends on specific requirements
    }
    
    sortTable(column) {
        // Implementation depends on specific requirements
    }
    
    filterTable(searchTerm) {
        // Implementation depends on specific requirements
    }
}

// Initialize components when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize image upload components
    document.querySelectorAll('.image-drop-zone').forEach(dropZone => {
        const id = dropZone.id.replace('DropZone', '');
        new ImageUpload(
            `${id}DropZone`,
            `${id}Input`,
            `${id}PreviewImg`
        );
    });
    
    // Initialize modals
    document.querySelectorAll('.modal').forEach(modal => {
        new Modal(modal.id);
    });
}); 