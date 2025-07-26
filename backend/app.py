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
from export_routes import export_bp
from flask_migrate import Migrate
from flask_cors import CORS, cross_origin
from celery_init import celery_init_app
from celery.schedules import crontab

app = None

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    jwt = JWTManager(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate = Migrate(app, db)
    cors = CORS(app)
    app.app_context().push()
    return app

app = create_app()
celery = celery_init_app(app)
celery.autodiscover_tasks()



# Register API routes
app.register_blueprint(api)
app.register_blueprint(subject_bp)
app.register_blueprint(chapter_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(question_bp)
app.register_blueprint(score_bp)
app.register_blueprint(summary_bp)
app.register_blueprint(scheduled_jobs_bp)
app.register_blueprint(export_bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)