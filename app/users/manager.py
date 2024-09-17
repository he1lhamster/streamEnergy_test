from typing import Optional

from fastapi import Depends
from fastapi_users import BaseUserManager, IntegerIDMixin
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_users.db import SQLAlchemyUserDatabase
from config import settings
from database import get_async_session
from users.models import User
from users.schemas import UserUpdate


# расширяем базовый функционал методов для работы с юзерами, добавляем получение по телеграм_ид
class SQLAlchemyUserDatabaseExtend(SQLAlchemyUserDatabase):
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        query = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        user = query.scalars().first()
        return user


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabaseExtend(session, User)


# расширяем базовый менеджер для работы с юзерами, указывая свои настройки и определяя методы
class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.JWT_SECRET
    verification_token_secret = settings.JWT_SECRET
    user_db_model = User

    async def on_after_register(self, user: User, request=None):
        print(f"User {user.id} has registered.")

    async def link_accounts_telegram(self, user_update: UserUpdate):
        _user = await self.is_user_exist_by_telegram_id(user_update.telegram_id)
        if _user:
            return _user

        user = await self.user_db.get_by_email(user_update.email)

        if not user:
            raise ValueError("User with this email does not exist.")

        await self.user_db.update(user, {"telegram_id": user_update.telegram_id})
        return user

    async def is_user_exist_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        return await self.user_db.get_by_telegram_id(telegram_id)


# используется для инъекции зависимости
async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

