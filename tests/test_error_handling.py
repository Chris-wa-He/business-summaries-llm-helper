"""
错误处理测试 / Error Handling Tests
"""

import pytest
from unittest.mock import Mock
from src.services.error_handler import RefinementErrorHandler, ErrorCategory, ErrorSeverity


class TestErrorHandler:
    """错误处理器测试 / Error Handler Tests"""
    
    @pytest.fixture
    def error_handler(self):
        return RefinementErrorHandler()
    
    def test_error_analysis(self, error_handler):
        """测试错误分析 / Test error analysis"""
        test_error = Exception("conversation session timeout")
        context = {"user_id": "test_user", "session_id": "test_session"}
        
        error_context = error_handler._analyze_error(test_error, context)
        
        assert error_context.category == ErrorCategory.CONVERSATION
        assert error_context.user_id == "test_user"
        assert "timeout" in error_context.message
    
    def test_error_handling_workflow(self, error_handler):
        """测试错误处理流程 / Test error handling workflow"""
        test_error = Exception("test error")
        context = {"user_id": "test_user"}
        
        result = error_handler.handle_error(test_error, context)
        
        assert "error_id" in result
        assert "message" in result
        assert "user_message" in result
        assert isinstance(result["success"], bool)
    
    def test_error_statistics(self, error_handler):
        """测试错误统计 / Test error statistics"""
        # 初始状态
        stats = error_handler.get_error_statistics()
        assert stats["total_errors"] == 0
        
        # 处理错误
        test_error = Exception("test error")
        error_handler.handle_error(test_error, {"test": True})
        
        # 检查统计
        stats = error_handler.get_error_statistics()
        assert stats["total_errors"] == 1


class TestAsyncProcessor:
    """异步处理器基础测试 / Basic Async Processor Tests"""
    
    def test_cache_manager(self):
        """测试缓存管理器 / Test cache manager"""
        from src.services.async_processor import CacheManager
        
        cache = CacheManager(default_ttl=1)
        
        # 设置和获取
        cache.set("test_key", "test_value")
        value = cache.get("test_key")
        assert value == "test_value"
        
        # 删除
        cache.delete("test_key")
        value = cache.get("test_key")
        assert value is None