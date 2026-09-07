import asyncio
import html
import logging
import os
from collections import Counter
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "").strip().lstrip("@")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Add it to your .env file or hosting environment.")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()

WELCOME_TEXT = (
    "👋 <b>Welcome to Bayan!</b>\n\n"
    "Bayan helps you rearrange mixed-up letters into possible words.\n\n"
    "🔤 <b>Try this sample:</b>\n"
    "Send: <code>TEACH</code>\n"
    "Result: <b>CHEAT</b>\n\n"
    "Send your letters below to get started."
)

HELP_TEXT = (
    "❓ <b>How Bayan works</b>\n\n"
    "1. Send mixed-up letters.\n"
    "2. Bayan checks its word list.\n"
    "3. Bayan returns possible words made from those letters.\n\n"
    "<b>Sample:</b> <code>TEACH</code> → possible words such as <b>TEACH</b> and <b>CHEAT</b>.\n\n"
    "Tip: use 2–15 letters for quick results."
)


def main_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text="🔤 Rearrange Letters", callback_data="rearrange")],
        [InlineKeyboardButton(text="📖 How It Works", callback_data="help")],
    ]
    if ADMIN_USERNAME:
        rows.append(
            [InlineKeyboardButton(text="💬 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def normalize_letters(text: str) -> str:
    return "".join(char.lower() for char in text if char.isalpha())


def load_word_list() -> set[str]:
    dictionary_path = Path(__file__).with_name("words.txt")
    paths = [dictionary_path, Path("/usr/share/dict/words")]

    for path in paths:
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as file:
                words = {
                    line.strip().lower()
                    for line in file
                    if line.strip().isalpha()
                }
            if words:
                return words
        except (FileNotFoundError, OSError):
            continue

    return set()


WORD_LIST = load_word_list()


def find_words(letters: str, limit: int = 20) -> list[str]:
    clean = normalize_letters(letters)
    if not clean:
        return []

    target = Counter(clean)
    results: list[str] = []

    for word in WORD_LIST:
        if len(word) < 2 or len(word) > len(clean):
            continue

        counts = Counter(word)
        if all(counts[ch] <= target[ch] for ch in counts):
            results.append(word)

    results.sort(key=lambda word: (-len(word), word))
    return results[:limit]


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(WELCOME_TEXT, reply_markup=main_keyboard())


@dp.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=main_keyboard())


@dp.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(HELP_TEXT, reply_markup=main_keyboard())


@dp.callback_query(F.data == "rearrange")
async def rearrange_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            "🔤 <b>Your turn!</b>\n\n"
            "Send mixed-up letters, for example <code>TEACH</code>."
        )


@dp.message(F.text)
async def word_handler(message: Message) -> None:
    text = message.text.strip()

    if text.startswith("/"):
        return

    clean = normalize_letters(text)

    if len(clean) < 2:
        await message.answer(
            "Please send at least 2 letters.\n\n"
            "Example: <code>TEACH</code>"
        )
        return

    if len(clean) > 15:
        await message.answer("Please use 15 letters or fewer for the quickest results.")
        return

    if not WORD_LIST:
        await message.answer(
            "I’m ready to help, but my word list is unavailable right now. "
            "Please check the bot setup and try again."
        )
        return

    results = find_words(clean)

    if not results:
        safe_letters = html.escape(clean.upper())
        await message.answer(
            f"🔎 No matching words found for <code>{safe_letters}</code>.\n\n"
            "Try a different set of letters."
        )
        return

    formatted = "\n".join(f"• <b>{html.escape(word.upper())}</b>" for word in results)
    safe_letters = html.escape(clean.upper())

    await message.answer(
        f"🔤 <b>Possible words from {safe_letters}</b>\n\n"
        f"{formatted}\n\n"
        "Send another set of letters to continue."
    )


async def main() -> None:
    logging.info("Bayan bot is starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bayan bot stopped")
