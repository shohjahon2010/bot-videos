import asyncio
import os
import tempfile
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

BOT_TOKEN = "8829008777:AAF9s4h6rqQKTaal8xJ_PmChFJTZCDZmyho"

CHANNELS = [
    {"id": -1003944298510, "name": "Мой канал", "url": "https://t.me/bott_videos"},
    {"id": -1003931850448, "name": "реклама бот", "url": "https://t.me/reklamaabot"},
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

def download_instagram_video(url: str) -> str:
    temp_dir = tempfile.mkdtemp()
    ydl_opts = {
        "outtmpl": os.path.join(temp_dir, "%(id)s.%(ext)s"),
        "format": "best[ext=mp4]/best",
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    return filename

@dp.message(Command("start"))
async def start(message: types.Message):
    if await check_subscription(message.from_user.id):
        await message.answer("Привет! Отправь мне ссылку на видео из Instagram, и я скачаю его без водяных знаков.")
    else:
        await message.answer("Чтобы пользоваться ботом, подпишись на каналы:", reply_markup=get_sub_keyboard())

@dp.callback_query()
async def check_sub_callback(callback: types.CallbackQuery):
    if await check_subscription(callback.from_user.id):
        await callback.message.edit_text("✅ Спасибо за подписку! Теперь отправь ссылку на видео.")
    else:
        await callback.answer("❌ Ты ещё не подписался на все каналы.", show_alert=True)

@dp.message(lambda message: message.text and "instagram.com" in message.text)
async def download_video(message: types.Message):
    if not await check_subscription(message.from_user.id):
        await message.answer("Сначала подпишись на каналы:", reply_markup=get_sub_keyboard())
        return

    status_msg = await message.answer("⏳ Скачиваю видео, подожди...")

    try:
        loop = asyncio.get_event_loop()
        file_path = await loop.run_in_executor(None, download_instagram_video, message.text.strip())

        await status_msg.edit_text("📤 Отправляю видео...")

        video = FSInputFile(file_path)
        await message.answer_video(video=video, caption="Готово! 🎬")

        await status_msg.delete()

        try:
            os.remove(file_path)
            os.rmdir(os.path.dirname(file_path))
        except Exception:
            pass

    except Exception as e:
        await status_msg.edit_text(f"❌ Не удалось скачать видео.\n\nОшибка: {str(e)[:200]}")

@dp.message()
async def echo(message: types.Message):
    await message.answer("Отправь мне ссылку на видео из Instagram.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
