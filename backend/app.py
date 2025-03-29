from flask import Flask
from config import Config
from flask_jwt_extended import JWTManager
from models import db, bcrypt
from routes import api
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)  # ✅ Initialize JWT here
bcrypt.init_app(app)
jwt.init_app(app)

migrate = Migrate(app, db)

# Register API routes
app.register_blueprint(api)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)