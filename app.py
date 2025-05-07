from flask import Flask
from config import Config
from utils.models import db
from utils.routes import auth_bp
from flask_jwt_extended import  JWTManager
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    jwt = JWTManager(app)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)