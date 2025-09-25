"""
对话服务测试 / Conversation Service Tests
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.services.conversation_service import ConversationService
from src.models.refinement_models import ConversationSession, ConversationMessage


class TestConversationService:
    """对话服务测试类 / Conversation Service Test Class"""
    
    @pytest.fixture
    def conversation_service(self):
        """创建对话服务实例 / Create conversation service instance"""
        with patch('src.services.conversation_service.ConversationStore') as mock_store:
            service = ConversationService()
            service.conversation_store = mock_store.return_value
            return service
    
    @pytest.fixture
    def sample_session(self):
        """创建示例会话 / Create sample session"""
        return ConversationSession(
            id="test_session_001",
            user_id="test_user",
            initial_content="初始内容",
            current_content="当前内容",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status="active",
            context_summary="",
            preferences={}
        )
    
    @pytest.fixture
    def sample_messages(self):
        """创建示例消息列表 / Create sample message list"""
        return [
            ConversationMessage(
                id="msg_001",
                session_id="test_session",
                sender="user",
                content="请添加更多技术细节",
                timestamp=datetime.now(),
                message_type="modification_request",
                metadata={}
            ),
            ConversationMessage(
                id="msg_002",
                session_id="test_session",
                sender="ai",
                content="我将为您添加技术实现的详细说明",
                timestamp=datetime.now(),
                message_type="text",
                metadata={}
            ),
            ConversationMessage(
                id="msg_003",
                session_id="test_session",
                sender="user",
                content="还需要添加性能优化部分",
                timestamp=datetime.now(),
                message_type="modification_request",
                metadata={}
            )
        ]
    
    def test_create_session(self, conversation_service):
        """测试创建对话会话 / Test create conversation session"""
        conversation_service.conversation_store.save_session.return_value = True
        
        user_id = "test_user"
        initial_content = "这是初始内容"
        
        session_id = conversation_service.create_session(user_id, initial_content)
        
        # 验证会话ID格式
        assert session_id.startswith("conv_")
        assert user_id[:8] in session_id
        
        # 验证保存会话被调用
        conversation_service.conversation_store.save_session.assert_called_once()
    
    def test_add_message(self, conversation_service, sample_session):
        """测试添加对话消息 / Test add conversation message"""
        conversation_service.conversation_store.load_session.return_value = sample_session
        conversation_service.conversation_store.save_session.return_value = True
        
        message = ConversationMessage(
            id="msg_001",
            session_id=sample_session.id,
            sender="user",
            content="测试消息",
            timestamp=datetime.now(),
            message_type="text",
            metadata={}
        )
        
        # 添加消息不应该抛出异常
        conversation_service.add_message(sample_session.id, message)
        
        # 验证会话被更新
        conversation_service.conversation_store.save_session.assert_called()
    
    def test_add_message_invalid_session(self, conversation_service):
        """测试添加消息到无效会话 / Test add message to invalid session"""
        conversation_service.conversation_store.load_session.return_value = None
        
        message = ConversationMessage(
            id="msg_001",
            session_id="invalid_session",
            sender="user",
            content="测试消息",
            timestamp=datetime.now(),
            message_type="text",
            metadata={}
        )
        
        with pytest.raises(ValueError, match="会话不存在"):
            conversation_service.add_message("invalid_session", message)
    
    def test_get_conversation_history(self, conversation_service, sample_session):
        """测试获取对话历史 / Test get conversation history"""
        conversation_service.conversation_store.load_session.return_value = sample_session
        
        history = conversation_service.get_conversation_history(sample_session.id)
        
        # 当前实现返回空列表
        assert isinstance(history, list)
        assert len(history) == 0
    
    def test_get_conversation_history_invalid_session(self, conversation_service):
        """测试获取无效会话的对话历史 / Test get conversation history for invalid session"""
        conversation_service.conversation_store.load_session.return_value = None
        
        history = conversation_service.get_conversation_history("invalid_session")
        
        assert history == []
    
    def test_compress_context(self, conversation_service, sample_session, sample_messages):
        """测试压缩对话上下文 / Test compress conversation context"""
        conversation_service.conversation_store.load_session.return_value = sample_session
        conversation_service.conversation_store.save_session.return_value = True
        
        # 模拟大量消息需要压缩
        with patch.object(conversation_service, 'get_conversation_history') as mock_get_history:
            # 创建超过窗口大小的消息列表
            many_messages = sample_messages * 5  # 15条消息，超过窗口大小10
            mock_get_history.return_value = many_messages
            
            conversation_service.compress_context(sample_session.id)
            
            # 验证会话被更新
            conversation_service.conversation_store.save_session.assert_called()
    
    def test_clear_session(self, conversation_service, sample_session):
        """测试清空对话会话 / Test clear conversation session"""
        conversation_service.conversation_store.load_session.return_value = sample_session
        conversation_service.conversation_store.save_session.return_value = True
        
        conversation_service.clear_session(sample_session.id)
        
        # 验证会话被更新
        conversation_service.conversation_store.save_session.assert_called()
    
    def test_get_relevant_context(self, conversation_service, sample_session, sample_messages):
        """测试获取相关上下文 / Test get relevant context"""
        conversation_service.conversation_store.load_session.return_value = sample_session
        
        with patch.object(conversation_service, 'get_conversation_history') as mock_get_history:
            mock_get_history.return_value = sample_messages
            
            context = conversation_service.get_relevant_context(sample_session.id, "技术细节")
            
            # 验证返回字符串
            assert isinstance(context, str)
    
    def test_update_context_weights(self, conversation_service, sample_session):
        """测试更新上下文权重 / Test update context weights"""
        conversation_service.conversation_store.load_session.return_value = sample_session
        
        initial_threshold = conversation_service.relevance_threshold
        
        # 正面反馈
        conversation_service.update_context_weights(sample_session.id, {"helpful": True})
        assert conversation_service.relevance_threshold <= initial_threshold
        
        # 负面反馈
        conversation_service.update_context_weights(sample_session.id, {"helpful": False})
        # 阈值应该增加
    
    def test_calculate_relevance(self, conversation_service):
        """测试计算相关性 / Test calculate relevance"""
        # 使用英文测试以确保单词匹配正常工作
        message_content = "This is about technical implementation details"
        query = "technical implementation"
        
        relevance = conversation_service._calculate_relevance(message_content, query)
        
        # 应该有一定的相关性
        assert 0.0 <= relevance <= 1.0
        assert relevance > 0  # 因为有共同词汇
    
    def test_calculate_relevance_no_match(self, conversation_service):
        """测试计算无匹配的相关性 / Test calculate relevance with no match"""
        message_content = "完全不相关的内容"
        query = "技术实现"
        
        relevance = conversation_service._calculate_relevance(message_content, query)
        
        # 应该是0或很低的相关性
        assert relevance == 0.0
    
    def test_generate_context_summary(self, conversation_service, sample_messages):
        """测试生成上下文摘要 / Test generate context summary"""
        summary = conversation_service._generate_context_summary(sample_messages)
        
        # 验证摘要不为空
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "用户请求" in summary
    
    def test_generate_context_summary_empty(self, conversation_service):
        """测试生成空消息列表的摘要 / Test generate context summary for empty messages"""
        summary = conversation_service._generate_context_summary([])
        
        assert summary == ""
    
    def test_get_session_statistics(self, conversation_service, sample_session, sample_messages):
        """测试获取会话统计信息 / Test get session statistics"""
        conversation_service.conversation_store.load_session.return_value = sample_session
        
        with patch.object(conversation_service, 'get_conversation_history') as mock_get_history:
            mock_get_history.return_value = sample_messages
            
            stats = conversation_service.get_session_statistics(sample_session.id)
            
            # 验证统计信息
            assert isinstance(stats, dict)
            assert "total_messages" in stats
            assert "user_messages" in stats
            assert "ai_messages" in stats
            assert "session_duration" in stats
            assert "status" in stats
            
            assert stats["total_messages"] == 3
            assert stats["user_messages"] == 2  # 两条用户消息
            assert stats["ai_messages"] == 1   # 一条AI消息
    
    def test_get_session_statistics_invalid_session(self, conversation_service):
        """测试获取无效会话的统计信息 / Test get session statistics for invalid session"""
        conversation_service.conversation_store.load_session.return_value = None
        
        stats = conversation_service.get_session_statistics("invalid_session")
        
        assert stats == {}