class GeneralService:
    @staticmethod
    def get_all(endpoint):
        return {"message": f"Get all {endpoint}"}

    @staticmethod
    def create(endpoint):
        return {"message": f"Create {endpoint}"}

    @staticmethod
    def get_by_id(endpoint, id):
        return {"message": f"Get {endpoint} with id {id}"}

    @staticmethod
    def update_by_id(endpoint, id):
        return {"message": f"Edit {endpoint} with id {id}"}

    @staticmethod
    def delete_by_id(endpoint, id):
        return {"message": f"Delete {endpoint} with id {id}"}

    @staticmethod
    def upload_file():
        return {"message": "File uploaded successfully"} 