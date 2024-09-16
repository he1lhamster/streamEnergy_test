from fastapi import APIRouter, Depends, Request
from loguru import logger
from starlette import status

from main import limiter
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
@limiter.limit("30/minute")
async def create_note(note_create: NoteCreate,
                      user: User = Depends(current_user),
                      accessor: ContentManager = Depends(),
                      ):
    try:
        new_note = await accessor.create_note(note_create, user.id)
        logger.info(f"Create note: User: {user.id}, Note: {new_note}")
        return new_note
    except Exception as e:
        logger.error(f"Error while creating note for {user.id}: {e}")
        return {"status": "error", "message": str(e)}


@router.patch("/{note_id}")
@limiter.limit("30/minute")
async def update_note(note_id: int,
                      note_update: NoteUpdate,
                      user: User = Depends(current_user),
                      accessor: ContentManager = Depends(),
                      ):
    try:
        new_note = await accessor.update_note(note_id, note_update, user.id)
        logger.info(f"Update note: User: {user.id}, Note: {new_note}")
        return new_note
    except Exception as e:
        logger.error(f"Error while updating note for {user.id}: {e}")
        return {"status": "error", "message": str(e)}


@router.get("")
@limiter.limit("30/minute")
async def get_notes(user: User = Depends(current_user),
                    accessor: ContentManager = Depends()
                    ):
    try:
        notes = await accessor.get_notes_by_user_id(user.id)
        logger.info(f"Get notes for User: {user.id}")
        return notes
    except Exception as e:
        logger.error(f"Error while getting notes for {user.id}: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/search")
@limiter.limit("30/minute")
async def search_notes_by_tag(tag_search: TagSearch,
                              user: User = Depends(current_user),
                              accessor: ContentManager = Depends()
                              ):
    try:
        notes = await accessor.get_notes_by_tag(tag_search, user_id=user.id)
        logger.info(f"Search notes by Tag: {tag_search} for User: {user.id}")
        return notes
    except Exception as e:
        logger.error(f"Error while Search notes by Tag: {tag_search} for {user.id}: {e}")
        return {"status": "error", "message": str(e)}


@router.delete("/{note_id}")
@limiter.limit("30/minute")
async def delete_note(note_id: int,
                      user: User = Depends(current_user),
                      accessor: ContentManager = Depends(),
                      ):
    try:
        await accessor.delete_note(note_id, user.id)
        logger.info(f"Delete Note: {note_id} for User: {user.id}")
        return
    except Exception as e:
        logger.error(f"Error while deleting Note: {note_id} for User: {user.id}: {e}")
        return {"status": "error", "message": str(e)}


# ----------- Telegram Handlers -------------

@router.post("/tg/{telegram_id}", status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_note_tg(
        telegram_id: int,
        note_create: NoteCreate,
        accessor: ContentManager = Depends(),
        user_manager: UserManager = Depends(get_user_manager)
):
    try:
        user = await user_manager.user_db.get_by_telegram_id(telegram_id)
        new_note = await accessor.create_note(note_create, user.id)
        logger.info(f"Create note: User: {user.id}, Note: {new_note}")
        return new_note
    except Exception as e:
        logger.error(f"TG: Error while creating note for {user.id}: {e}")
        return {"status": "error", "message": str(e)}


@router.patch("/tg/{telegram_id}/{note_id}")
@limiter.limit("30/minute")
async def update_note_tg(telegram_id: int,
                            note_id: int,
                         note_update: NoteUpdate,
                         user_manager: UserManager = Depends(get_user_manager),
                         accessor: ContentManager = Depends(),
                         ):
    try:
        user = await user_manager.user_db.get_by_telegram_id(telegram_id)
        new_note = await accessor.update_note(note_id, note_update, user.id)
        logger.info(f"Update note: User: {user.id}, Note: {new_note}")
        return new_note
    except Exception as e:
        logger.error(f"TG: Error while updating note for {user.id}: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/tg/{telegram_id}")
@limiter.limit("30/minute")
async def get_notes_tg(telegram_id: int,
                       user_manager: UserManager = Depends(get_user_manager),
                       accessor: ContentManager = Depends()
                       ):
    try:
        user = await user_manager.user_db.get_by_telegram_id(telegram_id)
        notes = await accessor.get_notes_by_user_id(user.id)
        logger.info(f"Get notes for User: {user.id}")
        return notes
    except Exception as e:
        logger.error(f"TG: Error while getting notes for {user.id}: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/tg/{telegram_id}/search")
@limiter.limit("30/minute")
async def search_notes_by_tag_tg(telegram_id: int,
                                 tag_search: str,
                                 user_manager: UserManager = Depends(get_user_manager),
                                 accessor: ContentManager = Depends()
                                 ):
    try:
        user = await user_manager.user_db.get_by_telegram_id(telegram_id)
        notes = await accessor.get_notes_by_tag(tag_search, user_id=user.id)
        logger.info(f"Search notes by Tag: {tag_search} for User: {user.id}")

        return notes
    except Exception as e:
        logger.error(f"TG: Error while Search notes by Tag: {tag_search} for {user.id}: {e}")
        return {"status": "error", "message": str(e)}


@router.delete("/tg/{telegram_id}/{note_id}")
@limiter.limit("30/minute")
async def delete_note_tg(telegram_id: int,
                         note_id: int,
                         user_manager: UserManager = Depends(get_user_manager),
                         accessor: ContentManager = Depends(),
                         ):
    try:
        user = await user_manager.user_db.get_by_telegram_id(telegram_id)
        await accessor.delete_note(note_id, user.id)
        logger.info(f"Delete Note: {note_id} for User: {user.id}")
        return
    except Exception as e:
        logger.error(f"TG: Error while deleting Note: {note_id} for User: {user.id}: {e}")
        return {"status": "error", "message": str(e)}
