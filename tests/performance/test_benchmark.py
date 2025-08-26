"""
性能基准测试 / Performance Benchmark Tests

测试系统提示词管理功能的性能指标。
Tests performance metrics for system prompt management functionality.
"""

import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock
from src.services.system_prompt_manager import SystemPromptManager


class TestPerformanceBenchmark:
    """性能基准测试类 / Performance Benchmark Test Class"""
    
    def setup_method(self):
        """设置测试环境 / Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.prompts_dir = self.temp_dir / "system_prompts"
        self.history_dir = self.temp_dir / "history_references"
        
        self.prompts_dir.mkdir(parents=True)
        self.history_dir.mkdir(parents=True)
        
        # 创建模拟对象 / Create mock objects
        self.mock_config = Mock()
        self.mock_config.get_app_config.return_value = {
            'system_prompts': {
                'prompts_folder': str(self.prompts_dir),
                'active_prompt': 'default'
            },
            'history_folder': str(self.history_dir)
        }
        
        self.mock_history = Mock()
        self.manager = SystemPromptManager(self.mock_config, self.mock_history)
    
    def teardown_method(self):
        """清理测试环境 / Cleanup test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_prompt_creation_performance(self):
        """测试提示词创建性能 / Test prompt creation performance"""
        prompt_count = 50
        start_time = time.time()
        
        for i in range(prompt_count):
            prompt_name = f"perf_test_{i:03d}"
            prompt_content = f"性能测试提示词内容 {i}"
            success = self.manager.create_prompt(prompt_name, prompt_content)
            assert success is True
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / prompt_count
        
        print(f"\n性能指标 / Performance Metrics:")
        print(f"创建 {prompt_count} 个提示词总时间: {total_time:.2f}秒")
        print(f"平均每个提示词创建时间: {avg_time:.4f}秒")
        
        # 性能要求：平均创建时间应小于0.1秒 / Performance requirement: avg creation time < 0.1s
        assert avg_time < 0.1, f"创建性能不达标: {avg_time:.4f}s > 0.1s"
    
    def test_prompt_reading_performance(self):
        """测试提示词读取性能 / Test prompt reading performance"""
        # 先创建一些提示词 / First create some prompts
        prompt_count = 20
        for i in range(prompt_count):
            prompt_name = f"read_test_{i:03d}"
            prompt_content = f"读取测试内容 {i}"
            self.manager.create_prompt(prompt_name, prompt_content)
        
        # 测试读取性能 / Test reading performance
        read_count = 100
        start_time = time.time()
        
        for i in range(read_count):
            prompt_name = f"read_test_{i % prompt_count:03d}"
            content = self.manager.get_prompt(prompt_name)
            assert content is not None
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / read_count
        
        print(f"\n读取性能指标 / Reading Performance Metrics:")
        print(f"读取 {read_count} 次总时间: {total_time:.2f}秒")
        print(f"平均每次读取时间: {avg_time:.4f}秒")
        
        # 性能要求：平均读取时间应小于0.02秒 / Performance requirement: avg read time < 0.02s
        assert avg_time < 0.02, f"读取性能不达标: {avg_time:.4f}s > 0.02s"
    
    def test_list_prompts_performance(self):
        """测试列表提示词性能 / Test list prompts performance"""
        # 创建大量提示词 / Create many prompts
        prompt_count = 100
        for i in range(prompt_count):
            prompt_name = f"list_test_{i:03d}"
            prompt_content = f"列表测试内容 {i}"
            self.manager.create_prompt(prompt_name, prompt_content)
        
        # 测试列表性能 / Test list performance
        list_count = 50
        start_time = time.time()
        
        for _ in range(list_count):
            prompts = self.manager.list_prompts()
            assert len(prompts) >= prompt_count
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / list_count
        
        print(f"\n列表性能指标 / List Performance Metrics:")
        print(f"列表操作 {list_count} 次总时间: {total_time:.2f}秒")
        print(f"平均每次列表时间: {avg_time:.4f}秒")
        
        # 性能要求：平均列表时间应小于0.05秒 / Performance requirement: avg list time < 0.05s
        assert avg_time < 0.05, f"列表性能不达标: {avg_time:.4f}s > 0.05s"
    
    def test_cache_effectiveness(self):
        """测试缓存效果 / Test cache effectiveness"""
        # 创建测试提示词 / Create test prompt
        prompt_name = "cache_test"
        prompt_content = "缓存测试内容"
        self.manager.create_prompt(prompt_name, prompt_content)
        
        # 第一次读取（无缓存）/ First read (no cache)
        start_time = time.time()
        content1 = self.manager.get_prompt(prompt_name)
        first_read_time = time.time() - start_time
        
        # 第二次读取（有缓存）/ Second read (with cache)
        start_time = time.time()
        content2 = self.manager.get_prompt(prompt_name)
        cached_read_time = time.time() - start_time
        
        assert content1 == content2
        
        print(f"\n缓存效果指标 / Cache Effectiveness Metrics:")
        print(f"首次读取时间: {first_read_time:.4f}秒")
        print(f"缓存读取时间: {cached_read_time:.4f}秒")
        print(f"性能提升: {(first_read_time / cached_read_time):.1f}x")
        
        # 缓存应该提供至少2倍的性能提升 / Cache should provide at least 2x performance improvement
        assert cached_read_time < first_read_time / 2, "缓存效果不明显"
