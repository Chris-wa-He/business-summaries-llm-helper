"""
对话服务模块 / Conversation Service Module

管理对话会话生命周期和上下文感知功能。
Manages conversation session lifecycle and context awareness functionality.
"""

import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..models.refinement_models import ConversationSession, ConversationMessage
from ..storage.conversation_store import ConversationStore


logger = logging.getLogger(__name__)


class ConversationService:
    """对话服务类 / Conversation Service Class"""
    
    def __init__(self):
        """初始化对话服务 / Initialize conversation service"""
        self.conversation_store = ConversationStore()
        self.context_window_size = 10  # 保留最近10轮对话
        self.relevance_threshold = 0.3  # 相关性阈值
        
        logger.info("对话服务初始化完成")
    
    def create_session(self, user_id: str, initial_content: str) -> str:
        """
        创建对话会话 / Create conversation session
        
        Args:
            user_id: 用户ID / User ID
            initial_content: 初始内容 / Initial content
            
        Returns:
            会话ID / Session ID
        """
        try:
            session = ConversationSession(
                id=f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id[:8]}",
                user_id=user_id,
                initial_content=initial_content,
                current_content=initial_content,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                status="active",
                context_summary="",
                preferences={}
            )
            
            self.conversation_store.save_session(session)
            logger.info(f"创建对话会话成功: {session.id}")
            return session.id
            
        except Exception as e:
            logger.error(f"创建对话会话失败: {e}")
            raise
    
    def add_message(self, session_id: str, message: ConversationMessage) -> None:
        """
        添加对话消息 / Add conversation message
        
        Args:
            session_id: 会话ID / Session ID
            message: 对话消息 / Conversation message
        """
        try:
            session = self.conversation_store.load_session(session_id)
            if not session:
                raise ValueError(f"会话不存在: {session_id}")
            
            # 更新会话时间
            session.updated_at = datetime.now()
            self.conversation_store.save_session(session)
            
            logger.info(f"添加对话消息成功: {session_id}")
            
        except Exception as e:
            logger.error(f"添加对话消息失败: {session_id}, 错误: {e}")
            raise
    
    def get_conversation_history(self, session_id: str) -> List[ConversationMessage]:
        """
        获取对话历史 / Get conversation history
        
        Args:
            session_id: 会话ID / Session ID
            
        Returns:
            对话消息列表 / List of conversation messages
        """
        try:
            session = self.conversation_store.load_session(session_id)
            if not session:
                return []
            
            # 这里返回空列表，实际实现中会从存储中获取消息
            # 当前版本专注于基础框架
            return []
            
        except Exception as e:
            logger.error(f"获取对话历史失败: {session_id}, 错误: {e}")
            return []
    
    def compress_context(self, session_id: str) -> None:
        """
        压缩对话上下文 / Compress conversation context
        
        Args:
            session_id: 会话ID / Session ID
        """
        try:
            session = self.conversation_store.load_session(session_id)
            if not session:
                return
            
            messages = self.get_conversation_history(session_id)
            
            # 如果消息数量超过窗口大小，进行压缩
            if len(messages) > self.context_window_size:
                # 保留最近的消息
                recent_messages = messages[-self.context_window_size:]
                
                # 生成上下文摘要
                context_summary = self._generate_context_summary(messages[:-self.context_window_size])
                session.context_summary = context_summary
                
                # 更新会话
                session.updated_at = datetime.now()
                self.conversation_store.save_session(session)
                
                logger.info(f"压缩对话上下文完成: {session_id}")
            
        except Exception as e:
            logger.error(f"压缩对话上下文失败: {session_id}, 错误: {e}")
    
    def clear_session(self, session_id: str) -> None:
        """
        清空对话会话 / Clear conversation session
        
        Args:
            session_id: 会话ID / Session ID
        """
        try:
            session = self.conversation_store.load_session(session_id)
            if not session:
                return
            
            # 重置会话状态
            session.context_summary = ""
            session.updated_at = datetime.now()
            self.conversation_store.save_session(session)
            
            logger.info(f"清空对话会话完成: {session_id}")
            
        except Exception as e:
            logger.error(f"清空对话会话失败: {session_id}, 错误: {e}")
    
    def get_relevant_context(self, session_id: str, query: str) -> str:
        """
        获取相关上下文 / Get relevant context
        
        Args:
            session_id: 会话ID / Session ID
            query: 查询内容 / Query content
            
        Returns:
            相关上下文 / Relevant context
        """
        try:
            session = self.conversation_store.load_session(session_id)
            if not session:
                return ""
            
            messages = self.get_conversation_history(session_id)
            relevant_messages = []
            
            # 计算消息相关性
            for message in messages[-self.context_window_size:]:
                relevance_score = self._calculate_relevance(message.content, query)
                if relevance_score > self.relevance_threshold:
                    relevant_messages.append((message, relevance_score))
            
            # 按相关性排序
            relevant_messages.sort(key=lambda x: x[1], reverse=True)
            
            # 构建上下文
            context_parts = []
            if session.context_summary:
                context_parts.append(f"历史摘要: {session.context_summary}")
            
            for message, score in relevant_messages[:5]:  # 最多5条相关消息
                context_parts.append(f"[{message.sender}]: {message.content}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"获取相关上下文失败: {session_id}, 错误: {e}")
            return ""
    
    def update_context_weights(self, session_id: str, feedback: Dict) -> None:
        """
        更新上下文权重 / Update context weights
        
        Args:
            session_id: 会话ID / Session ID
            feedback: 反馈信息 / Feedback information
        """
        try:
            session = self.conversation_store.load_session(session_id)
            if not session:
                return
            
            # 根据反馈调整上下文权重
            # 这里是基础实现，后续可以扩展为更复杂的学习算法
            if feedback.get("helpful", False):
                # 正面反馈，增加相关性阈值的权重
                self.relevance_threshold = max(0.1, self.relevance_threshold - 0.05)
            else:
                # 负面反馈，降低相关性阈值的权重
                self.relevance_threshold = min(0.8, self.relevance_threshold + 0.05)
            
            logger.info(f"更新上下文权重完成: {session_id}")
            
        except Exception as e:
            logger.error(f"更新上下文权重失败: {session_id}, 错误: {e}")
    
    def _calculate_relevance(self, message_content: str, query: str) -> float:
        """
        计算消息与查询的相关性 / Calculate relevance between message and query
        
        Args:
            message_content: 消息内容 / Message content
            query: 查询内容 / Query content
            
        Returns:
            相关性得分 / Relevance score
        """
        try:
            # 简单的关键词匹配算法
            message_words = set(re.findall(r'\w+', message_content.lower()))
            query_words = set(re.findall(r'\w+', query.lower()))
            
            if not query_words:
                return 0.0
            
            # 计算交集比例
            common_words = message_words & query_words
            relevance_score = len(common_words) / len(query_words)
            
            # 考虑消息长度因子
            length_factor = min(1.0, len(message_content) / 100)
            
            return relevance_score * length_factor
            
        except Exception as e:
            logger.error(f"计算相关性失败: {e}")
            return 0.0
    
    def _generate_context_summary(self, messages: List[ConversationMessage]) -> str:
        """
        生成上下文摘要 / Generate context summary
        
        Args:
            messages: 消息列表 / Message list
            
        Returns:
            上下文摘要 / Context summary
        """
        try:
            if not messages:
                return ""
            
            # 简单的摘要生成：提取关键信息
            summary_parts = []
            
            # 统计消息类型
            user_messages = [m for m in messages if m.sender == "user"]
            ai_messages = [m for m in messages if m.sender == "ai"]
            
            if user_messages:
                # 提取用户的主要请求
                recent_requests = [m.content[:50] + "..." for m in user_messages[-3:]]
                summary_parts.append(f"用户请求: {'; '.join(recent_requests)}")
            
            if ai_messages:
                summary_parts.append(f"AI响应数量: {len(ai_messages)}")
            
            return " | ".join(summary_parts)
            
        except Exception as e:
            logger.error(f"生成上下文摘要失败: {e}")
            return ""
    
    def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话统计信息 / Get session statistics
        
        Args:
            session_id: 会话ID / Session ID
            
        Returns:
            统计信息 / Statistics information
        """
        try:
            session = self.conversation_store.load_session(session_id)
            if not session:
                return {}
            
            messages = self.get_conversation_history(session_id)
            
            user_messages = [m for m in messages if m.sender == "user"]
            ai_messages = [m for m in messages if m.sender == "ai"]
            
            return {
                "total_messages": len(messages),
                "user_messages": len(user_messages),
                "ai_messages": len(ai_messages),
                "session_duration": (datetime.now() - session.created_at).total_seconds(),
                "last_activity": session.updated_at.isoformat(),
                "context_summary_length": len(session.context_summary),
                "status": session.status
            }
            
        except Exception as e:
            logger.error(f"获取会话统计失败: {session_id}, 错误: {e}")
            return {}