from flask import Flask
from config import Config
from flask_jwt_extended import JWTManager
from models import db, bcrypt
from routes import api
from subject_routes import subject_bp
from chapter_routes import chapter_bp
from quiz_routes import quiz_bp
from question_routes import question_bp
from score_routes import score_bp
from summary_routes import summary_bp
from scheduled_jobs_routes import scheduled_jobs_bp
from flask_migrate import Migrate
from flask_cors import CORS, cross_origin
from celery_config import celery_app

app = Flask(__name__)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)  # ✅ Initialize JWT here
bcrypt.init_app(app)
jwt.init_app(app)

migrate = Migrate(app, db)

# Configure Celery
celery_app.conf.update(broker_url=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'))

# Make Celery work with Flask context
class ContextTask(celery_app.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery_app.Task = ContextTask

# Register API routes
app.register_blueprint(api)
app.register_blueprint(subject_bp)
app.register_blueprint(chapter_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(question_bp)
app.register_blueprint(score_bp)
app.register_blueprint(summary_bp)
app.register_blueprint(scheduled_jobs_bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)