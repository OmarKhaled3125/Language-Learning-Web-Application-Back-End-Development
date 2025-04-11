from app.routes.levels import levels_bp
from app.routes.lessons import lessons_bp
print("Starting the Flask app")

from app import create_app
app = create_app()

#Base URL : http://127.0.0.1:5000

app.register_blueprint(levels_bp)
app.register_blueprint(lessons_bp)

if __name__ == "__main__":
    app.run(debug=True)



