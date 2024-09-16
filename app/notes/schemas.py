from pydantic import BaseModel


class TagCreate(BaseModel):
    name: str


class TagSearch(BaseModel):
    name: str


class NoteCreate(BaseModel):
    title: str
    content: str
    tags: list[str]


class NoteUpdate(BaseModel):
    id: int
    title: str
    content: str
    tags: list[str]

