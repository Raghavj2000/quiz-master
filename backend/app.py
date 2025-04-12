from flask import Flask
from config import Config
from flask_jwt_extended import JWTManager
from models import db, bcrypt
from routes import api
from subject_routes import subject_bp
from chapter_routes import chapter_bp
from flask_migrate import Migrate
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)  # ✅ Initialize JWT here
bcrypt.init_app(app)
jwt.init_app(app)

migrate = Migrate(app, db)

# Register API routes
app.register_blueprint(api)
app.register_blueprint(subject_bp)
app.register_blueprint(chapter_bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)