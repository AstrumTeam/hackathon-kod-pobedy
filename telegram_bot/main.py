import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

from faq import FAQ


load_dotenv()

logging.basicConfig(level=logging.INFO)

BOT_TOKEN   = os.getenv("BOT_TOKEN")
SUPPORT_CHAT_ID = os.getenv("SUPPORT_CHAT_ID")

if not BOT_TOKEN or not SUPPORT_CHAT_ID:
    raise ValueError("Please set BOT_TOKEN and SUPPORT_CHAT_ID in .env file")


bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


class SupportStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_rating = State()
    waiting_for_reply = State()



active_conversations = {}
pending_replies = {}


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я бот технической поддержки.\n"
        "Задайте свой вопрос, и я передам его команде поддержки.\n"
        "Используйте /help для получения дополнительной информации.\n"
        "Используйте /faq для просмотра часто задаваемых вопросов."
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📝 Как пользоваться ботом:\n\n"
        "1. Просто напишите ваш вопрос\n"
        "2. Опишите проблему максимально подробно\n"
        "3. При необходимости прикрепите скриншот\n"
        "4. Используйте /faq для просмотра частых вопросов\n\n"
        "Наша команда поддержки ответит вам в ближайшее время."
    )

@dp.message(Command("faq"))
async def cmd_faq(message: Message):
    faq_text = "📚 Часто задаваемые вопросы:\n\n"
    for question, answer in FAQ.items():
        faq_text += f"❓ {question.capitalize()}\n{answer}\n\n"
    await message.answer(faq_text)

@dp.message(F.text)
async def handle_question(message: Message, state: FSMContext):
    if str(message.chat.id) == SUPPORT_CHAT_ID and message.reply_to_message:
        original_text = message.reply_to_message.text or message.reply_to_message.caption
        
        user_id = None
        if original_text:
            for line in original_text.split('\n'):
                if "ID:" in line:
                    try:
                        user_id = int(line.split("ID:")[1].strip().split(")")[0])
                        break
                    except (ValueError, IndexError):
                        continue

        if user_id and user_id in active_conversations:
            await bot.send_message(
                active_conversations[user_id],
                f"📬 Ответ от поддержки:\n\n{message.text}\n\n"
                "Пожалуйста, оцените качество ответа:",
                reply_markup=get_rating_keyboard()
            )

            await message.reply("✅ Ответ отправлен пользователю")
        return


    message_lower = message.text.lower()
    for question, answer in FAQ.items():
        if question in message_lower:
            await message.answer(f"📚 Ответ на ваш вопрос:\n\n{answer}")
            return

    active_conversations[message.from_user.id] = message.chat.id

    await bot.send_message(
        SUPPORT_CHAT_ID,
        f"📩 Новый вопрос от пользователя {message.from_user.full_name} (ID: {message.from_user.id}):\n\n"
        f"{message.text}"
    )
    
    await message.answer(
        "✅ Ваш вопрос получен! Наша команда поддержки рассмотрит его и ответит вам в ближайшее время."
    )


@dp.message(F.photo | F.document)
async def handle_files(message: Message):

    active_conversations[message.from_user.id] = message.chat.id


    if message.photo:
        file_id = message.photo[-1].file_id
        caption = f"📸 Фото от пользователя {message.from_user.full_name} (ID: {message.from_user.id})"
        if message.caption:
            caption += f"\n\nПодпись: {message.caption}"
        await bot.send_photo(SUPPORT_CHAT_ID, file_id, caption=caption)
    elif message.document:
        file_id = message.document.file_id
        caption = f"📄 Документ от пользователя {message.from_user.full_name} (ID: {message.from_user.id})"
        if message.caption:
            caption += f"\n\nПодпись: {message.caption}"
        await bot.send_document(SUPPORT_CHAT_ID, file_id, caption=caption)


    await message.answer(
        "✅ Ваш файл получен! Наша команда поддержки рассмотрит его и ответит вам в ближайшее время."
    )


@dp.callback_query(lambda c: c.data.startswith('rate_'))
async def process_rating(callback: CallbackQuery):
    rating = callback.data.split('_')[1]
    await callback.message.edit_text(
        f"{callback.message.text}\n\n"
        f"Спасибо за вашу оценку: {rating} ⭐"
    )
    await callback.answer()

def get_rating_keyboard():
    builder = InlineKeyboardBuilder()
    for i in range(1, 6):
        builder.button(text=f"{i}⭐", callback_data=f"rate_{i}")
    builder.adjust(5)
    return builder.as_markup()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
