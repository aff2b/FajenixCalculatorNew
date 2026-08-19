import re
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests
from telegram import Update
from telegram.constants import ChatType
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import (
    BOT_NAME,
    CURRENCY_API_URL,
    DEFAULT_WEATHER_COUNTRY,
    TOKEN,
    WEATHER_API_KEY,
)
from smart_calculator import calculate as smart_calculate


# Comprehensive common-city/country aliases. The bot also accepts IANA
# timezone names directly, e.g. /time Asia/Kolkata.
TIMEZONE_ALIASES = {
    "india": "Asia/Kolkata", "delhi": "Asia/Kolkata", "mumbai": "Asia/Kolkata",
    "kolkata": "Asia/Kolkata", "bangalore": "Asia/Kolkata", "bengaluru": "Asia/Kolkata",
    "chennai": "Asia/Kolkata", "hyderabad": "Asia/Kolkata", "pune": "Asia/Kolkata",
    "bangladesh": "Asia/Dhaka", "dhaka": "Asia/Dhaka", "pakistan": "Asia/Karachi",
    "karachi": "Asia/Karachi", "lahore": "Asia/Karachi",
    "nepal": "Asia/Kathmandu", "kathmandu": "Asia/Kathmandu",
    "sri lanka": "Asia/Colombo", "colombo": "Asia/Colombo",
    "myanmar": "Asia/Yangon", "yangon": "Asia/Yangon",
    "thailand": "Asia/Bangkok", "bangkok": "Asia/Bangkok",
    "vietnam": "Asia/Ho_Chi_Minh", "ho chi minh": "Asia/Ho_Chi_Minh",
    "indonesia": "Asia/Jakarta", "jakarta": "Asia/Jakarta",
    "singapore": "Asia/Singapore",
    "malaysia": "Asia/Kuala_Lumpur", "kuala lumpur": "Asia/Kuala_Lumpur",
    "philippines": "Asia/Manila", "manila": "Asia/Manila",
    "china": "Asia/Shanghai", "beijing": "Asia/Shanghai", "shanghai": "Asia/Shanghai",
    "hong kong": "Asia/Hong_Kong",
    "japan": "Asia/Tokyo", "tokyo": "Asia/Tokyo",
    "south korea": "Asia/Seoul", "korea": "Asia/Seoul", "seoul": "Asia/Seoul",
    "taiwan": "Asia/Taipei", "taipei": "Asia/Taipei",
    "uae": "Asia/Dubai", "dubai": "Asia/Dubai", "abu dhabi": "Asia/Dubai",
    "saudi arabia": "Asia/Riyadh", "riyadh": "Asia/Riyadh",
    "qatar": "Asia/Qatar", "doha": "Asia/Qatar",
    "israel": "Asia/Jerusalem", "jerusalem": "Asia/Jerusalem",
    "turkey": "Europe/Istanbul", "istanbul": "Europe/Istanbul",
    "iran": "Asia/Tehran", "iraq": "Asia/Baghdad", "kuwait": "Asia/Kuwait",
    "uk": "Europe/London", "united kingdom": "Europe/London", "london": "Europe/London",
    "ireland": "Europe/Dublin", "dublin": "Europe/Dublin",
    "france": "Europe/Paris", "paris": "Europe/Paris",
    "germany": "Europe/Berlin", "berlin": "Europe/Berlin",
    "italy": "Europe/Rome", "rome": "Europe/Rome",
    "spain": "Europe/Madrid", "madrid": "Europe/Madrid",
    "portugal": "Europe/Lisbon", "lisbon": "Europe/Lisbon",
    "netherlands": "Europe/Amsterdam", "amsterdam": "Europe/Amsterdam",
    "switzerland": "Europe/Zurich", "zurich": "Europe/Zurich",
    "austria": "Europe/Vienna", "vienna": "Europe/Vienna",
    "greece": "Europe/Athens", "athens": "Europe/Athens",
    "russia": "Europe/Moscow", "moscow": "Europe/Moscow",
    "ukraine": "Europe/Kyiv", "kyiv": "Europe/Kyiv",
    "egypt": "Africa/Cairo", "cairo": "Africa/Cairo",
    "nigeria": "Africa/Lagos", "lagos": "Africa/Lagos",
    "ghana": "Africa/Accra", "accra": "Africa/Accra",
    "kenya": "Africa/Nairobi", "nairobi": "Africa/Nairobi",
    "south africa": "Africa/Johannesburg", "johannesburg": "Africa/Johannesburg",
    "morocco": "Africa/Casablanca", "casablanca": "Africa/Casablanca",
    "algeria": "Africa/Algiers", "algiers": "Africa/Algiers",
    "usa": "America/New_York", "united states": "America/New_York",
    "new york": "America/New_York", "new york city": "America/New_York",
    "california": "America/Los_Angeles", "los angeles": "America/Los_Angeles",
    "san francisco": "America/Los_Angeles", "chicago": "America/Chicago",
    "denver": "America/Denver", "houston": "America/Chicago",
    "canada": "America/Toronto", "toronto": "America/Toronto", "vancouver": "America/Vancouver",
    "mexico": "America/Mexico_City", "mexico city": "America/Mexico_City",
    "brazil": "America/Sao_Paulo", "sao paulo": "America/Sao_Paulo",
    "argentina": "America/Argentina/Buenos_Aires", "buenos aires": "America/Argentina/Buenos_Aires",
    "chile": "America/Santiago", "santiago": "America/Santiago",
    "colombia": "America/Bogota", "bogota": "America/Bogota",
    "peru": "America/Lima", "lima": "America/Lima",
    "new zealand": "Pacific/Auckland", "auckland": "Pacific/Auckland",
    "australia": "Australia/Sydney", "sydney": "Australia/Sydney",
    "melbourne": "Australia/Melbourne", "perth": "Australia/Perth",
    "fiji": "Pacific/Fiji", "suva": "Pacific/Fiji",
    "hawaii": "Pacific/Honolulu", "honolulu": "Pacific/Honolulu",
}


def format_amount(value):
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return f"{value:g}"


def get_weather(city):
    if not WEATHER_API_KEY:
        return None, "missing_key"

    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
    }

    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params=params,
            timeout=10,
        )

        if response.status_code != 200:
            return None, "unavailable"

        data = response.json()

        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temp": data["main"]["temp"],
            "feels": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "weather": data["weather"][0]["description"].title(),
            "wind": data["wind"]["speed"],
            "pressure": data["main"].get("pressure"),
            "visibility": data.get("visibility"),
        }, None

    except (requests.RequestException, KeyError, TypeError, ValueError):
        return None, "unavailable"


def weather_text(weather):
    visibility = ""
    if weather.get("visibility") is not None:
        visibility = f"\n👁 Visibility: {weather['visibility'] / 1000:.1f} km"

    pressure = ""
    if weather.get("pressure") is not None:
        pressure = f"\n🧭 Pressure: {weather['pressure']} hPa"

    return (
        f"🌤 Weather in {weather['city']}, {weather['country']}\n\n"
        f"🌡 Temperature: {weather['temp']}°C\n"
        f"🤒 Feels like: {weather['feels']}°C\n"
        f"☁️ Condition: {weather['weather']}\n"
        f"💧 Humidity: {weather['humidity']}%\n"
        f"💨 Wind: {weather['wind']} m/s"
        f"{pressure}{visibility}"
    )


async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "🌤 Usage: /weather <city>\nExample: /weather Delhi"
        )
        return

    city = " ".join(context.args)
    if DEFAULT_WEATHER_COUNTRY and "," not in city:
        city = f"{city},{DEFAULT_WEATHER_COUNTRY}"

    weather, error = get_weather(city)

    if error == "missing_key":
        await update.message.reply_text(
            "❌ Weather is not configured yet. Add WEATHER_API_KEY in Railway Variables."
        )
        return

    if weather is None:
        await update.message.reply_text(
            "❌ I couldn't find that city or the weather service is unavailable."
        )
        return

    await update.message.reply_text(weather_text(weather))


def convert_currency(amount, from_currency, to_currency):
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    try:
        response = requests.get(
            f"{CURRENCY_API_URL}{from_currency}",
            timeout=10,
        )
        if response.status_code != 200:
            return None

        data = response.json()
        if data.get("result") != "success":
            return None

        rate = data.get("rates", {}).get(to_currency)
        if rate is None:
            return None

        return amount * rate

    except (requests.RequestException, TypeError, ValueError):
        return None


def parse_currency(text):
    cleaned = re.sub(r"[?,]", "", text.strip().upper())
    cleaned = re.sub(r"\s+", " ", cleaned)

    patterns = [
        r"^(\d+(?:\.\d+)?)\s*([A-Z]{3})\s+(?:TO|IN|INTO)\s+([A-Z]{3})$",
        r"^(\d+(?:\.\d+)?)\s*([A-Z]{3})\s+HOW\s+MUCH\s+([A-Z]{3})$",
        r"^CONVERT\s+(\d+(?:\.\d+)?)\s*([A-Z]{3})\s+(?:TO|IN|INTO)\s+([A-Z]{3})$",
        r"^HOW\s+MUCH\s+IS\s+(\d+(?:\.\d+)?)\s*([A-Z]{3})\s+IN\s+([A-Z]{3})$",
        r"^HOW\s+MUCH\s+IS\s+(\d+(?:\.\d+)?)\s*([A-Z]{3})\s+TO\s+([A-Z]{3})$",
        r"^(\d+(?:\.\d+)?)\s*([A-Z]{3})\s+USE\s+([A-Z]{3})$",
    ]

    for pattern in patterns:
        match = re.fullmatch(pattern, cleaned)
        if match:
            return float(match.group(1)), match.group(2), match.group(3)

    return None


async def currency_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 3 or context.args[1].lower() not in ("to", "in"):
        await update.message.reply_text(
            "💱 Usage: /convert 200 INR USD\nExample: /convert 200 INR USD"
        )
        return

    try:
        amount = float(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid amount.")
        return

    from_currency = context.args[1] if context.args[1].lower() not in ("to", "in") else None
    # Normal documented form: /convert 200 INR USD
    if from_currency is None:
        from_currency = context.args[0]
        await update.message.reply_text("💱 Usage: /convert 200 INR USD")
        return


async def convert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 3:
        await update.message.reply_text(
            "💱 Usage: /convert 200 INR USD"
        )
        return

    try:
        amount = float(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid amount.")
        return

    from_currency = context.args[1].upper()
    to_currency = context.args[2].upper()

    result = convert_currency(amount, from_currency, to_currency)

    if result is None:
        await update.message.reply_text(
            "❌ Conversion failed. Check the currency codes."
        )
        return

    await update.message.reply_text(
        f"💱 {format_amount(amount)} {from_currency} = "
        f"{format_amount(result)} {to_currency}"
    )


def resolve_timezone(location):
    key = re.sub(r"\s+", " ", location.strip().lower())
    if key in TIMEZONE_ALIASES:
        return TIMEZONE_ALIASES[key]

    # Direct IANA timezone, e.g. Asia/Kolkata.
    try:
        ZoneInfo(location.strip())
        return location.strip()
    except ZoneInfoNotFoundError:
        return None


async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "🕐 Usage: /time <city/country/timezone>\n"
            "Examples:\n"
            "/time India\n"
            "/time Tokyo\n"
            "/time America/New_York"
        )
        return

    location = " ".join(context.args)
    timezone_name = resolve_timezone(location)

    if timezone_name is None:
        await update.message.reply_text(
            "❌ I couldn't identify that timezone.\n"
            "Try a major city/country or an IANA timezone such as Asia/Kolkata."
        )
        return

    now = datetime.now(ZoneInfo(timezone_name))
    offset = now.strftime("%z")
    offset = f"{offset[:3]}:{offset[3:]}" if len(offset) == 5 else offset

    await update.message.reply_text(
        f"🕐 Time: {location.title()}\n\n"
        f"📅 {now.strftime('%A, %d %B %Y')}\n"
        f"⏰ {now.strftime('%I:%M:%S %p')}\n"
        f"🌍 Timezone: {timezone_name}\n"
        f"🧭 UTC offset: {offset}"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Fajenix Calculator! 🧩\n\n"
        "🧮 Advanced Calculator\n"
        "🌤 Worldwide Weather\n"
        "💱 Currency Converter\n"
        "🕐 Worldwide Timezones\n\n"
        "Use /help for examples."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Fajenix Calculator — Commands\n\n"
        "🧮 MATH\n"
        "4+5\n"
        "2^10\n"
        "sin30°\n"
        "cos60°\n"
        "tan45°\n"
        "sqrt(25)\n"
        "log(100)\n"
        "25% of 480\n\n"
        "🌤 WEATHER\n"
        "/weather Delhi\n"
        "/weather Tokyo\n\n"
        "💱 CURRENCY\n"
        "200 INR to USD\n"
        "200 INR in USD\n"
        "How much is 200 INR in USD?\n"
        "/convert 200 INR USD\n\n"
        "🕐 TIME\n"
        "/time India\n"
        "/time Tokyo\n"
        "/time London\n"
        "/time America/New_York\n\n"
        "💡 Normal chat messages are ignored."
    )


async def calculate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    original_text = update.message.text.strip()
    if not original_text:
        return

    # Natural weather request.
    if original_text.lower().startswith("weather "):
        city = original_text[8:].strip()
        weather, error = get_weather(city)

        if error == "missing_key":
            await update.message.reply_text(
                "❌ Weather is not configured. Add WEATHER_API_KEY in Railway Variables."
            )
        elif weather is None:
            await update.message.reply_text(
                "❌ I couldn't find that city or the weather service is unavailable."
            )
        else:
            await update.message.reply_text(weather_text(weather))
        return

    # Natural currency request.
    currency = parse_currency(original_text)
    if currency:
        amount, from_currency, to_currency = currency
        result = convert_currency(amount, from_currency, to_currency)

        if result is None:
            await update.message.reply_text(
                "❌ Conversion failed. Check the 3-letter currency codes."
            )
        else:
            await update.message.reply_text(
                f"💱 {format_amount(amount)} {from_currency} = "
                f"{format_amount(result)} {to_currency}"
            )
        return

    # Ignore ordinary conversation. Only attempt calculation when the
    # message has mathematical evidence.
    math_function_pattern = (
        r"\b(sin|cos|tan|asin|acos|atan|sqrt|log|ln|abs|round|pow|"
        r"floor|ceil|factorial|fact)\b"
    )

    looks_like_math = bool(
        re.fullmatch(r"[+-]?\d+(?:\.\d+)?", original_text)
        or re.search(r"[+\-*/^×÷−]", original_text)
        or re.search(math_function_pattern, original_text.lower())
        or re.search(
            r"\b\d+(?:\.\d+)?\s*%\s*of\s*\d+",
            original_text.lower()
        )
        or re.search(r"\b(pi|π|e)\b", original_text.lower())
    )

    if not looks_like_math:
        return

    try:
        result = smart_calculate(original_text)
        await update.message.reply_text(f"⚡ Answer: {result}")
    except Exception:
        await update.message.reply_text(
            "❌ Invalid expression.\n"
            "Try: 4+5, 2^10, sin30°, sqrt(25)"
        )


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is not configured.")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("weather", weather_command))
    app.add_handler(CommandHandler("time", time_command))
    app.add_handler(CommandHandler("convert", convert_command))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, calculate_message)
    )

    print(f"{BOT_NAME} is running...")
    app.run_polling()


if __name__ == "__main__":
    main()

