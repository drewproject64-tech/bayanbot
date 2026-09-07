# Bayan Bot

Bayan is a simple Telegram word-rearranging utility. Users send mixed-up letters and receive possible words that can be formed from them.

## User experience

- `/start` opens a clear welcome screen.
- The welcome message includes a real sample: `TEACH` → `CHEAT`.
- **Rearrange Letters** tells users exactly what to send.
- **How It Works** explains the flow in a few lines.
- Users can send letters directly without pressing a button.
- Invalid or overly long input receives a helpful response.
- Optional **Contact Admin** button is controlled by `ADMIN_USERNAME`.

## Telegram Ads destination sample

Use factual, destination-matching copy such as:

> Rearrange mixed-up letters into possible words with Bayan. Try a sample and start solving word puzzles.

The ad should describe the actual bot experience and point directly to Bayan. Approval is subject to Telegram's current advertising review and policies; this wording is designed to be clear and non-misleading, not to guarantee approval.

## Setup

1. Install Python 3.10+.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and set your bot token:

```env
BOT_TOKEN=your_bot_token
ADMIN_USERNAME=your_admin_username
```

`ADMIN_USERNAME` is optional. Leave it empty if you do not need the admin button.

4. Start the bot:

```bash
python bot.py
```

Keep `words.txt` in the same directory as `bot.py`.

## Example

Send:

```text
TEACH
```

Bayan returns possible words from those letters, such as `TEACH` and `CHEAT`, based on the included dictionary.
