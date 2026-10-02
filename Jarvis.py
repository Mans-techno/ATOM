import asyncio
import aiohttp
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from connection import create_table
from service import save_message, get_history, clear_history
import os


load_dotenv()

AI_URL = "https://api.inceptionlabs.ai/v1/chat/completions"
AI_API_KEY = os.getenv("AI_API_KEY")

BTN_START = "🤖 Начать общение"
BTN_STOP = "⛔ Закончить общение"

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=BTN_START)]],
    resize_keyboard=True
)
stop_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=BTN_STOP)]],
    resize_keyboard=True
)

router = Router()


class ChatAI(StatesGroup):
    chatting = State()


async def ask_ai(history):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            AI_URL,
            headers={
                "Authorization": f"Bearer {AI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mercury-2.5",
                "reasoning_effort": "high",
                "messages": history
            }
        ) as response:
            data = await response.json()
            return data["choices"][0]["message"]["content"]


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Я ATOM — твой личный ИИ-помощник ⚛️\n"
        "Отвечу на вопросы, помогу с учёбой и кодом, "
        "подскажу идею или просто поболтаю.\n\n"
        "📌 Команды:\n"
        "/chat — начать общение\n"
        "/stop — закончить общение\n"
        "/clear — очистить историю\n\n"
        "Жми «🤖 Начать общение» — и поехали! 🚀",
        reply_markup=start_keyboard
    )


@router.message(Command("chat"))
@router.message(F.text == BTN_START)
async def start_chat(message: Message, state: FSMContext):
    await state.set_state(ChatAI.chatting)
    await message.answer(
        "Общение с ИИ начато 💬\nПиши свои запросы:",
        reply_markup=stop_keyboard
    )


@router.message(Command("stop"))
@router.message(F.text == BTN_STOP)
async def stop_chat(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Общение с ИИ закончено.",
        reply_markup=start_keyboard
    )



@router.message(Command("clear"))
async def cmd_clear(message: Message):
    await clear_history(message.from_user.id)
    await message.answer("История общения очищена.")


@router.message(ChatAI.chatting, F.text)
async def chat_with_ai(message: Message, state: FSMContext):
    history = await get_history(message.from_user.id)
    history.append({"role": "user", "content": message.text})

    await message.bot.send_chat_action(message.chat.id, "typing")
    try:
        answer = await ask_ai(history)
    except Exception as error:
        await message.answer(f"Ошибка при обращении к ИИ: {error}")
        return

    await save_message(message.from_user.id, message.text, answer)
    await message.answer(answer)


@router.message()
async def not_in_chat(message: Message):
    await message.answer(
        "Чтобы поговорить с ИИ, нажми кнопку или отправь /chat",
        reply_markup=start_keyboard
    )



async def main():
    await create_table()
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
