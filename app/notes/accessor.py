from typing import List, Tuple

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_async_session
from notes.models import Note, Tag
from notes.schemas import NoteCreate, NoteUpdate, TagSearch


class ContentManager:
    def __init__(self, session: Session = Depends(get_async_session)):
        self.session = session

    async def create_note(self, note: NoteCreate, user_id: int) -> Note:
        db_note = Note(
            title=note.title,
            content=note.content,
            user_id=user_id,
        )
        self.session.add(db_note)
        await self.session.commit()

        for tag_name in note.tags:
            result = await self.session.execute(
                select(Tag).where(Tag.name == tag_name)
            )
            tag = result.scalars().first()

            if not tag:
                tag = Tag(name=tag_name)
                self.session.add(tag)
                await self.session.commit()

            await self.session.refresh(db_note)
            db_note.tags.append(tag)

        await self.session.commit()
        await self.session.refresh(db_note)
        return db_note

    async def get_note_by_id(self, note_id: int) -> Note:
        return await self.session.get(Note, note_id)

    async def get_notes_by_user_id(self, user_id: int) -> List[Note]:
        notes = await self.session.execute(select(Note)
                                           .where(Note.user_id == user_id)
                                           )
        return notes.scalars().all()

    async def update_note(self, note_id, note: NoteUpdate, user_id: int) -> Note:
        db_note = await self.get_note_by_id(note_id)
        assert db_note.user_id == user_id  # user can check only their notes
        if note.title:
            db_note.title = note.title
        if note.content:
            db_note.content = note.content
        await self.session.commit()
        return db_note

    async def delete_archive_note(self, note_id: int, user_id: int):
        db_note = await self.get_note_by_id(note_id)
        assert db_note.user_id == user_id  # user can delete only their notes
        await self.session.delete(db_note)
        await self.session.commit()
        return

    async def get_notes_by_tag(self, tag_search: str, user_id: int) -> List[Note] | None:
        notes = await self.session.execute(select(Note)
                                           .join(Note.tags)
                                           .filter(Tag.name == tag_search)
                                           .filter(Note.user_id == user_id))
        return notes.scalars().all()
