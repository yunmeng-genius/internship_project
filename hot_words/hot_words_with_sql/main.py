from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/create_hot_words/', response_model=schemas.User)
def create_hot_words(hotWord: schemas.HotWordCreate, db: Session = Depends(get_db)):
    db_hot_words = crud.get_hot_words(db, hotWord=hotWord.id)
    if hotWord.hotWord in db_hot_words:
        raise HTTPException(
            status_code=400, detail="HotWord already registered")
    return crud.create_hot_word(db=db, hotWord=hotWord)


@app.get('/hot_words', response_model=list[schemas.HotWord])
def read_hot_words(db: Session = Depends(get_db)):
    hot_words = crud.get_hot_words(db)
    return hot_words


@app.get('/hot_words/{id}', response_model=schemas.HotWord)
def read_hot_words(id: str, db: Session = Depends(get_db)):
    hot_words = crud.get_hot_words(db, id=id)
    if hot_words is None:
        raise HTTPException(status_code=404, detail="User not found")
    return hot_words
