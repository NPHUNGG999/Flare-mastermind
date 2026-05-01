"""
============================================
 FLARE AI - Gemini Handler (TIẾT KIỆM QUOTA)
============================================
Max tokens: 250
History: 3 cặp tin nhắn gần nhất
Prompt được tối ưu ngắn gọn
============================================
"""

import asyncio
from typing import Dict, List, Optional, Any
import google.generativeai as genai

from ..utils.config import config
from ..utils.logger import get_logger
from .conversation import ConversationManager

log = get_logger(__name__)

class GeminiHandler:
    """
    Handler cho Google Gemini API - TIẾT KIỆM QUOTA
    
    Giới hạn:
    - Max output tokens: 250
    - History: 3 cặp gần nhất
    - Prompt được rút gọn tối đa
    """
    
    def __init__(self):
        """Khởi tạo handler với cấu hình tiết kiệm"""
        genai.configure(api_key=config.gemini.api_key)
        
        self.model_name = config.gemini.model
        self.temperature = config.gemini.temperature
        self.max_tokens = config.gemini.max_tokens  # 250 tokens
        self.conversation_manager = ConversationManager()
        
        # Cấu hình generation SIÊU TIẾT KIỆM
        generation_config = {
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens,  # CHỈ 250 TOKENS
            "top_p": 0.95,
            "top_k": 40,
        }
        
        # Safety settings
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        # Khởi tạo model
        try:
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            log.info(f"✅ Gemini Handler: {self.model_name} | Max tokens: {self.max_tokens}")
        except Exception as e:
            log.error(f"❌ Lỗi model, fallback về gemini-pro: {e}")
            self.model_name = "gemini-pro"
            self.model = genai.GenerativeModel(
                model_name="gemini-pro",
                generation_config=generation_config,
                safety_settings=safety_settings
            )
        
        self.prompts = config.prompts
        
        # Đếm request để kiểm soát rate limit
        self.request_count = 0
        self.last_reset_time = asyncio.get_event_loop().time()
    
    async def get_response(
        self,
        user_id: str,
        message: str,
        prompt_type: str = "default",
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Lấy phản hồi NGẮN GỌN từ Gemini
        
        Returns:
            Phản hồi tối đa 250 tokens
        """
        try:
            # Kiểm tra rate limit
            await self._check_rate_limit()
            
            # Lấy conversation
            conv = self.conversation_manager.get_conversation(user_id)
            
            # Chuẩn bị prompt SIÊU NGẮN
            full_prompt = self._prepare_short_prompt(
                conversation=conv,
                prompt_type=prompt_type,
                system_prompt=system_prompt,
                user_message=message
            )
            
            # Log độ dài prompt
            log.debug(f"Prompt length: {len(full_prompt)} chars")
            
            # Gọi API
            response = await self._call_gemini_api(full_prompt)
            
            # Lấy response
            if hasattr(response, 'text') and response.text:
                ai_response = response.text
                # Cắt nếu vượt quá (an toàn)
                if len(ai_response) > 1000:
                    ai_response = ai_response[:997] + "..."
            else:
                ai_response = "⚠️ Không có phản hồi. Thử lại nhé!"
            
            # Lưu history (chỉ lưu bản rút gọn)
            conv.add_message("user", message[:200])  # Chỉ lưu 200 ký tự
            conv.add_message("assistant", ai_response[:200])
            
            return ai_response
            
        except Exception as e:
            error_msg = str(e)
            log.error(f"Gemini error: {error_msg[:100]}")
            
            if "API_KEY" in error_msg.upper():
                return "❌ Lỗi API Key. Kiểm tra .env"
            elif "429" in error_msg or "RATE" in error_msg.upper():
                return "⏰ Đợi 30s rồi thử lại nhé!"
            elif "SAFETY" in error_msg.upper():
                return "⚠️ Nội dung bị chặn. Thử khác đi!"
            else:
                return f"❌ Lỗi: {error_msg[:80]}"
    
    async def _check_rate_limit(self):
        """Kiểm tra và giới hạn request"""
        current_time = asyncio.get_event_loop().time()
        
        # Reset counter mỗi 60 giây
        if current_time - self.last_reset_time > 60:
            self.request_count = 0
            self.last_reset_time = current_time
        
        # Nếu vượt quá giới hạn
        if self.request_count >= config.gemini.max_requests_per_minute:
            wait_time = 60 - (current_time - self.last_reset_time)
            if wait_time > 0:
                log.warning(f"⏳ Rate limit, đợi {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
                self.request_count = 0
                self.last_reset_time = asyncio.get_event_loop().time()
        
        self.request_count += 1
    
    def _prepare_short_prompt(
        self,
        conversation: "Conversation",
        prompt_type: str = "default",
        system_prompt: Optional[str] = None,
        user_message: str = ""
    ) -> str:
        """
        Chuẩn bị prompt SIÊU NGẮN để tiết kiệm token
        
        Format:
        [System ngắn]
        [3 cặp history gần nhất - rút gọn]
        [Câu hỏi hiện tại]
        """
        prompt_parts = []
        
        # 1. System prompt CỰC NGẮN
        if system_prompt:
            # Chỉ lấy 100 ký tự đầu của system prompt
            prompt_parts.append(f"System: {system_prompt[:100]}")
        else:
            # System mặc định siêu ngắn
            prompt_parts.append(f"System: You are {config.bot.name}, a helpful AI. Answer briefly in 2-3 sentences. Use Discord markdown.")
        
        # 2. History - CHỈ 3 CẶP GẦN NHẤT, mỗi tin rút gọn còn 150 ký tự
        history = conversation.get_context(last_n=3)
        
        if history:
            prompt_parts.append("History:")
            for msg in history:
                role = "U" if msg["role"] == "user" else "A"
                # Cắt cực ngắn
                content = msg["content"][:150]
                prompt_parts.append(f"{role}: {content}")
        
        # 3. Câu hỏi hiện tại - cắt còn 300 ký tự
        short_message = user_message[:300]
        prompt_parts.append(f"Q: {short_message}")
        prompt_parts.append("A: ")
        
        return "\n".join(prompt_parts)
    
    async def _call_gemini_api(
        self,
        prompt: str,
        max_retries: int = 2,
        retry_delay: float = 3.0
    ) -> Any:
        """Gọi Gemini API với retry"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = await asyncio.to_thread(
                    self.model.generate_content,
                    prompt
                )
                
                if response and response.text:
                    return response
                else:
                    raise Exception("Empty response")
                    
            except Exception as e:
                last_error = e
                error_str = str(e)
                
                # Chỉ retry với lỗi server/rate limit
                if any(x in error_str for x in ["429", "500", "502", "503"]):
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        log.warning(f"Retry {attempt + 1}/{max_retries} in {wait_time}s")
                        await asyncio.sleep(wait_time)
                        continue
                break
        
        raise last_error or Exception("API call failed")
    
    def clear_user_history(self, user_id: str) -> bool:
        """Xóa lịch sử"""
        return self.conversation_manager.clear_conversation(user_id)
    
    def get_stats(self) -> Dict:
        """Thống kê"""
        return {
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "requests_this_minute": self.request_count,
            **self.conversation_manager.get_stats()
        }