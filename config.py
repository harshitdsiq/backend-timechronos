import os
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY","kjkszpj")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dragon") 
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:first@localhost:5432/postgres"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    