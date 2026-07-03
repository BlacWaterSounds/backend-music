from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(String, primary_key=True)
    user_id = Column(String)
    prompt = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
