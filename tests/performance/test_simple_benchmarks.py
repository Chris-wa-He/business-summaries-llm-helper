"""
简化性能基准测试 / Simplified Performance Benchmark Tests
"""

import pytest
import time
import asyncio
from unittest.mock import Mock

from src.utils.input_validator import InputValidator
from src.services.error_handler import RefinementErrorHandler
from src.services.conversation_service import ConversationService
from src.services.version_service import VersionService
from src.services.async_processor import AsyncProcessor, CacheManager


class TestBasicPerformance:
    """基础性能测试 / Basic Performance Tests"""
    
    def test_input_validation_performance(self):
        """测试输入验证性能 / Test input validation performance"""
        validator = InputValidator()
        
        # 性能测试 / Performance test
        test_count = 100
        start_time = time.time()
        
        for i in range(test_count):
            result = validator.validate_user_message(f"测试消息 {i}")
            assert result.is_valid
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / test_count
        
        # 性能基准：平均每次验证应在10ms内完成
        # Performance benchmark: Average validation should complete within 10ms
        assert avg_time < 0.01, f"平均验证时间 {avg_time:.4f}s 超出10ms基准"
        assert total_time < 1.0, f"总验证时间 {total_time:.3f}s 超出1秒基准"
    
    def test_error_handling_performance(self):
        """测试错误处理性能 / Test error handling performance"""
        error_handler = RefinementErrorHandler()
        
        # 性能测试 / Performance test
        test_count = 50
        start_time = time.time()
        
        for i in range(test_count):
            test_error = Exception(f"测试错误 {i}")
            result = error_handler.handle_error(test_error, {"test": i})
            assert "error_id" in result
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / test_count
        
        # 性能基准：平均每次错误处理应在5ms内完成
        # Performance benchmark: Average error handling should complete within 5ms
        assert avg_time < 0.005, f"平均错误处理时间 {avg_time:.4f}s 超出5ms基准"
        assert total_time < 0.5, f"总错误处理时间 {total_time:.3f}s 超出0.5秒基准"
    
    def test_conversation_service_performance(self):
        """测试对话服务性能 / Test conversation service performance"""
        conversation_service = ConversationService()
        
        # 性能测试 / Performance test
        session_count = 20
        start_time = time.time()
        
        sessions = []
        for i in range(session_count):
            session_id = conversation_service.create_session(f"user_{i}", f"内容 {i}")
            sessions.append(session_id)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / session_count
        
        # 性能基准：平均每次会话创建应在5ms内完成
        # Performance benchmark: Average session creation should complete within 5ms
        assert avg_time < 0.005, f"平均会话创建时间 {avg_time:.4f}s 超出5ms基准"
        assert len(sessions) == session_count
    
    def test_cache_performance(self):
        """测试缓存性能 / Test cache performance"""
        cache = CacheManager()
        
        # 缓存写入性能测试 / Cache write performance test
        write_count = 1000
        start_time = time.time()
        
        for i in range(write_count):
            cache.set(f"key_{i}", f"value_{i}")
        
        write_time = time.time() - start_time
        
        # 缓存读取性能测试 / Cache read performance test
        start_time = time.time()
        
        for i in range(write_count):
            value = cache.get(f"key_{i}")
            assert value == f"value_{i}"
        
        read_time = time.time() - start_time
        
        # 性能基准 / Performance benchmarks
        assert write_time < 0.1, f"缓存写入耗时 {write_time:.3f}s，超出0.1秒基准"
        assert read_time < 0.05, f"缓存读取耗时 {read_time:.3f}s，超出0.05秒基准"


class TestScalabilityBenchmarks:
    """可扩展性基准测试 / Scalability Benchmark Tests"""
    
    def test_input_size_scalability(self):
        """测试输入大小可扩展性 / Test input size scalability"""
        validator = InputValidator()
        
        # 测试不同大小的输入 / Test different input sizes
        input_sizes = [10, 50, 100, 200]
        
        for size in input_sizes:
            test_input = "测试 " * size  # 创建指定大小的输入
            
            start_time = time.time()
            result = validator.validate_user_message(test_input, max_length=size * 10)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # 性能基准：处理时间应保持在合理范围内
            # Performance benchmark: Processing time should remain within reasonable range
            assert processing_time < 0.1, f"大小 {size} 处理耗时 {processing_time:.4f}s，超出0.1秒基准"
    
    def test_concurrent_operations(self):
        """测试并发操作 / Test concurrent operations"""
        import threading
        
        validator = InputValidator()
        results = []
        errors = []
        
        def validate_messages():
            try:
                for i in range(25):  # 每个线程处理25条消息
                    result = validator.validate_user_message(f"并发测试消息 {i}")
                    results.append(result.is_valid)
            except Exception as e:
                errors.append(str(e))
        
        # 创建多个线程 / Create multiple threads
        threads = []
        thread_count = 4
        
        start_time = time.time()
        
        for _ in range(thread_count):
            thread = threading.Thread(target=validate_messages)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成 / Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 性能基准：并发操作应在合理时间内完成
        # Performance benchmark: Concurrent operations should complete within reasonable time
        assert total_time < 2.0, f"并发操作耗时 {total_time:.3f}s，超出2秒基准"
        assert len(results) == thread_count * 25
        assert len(errors) == 0, f"并发操作出现错误: {errors}"


class TestPerformanceOptimization:
    """性能优化测试 / Performance Optimization Tests"""
    
    def test_performance_baseline(self):
        """测试性能基线 / Test performance baseline"""
        # 建立性能基线 / Establish performance baseline
        baseline_metrics = {}
        
        # 输入验证基线 / Input validation baseline
        validator = InputValidator()
        start_time = time.time()
        for i in range(100):
            validator.validate_user_message(f"基线测试 {i}")
        baseline_metrics['validation'] = time.time() - start_time
        
        # 错误处理基线 / Error handling baseline
        error_handler = RefinementErrorHandler()
        start_time = time.time()
        for i in range(50):
            error_handler.handle_error(Exception(f"基线错误 {i}"), {"baseline": True})
        baseline_metrics['error_handling'] = time.time() - start_time
        
        # 会话创建基线 / Session creation baseline
        conversation_service = ConversationService()
        start_time = time.time()
        for i in range(20):
            conversation_service.create_session(f"baseline_user_{i}", f"基线内容 {i}")
        baseline_metrics['session_creation'] = time.time() - start_time
        
        # 验证基线指标 / Verify baseline metrics
        assert baseline_metrics['validation'] < 1.0, "输入验证基线超出预期"
        assert baseline_metrics['error_handling'] < 0.5, "错误处理基线超出预期"
        assert baseline_metrics['session_creation'] < 0.2, "会话创建基线超出预期"
        
        return baseline_metrics
    
    def test_optimization_effectiveness(self):
        """测试优化效果 / Test optimization effectiveness"""
        # 测试缓存优化效果 / Test cache optimization effectiveness
        cache = CacheManager()
        
        # 无缓存性能 / Performance without cache
        start_time = time.time()
        for i in range(100):
            # 模拟复杂计算 / Mock complex computation
            result = f"computed_value_{i}"
        no_cache_time = time.time() - start_time
        
        # 有缓存性能 / Performance with cache
        start_time = time.time()
        for i in range(100):
            cached_value = cache.get(f"key_{i}")
            if cached_value is None:
                result = f"computed_value_{i}"
                cache.set(f"key_{i}", result)
            else:
                result = cached_value
        
        # 第二次访问（应该命中缓存）/ Second access (should hit cache)
        start_time = time.time()
        for i in range(100):
            cached_value = cache.get(f"key_{i}")
            assert cached_value is not None
        cache_time = time.time() - start_time
        
        # 验证缓存优化效果 / Verify cache optimization effectiveness
        assert cache_time < no_cache_time, "缓存应该提高性能"
        assert cache_time < 0.01, f"缓存访问时间 {cache_time:.4f}s 应该很快"


@pytest.mark.asyncio
class TestAsyncPerformance:
    """异步性能测试 / Async Performance Tests"""
    
    async def test_async_processor_performance(self):
        """测试异步处理器性能 / Test async processor performance"""
        processor = AsyncProcessor(max_workers=3)
        await processor.start()
        
        # 提交任务性能测试 / Task submission performance test
        task_count = 10
        start_time = time.time()
        
        tasks = []
        for i in range(task_count):
            task = processor.submit_task("refinement", {"data": f"test_{i}"})
            tasks.append(task)
        
        task_ids = await asyncio.gather(*tasks)
        submission_time = time.time() - start_time
        
        # 性能基准：任务提交应该很快
        # Performance benchmark: Task submission should be fast
        assert submission_time < 0.5, f"任务提交耗时 {submission_time:.3f}s，超出0.5秒基准"
        assert len(task_ids) == task_count
        
        await processor.stop()
    
    async def test_concurrent_async_operations(self):
        """测试并发异步操作 / Test concurrent async operations"""
        # 模拟并发异步操作 / Mock concurrent async operations
        async def async_operation(delay: float):
            await asyncio.sleep(delay)
            return f"completed_after_{delay}"
        
        # 并发执行多个异步操作 / Execute multiple async operations concurrently
        operations = [async_operation(0.01) for _ in range(10)]
        
        start_time = time.time()
        results = await asyncio.gather(*operations)
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # 性能基准：并发执行应该比串行执行快
        # Performance benchmark: Concurrent execution should be faster than serial
        assert total_time < 0.1, f"并发异步操作耗时 {total_time:.3f}s，应该接近单个操作时间"
        assert len(results) == 10


class TestPerformanceReport:
    """性能报告测试 / Performance Report Tests"""
    
    def test_generate_performance_summary(self):
        """测试生成性能摘要 / Test generate performance summary"""
        # 收集性能数据 / Collect performance data
        performance_data = {}
        
        # 测试输入验证性能 / Test input validation performance
        validator = InputValidator()
        start_time = time.time()
        for i in range(100):
            validator.validate_user_message(f"性能测试 {i}")
        performance_data['input_validation'] = {
            'total_time': time.time() - start_time,
            'operations': 100,
            'avg_time': (time.time() - start_time) / 100
        }
        
        # 测试错误处理性能 / Test error handling performance
        error_handler = RefinementErrorHandler()
        start_time = time.time()
        for i in range(50):
            error_handler.handle_error(Exception(f"性能测试错误 {i}"), {"perf_test": True})
        performance_data['error_handling'] = {
            'total_time': time.time() - start_time,
            'operations': 50,
            'avg_time': (time.time() - start_time) / 50
        }
        
        # 生成性能摘要 / Generate performance summary
        summary = {
            'total_components_tested': len(performance_data),
            'overall_performance': 'Good' if all(
                data['avg_time'] < 0.01 for data in performance_data.values()
            ) else 'Needs Improvement',
            'details': performance_data
        }
        
        # 验证摘要 / Verify summary
        assert summary['total_components_tested'] == 2
        assert 'input_validation' in summary['details']
        assert 'error_handling' in summary['details']
        
        return summary