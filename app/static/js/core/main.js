// Load levels when the page loads
document.addEventListener('DOMContentLoaded', () => {
    loadLevels();
    initializeImageDropZones();
});

// Initialize image drop zones
function initializeImageDropZones() {
    setupDropZone('imageDropZone', 'imageInput', 'imagePreview', 'previewImg');
    setupDropZone('editImageDropZone', 'editImageInput', 'editImagePreview', 'editPreviewImg');
}

// Setup drop zone functionality
function setupDropZone(dropZoneId, inputId, previewId, previewImgId) {
    const dropZone = document.getElementById(dropZoneId);
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    const previewImg = document.getElementById(previewImgId);
    
    // Click to select file
    dropZone.addEventListener('click', () => input.click());
    
    // Handle file selection
    input.addEventListener('change', () => {
        handleFiles(input.files, preview, previewImg);
    });
    
    // Drag and drop events
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files, preview, previewImg);
    });
    
    // Remove image button
    const removeBtn = preview.querySelector('.remove-image');
    if (removeBtn) {
        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            input.value = '';
            preview.hidden = true;
            dropZone.querySelector('.drop-zone-prompt').hidden = false;
        });
    }
}

// Handle dropped or selected files
function handleFiles(files, preview, previewImg) {
    if (files.length === 0) return;
    
    const file = files[0];
    if (!file.type.startsWith('image/')) {
        showErrorMessage('Please select an image file');
        return;
    }

    // Check file size (limit to 5MB)
    const maxSize = 5 * 1024 * 1024; // 5MB in bytes
    if (file.size > maxSize) {
        showErrorMessage('Image file is too large. Maximum size is 5MB.');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = () => {
        previewImg.src = reader.result;
        preview.hidden = false;
        preview.parentElement.querySelector('.drop-zone-prompt').hidden = true;
    };
    reader.readAsDataURL(file);
}

// Load all levels
async function loadLevels() {
    try {
        const response = await fetch('/api/levels/');
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        const levels = await response.json();
        const tableBody = document.getElementById('levelsTableBody');
        tableBody.innerHTML = '';

        if (levels.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center">No levels found</td>
                </tr>
            `;
            return;
        }

        levels.forEach(level => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${level.id}</td>
                <td>${level.name}</td>
                <td>${level.description || ''}</td>
                <td>${level.image ? `<img src="${level.image}" alt="${level.name}" onerror="this.src='static/img/placeholder.png';" style="max-height: 50px;">` : ''}</td>
                <td class="action-buttons">
                    <button class="btn btn-sm btn-primary" onclick="editLevel(${level.id})">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="showDeleteModal(${level.id})">Delete</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading levels:', error);
        showErrorMessage('Failed to load levels. Please try again later.');
    }
}

// Show error message in a more user-friendly way
function showErrorMessage(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show';
    errorDiv.role = 'alert';
    errorDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.querySelector('main').insertBefore(errorDiv, document.querySelector('main').firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = bootstrap.Alert.getOrCreateInstance(errorDiv);
        alert.close();
    }, 5000);
}

// Upload image and return URL
async function uploadImage(file) {
    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await fetch('/api/levels/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to upload image');
        }

        const data = await response.json();
        return data.url;
    } catch (error) {
        console.error('Error uploading image:', error);
        throw new Error('Failed to upload image. Please try again.');
    }
}

// Show success message
function showSuccessMessage(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'alert alert-success alert-dismissible fade show';
    successDiv.role = 'alert';
    successDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.querySelector('main').insertBefore(successDiv, document.querySelector('main').firstChild);
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        const alert = bootstrap.Alert.getOrCreateInstance(successDiv);
        alert.close();
    }, 3000);
}

// Show edit modal with level data
async function editLevel(id) {
    try {
        const response = await fetch(`/api/levels/${id}`);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Failed to load level details`);
        }
        
        const level = await response.json();
        document.getElementById('editId').value = level.id;
        document.getElementById('editName').value = level.name;
        document.getElementById('editDescription').value = level.description || '';
        
        // Set up image preview if there's an existing image
        if (level.image) {
            const previewImg = document.getElementById('editPreviewImg');
            previewImg.src = level.image;
            document.getElementById('editImagePreview').hidden = false;
            document.querySelector('#editImageDropZone .drop-zone-prompt').hidden = true;
        }

        const modal = new bootstrap.Modal(document.getElementById('editLevelModal'));
        modal.show();
    } catch (error) {
        console.error('Error loading level:', error);
        showErrorMessage(error.message || 'Failed to load level details. Please try again.');
    }
}

// Update level
async function updateLevel() {
    const id = document.getElementById('editId').value;
    const name = document.getElementById('editName').value.trim();
    const description = document.getElementById('editDescription').value.trim();
    const imageInput = document.getElementById('editImageInput');

    if (!name) {
        showErrorMessage('Level name is required');
        return;
    }

    try {
        let imageUrl = '';
        // If there's a new file selected, upload it
        if (imageInput.files.length > 0) {
            imageUrl = await uploadImage(imageInput.files[0]);
        } else {
            // If no new file is selected, keep the existing image URL if it exists
            const previewImg = document.getElementById('editPreviewImg');
            // Only use the src if it's not a data URL (base64)
            if (previewImg.src && !previewImg.src.startsWith('data:')) {
                const url = new URL(previewImg.src, window.location.origin);
                imageUrl = url.pathname;
            }
        }

        const response = await fetch(`/api/levels/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name,
                description,
                image: imageUrl
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to update level');
        }

        // Close modal and refresh table
        const modal = bootstrap.Modal.getInstance(document.getElementById('editLevelModal'));
        modal.hide();
        await loadLevels();
        showSuccessMessage('Level updated successfully');
    } catch (error) {
        console.error('Error updating level:', error);
        showErrorMessage(error.message || 'Failed to update level. Please try again.');
    }
}

// Show delete confirmation modal
function showDeleteModal(id) {
    document.getElementById('deleteId').value = id;
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
    modal.show();
}

// Delete level
async function confirmDelete() {
    const id = document.getElementById('deleteId').value;

    try {
        const response = await fetch(`/api/levels/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to delete level');
        }

        // Close modal and refresh table
        const modal = bootstrap.Modal.getInstance(document.getElementById('deleteModal'));
        modal.hide();
        await loadLevels();
        showSuccessMessage('Level deleted successfully');
    } catch (error) {
        console.error('Error deleting level:', error);
        showErrorMessage(error.message || 'Failed to delete level. Please try again.');
    }
}

// Add new level
async function addLevel() {
    const name = document.getElementById('name').value.trim();
    const description = document.getElementById('description').value.trim();
    const imageInput = document.getElementById('imageInput');
    
    if (!name) {
        showErrorMessage('Level name is required');
        return;
    }

    try {
        let imageUrl = '';
        if (imageInput.files.length > 0) {
            imageUrl = await uploadImage(imageInput.files[0]);
        }

        const response = await fetch('/api/levels/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name,
                description,
                image: imageUrl
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to add level');
        }

        // Close modal and refresh table
        const modal = bootstrap.Modal.getInstance(document.getElementById('addLevelModal'));
        modal.hide();
        document.getElementById('addLevelForm').reset();
        document.getElementById('imagePreview').hidden = true;
        document.querySelector('#imageDropZone .drop-zone-prompt').hidden = false;
        await loadLevels();
        showSuccessMessage('Level added successfully');
    } catch (error) {
        console.error('Error adding level:', error);
        showErrorMessage(error.message || 'Failed to add level. Please try again.');
    }
}

// Common functionality for the application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Image upload preview
    document.querySelectorAll('.image-drop-zone').forEach(function(dropZone) {
        const input = dropZone.querySelector('input[type="file"]');
        const preview = dropZone.querySelector('.image-preview');
        const previewImg = preview.querySelector('img');
        const prompt = dropZone.querySelector('.drop-zone-prompt');

        // Handle drag and drop
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });

        function highlight(e) {
            dropZone.classList.add('dragover');
        }

        function unhighlight(e) {
            dropZone.classList.remove('dragover');
        }

        dropZone.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFiles(files);
        }

        dropZone.addEventListener('click', () => {
            input.click();
        });

        input.addEventListener('change', function() {
            handleFiles(this.files);
        });

        function handleFiles(files) {
            if (files.length > 0) {
                const file = files[0];
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        previewImg.src = e.target.result;
                        preview.hidden = false;
                        prompt.hidden = true;
                    };
                    reader.readAsDataURL(file);
                }
            }
        }

        // Remove image
        const removeBtn = preview.querySelector('.remove-image');
        removeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            input.value = '';
            preview.hidden = true;
            prompt.hidden = false;
        });
    });
}); 