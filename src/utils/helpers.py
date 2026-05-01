"""
============================================
 FLARE AI - Helper Functions
============================================
Các hàm tiện ích dùng chung
============================================
"""

import discord
from typing import List, Optional, Union
from datetime import datetime

def format_code_block(code: str, language: str = "") -> str:
    """
    Format code thành Discord code block
    
    Args:
        code: Nội dung code
        language: Ngôn ngữ lập trình (python, javascript, etc.)
    
    Returns:
        Chuỗi code block đã format
    
    Example:
        >>> format_code_block("print('hello')", "python")
        '```python\\nprint('hello')\\n```'
    """
    return f"```{language}\n{code}\n```"

def split_long_message(
    content: str,
    max_length: int = 2000,
    delimiter: str = "\n"
) -> List[str]:
    """
    Chia tin nhắn dài thành nhiều phần nhỏ
    
    Args:
        content: Nội dung cần chia
        max_length: Độ dài tối đa mỗi phần (Discord limit: 2000)
        delimiter: Ký tự phân cách ưu tiên
    
    Returns:
        Danh sách các phần tin nhắn
    
    Example:
        >>> split_long_message("dòng1\\ndòng2\\ndòng3", max_length=10)
        ['dòng1', 'dòng2', 'dòng3']
    """
    if len(content) <= max_length:
        return [content]
    
    chunks = []
    lines = content.split(delimiter)
    current_chunk = ""
    
    for line in lines:
        # Nếu thêm dòng này vượt quá max_length
        if len(current_chunk) + len(line) + len(delimiter) > max_length:
            if current_chunk:
                chunks.append(current_chunk.rstrip(delimiter))
            
            # Nếu 1 dòng quá dài, cắt nhỏ
            if len(line) > max_length:
                for i in range(0, len(line), max_length):
                    chunks.append(line[i:i + max_length])
                current_chunk = ""
            else:
                current_chunk = line + delimiter
        else:
            current_chunk += line + delimiter
    
    if current_chunk:
        chunks.append(current_chunk.rstrip(delimiter))
    
    return chunks

def create_embed(
    title: str,
    description: str = "",
    color: int = 0x00ffcc,
    fields: Optional[List[dict]] = None,
    author: Optional[Union[discord.User, discord.Member]] = None,
    footer: Optional[str] = None,
    thumbnail: Optional[str] = None,
    image: Optional[str] = None
) -> discord.Embed:
    """
    Tạo Discord Embed đẹp mắt
    
    Args:
        title: Tiêu đề embed
        description: Mô tả
        color: Màu sắc (hex)
        fields: Danh sách fields [{name, value, inline}]
        author: Tác giả
        footer: Chân trang
        thumbnail: URL ảnh nhỏ
        image: URL ảnh lớn
    
    Returns:
        discord.Embed object
    
    Example:
        >>> embed = create_embed(
        ...     title="Hello",
        ...     description="World",
        ...     fields=[{"name": "Field1", "value": "Value1"}]
        ... )
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow()
    )
    
    if author:
        embed.set_author(
            name=author.display_name,
            icon_url=author.display_avatar.url if author.display_avatar else None
        )
    
    if fields:
        for field in fields:
            embed.add_field(
                name=field.get("name", ""),
                value=field.get("value", ""),
                inline=field.get("inline", False)
            )
    
    if footer:
        embed.set_footer(text=footer)
    
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    
    if image:
        embed.set_image(url=image)
    
    return embed

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Làm sạch input từ user
    
    Args:
        text: Text cần làm sạch
        max_length: Độ dài tối đa
    
    Returns:
        Text đã được làm sạch
    """
    # Xóa khoảng trắng thừa
    text = " ".join(text.split())
    
    # Cắt nếu quá dài
    if len(text) > max_length:
        text = text[:max_length - 3] + "..."
    
    return text.strip()

def get_timestamp() -> str:
    """Lấy timestamp hiện tại format đẹp"""
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Cắt ngắn text với suffix"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
