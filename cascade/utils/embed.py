from typing import Optional, List, Dict, Any
from datetime import datetime
from .color import Color

class EmbedField:
    def __init__(self, name: str, value: str, inline: bool = False):
        self.name = name
        self.value = value
        self.inline = inline
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'value': self.value,
            'inline': self.inline
        }

class EmbedAuthor:
    def __init__(self, name: str, url: str = None, icon_url: str = None):
        self.name = name
        self.url = url
        self.icon_url = icon_url
    
    def to_dict(self) -> dict:
        data = {'name': self.name}
        if self.url:
            data['url'] = self.url
        if self.icon_url:
            data['icon_url'] = self.icon_url
        return data

class EmbedFooter:
    def __init__(self, text: str, icon_url: str = None):
        self.text = text
        self.icon_url = icon_url
    
    def to_dict(self) -> dict:
        data = {'text': self.text}
        if self.icon_url:
            data['icon_url'] = self.icon_url
        return data

class Embed:
    def __init__(
        self,
        title: str = None,
        description: str = None,
        url: str = None,
        color: int = None,
        timestamp: datetime = None
    ):
        self.title = title
        self.description = description
        self.url = url
        self.color = color
        self.timestamp = timestamp
        self.fields: List[EmbedField] = []
        self.author: Optional[EmbedAuthor] = None
        self.footer: Optional[EmbedFooter] = None
        self.image_url: Optional[str] = None
        self.thumbnail_url: Optional[str] = None
    
    def add_field(self, name: str, value: str, inline: bool = False) -> 'Embed':
        self.fields.append(EmbedField(name, value, inline))
        return self
    
    def set_author(self, name: str, url: str = None, icon_url: str = None) -> 'Embed':
        self.author = EmbedAuthor(name, url, icon_url)
        return self
    
    def set_footer(self, text: str, icon_url: str = None) -> 'Embed':
        self.footer = EmbedFooter(text, icon_url)
        return self
    
    def set_image(self, url: str) -> 'Embed':
        self.image_url = url
        return self
    
    def set_thumbnail(self, url: str) -> 'Embed':
        self.thumbnail_url = url
        return self
    
    def set_color(self, color: int) -> 'Embed':
        self.color = color
        return self
    
    def to_dict(self) -> dict:
        data = {}
        
        if self.title:
            data['title'] = self.title
        if self.description:
            data['description'] = self.description
        if self.url:
            data['url'] = self.url
        if self.color is not None:
            data['color'] = self.color
        if self.timestamp:
            data['timestamp'] = self.timestamp.isoformat()
        
        if self.fields:
            data['fields'] = [f.to_dict() for f in self.fields]
        if self.author:
            data['author'] = self.author.to_dict()
        if self.footer:
            data['footer'] = self.footer.to_dict()
        if self.image_url:
            data['image'] = {'url': self.image_url}
        if self.thumbnail_url:
            data['thumbnail'] = {'url': self.thumbnail_url}
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Embed':
        embed = cls(
            title=data.get('title'),
            description=data.get('description'),
            url=data.get('url'),
            color=data.get('color')
        )
        
        if 'timestamp' in data:
            embed.timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        
        if 'author' in data:
            author = data['author']
            embed.set_author(
                author['name'],
                author.get('url'),
                author.get('icon_url')
            )
        
        if 'footer' in data:
            footer = data['footer']
            embed.set_footer(footer['text'], footer.get('icon_url'))
        
        if 'image' in data:
            embed.set_image(data['image']['url'])
        
        if 'thumbnail' in data:
            embed.set_thumbnail(data['thumbnail']['url'])
        
        if 'fields' in data:
            for field in data['fields']:
                embed.add_field(
                    field['name'],
                    field['value'],
                    field.get('inline', False)
                )
        
        return embed
