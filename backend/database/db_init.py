from sqlalchemy import create_engine
from .models import Base
import os


def init_database():
    """初始化数据库 - 连接到项目中的 db.sql"""
    # 确定项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    parent_dir = os.path.dirname(project_root)
    database_dir = os.path.join(parent_dir, 'database')
    db_path = os.path.join(database_dir, 'db.sql')

    # 创建数据库URL
    db_url = f"sqlite:///{db_path}"

    print(f"📁 数据库路径: {db_path}")

    # 创建引擎并初始化表
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)

    print("✅ 数据库初始化完成")
    return engine


def get_session(engine=None):
    """获取数据库会话"""
    from sqlalchemy.orm import sessionmaker

    if engine is None:
        engine = init_database()

    Session = sessionmaker(bind=engine)
    return Session()