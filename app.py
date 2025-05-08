from flask import Flask,jsonify
from config import Config
from utils.models import db
from utils.routes import auth_bp
from flask_jwt_extended import  JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    with app.app_context():
        db.create_all()

    return app

app = create_app()
CORS(app, resources={
    r"/*" : {
    "origins":
        "*"
        }
    }
)
@app.route('/')
def hello_world():
    return jsonify(message="Hello World"), 200

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')