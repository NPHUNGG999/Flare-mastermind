"""
============================================
 FLARE AI - AI Package
============================================
Xử lý trí tuệ nhân tạo (Gemini API)
============================================
"""

from .gemini_handler import GeminiHandler
from .conversation import Conversation, ConversationManager

__all__ = ["GeminiHandler", "Conversation", "ConversationManager"]