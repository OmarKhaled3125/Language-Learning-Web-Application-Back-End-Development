
from typing import Any, Dict, Optional, Tuple
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import HTTPException


class BaseController:
    
    def __init__(self, name: str, import_name: str, url_prefix: Optional[str] = None):
     
        self.blueprint = Blueprint(name, import_name, url_prefix=url_prefix)
        self._register_error_handlers()
    
    def _register_error_handlers(self) -> None:
        """Register common error handlers for the blueprint."""
        @self.blueprint.errorhandler(HTTPException)
        def handle_http_error(error: HTTPException) -> Tuple[Dict[str, Any], int]:
            """Handle HTTP exceptions."""
            response = {
                'error': error.name,
                'message': error.description,
                'status_code': error.code
            }
            return jsonify(response), error.code
    
    def success_response(self, data: Any = None, message: str = "Success", status_code: int = 200) -> Tuple[Dict[str, Any], int]:
       
        response = {
            'status': 'success',
            'message': message,
            'data': data
        }
        return jsonify(response), status_code
    
    def error_response(self, message: str, status_code: int = 400, errors: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], int]:
        response = {
            'status': 'error',
            'message': message
        }
        if errors:
            response['errors'] = errors
        return jsonify(response), status_code
    
    def get_request_data(self) -> Dict[str, Any]:

        if request.is_json:
            return request.get_json()
        return request.form.to_dict() 