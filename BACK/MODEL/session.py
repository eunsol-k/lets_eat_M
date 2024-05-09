from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from configs.DB_config import DB_URL

Database = create_engine(DB_URL, max_overflow=0)
Session = sessionmaker(autocommit=False, autoflush=False, bind=Database)