from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app import models, schemas, database

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=list[schemas.BookResponse])
def get_all_books(db: Session = Depends(database.get_db)):
    return db.query(models.Book).all()


@router.get("/{book_id}", response_model=schemas.BookResponse)
def get_one_book(book_id: int, db: Session = Depends(database.get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Kitob topilmadi!")
    return book


@router.post("/", response_model=schemas.BookResponse, status_code=201)
def create_book(book: schemas.BookCreate, db: Session = Depends(database.get_db)):
    new_book = models.Book(**book.dict())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@router.put("/{book_id}", response_model=schemas.BookResponse)
def update_book(book_id: int, book_data: schemas.BookUpdate, db: Session = Depends(database.get_db)):
    existing = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Kitob topilmadi!")

    for key, value in book_data.dict().items():
        setattr(existing, key, value)

    db.commit()
    db.refresh(existing)
    return existing


@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(database.get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Kitob topilmadi!")

    db.delete(book)
    db.commit()
    return {"sms": "Kitob yo'q qilindi!"}


@router.get("/search/", response_model=list[schemas.BookResponse])
def search_books(search: str = Query(..., min_length=1), db: Session = Depends(database.get_db)):
    return db.query(models.Book).filter(
        or_(
            models.Book.title.ilike(f"%{search}%"),
            models.Book.author.ilike(f"%{search}%")
        )
    ).all()


@router.get("/filter/", response_model=list[schemas.BookResponse])
def filter_books(
    min: int = Query(..., ge=0),
    max: int = Query(..., ge=0),
    db: Session = Depends(database.get_db)
):
    if min > max:
        raise HTTPException(status_code=400, detail="min qiymat max qiymatdan katta bo'lmasligi kerak!")

    return db.query(models.Book).filter(models.Book.year.between(min, max)).all()
