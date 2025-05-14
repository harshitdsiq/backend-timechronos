from flask import Flask,jsonify
from config import Config
from utils.schema.models import db
from utils.routes import auth_bp
from flask_jwt_extended import  JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
import os


def create_app():
    load_dotenv() 
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['JWT_ALGORITHM'] = app.config['JWT_ALGORITHM']
    app.config['JWT_PRIVATE_KEY'] = app.config['JWT_PRIVATE_KEY']
    app.config['JWT_PUBLIC_KEY'] = app.config['JWT_PUBLIC_KEY']
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  
    
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



from utils.api.authentication.auth_helper import auth_helper
app.register_blueprint(auth_helper)


from utils.api.company import company_bp
app.register_blueprint(company_bp)

from utils.api.client import client_bp
app.register_blueprint(client_bp)

from utils.api.projects import project_bp
app.register_blueprint(project_bp)

from utils.api.tasks import task_bp
app.register_blueprint(task_bp)


from utils.api.timesheets import timesheet_bp
app.register_blueprint(timesheet_bp)

from utils.api.users import user_bp
app.register_blueprint(user_bp)


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')