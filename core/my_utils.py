import re


def escape_for_telegram(text: str) -> str:
    """Экранирует символы, которые вызывают ошибку Telegram API в строке."""
    return re.sub(r'([()/!-\[\]|=.])', r'\\\1', text)
