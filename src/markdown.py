import re

def escape_markdown(text):
    if not text:
        return 'N/A'
    # Экранируем специальные символы Markdown
    return re.sub(r'([*_`\[\]()~>#+-=|{}.!])', r'\\\1', text)