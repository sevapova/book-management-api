from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel, Field

DATABASE_URL = "sqlite:///./books.db"  
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    author = Column(String(200))
    genre = Column(String(100))
    year = Column(Integer)
    rating = Column(Float)

class BookBase(BaseModel):
    title: str
    author: str
    genre: str
    year: int
    rating: float = Field(ge=0, le=5)


class BookCreate(BookBase):
    title: str
    author: str
    genre: str
    year: int
    rating: float = Field(ge=0, le=5)

class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    genre: str | None = None
    year: int | None = None
    rating: float | None = Field(default=None, ge=0, le=5)


class BookResponse(BookBase):
    id: int

    class Config:
        orm_mode = True


app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.post("/books/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book_in: BookCreate, db: Session = Depends(get_db)):
    book = Book(**book_in.dict())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@app.get("/books/", response_model=list[BookResponse])
def read_books(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    return books


@app.get("/books/{book_id}", response_model=BookResponse)
def read_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book_update: BookUpdate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    for key, value in book_update.dict(exclude_unset=True).items():
        setattr(book, key, value)

    db.commit()
    db.refresh(book)
    return book


@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(book)
    db.commit()
    return {"message": "Book deleted successfully"}
