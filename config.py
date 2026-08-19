import os

BOT_NAME = "Fajenix Calculator🧩"

# Secrets are supplied through Railway Variables.
BOT_TOKEN = os.getenv("BOT_TOKEN")
TOKEN = BOT_TOKEN

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

CURRENCY_API_URL = "https://open.er-api.com/v6/latest/"

# Optional: set a default country for weather/city searches if desired.
DEFAULT_WEATHER_COUNTRY = os.getenv("DEFAULT_WEATHER_COUNTRY", "")

