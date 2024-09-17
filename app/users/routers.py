from fastapi import APIRouter, Depends

from users.auth import fastapi_users, auth_backend
from users.manager import UserManager, get_user_manager
from users.schemas import UserUpdate, UserExistTelegram, UserRead, UserCreate

router = APIRouter(
    prefix="/users",
    tags=["users", ],
)


@router.post("/auth/link-accounts")
async def register(
        user_update: UserUpdate,
        user_manager: UserManager = Depends(get_user_manager)
):
    user = await user_manager.link_accounts_telegram(user_update)
    return user


@router.get("/auth/exist")
async def register(
        telegram_id: int,
        user_manager: UserManager = Depends(get_user_manager)
):
    user = await user_manager.is_user_exist_by_telegram_id(telegram_id)
    return user


router.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
# router.include_router(fastapi_users.get_users_router(), prefix="/", tags=["users"])
