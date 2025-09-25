"""
性能基准测试 / Performance Benchmark Tests
"""

import pytest
import time
import asyncio
import psutil
import os
from unittest.mock import Mock, patch, AsyncMock

from src.utils.input_validator import InputValidator
from src.services.error_handler import RefinementErrorHandler
from src.services.conversation_service import ConversationService
from src.services.version_service import VersionService
from src.services.async_processor import AsyncProcessor, CacheManager


class TestPerformanceBenchmarks:
    """性能基准测试 / Performance Benchmark Tests"""
    
    def test_input_validation_performance(self):
        """测试输入验证性能 / Test input validation performance"""
        validator = InputValidator()
        
        # 基准测试参数 / Benchmark parameters
        test_messages = [
            "请帮我优化这个案例总结",
            "添加更多技术细节和分析",
            "调整语言风格使其更加专业",
            "重新组织内容结构"
        ] * 25  # 100条消息
        
        start_time = time.time()
        
        for message in test_messages:
            result = validator.validate_user_message(message)
            assert result.is_valid
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 性能基准：100条消息应在1秒内完成验证
        # Performance benchmark: 100 messages should be validated within 1 second
        assert total_time < 1.0, f"验证耗时 {total_time:.3f}s，超出1秒基准"
        
        # 计算吞吐量 / Calculate throughput
        throughput = len(test_messages) / total_time
        assert throughput > 100, f"吞吐量 {throughput:.1f} msg/s 低于100 msg/s基准"
    
    def test_error_handling_performance(self):
        """测试错误处理性能 / Test error handling performance"""
        error_handler = RefinementErrorHandler()
        
        # 生成测试错误 / Generate test errors
        test_errors = [Exception(f"测试错误 {i}") for i in range(50)]
        
        start_time = time.time()
        
        for error in test_errors:
            result = error_handler.handle_error(error, {"test": True})
            assert "error_id" in result
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 性能基准：50个错误应在0.5秒内处理完成
        # Performance benchmark: 50 errors should be handled within 0.5 seconds
        assert total_time < 0.5, f"错误处理耗时 {total_time:.3f}s，超出0.5秒基准"
    
    def test_conversation_service_performance(self):
        """测试对话服务性能 / Test conversation service performance"""
        conversation_service = ConversationService()
        
        # 创建多个会话 / Create multiple sessions
        session_count = 20
        start_time = time.time()
        
        sessions = []
        for i in range(session_count):
            session_id = conversation_service.create_session(f"user_{i}", f"内容 {i}")
            sessions.append(session_id)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # 性能基准：20个会话应在0.2秒内创建完成
        # Performance benchmark: 20 sessions should be created within 0.2 seconds
        assert creation_time < 0.2, f"会话创建耗时 {creation_time:.3f}s，超出0.2秒基准"
        assert len(sessions) == session_count
    
    def test_version_service_performance(self):
        """测试版本服务性能 / Test version service performance"""
        version_service = VersionService()
        
        # 创建多个版本 / Create multiple versions
        version_count = 30
        start_time = time.time()
        
        versions = []
        for i in range(version_count):
            version_id = version_service.create_version(
                "test_session", f"内容版本 {i}", "modification"
            )
            versions.append(version_id)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # 性能基准：30个版本应在0.3秒内创建完成
        # Performance benchmark: 30 versions should be created within 0.3 seconds
        assert creation_time < 0.3, f"版本创建耗时 {creation_time:.3f}s，超出0.3秒基准"
        assert len(versions) == version_count
    
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


class TestMemoryUsage:
    """内存使用测试 / Memory Usage Tests"""
    
    def test_memory_usage_baseline(self):
        """测试内存使用基线 / Test memory usage baseline"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 创建服务实例 / Create service instances
        validator = InputValidator()
        error_handler = RefinementErrorHandler()
        conversation_service = ConversationService()
        version_service = VersionService()
        
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - initial_memory
        
        # 内存基准：基础组件内存增长应小于50MB
        # Memory benchmark: Basic components memory increase should be less than 50MB
        assert memory_increase < 50, f"内存增长 {memory_increase:.1f}MB，超出50MB基准"
    
    def test_memory_leak_detection(self):
        """测试内存泄漏检测 / Test memory leak detection"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 重复创建和销毁对象 / Repeatedly create and destroy objects
        for _ in range(10):
            validator = InputValidator()
            for i in range(100):
                result = validator.validate_user_message(f"测试消息 {i}")
                assert result.is_valid
            del validator
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        # 内存泄漏基准：重复操作后内存增长应小于10MB
        # Memory leak benchmark: Memory growth after repeated operations should be less than 10MB
        assert memory_growth < 10, f"可能存在内存泄漏，内存增长 {memory_growth:.1f}MB"


class TestConcurrencyPerformance:
    """并发性能测试 / Concurrency Performance Tests"""
    
    @pytest.mark.asyncio
    async def test_async_processor_performance(self):
        """测试异步处理器性能 / Test async processor performance"""
        processor = AsyncProcessor(max_workers=3)
        await processor.start()
        
        # 提交多个任务 / Submit multiple tasks
        task_count = 10
        start_time = time.time()
        
        tasks = []
        for i in range(task_count):
            task = processor.submit_task("refinement", {"data": f"test_{i}"})
            tasks.append(task)
        
        task_ids = await asyncio.gather(*tasks)
        
        # 等待任务完成 / Wait for tasks to complete
        await asyncio.sleep(0.5)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 性能基准：10个任务应在1秒内提交完成
        # Performance benchmark: 10 tasks should be submitted within 1 second
        assert total_time < 1.0, f"任务提交耗时 {total_time:.3f}s，超出1秒基准"
        assert len(task_ids) == task_count
        
        await processor.stop()
    
    def test_concurrent_validation(self):
        """测试并发验证性能 / Test concurrent validation performance"""
        import threading
        
        validator = InputValidator()
        results = []
        
        def validate_messages():
            for i in range(50):
                result = validator.validate_user_message(f"并发测试消息 {i}")
                results.append(result.is_valid)
        
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
        
        # 性能基准：4个线程并发验证200条消息应在2秒内完成
        # Performance benchmark: 4 threads validating 200 messages concurrently should complete within 2 seconds
        assert total_time < 2.0, f"并发验证耗时 {total_time:.3f}s，超出2秒基准"
        assert len(results) == thread_count * 50
        assert all(results), "所有验证都应该成功"


class TestScalabilityBenchmarks:
    """可扩展性基准测试 / Scalability Benchmark Tests"""
    
    def test_large_input_handling(self):
        """测试大输入处理 / Test large input handling"""
        validator = InputValidator()
        
        # 测试不同大小的输入 / Test different input sizes
        input_sizes = [100, 500, 1000, 2000]  # 字符数
        
        for size in input_sizes:
            large_input = "测试内容 " * (size // 4)  # 约为指定字符数
            
            start_time = time.time()
            result = validator.validate_user_message(large_input, max_length=size + 100)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # 性能基准：处理时间应与输入大小呈线性关系
            # Performance benchmark: Processing time should be linear with input size
            expected_max_time = size / 10000  # 每10000字符1秒
            assert processing_time < expected_max_time, f"大小 {size} 处理耗时 {processing_time:.3f}s，超出预期"
            assert result.is_valid
    
    def test_session_scalability(self):
        """测试会话可扩展性 / Test session scalability"""
        conversation_service = ConversationService()
        
        # 测试不同数量的会话 / Test different numbers of sessions
        session_counts = [10, 50, 100]
        
        for count in session_counts:
            start_time = time.time()
            
            sessions = []
            for i in range(count):
                session_id = conversation_service.create_session(f"user_{i}", f"内容 {i}")
                sessions.append(session_id)
            
            end_time = time.time()
            creation_time = end_time - start_time
            
            # 性能基准：创建时间应与会话数量呈线性关系
            # Performance benchmark: Creation time should be linear with session count
            expected_max_time = count / 1000  # 每1000个会话1秒
            assert creation_time < expected_max_time, f"创建 {count} 个会话耗时 {creation_time:.3f}s，超出预期"
            assert len(sessions) == count


@pytest.mark.slow
class TestLoadTesting:
    """负载测试 / Load Testing"""
    
    def test_sustained_load(self):
        """测试持续负载 / Test sustained load"""
        validator = InputValidator()
        error_handler = RefinementErrorHandler()
        
        # 持续负载测试 / Sustained load test
        duration = 5  # 秒
        start_time = time.time()
        operations = 0
        
        while time.time() - start_time < duration:
            # 验证操作 / Validation operation
            result = validator.validate_user_message("持续负载测试消息")
            assert result.is_valid
            
            # 错误处理操作 / Error handling operation
            test_error = Exception("负载测试错误")
            error_result = error_handler.handle_error(test_error, {"load_test": True})
            assert "error_id" in error_result
            
            operations += 2
        
        actual_duration = time.time() - start_time
        ops_per_second = operations / actual_duration
        
        # 性能基准：每秒应处理至少100个操作
        # Performance benchmark: Should handle at least 100 operations per second
        assert ops_per_second >= 100, f"每秒操作数 {ops_per_second:.1f}，低于100基准"
    
    def test_peak_load_handling(self):
        """测试峰值负载处理 / Test peak load handling"""
        conversation_service = ConversationService()
        
        # 峰值负载：快速创建大量会话
        # Peak load: Rapidly create many sessions
        peak_sessions = 200
        start_time = time.time()
        
        sessions = []
        for i in range(peak_sessions):
            try:
                session_id = conversation_service.create_session(f"peak_user_{i}", f"峰值内容 {i}")
                sessions.append(session_id)
            except Exception as e:
                # 记录但不失败测试 / Log but don't fail test
                print(f"峰值负载下创建会话失败: {e}")
        
        end_time = time.time()
        peak_time = end_time - start_time
        
        # 性能基准：峰值负载下至少应成功创建80%的会话
        # Performance benchmark: Should successfully create at least 80% of sessions under peak load
        success_rate = len(sessions) / peak_sessions
        assert success_rate >= 0.8, f"峰值负载成功率 {success_rate:.1%}，低于80%基准"
        assert peak_time < 5.0, f"峰值负载处理耗时 {peak_time:.3f}s，超出5秒基准"


class TestPerformanceRegression:
    """性能回归测试 / Performance Regression Tests"""
    
    def test_baseline_performance_metrics(self):
        """测试基线性能指标 / Test baseline performance metrics"""
        # 建立性能基线 / Establish performance baseline
        metrics = {}
        
        # 输入验证基线 / Input validation baseline
        validator = InputValidator()
        start_time = time.time()
        for i in range(100):
            validator.validate_user_message(f"基线测试消息 {i}")
        metrics['validation_time'] = time.time() - start_time
        
        # 错误处理基线 / Error handling baseline
        error_handler = RefinementErrorHandler()
        start_time = time.time()
        for i in range(50):
            error_handler.handle_error(Exception(f"基线错误 {i}"), {"baseline": True})
        metrics['error_handling_time'] = time.time() - start_time
        
        # 会话创建基线 / Session creation baseline
        conversation_service = ConversationService()
        start_time = time.time()
        for i in range(20):
            conversation_service.create_session(f"baseline_user_{i}", f"基线内容 {i}")
        metrics['session_creation_time'] = time.time() - start_time
        
        # 验证基线指标 / Verify baseline metrics
        assert metrics['validation_time'] < 1.0, "输入验证基线超出预期"
        assert metrics['error_handling_time'] < 0.5, "错误处理基线超出预期"
        assert metrics['session_creation_time'] < 0.2, "会话创建基线超出预期"
        
        # 记录基线用于回归测试 / Record baseline for regression testing
        print(f"性能基线指标: {metrics}")
        
        return metrics