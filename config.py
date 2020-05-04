class Config:
    SECRET_KEY = '81ecf14c61b12413867cfdc1c947fb53'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:2222@127.0.0.1:5432/ssn'
    SQLALCHEMY_TRACK_MODIFICATIONS = False