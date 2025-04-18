// Component-specific JavaScript functionality

// Image Upload Component
function initImageUpload(containerId) {
    console.log('Initializing image upload for container:', containerId);
    
    const container = document.getElementById(containerId);
    if (!container) {
        console.warn(`Container not found: ${containerId}`);
        return null;
    }

    const input = container.querySelector('input[type="file"]');
    const preview = container.querySelector('.image-preview');
    const uploadContent = container.querySelector('.upload-content');
    
    if (!input || !preview || !uploadContent) {
        console.warn('Missing required elements:', {
            input: !!input,
            preview: !!preview,
            uploadContent: !!uploadContent
        });
        return null;
    }
    
    console.log('Image upload initialized successfully');
    return {
        clearImage: function() {
            clearImage(input.id);
        },
        getCurrentImage: function() {
            return input.files[0];
        }
    };
}
