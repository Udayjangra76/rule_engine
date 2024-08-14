from flask import Flask, send_from_directory
from flask import jsonify
from .views import api_bp
from .models import db
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
migrate = Migrate()
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
def create_app():
    app = Flask(__name__, static_folder='static')
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    db.init_app(app)
    app.register_blueprint(api_bp)
    

    migrate.init_app(app, db)

    @app.route('/')
    def index():
        return send_from_directory('static', 'index.html')

    return app
