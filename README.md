# Fajenix Calculator

Premium Telegram calculator bot with custom emoji UI.

## Features

- Advanced calculator using a safe AST evaluator
- Percentage calculations
- Trigonometric functions in degrees
- Currency conversion
- Worldwide weather
- Worldwide timezone lookup
- `/profile`, `/settings`, and `/premium`
- Telegram custom emojis integrated into bot responses
- Strict math-only message detection; ordinary chat such as `Hello 7+8` is ignored
- No custom-emoji numeric IDs are shown to users

## Environment variables

Set these in Railway (or your deployment environment):

- `BOT_TOKEN` — Telegram bot token
- `WEATHER_API_KEY` — OpenWeather API key (optional; weather is disabled without it)
- `DEFAULT_WEATHER_COUNTRY` — optional default country code for weather searches

## Files

- `bot.py` — Telegram handlers and application entry point
- `smart_calculator.py` — calculator engine
- `custom_emojis.py` — centralized Telegram custom emoji IDs and HTML helpers
- `config.py` — environment configuration
- `requirements.txt` — Python dependencies

## Custom emojis

The supplied custom emoji IDs are stored in `custom_emojis.py`. The bot sends them using Telegram's HTML `<tg-emoji emoji-id="...">` entity syntax with Unicode fallbacks.

Do not put your bot token or API keys in source control.
