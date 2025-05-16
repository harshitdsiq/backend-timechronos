import os
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") 
    JWT_ALGORITHM = 'RS256'
    PRIVATE_KEY_PATH = os.path.join(os.path.dirname(__file__), 'private.pem')
    PUBLIC_KEY_PATH = os.path.join(os.path.dirname(__file__), 'public.pem')
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'  
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = 'noreply@yourdomain.com'
    with open(PRIVATE_KEY_PATH, 'r') as f:
        JWT_PRIVATE_KEY = f.read()

    with open(PUBLIC_KEY_PATH, 'r') as f:
        JWT_PUBLIC_KEY = f.read()

    