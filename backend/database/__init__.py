import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# 数据库文件路径 - 指向项目中的 db.sql
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'db.sql')
DATABASE_URL = f"sqlite:///{DB_PATH}"

# 创建引擎
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)