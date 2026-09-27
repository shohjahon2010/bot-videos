import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8829008777:AAF9s4h6rqQKTaal8xJ_PmChFJTZCDZmyho"

CHANNELS = [
    {"id": -1001234567890, "name": "Канал 1", "url": "https://t.me/канал1"},
    {"id": -1001234567890, "name": "Канал 2", "url": "https://t.me/канал2"},
]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def check_subscription(user_id: int) -> bool:
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception:
            return False
    return True

def get_sub_keyboard():
    buttons = []
    for ch in CHANNELS:
        buttons.append([InlineKeyboardButton(text="📢 " + ch["name"], url=ch["url"])])
    buttons.append([InlineKeyboardButton(text="✅ Я подписался", callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("start"))
async def start(message: types.Message):
    if await check_subscription(message.from_user.id):
        await message.answer("Привет! Отправь ссылку на видео из Instagram.")
    else:
        await message.answer("Подпишись на каналы:", reply_markup=get_sub_keyboard())

@dp.callback_query()
async def check_sub_callback(callback: types.CallbackQuery):
    if await check_subscription(callback.from_user.id):
        await callback.message.edit_text("✅ Спасибо! Теперь отправь ссылку.")
    else:
        await callback.answer("❌ Ты не подписался.", show_alert=True)

@dp.message()
async def echo(message: types.Message):
    await message.answer("Отправь ссылку на видео из Instagram.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
