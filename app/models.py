from sqlalchemy import Column, String, Integer, Float, CHECK
from .database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, nullable=False, unique=True)
    title = Column(String(256), nullable=False)
    auther = Column(String(128), nullable=False)
    genre = Column(String(120))
    year = Column(Integer)
    rating = Column(Float)

