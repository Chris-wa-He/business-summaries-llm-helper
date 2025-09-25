"""
对话服务性能测试 / Conversation Service Performance Tests
"""

import pytest
import time
from unittest.mock import Mock, patch

from src.services.conversation_service import ConversationService
from src.models.refinement_models import ConversationMessage


class TestConversationPerformance:
    """对话服务性能测试类 / Conversation Service Performance Test Class"""
    
    @pytest.fixture
    def conversation_service(self):
        """创建对话服务实例 / Create conversation service instance"""
        with patch('src.services.conversation_service.ConversationStore') as mock_store:
            service = ConversationService()
            service.conversation_store = mock_store.return_value
            service.conversation_store.save_session.return_value = True
            return service
    
    def test_create_session_performance(self, conversation_service):
        """测试创建会话的性能 / Test create session performance"""
        start_time = time.time()
        
        # 创建多个会话
        session_ids = []
        for i in range(100):
            session_id = conversation_service.create_session(f"user_{i}", f"内容_{i}")
            session_ids.append(session_id)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 验证性能要求：100个会话创建应该在1秒内完成
        assert duration < 1.0
        assert len(session_ids) == 100
        
        # 验证平均每个会话创建时间
        avg_time_per_session = duration / 100
        assert avg_time_per_session < 0.01  # 每个会话创建时间应该小于10ms
    
    def test_relevance_calculation_performance(self, conversation_service):
        """测试相关性计算的性能 / Test relevance calculation performance"""
        # 创建大量测试数据
        long_message = "This is a very long message with many technical implementation details " * 50
        query = "technical implementation"
        
        start_time = time.time()
        
        # 计算1000次相关性
        for _ in range(1000):
            relevance = conversation_service._calculate_relevance(long_message, query)
            assert 0.0 <= relevance <= 1.0
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 验证性能要求：1000次计算应该在1秒内完成
        assert duration < 1.0
        
        # 验证平均每次计算时间
        avg_time_per_calculation = duration / 1000
        assert avg_time_per_calculation < 0.001  # 每次计算应该小于1ms
    
    def test_context_summary_performance(self, conversation_service):
        """测试上下文摘要生成的性能 / Test context summary generation performance"""
        # 创建大量消息
        messages = []
        for i in range(1000):
            message = ConversationMessage(
                id=f"msg_{i}",
                session_id="test_session",
                sender="user" if i % 2 == 0 else "ai",
                content=f"这是第{i}条消息，包含一些技术实现的详细内容",
                timestamp=time.time(),
                message_type="text",
                metadata={}
            )
            messages.append(message)
        
        start_time = time.time()
        
        # 生成摘要
        summary = conversation_service._generate_context_summary(messages)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 验证性能要求：1000条消息的摘要生成应该在0.1秒内完成
        assert duration < 0.1
        assert isinstance(summary, str)
        assert len(summary) > 0
    
    @pytest.mark.slow
    def test_large_context_handling(self, conversation_service):
        """测试大量上下文处理的性能 / Test large context handling performance"""
        with patch.object(conversation_service, 'get_conversation_history') as mock_get_history:
            # 模拟大量历史消息
            large_message_list = []
            for i in range(10000):  # 10000条消息
                message = ConversationMessage(
                    id=f"msg_{i}",
                    session_id="test_session",
                    sender="user" if i % 2 == 0 else "ai",
                    content=f"Message {i} with technical content and implementation details",
                    timestamp=time.time(),
                    message_type="text",
                    metadata={}
                )
                large_message_list.append(message)
            
            mock_get_history.return_value = large_message_list
            
            start_time = time.time()
            
            # 获取相关上下文
            context = conversation_service.get_relevant_context("test_session", "technical implementation")
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 验证性能要求：处理10000条消息应该在2秒内完成
            assert duration < 2.0
            assert isinstance(context, str)
    
    def test_concurrent_session_creation(self, conversation_service):
        """测试并发会话创建的性能 / Test concurrent session creation performance"""
        import threading
        import queue
        
        result_queue = queue.Queue()
        
        def create_sessions(start_index, count):
            """创建会话的工作函数 / Worker function to create sessions"""
            session_ids = []
            for i in range(start_index, start_index + count):
                try:
                    session_id = conversation_service.create_session(f"user_{i}", f"内容_{i}")
                    session_ids.append(session_id)
                except Exception as e:
                    session_ids.append(f"error_{e}")
            result_queue.put(session_ids)
        
        start_time = time.time()
        
        # 创建5个线程，每个创建20个会话
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_sessions, args=(i * 20, 20))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 收集结果
        all_session_ids = []
        while not result_queue.empty():
            session_ids = result_queue.get()
            all_session_ids.extend(session_ids)
        
        # 验证性能要求：并发创建100个会话应该在2秒内完成
        assert duration < 2.0
        assert len(all_session_ids) == 100
        
        # 验证没有错误
        error_count = sum(1 for sid in all_session_ids if str(sid).startswith("error_"))
        assert error_count == 0