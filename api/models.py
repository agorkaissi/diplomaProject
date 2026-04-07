from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from db import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=True, index=True)
    description = Column(Text, nullable=True)
    domain = Column(String(100), nullable=False)
    tags = Column(Text, nullable=False)
    docs_path = Column(String(255), nullable=False)
    prompt = Column(Text, nullable=False)
    active = Column(Boolean, nullable=False, default=True)

