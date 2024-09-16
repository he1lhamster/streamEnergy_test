from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from starlette import status

from notes.accessor import ContentManager

from notes.schemas import NoteCreate, TagSearch, NoteUpdate
from users.auth import current_user
from users.manager import get_user_manager, UserManager
from users.models import User

router = APIRouter(
    prefix="/notes",
    tags=["notes", ],
)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_note(note_create: NoteCreate,
                      user: User = Depends(current_user),
                      accessor: ContentManager = Depends(),
                      ):
    new_note = await accessor.create_note(note_create, user.id)
    return new_note


@router.patch("/{note_id}")
async def update_note(note_id: int,
                      note_update: NoteUpdate,
                      user: User = Depends(current_user),
                      accessor: ContentManager = Depends(),
                      ):
    new_note = await accessor.update_note(note_id, note_update, user.id)
    return new_note


@router.get("")
async def get_notes(user: User = Depends(current_user),
                    accessor: ContentManager = Depends()
                    ):
    return await accessor.get_notes_by_user_id(user.id)


@router.get("/search")
async def search_notes_by_tag(tag_search: TagSearch,
                              user: User = Depends(current_user),
                              accessor: ContentManager = Depends()
                              ):
    return await accessor.get_notes_by_tag(tag_search, user_id=user.id)


@router.delete("/{note_id}")
async def delete_note(note_id: int,
                      user: User = Depends(current_user),
                      accessor: ContentManager = Depends(),
                      ):
    new_note = await accessor.update_note(note_id, user.id)
    return new_note


# ----------- Telegram Handlers -------------

@router.post("/tg/{telegram_id}", status_code=status.HTTP_201_CREATED)
async def create_note_tg(
        telegram_id: int,
        note_create: NoteCreate,
        accessor: ContentManager = Depends(),
        user_manager: UserManager = Depends(get_user_manager)
):
    user = await user_manager.user_db.get_by_telegram_id(telegram_id)
    new_note = await accessor.create_note(note_create, user.id)
    return new_note


@router.patch("/tg/{telegram_id}/{note_id}")
async def update_note_tg(telegram_id: int,
                            note_id: int,
                         note_update: NoteUpdate,
                         user_manager: UserManager = Depends(get_user_manager),
                         accessor: ContentManager = Depends(),
                         ):
    user = await user_manager.user_db.get_by_telegram_id(telegram_id)
    new_note = await accessor.update_note(note_id, note_update, user.id)
    return new_note


@router.get("/tg/{telegram_id}")
async def get_notes_tg(telegram_id: int,
                       user_manager: UserManager = Depends(get_user_manager),
                       accessor: ContentManager = Depends()
                       ):
    user = await user_manager.user_db.get_by_telegram_id(telegram_id)
    return await accessor.get_notes_by_user_id(user.id)


@router.get("/tg/{telegram_id}/search")
async def search_notes_by_tag_tg(telegram_id: int,
                                 tag_search: str,
                                 user_manager: UserManager = Depends(get_user_manager),
                                 accessor: ContentManager = Depends()
                                 ):
    print('TTAG SEARCH')
    user = await user_manager.user_db.get_by_telegram_id(telegram_id)
    return await accessor.get_notes_by_tag(tag_search, user_id=user.id)


@router.delete("/tg/{telegram_id}/{note_id}")
async def delete_note_tg(telegram_id: int,
                         note_id: int,
                         user_manager: UserManager = Depends(get_user_manager),
                         accessor: ContentManager = Depends(),
                         ):
    user = await user_manager.user_db.get_by_telegram_id(telegram_id)
    new_note = await accessor.update_note(note_id, user.id)
    return new_note
