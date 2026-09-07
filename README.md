# Bayan Bot

A simple Telegram word rearranging bot built with Python and aiogram 3.x.

## Features

- Rearranges mixed-up letters into possible words.
- Simple `/start` and `/help` commands.
- Inline buttons for an easy user experience.
- Optional admin contact button.
- Uses a local `words.txt` dictionary.

## Setup

1. Install Python 3.10+.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and set your Telegram bot token:

```env
BOT_TOKEN=your_bot_token
ADMIN_USERNAME=your_admin_username
```

4. Start the bot:

```bash
python bot.py
```

Keep `words.txt` in the same directory as `bot.py` so Bayan can find words.
