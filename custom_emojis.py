"""Telegram custom emoji definitions and helpers for Fajenix Calculator."""

from html import escape

# Custom emoji IDs supplied for Fajenix Calculator Bot v3.
CUSTOM_EMOJI_IDS = {
    "calculator": "6258008641534698537",
    "numbers": "6260559534280942037",
    "success": "6291889503934095924",
    "error": "6260381026850186008",
    "calculation": "6260500615919575542",
    "currency": "5197434882321567830",
    "money": "5195033767969839232",
    "conversion": "6258065652930585820",
    "globe": "6080076551712413321",
    "info": "6079983015914641137",
    "settings": "6260182522051701559",
    "help": "6260301720279064651",
    "loading": "6242308461598610637",
    "profile": "6260356000075751475",
    "premium": "6260430410384155184",
    "temperature": "5470049770997292425",
    "feels": "6260026906796630644",
    "condition": "5785109764170060865",
    "humidity": "6291652426034323357",
    "wind": "6260291661465658203",
    "pressure": "5411200584374056500",
    "visibility": "6291623443595014792",
    "date": "6289569375485697039",
    "timezone": "6260541950684831058",
    "bot_header": "6260114339445873234",
    "weather": "6237491831869806976",
    "ignored": "6237702328216982810",
    "branding": "6291579128122449693",
}

FALLBACKS = {
    "calculator": "🧮",
    "numbers": "🔢",
    "success": "✅",
    "error": "❌",
    "calculation": "⚡",
    "currency": "💱",
    "money": "💰",
    "conversion": "📈",
    "globe": "🌐",
    "info": "📊",
    "settings": "⚙️",
    "help": "❓",
    "loading": "🕐",
    "profile": "👤",
    "premium": "⭐",
    "temperature": "🌡️",
    "feels": "🤒",
    "condition": "☁️",
    "humidity": "💧",
    "wind": "💨",
    "pressure": "🧭",
    "visibility": "👁️",
    "date": "📅",
    "timezone": "🌍",
    "bot_header": "🤖",
    "weather": "🌤️",
    "ignored": "💡",
    "branding": "🧩",
}


def emoji(name: str) -> str:
    """Return Telegram HTML for a custom emoji.

    The numeric custom-emoji ID is encoded in the Telegram entity and is
    never included as visible message text.
    """
    emoji_id = CUSTOM_EMOJI_IDS[name]
    fallback = escape(FALLBACKS[name])
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'
