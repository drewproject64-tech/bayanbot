import asyncio
import logging
import os
from collections import Counter

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

bot = Bot(token=TOKEN)
dp = Dispatcher()

WELCOME_TEXT = (
    "👋 Welcome to <b>Bayan</b>!\n\n"
    "Unscramble letters and discover possible words.\n\n"
    "🔤 Send me mixed-up letters and I’ll find word combinations for you.\n\n"
    "Example: <code>TEACH</code> → <b>CHEAT</b>"
)


def main_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🔤 Rearrange Word", callback_data="rearrange")],
        [InlineKeyboardButton(text="❓ How to Use", callback_data="help")],
    ]
    if ADMIN_USERNAME:
        buttons.append([InlineKeyboardButton(text="💬 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME.lstrip('@')}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def normalize_letters(text: str) -> str:
    return "".join(char.lower() for char in text if char.isalpha())


def load_word_list() -> set[str]:
    paths = ["words.txt", "/usr/share/dict/words"]
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                words = {
                    line.strip().lower()
                    for line in file
                    if line.strip().isalpha()
                }
            if words:
                return words
        except FileNotFoundError:
            continue
    return set()


WORD_LIST = load_word_list()


def find_words(letters: str, limit: int = 20) -> list[str]:
    clean = normalize_letters(letters)
    if not clean:
        return []

    target = Counter(clean)
    candidates: list[str] = []

    for word in WORD_LIST:
        if len(word) < 2 or len(word) > len(clean):
            continue
        counts = Counter(word)
        if all(counts[ch] <= target[ch] for ch in counts):
            candidates.append(word)

    candidates.sort(key=lambda word: (-len(word), word))
    return candidates[:limit]


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(WELCOME_TEXT, reply_markup=main_keyboard())


@dp.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(
        "❓ <b>How to use Bayan</b>\n\n"
        "Send mixed-up letters, for example <code>TEACH</code>.\n"
        "Bayan will return possible words that can be formed from those letters.\n\n"
        "Tip: longer letter sets can produce more results."
    )


@dp.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text(
        "❓ <b>How to use Bayan</b>\n\n"
        "Send mixed-up letters, for example <code>TEACH</code>.\n"
        "Bayan will return possible words that can be formed from those letters.\n\n"
        "Tip: longer letter sets can produce more results.",
        reply_markup=main_keyboard(),
    )


@dp.callback_query(F.data == "rearrange")
async def rearrange_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer("🔤 Send me the mixed-up letters, for example <code>TEACH</code>.")


@dp.message(F.text)
async def word_handler(message: Message) -> None:
    text = message.text.strip()
    if text.startswith("/"):
        return

    clean = normalize_letters(text)
    if len(clean) < 2:
        await message.answer("Please send at least 2 letters, such as <code>TEACH</code>.")
        return

    if not WORD_LIST:
        await message.answer(
            "⚠️ I’m ready, but the word list is missing. Add a <code>words.txt</code> file to the bot folder and restart me."
        )
        return

    results = find_words(clean)
    if not results:
        await message.answer(
            f"🔎 I couldn't find a matching word for <code>{clean.upper()}</code>.\n\nTry another set of letters."
        )
        return

    formatted = "\n".join(f"• <b>{word.upper()}</b>" for word in results)
    await message.answer(
        f"🔤 <b>Words from {clean.upper()}</b>\n\n{formatted}\n\n"
        f"Found {len(results)} result(s)."
    )


async def main() -> None:
    logging.info("Bayan bot is starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bayan bot stopped")
