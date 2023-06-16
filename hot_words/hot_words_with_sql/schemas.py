from pydantic import BaseModel


class HotWordBase(BaseModel):
    id: str
    hotWord: str


class HotWordCreate(HotWordBase):
    pass


class HotWord(HotWordBase):

    class Config:
        orm_mode = True
