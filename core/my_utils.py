import re


def escape_for_telegram(text: str) -> str:
    """Экранирует символы '(', ')', '-' в строке."""
    return re.sub(r'([()/!-\[\]|=.])', r'\\\1', text)
