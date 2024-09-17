import asyncio
import logging
import os
import sys
from typing import Callable, Awaitable, Any
import httpx
from email_validator import validate_email, EmailNotValidError  # Import the validator
from aiogram import Bot, Dispatcher, Router, BaseMiddleware, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, Update, CallbackQuery

# from config import settings
# # API_TOKEN = settings.API_TOKEN
# # FASTAPI_URL = "http://127.0.0.1:8000/"
# FASTAPI_URL = "http://app:8000/"

# используем переменные окружения, чтобы получить константные данные
API_TOKEN = os.getenv("API_TOKEN")
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://fastapi-app:8000/")

# инициализация бота
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)


# определяем состояния, когда мы ожидаем пользовательский ввод
class NoteForm(StatesGroup):
    title = State()
    content = State()
    tags = State()


class LinkEmailForm(StatesGroup):
    email = State()


async def check_user_existence(user_id: int):
    """
    функция, проверяющая через апи - существует ли пользователь в БД
    с таким же телеграм ид
    :param user_id:
    :return: dict
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FASTAPI_URL}users/auth/exist", params={
            "telegram_id": user_id
        })
    return response.json()


class UserCheckMiddleware(BaseMiddleware):
    """
    Мидлвара для бота - проверяет авторизован ли пользователь, если да - пропускаем дальше.
    Если нет - требуем связать аккаунты, указав почту, через который юзер был зарегистрирован в БД.
    """
    def __init__(self):
        super().__init__()

    async def __call__(self, handler: Callable[[Update, dict], Awaitable[Any]], event: Update, data: dict) -> Any:

        if isinstance(event, Message):
            user = event.from_user
            db_user = await check_user_existence(user.id)

            fsm_context = data.get('state', None)
            state = await fsm_context.get_state() if fsm_context else None

            if db_user or state == LinkEmailForm.email.state:
                return await handler(event, data)

            await event.answer(
                "Hello! Before starting using this bot you have to link your Telegram accounts with already registered account in system.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                                                    [
                                                                        InlineKeyboardButton(text='Link Accounts', callback_data='link_accounts')
                                                                    ]
                ]))
            await data["state"].set_state("awaiting_email")
        else:
            return await handler(event, data)


dp.message.middleware(UserCheckMiddleware())
dp.callback_query.middleware(UserCheckMiddleware())


# инлей будет часто вызываться, поэтому вынесем его в отдельную переменную
inline_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Добавить заметку', callback_data='add_note'),
        InlineKeyboardButton(text='Искать по тегу', callback_data='search_by_tag'),
    ],
    [
        InlineKeyboardButton(text='Показать мои заметки', callback_data='show_my_notes')
    ]
])


@router.message(Command(commands=['start', 'help']))
async def command_start_handler(message: Message):
    user = message.from_user.username
    await message.answer(f"Hi, {user}! I'm a telegram bot for FastAPI test app 🙌", reply_markup=inline_kb)


# роутер для связки аккаунтов. Ожидаем почту от юзера
@router.callback_query(F.data == "link_accounts")
async def add_note_start_handler(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("Please, provide me your registered email")
    await state.set_state(LinkEmailForm.email)


@router.message(LinkEmailForm.email)
async def handle_email(message: Message, state: FSMContext):
    """
    Принимаем почту от пользователя и валидируем ее написание. Если ок - пытаемся найти юзера с
    такой почтой в БД. При нахождении - получаем успешный ответ от сервера.
    :param message:
    :param state:
    :return: message
    """
    try:
        email = message.text.strip()
        valid_email = validate_email(email)

        telegram_id = message.from_user.id

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{FASTAPI_URL}users/auth/link-accounts", json={
                "email": email,
                "telegram_id": telegram_id
            })
            if response.status_code == 200:
                await message.answer("Accounts successfully linked!", reply_markup=inline_kb)
                await state.clear()
            else:
                await message.answer("An error occupied during linking accounts. Pleasy try again")
                # await state.clear()

    except EmailNotValidError as e:
        await message.answer(f"Wrong email: {str(e)}. Please try again.")
        return


"""
Несколько взаимосвязанных методов. Просим у пользователя последовательно ввести
заголовок, текст заметки и теги. На последнем шаге сохраняем заметку и сообщаем об этом пользователю
"""
@router.callback_query(F.data == "add_note")
async def add_note_start_handler(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Please enter the title of the note:")
    await state.set_state(NoteForm.title)


@router.message(NoteForm.title)
async def add_note_content_handler(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Now enter the content of the note:")
    await state.set_state(NoteForm.content)


@router.message(NoteForm.content)
async def add_note_tags_handler(message: Message, state: FSMContext):
    await state.update_data(content=message.text)
    await message.answer("Finally, enter the tags (separated by commas):")
    await state.set_state(NoteForm.tags)


@router.message(NoteForm.tags)
async def save_note_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    title = data['title']
    content = data['content']
    user_id = message.from_user.id

    tags = [x.strip() for x in message.text.split(',')]
    if all(tag.isalnum() for tag in tags):

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{FASTAPI_URL}notes/tg/{user_id}", json={
                "title": title,
                "content": content,
                "tags": tags,
            })

        if response.status_code == 201:
            await message.answer("Your note has been successfully added!", reply_markup=inline_kb)
        else:
            await message.answer("Error saving note. Please try again.", reply_markup=inline_kb)
        await state.clear()
    else:
        await message.reply("Invalid tags detected. Tags must be alphanumeric only. Please provide tags again.")
        await state.set_state(NoteForm.tags)


# функция просит ввести тэг для поиска
@router.callback_query(F.data == "search_by_tag")
async def add_note_start_handler(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("Please enter the tag you want to search for:")
    await state.set_state("awaiting_tag")


# получим пользовательский ввод - отправляем запрос на сервер, чтобы получить заметки с этим тегом
@router.message(StateFilter("awaiting_tag"))
async def handle_tag_search(message: Message, state: FSMContext):
    tag = message.text.strip()
    user_id = message.from_user.id
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FASTAPI_URL}notes/tg/{user_id}/search", params={"tag_search": tag,})
        if response.status_code == 200:
            notes = response.json()
            if notes:
                response = "\n\n".join([f"Title: {note['title']}\nContent: {note['content']}\nTags: {', '.join([x for x in note['tags']])}" for note in notes])
                await message.reply(f"Notes found: \n\n{response}")
            else:
                await message.reply("No notes found with this tag.")
    await state.clear()

# функция покажет все записи пользователя в БД
@router.callback_query(F.data == "show_my_notes")
async def show_my_notes_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FASTAPI_URL}notes/tg/{user_id}")

        if response.status_code == 200:
            notes = response.json()
            if notes:
                notes_text = "\n\n".join([f"Title: {note['title']}\nContent: {note['content']}\nTags: {', '.join([x for x in note['tags']])}" for note in notes])
                await call.message.answer(f"Your notes:\n\n{notes_text}")
                await call.answer()
            else:
                await call.answer("You have no notes.")
        else:
            await call.answer("Failed to retrieve your notes.")


async def main() -> None:
    while True:
        try:
            await dp.start_polling(bot)
        except Exception as e:
            await asyncio.sleep(3)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
