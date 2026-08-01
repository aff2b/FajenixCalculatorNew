from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import TOKEN, BOT_NAME
from smart_calculator import calculate as smart_calculate

import os
import requests

WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Fajenix Calculator!\n\n"
        "Available Features:\n"
        "🧮 Calculator\n"
        "🌤 Weather\n"
        "💱 Currency Converter\n\n"
        "Use /help to see all commands."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Fajenix Calculator\n\n"
        "Examples:\n\n"
        "25+75\n"
        "2^10\n"
        "25% of 480\n\n"
        "weather Delhi\n"
        "weather London\n\n"
        "100 USD TO INR\n"
        "500 INR TO BDT"
    )


def get_weather(city):
    if not WEATHER_API_KEY:
        return None

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={WEATHER_API_KEY}&units=metric"
    )

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temp": data["main"]["temp"],
            "feels": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "weather": data["weather"][0]["description"].title(),
            "wind": data["wind"]["speed"],
        }

    except Exception:
        return None


def convert_currency(amount, from_currency, to_currency):
    url = f"https://open.er-api.com/v6/latest/{from_currency.upper()}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        if data.get("result") != "success":
            return None

        rates = data.get("rates", {})

        if to_currency.upper() not in rates:
            return None

        return round(amount * rates[to_currency.upper()], 2)

    except Exception:
        return None


async def calculate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    original_text = update.message.text.strip()
    text = original_text.lower()

    # Weather
    if text.startswith("weather "):
        city = original_text[8:].strip()
        weather = get_weather(city)

        if weather is None:
            await update.message.reply_text(
                "❌ City not found or weather service unavailable."
            )
        else:
            await update.message.reply_text(
                f"🌤 Weather in {weather['city']}, {weather['country']}\n\n"
                f"🌡 Temperature: {weather['temp']}°C\n"
                f"🤒 Feels like: {weather['feels']}°C\n"
                f"☁️ Condition: {weather['weather']}\n"
                f"💧 Humidity: {weather['humidity']}%\n"
                f"💨 Wind: {weather['wind']} m/s"
            )
        return

    # Currency
    parts = original_text.upper().split()

    if len(parts) == 4 and parts[2] == "TO":
        try:
            amount = float(parts[0])
        except ValueError:
            amount = None

        if amount is not None:
            result = convert_currency(amount, parts[1], parts[3])

            if result is None:
                await update.message.reply_text("❌ Invalid currency code.")
            else:
                await update.message.reply_text(
                    f"💱 {amount} {parts[1]} = {result} {parts[3]}"
                )
            return

    # Calculator
    try:
        result = smart_calculate(text)
        await update.message.reply_text(f"⚡ Answer: {result}")
    except Exception:
        await update.message.reply_text("❌ Invalid expression.")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            calculate_message,
        )
    )

    print(f"{BOT_NAME} is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
