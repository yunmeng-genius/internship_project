from sqlalchemy.orm import Session

from . import models, schemas


def get_hot_words(db: Session, id: str):
    return db.query(models.HotWord).filter(models.HotWord.id == id).all()

def get_all_hot_words(db: Session):
    return db.query(models.HotWord).all()

def create_hot_word(db: Session, hotWord: schemas.HotWordCreate):
    db_hot_word = models.HotWord(id = hotWord.id, hotWord = hotWord.hotWord)
    db.add(db_hot_word)
    db.commit()
    db.refresh(db_hot_word)
    return db_hot_word
