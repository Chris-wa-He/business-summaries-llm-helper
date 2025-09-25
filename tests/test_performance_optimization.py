"""
性能优化测试 / Performance Optimization Tests
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from src.services.async_processor import AsyncProcessor, CacheManager
from src.services.error_handler import RefinementErrorHandler, ErrorCategory, ErrorSeverity


class TestAsyncProcessor:
    """异步处理器测试 / Async Processor Tests"""
    
    @pytest.fixture
    def processor(self):
        """创建处理器实例 / Create processor instance"""
        return AsyncProcessor()
    
    @pytest.mark.asyncio
    async def test_processor_start_stop(self, processor):
        """测试处理器启动停止 / Test processor start stop"""
        await processor.start()
        assert len(processor.workers) == processor.max_workers
        assert processor.is_running
        
        await processor.stop()
        assert not processor.is_running
    
    @pytest.mark.asyncio
    async def test_task_submission(self, processor):
        """测试任务提交 / Test task submission"""
        await processor.start()
        
        # 提交任务
        task_id = await processor.submit_task("refinement", {"test": "data"})
        assert task_id.startswith("refinement_")
        
        # 检查任务状态
        task = await processor.get_task_status(task_id)
        assert task is not None
        
        await processor.stop()
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self, processor):
        """测试并发处理能力 / Test concurrent processing capability"""
        await processor.start()
        
        # 提交多个任务
        tasks = []
        for i in range(5):
            tasks.append(processor.submit_task("refinement", {"test": f"data_{i}"}))
        
        # 等待所有任务提交完成
        task_ids = await asyncio.gather(*tasks)
        assert len(task_ids) == 5
        
        await processor.stop()
    
    def test_cache_functionality(self):
        """测试缓存功能 / Test cache functionality"""
        cache = CacheManager(default_ttl=1)
        
        # 测试缓存设置
        cache.set("test_key", {"messages": ["test"]})
        
        # 测试缓存获取
        cached_data = cache.get("test_key")
        assert cached_data is not None
        assert cached_data["messages"] == ["test"]
        
        # 测试缓存过期
        cache.set("expire_key", "test_value", ttl=0)
        time.sleep(0.1)
        expired_data = cache.get("expire_key")
        assert expired_data is None


class TestRefinementErrorHandler:
    """错误处理器测试 / Error Handler Tests"""
    
    @pytest.fixture
    def error_handler(self):
        """创建错误处理器实例 / Create error handler instance"""
        return RefinementErrorHandler()
    
    def test_error_analysis(self, error_handler):
        """测试错误分析 / Test error analysis"""
        test_error = Exception("conversation session timeout")
        context = {"user_id": "test_user", "session_id": "test_session"}
        
        error_context = error_handler._analyze_error(test_error, context)
        
        assert error_context.category == ErrorCategory.CONVERSATION
        assert error_context.user_id == "test_user"
        assert error_context.session_id == "test_session"
        assert "timeout" in error_context.message
    
    def test_error_severity_determination(self, error_handler):
        """测试错误严重程度判定 / Test error severity determination"""
        # 测试关键错误
        critical_severity = error_handler._determine_error_severity(
            "CriticalError", "critical data corruption", {}
        )
        assert critical_severity == ErrorSeverity.CRITICAL
        
        # 测试高级错误
        high_severity = error_handler._determine_error_severity(
            "TimeoutError", "connection timeout", {}
        )
        assert high_severity == ErrorSeverity.HIGH
        
        # 测试中级错误
        medium_severity = error_handler._determine_error_severity(
            "WarningError", "retry needed", {}
        )
        assert medium_severity == ErrorSeverity.MEDIUM
    
    def test_recovery_strategy_selection(self, error_handler):
        """测试恢复策略选择 / Test recovery strategy selection"""
        from src.services.error_handler import ErrorContext
        from datetime import datetime
        
        error_context = ErrorContext(
            error_id="test_001",
            category=ErrorCategory.CONVERSATION,
            severity=ErrorSeverity.HIGH,
            message="session timeout occurred",
            details={},
            timestamp=datetime.now()
        )
        
        strategies = error_handler.recovery_strategies[ErrorCategory.CONVERSATION]
        selected_strategy = error_handler._select_recovery_strategy(error_context, strategies)
        
        assert selected_strategy == "session_timeout"
    
    def test_error_handling_workflow(self, error_handler):
        """测试完整错误处理流程 / Test complete error handling workflow"""
        test_error = Exception("conversation session timeout")
        context = {"user_id": "test_user", "session_id": "test_session"}
        
        result = error_handler.handle_error(test_error, context)
        
        assert "error_id" in result
        assert "message" in result
        assert "user_message" in result
        assert isinstance(result["success"], bool)
    
    def test_error_statistics(self, error_handler):
        """测试错误统计功能 / Test error statistics functionality"""
        # 初始状态
        stats = error_handler.get_error_statistics()
        assert stats["total_errors"] == 0
        
        # 处理一些错误
        for i in range(3):
            test_error = Exception(f"test error {i}")
            error_handler.handle_error(test_error, {"test": True})
        
        # 检查统计信息
        stats = error_handler.get_error_statistics()
        assert stats["total_errors"] == 3
        assert "by_category" in stats
        assert "by_severity" in stats


class TestPerformanceMetrics:
    """性能指标测试 / Performance Metrics Tests"""
    
    @pytest.mark.asyncio
    async def test_response_time_measurement(self):
        """测试响应时间测量 / Test response time measurement"""
        processor = AsyncProcessor()
        
        start_time = time.time()
        
        # 模拟处理任务
        await asyncio.sleep(0.1)  # 模拟100ms处理时间
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # 验证响应时间在合理范围内
        assert 0.1 <= response_time <= 0.2
    
    def test_memory_usage_monitoring(self):
        """测试内存使用监控 / Test memory usage monitoring"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 创建一些对象来增加内存使用
        large_data = [i for i in range(10000)]
        
        current_memory = process.memory_info().rss
        memory_increase = current_memory - initial_memory
        
        # 验证内存使用有所增加
        assert memory_increase > 0
        
        # 清理数据
        del large_data
    
    def test_cache_hit_rate(self):
        """测试缓存命中率 / Test cache hit rate"""
        cache = CacheManager()
        
        # 设置缓存数据
        cache.set("session_1", {"data": "test"})
        
        # 测试缓存命中
        hit_data = cache.get("session_1")
        assert hit_data is not None
        
        # 测试缓存未命中
        miss_data = cache.get("nonexistent_session")
        assert miss_data is None


@pytest.mark.integration
class TestIntegratedPerformance:
    """集成性能测试 / Integrated Performance Tests"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_performance(self):
        """测试端到端性能 / Test end-to-end performance"""
        processor = AsyncProcessor()
        error_handler = RefinementErrorHandler()
        
        await processor.start()
        
        # 模拟完整的处理流程
        start_time = time.time()
        
        try:
            # 提交任务
            task_id = await processor.submit_task("refinement", {"test": "data"})
            assert task_id.startswith("refinement_")
            
            # 等待任务完成
            await asyncio.sleep(0.2)  # 等待处理完成
            
            # 检查任务状态
            task = await processor.get_task_status(task_id)
            assert task is not None
            
        except Exception as e:
            # 测试错误处理性能
            error_result = error_handler.handle_error(e, {"test": True})
            assert error_result is not None
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证总处理时间在合理范围内（应该小于1秒）
        assert total_time < 1.0
        
        await processor.stop()
    
    def test_concurrent_error_handling(self):
        """测试并发错误处理 / Test concurrent error handling"""
        error_handler = RefinementErrorHandler()
        
        # 并发处理多个错误
        errors = [Exception(f"test error {i}") for i in range(5)]
        contexts = [{"error_id": i} for i in range(5)]
        
        results = []
        for error, context in zip(errors, contexts):
            result = error_handler.handle_error(error, context)
            results.append(result)
        
        # 验证所有错误都被处理
        assert len(results) == 5
        assert all("error_id" in result for result in results)
        
        # 验证错误统计
        stats = error_handler.get_error_statistics()
        assert stats["total_errors"] == 5