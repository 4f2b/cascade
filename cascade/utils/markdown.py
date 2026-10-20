import re
from typing import Dict, List, Tuple

class MarkdownProcessor:
    BOLD = re.compile(r'\*\*(.*?)\*\*')
    ITALIC = re.compile(r'\*(.*?)\*|_(.*?)_')
    UNDERLINE = re.compile(r'__(.*?)__')
    STRIKETHROUGH = re.compile(r'~~(.*?)~~')
    CODE_INLINE = re.compile(r'`([^`]+)`')
    CODE_BLOCK = re.compile(r'```(?:(\w+)\n)?(.*?)```', re.DOTALL)
    SPOILER = re.compile(r'\|\|(.*?)\|\|')
    QUOTE = re.compile(r'^> (.+)$', re.MULTILINE)
    BLOCKQUOTE = re.compile(r'^>>> (.+)', re.DOTALL | re.MULTILINE)
    
    @classmethod
    def strip(cls, text: str) -> str:
        text = cls.CODE_BLOCK.sub(r'\2', text)
        text = cls.CODE_INLINE.sub(r'\1', text)
        text = cls.BOLD.sub(r'\1', text)
        text = cls.UNDERLINE.sub(r'\1', text)
        text = cls.ITALIC.sub(r'\1\2', text)
        text = cls.STRIKETHROUGH.sub(r'\1', text)
        text = cls.SPOILER.sub(r'\1', text)
        text = cls.BLOCKQUOTE.sub(r'\1', text)
        text = cls.QUOTE.sub(r'\1', text)
        return text
    
    @classmethod
    def escape(cls, text: str, *, mass_mentions: bool = False, invites: bool = False) -> str:
        text = text.replace('\\', '\\\\')
        text = text.replace('*', '\\*')
        text = text.replace('_', '\\_')
        text = text.replace('`', '\\`')
        text = text.replace('~', '\\~')
        text = text.replace('>', '\\>')
        text = text.replace('|', '\\|')
        
        if mass_mentions:
            text = text.replace('@everyone', '@\u200beveryone')
            text = text.replace('@here', '@\u200bhere')
        
        if invites:
            text = text.replace('discord.gg/', 'discord\u200b.gg/')
        
        return text
    
    @classmethod
    def extract_mentions(cls, text: str) -> Dict[str, List[str]]:
        users = re.findall(r'<@!?(\d+)>', text)
        roles = re.findall(r'<@&(\d+)>', text)
        channels = re.findall(r'<#(\d+)>', text)
        
        return {
            'users': users,
            'roles': roles,
            'channels': channels
        }
    
    @classmethod
    def extract_emojis(cls, text: str) -> List[Tuple[str, str, bool]]:
        custom = re.findall(r'<(a?):(\w+):(\d+)>', text)
        return [(name, emoji_id, animated == 'a') for animated, name, emoji_id in custom]
    
    @classmethod
    def extract_links(cls, text: str) -> List[str]:
        return re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)
    
    @classmethod
    def extract_code_blocks(cls, text: str) -> List[Tuple[str, str]]:
        matches = cls.CODE_BLOCK.findall(text)
        return [(lang or '', code) for lang, code in matches]

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

def code_block(text: str, language: str = '') -> str:
    return f'```{language}\n{text}\n```'

def spoiler(text: str) -> str:
    return f'||{text}||'

def quote(text: str) -> str:
    return '\n'.join(f'> {line}' for line in text.split('\n'))

def blockquote(text: str) -> str:
    return f'>>> {text}'

def hyperlink(text: str, url: str) -> str:
    return f'[{text}]({url})'

def masked_link(text: str, url: str) -> str:
    return f'[{text}]({url} "{text}")'
