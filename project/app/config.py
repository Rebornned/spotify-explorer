import os
from dotenv import load_dotenv

# ====================================================
#           Configuração da Flask API
# ====================================================
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    
    # 2. Se não existir (Local), ele monta a string do MySQL usando seu código atual
    if not SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://"
            f"{os.getenv('DB_USER')}:"
            f"{os.getenv('DB_PASSWORD')}@"
            f"{os.getenv('DB_HOST')}:"
            f"{os.getenv('DB_PORT')}/"
            f"{os.getenv('DB_NAME')}"
        )
    # Log das consultas SQL apenas em desenvolvimento.
    # Em produção polui o log do servidor e expõe a estrutura interna do banco.
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "0") == "1"
    SQLALCHEMY_TRACK_MODIFICATIONS = False