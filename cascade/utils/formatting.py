import re
from typing import Union


def escape_markdown(text: str, *, as_needed: bool = False, ignore_links: bool = True) -> str:
    if as_needed:
        text = re.sub(r'\\', r'\\\\', text)
        text = re.sub(r'([*_`~|])', r'\\\1', text)
    else:
        text = text.replace('\\', '\\\\')
        text = text.replace('*', '\\*')
        text = text.replace('_', '\\_')
        text = text.replace('`', '\\`')
        text = text.replace('~', '\\~')
        text = text.replace('|', '\\|')
    
    if ignore_links:
        return text
    
    return re.sub(r'(\[.+?\]\(.+?\))', r'\\\1', text)


def escape_mentions(text: str) -> str:
    text = text.replace('@', '@\u200b')
    text = text.replace('#', '#\u200b')
    return text


def bold(text: str) -> str:
    return f'**{text}**'


def italic(text: str) -> str:
    return f'*{text}*'


def underline(text: str) -> str:
    return f'__{text}__'


def strikethrough(text: str) -> str:
    return f'~~{text}~~'


def code(text: str) -> str:
    return f'`{text}`'


def codeblock(text: str, language: str = '') -> str:
    return f'```{language}\n{text}\n```'


def spoiler(text: str) -> str:
    return f'||{text}||'


def quote(text: str) -> str:
    return '\n'.join(f'> {line}' for line in text.split('\n'))


def blockquote(text: str) -> str:
    return f'>>> {text}'


def hyperlink(text: str, url: str) -> str:
    return f'[{text}]({url})'


def timestamp(unix: Union[int, float], style: str = 'f') -> str:
    return f'<t:{int(unix)}:{style}>'
