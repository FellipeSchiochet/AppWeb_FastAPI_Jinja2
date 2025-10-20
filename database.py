# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Caminho do arquivo do banco SQLite
DATABASE_URL = "sqlite:///./itens.db"

# Cria o engine (conexão com o banco)
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Cria a fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

# Dependência (para usar nas rotas)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
