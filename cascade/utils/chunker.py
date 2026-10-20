from typing import List, TypeVar, Iterator

T = TypeVar('T')

def chunk(items: List[T], size: int) -> Iterator[List[T]]:
    for i in range(0, len(items), size):
        yield items[i:i + size]

def split_content(text: str, max_length: int = 2000, separator: str = '\n') -> List[str]:
    if len(text) <= max_length:
        return [text]
    
    parts = []
    current = []
    current_length = 0
    
    for line in text.split(separator):
        line_length = len(line) + len(separator)
        
        if current_length + line_length > max_length:
            if current:
                parts.append(separator.join(current))
                current = []
                current_length = 0
            
            if line_length > max_length:
                for i in range(0, len(line), max_length):
                    parts.append(line[i:i + max_length])
            else:
                current.append(line)
                current_length = line_length
        else:
            current.append(line)
            current_length += line_length
    
    if current:
        parts.append(separator.join(current))
    
    return parts

def paginate(items: List[T], per_page: int = 10) -> List[List[T]]:
    return list(chunk(items, per_page))
