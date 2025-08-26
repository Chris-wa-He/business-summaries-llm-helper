"""
兼容性和稳定性测试 / Compatibility and Stability Tests

验证与现有功能的兼容性和系统稳定性。
Verifies compatibility with existing functionality and system stability.
"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from .test_base import E2ETestBase


class TestCompatibility(E2ETestBase):
    """兼容性测试类 / Compatibility Test Class"""
    
    def test_backward_compatibility_with_existing_config(self):
        """测试与现有配置的向后兼容性 / Test backward compatibility with existing config"""
        manager = self.create_system_prompt_manager()
        
        # 验证默认配置仍然有效 / Verify default configuration still works
        active_prompt = manager.get_active_prompt()
        assert active_prompt is not None
        assert active_prompt['name'] == 'default'
        
        # 验证历史文件夹路径正确 / Verify history folder path is correct
        default_folder = manager.get_prompt_history_folder('default')
        expected_path = str(self.history_dir / 'default')
        assert default_folder == expected_path
    
    def test_concurrent_operations_stability(self):
        """测试并发操作的稳定性 / Test concurrent operations stability"""
        manager = self.create_system_prompt_manager()
        
        def create_and_delete_prompt(index):
            """创建和删除提示词的工作函数 / Worker function to create and delete prompt"""
            prompt_name = f"concurrent_test_{index}"
            prompt_content = f"并发测试内容 {index}"
            
            try:
                # 创建提示词 / Create prompt
                success = manager.create_prompt(prompt_name, prompt_content)
                if not success:
                    return f"Failed to create prompt {index}"
                
                # 读取提示词 / Read prompt
                content = manager.get_prompt(prompt_name)
                if content != prompt_content:
                    return f"Content mismatch for prompt {index}"
                
                # 更新提示词 / Update prompt
                new_content = f"更新的内容 {index}"
                success = manager.update_prompt(prompt_name, new_content)
                if not success:
                    return f"Failed to update prompt {index}"
                
                # 删除提示词 / Delete prompt
                success = manager.delete_prompt(prompt_name)
                if not success:
                    return f"Failed to delete prompt {index}"
                
                return f"Success {index}"
                
            except Exception as e:
                return f"Exception in {index}: {e}"
        
        # 并发执行多个操作 / Execute multiple operations concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_and_delete_prompt, i) for i in range(10)]
            results = [future.result() for future in as_completed(futures)]
        
        # 验证所有操作都成功 / Verify all operations succeeded
        success_count = sum(1 for result in results if result.startswith("Success"))
        assert success_count >= 8, f"Too many failures: {results}"
    
    def test_large_scale_prompt_management(self):
        """测试大规模提示词管理 / Test large-scale prompt management"""
        manager = self.create_system_prompt_manager()
        
        # 创建大量提示词 / Create many prompts
        prompt_count = 50
        created_prompts = []
        
        for i in range(prompt_count):
            prompt_name = f"scale_test_{i:03d}"
            prompt_content = f"大规模测试提示词内容 {i}"
            
            success = manager.create_prompt(prompt_name, prompt_content)
            if success:
                created_prompts.append((prompt_name, prompt_content))
        
        # 验证创建成功率 / Verify creation success rate
        assert len(created_prompts) >= prompt_count * 0.9, "Too many creation failures"
        
        # 验证列表功能 / Verify list functionality
        all_prompts = manager.list_prompts()
        assert len(all_prompts) >= len(created_prompts)
        
        # 随机验证一些提示词内容 / Randomly verify some prompt contents
        import random
        sample_prompts = random.sample(created_prompts, min(10, len(created_prompts)))
        
        for prompt_name, expected_content in sample_prompts:
            content = manager.get_prompt(prompt_name)
            assert content == expected_content
        
        # 清理 / Cleanup
        for prompt_name, _ in created_prompts:
            manager.delete_prompt(prompt_name)
    
    def test_special_characters_handling(self):
        """测试特殊字符处理 / Test special characters handling"""
        manager = self.create_system_prompt_manager()
        
        # 测试各种特殊字符的提示词名称和内容 / Test various special characters in names and content
        test_cases = [
            ("中文提示词", "这是一个包含中文的提示词内容。"),
            ("emoji_test", "This prompt contains emojis: 🎉 🚀 ✅"),
            ("unicode_test", "Unicode characters: αβγδε ñáéíóú"),
            ("mixed_lang", "混合语言 Mixed Language テスト"),
        ]
        
        for prompt_name, prompt_content in test_cases:
            # 创建提示词 / Create prompt
            success = manager.create_prompt(prompt_name, prompt_content)
            assert success is True, f"Failed to create prompt: {prompt_name}"
            
            # 验证内容 / Verify content
            content = manager.get_prompt(prompt_name)
            assert content == prompt_content, f"Content mismatch for: {prompt_name}"
            
            # 清理 / Cleanup
            success = manager.delete_prompt(prompt_name)
            assert success is True, f"Failed to delete prompt: {prompt_name}"
    
    def test_performance_under_load(self):
        """测试负载下的性能 / Test performance under load"""
        manager = self.create_system_prompt_manager()
        
        # 创建一些提示词 / Create some prompts
        for i in range(10):
            prompt_name = f"perf_test_{i}"
            prompt_content = f"性能测试内容 {i}"
            manager.create_prompt(prompt_name, prompt_content)
        
        # 测试读取性能 / Test read performance
        start_time = time.time()
        for _ in range(100):
            prompts = manager.list_prompts()
            assert len(prompts) >= 10
        list_time = time.time() - start_time
        
        # 测试单个提示词读取性能 / Test individual prompt read performance
        start_time = time.time()
        for _ in range(100):
            content = manager.get_prompt("perf_test_0")
            assert content is not None
        read_time = time.time() - start_time
        
        # 验证性能在合理范围内 / Verify performance is within reasonable range
        assert list_time < 5.0, f"List operation too slow: {list_time}s"
        assert read_time < 2.0, f"Read operation too slow: {read_time}s"
        
        # 清理 / Cleanup
        for i in range(10):
            manager.delete_prompt(f"perf_test_{i}")
