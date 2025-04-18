// Levels Page Controller
class LevelsController {
    constructor() {
        this.tableBody = document.getElementById('levelsTableBody');
        this.addForm = document.getElementById('addLevelForm');
        this.editForm = document.getElementById('editLevelForm');
        
        this.initialize();
    }
    
    initialize() {
        this.loadLevels();
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Add level form submit
        if (this.addForm) {
            this.addForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.addLevel();
            });
        }
        
        // Edit level form submit
        if (this.editForm) {
            this.editForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.updateLevel();
            });
        }
        
        // Delete confirmation
        document.querySelectorAll('.delete-level').forEach(button => {
            button.addEventListener('click', (e) => {
                const id = e.target.dataset.id;
                this.confirmDelete(id);
            });
        });
    }
    
    async loadLevels() {
        try {
            const response = await Utils.fetchData('/api/levels');
            this.renderLevels(response.data);
        } catch (error) {
            new Alert('Failed to load levels', 'danger');
        }
    }
    
    renderLevels(levels) {
        if (!this.tableBody) return;
        
        this.tableBody.innerHTML = '';
        
        levels.forEach(level => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${level.id}</td>
                <td>${level.name}</td>
                <td>${level.description}</td>
                <td>
                    <img src="${level.image_url}" alt="${level.name}" class="img-thumbnail" style="width: 50px; height: 50px;">
                </td>
                <td>
                    <div class="btn-group">
                        <button class="btn btn-sm btn-primary edit-level" data-id="${level.id}">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger delete-level" data-id="${level.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            
            this.tableBody.appendChild(row);
        });
        
        // Reattach event listeners
        this.setupEventListeners();
    }
    
    async addLevel() {
        try {
            const formData = new FormData(this.addForm);
            
            const response = await Utils.fetchData('/api/levels', {
                method: 'POST',
                body: formData
            });
            
            new Alert('Level added successfully', 'success');
            Utils.hideModal('addLevelModal');
            this.loadLevels();
            this.addForm.reset();
        } catch (error) {
            new Alert('Failed to add level', 'danger');
        }
    }
    
    async editLevel(id) {
        try {
            const response = await Utils.fetchData(`/api/levels/${id}`);
            const level = response.data;
            
            document.getElementById('editId').value = level.id;
            document.getElementById('editName').value = level.name;
            document.getElementById('editDescription').value = level.description;
            
            if (level.image_url) {
                document.getElementById('editPreviewImg').src = level.image_url;
                document.getElementById('editImagePreview').hidden = false;
            }
            
            Utils.showModal('editLevelModal');
        } catch (error) {
            new Alert('Failed to load level data', 'danger');
        }
    }
    
    async updateLevel() {
        try {
            const id = document.getElementById('editId').value;
            const formData = new FormData(this.editForm);
            
            const response = await Utils.fetchData(`/api/levels/${id}`, {
                method: 'PUT',
                body: formData
            });
            
            new Alert('Level updated successfully', 'success');
            Utils.hideModal('editLevelModal');
            this.loadLevels();
        } catch (error) {
            new Alert('Failed to update level', 'danger');
        }
    }
    
    async deleteLevel(id) {
        try {
            const response = await Utils.fetchData(`/api/levels/${id}`, {
                method: 'DELETE'
            });
            
            new Alert('Level deleted successfully', 'success');
            Utils.hideModal('deleteModal');
            this.loadLevels();
        } catch (error) {
            new Alert('Failed to delete level', 'danger');
        }
    }
    
    confirmDelete(id) {
        document.getElementById('deleteId').value = id;
        Utils.showModal('deleteModal');
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new LevelsController();
}); 