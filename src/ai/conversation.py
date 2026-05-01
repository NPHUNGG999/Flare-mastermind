"""
============================================
 FLARE AI - Conversation Manager
============================================
Quản lý lịch sử hội thoại
============================================
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import OrderedDict

from ..utils.logger import get_logger
from ..utils.config import config

log = get_logger(__name__)

class Conversation:
    """
    Quản lý một cuộc hội thoại
    
    Features:
    - Lưu trữ lịch sử tin nhắn
    - Tự động cắt bớt khi quá dài
    - Theo dõi thời gian hoạt động
    """
    
    def __init__(self, user_id: str, max_history: Optional[int] = None):
        """
        Khởi tạo conversation
        
        Args:
            user_id: ID của user
            max_history: Số cặp tin nhắn tối đa
        """
        self.user_id = user_id
        self.max_history = max_history or config.bot.max_history
        self.messages: List[Dict[str, str]] = []
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
    
    def add_message(self, role: str, content: str):
        """
        Thêm tin nhắn vào lịch sử
        
        Args:
            role: 'user' hoặc 'assistant' hoặc 'system'
            content: Nội dung tin nhắn
        """
        self.messages.append({
            "role": role,
            "content": content
        })
        self.last_activity = datetime.utcnow()
        
        # Tự động cắt bớt nếu quá dài
        max_messages = self.max_history * 2  # user + assistant pairs
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]
    
    def get_context(self, last_n: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Lấy context cho AI
        
        Args:
            last_n: Số cặp tin nhắn gần nhất
        
        Returns:
            Danh sách messages đã format
        """
        n = last_n or self.max_history
        max_messages = n * 2
        return self.messages[-max_messages:]
    
    def clear(self):
        """Xóa toàn bộ lịch sử"""
        self.messages.clear()
        log.debug(f"Đã xóa lịch sử của user {self.user_id}")
    
    @property
    def message_count(self) -> int:
        """Tổng số tin nhắn"""
        return len(self.messages)
    
    def is_expired(self, timeout_hours: int = 24) -> bool:
        """Kiểm tra conversation có hết hạn không"""
        return datetime.utcnow() - self.last_activity > timedelta(hours=timeout_hours)

class ConversationManager:
    """
    Quản lý tất cả conversations
    
    Features:
    - Tạo/lấy conversation cho user
    - Tự động dọn dẹp conversations cũ
    - Giới hạn số lượng conversations
    """
    
    def __init__(self, max_conversations: int = 1000):
        """
        Khởi tạo manager
        
        Args:
            max_conversations: Số conversations tối đa
        """
        self.conversations: Dict[str, Conversation] = OrderedDict()
        self.max_conversations = max_conversations
    
    def get_conversation(self, user_id: str) -> Conversation:
        """
        Lấy hoặc tạo conversation cho user
        
        Args:
            user_id: ID của user
        
        Returns:
            Conversation instance
        """
        # Tạo mới nếu chưa có
        if user_id not in self.conversations:
            # Dọn dẹp nếu quá nhiều
            if len(self.conversations) >= self.max_conversations:
                self._cleanup_old_conversations()
            
            self.conversations[user_id] = Conversation(user_id)
            log.debug(f"Tạo conversation mới cho user {user_id}")
        
        return self.conversations[user_id]
    
    def clear_conversation(self, user_id: str) -> bool:
        """
        Xóa lịch sử conversation của user
        
        Args:
            user_id: ID của user
        
        Returns:
            True nếu thành công
        """
        if user_id in self.conversations:
            self.conversations[user_id].clear()
            log.info(f"Đã xóa lịch sử của user {user_id}")
            return True
        return False
    
    def remove_conversation(self, user_id: str) -> bool:
        """
        Xóa hoàn toàn conversation
        
        Args:
            user_id: ID của user
        
        Returns:
            True nếu đã xóa
        """
        if user_id in self.conversations:
            del self.conversations[user_id]
            log.info(f"Đã xóa conversation của user {user_id}")
            return True
        return False
    
    def _cleanup_old_conversations(self):
        """Dọn dẹp conversations cũ hoặc hết hạn"""
        # Xóa conversations đã hết hạn (24h không hoạt động)
        expired = [
            uid for uid, conv in self.conversations.items()
            if conv.is_expired()
        ]
        for uid in expired:
            del self.conversations[uid]
            log.debug(f"Đã xóa conversation hết hạn của user {uid}")
        
        # Nếu vẫn quá nhiều, xóa 10% cũ nhất
        if len(self.conversations) >= self.max_conversations:
            remove_count = max(1, len(self.conversations) // 10)
            for _ in range(remove_count):
                self.conversations.popitem(last=False)
    
    @property
    def total_conversations(self) -> int:
        """Tổng số conversations đang quản lý"""
        return len(self.conversations)
    
    def get_stats(self) -> Dict[str, int]:
        """
        Lấy thống kê
        
        Returns:
            Dict chứa các số liệu thống kê
        """
        total_messages = sum(conv.message_count for conv in self.conversations.values())
        return {
            "total_conversations": len(self.conversations),
            "total_messages": total_messages,
            "avg_messages": total_messages / max(1, len(self.conversations))
        }
