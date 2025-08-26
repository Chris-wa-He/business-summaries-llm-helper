"""
系统提示词工作流集成测试 / System Prompt Workflow Integration Tests

测试完整的提示词管理工作流
Test complete prompt management workflow
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from src.services.system_prompt_service import SystemPromptService
from src.services.system_prompt_manager import SystemPromptManager
from src.processors.history_processor import HistoryProcessor
from src.exceptions.system_prompt_exceptions import PromptValidationError, PromptNotFoundError


class TestPromptWorkflowIntegration:
    """提示词工作流集成测试类 / Prompt Workflow Integration Test Class"""
    
    @pytest.fixture
    def temp_dirs(self):
        """创建临时目录 / Create temporary directories"""
        temp_dir = tempfile.mkdtemp()
        dirs = {
            'base': Path(temp_dir),
            'prompts': Path(temp_dir) / 'prompts',
            'history': Path(temp_dir) / 'history'
        }
        
        # 创建目录 / Create directories
        dirs['prompts'].mkdir(parents=True)
        dirs['history'].mkdir(parents=True)
        
        yield dirs
        
        # 清理 / Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def prompt_service(self, temp_dirs):
        """创建提示词服务 / Create prompt service"""
        return SystemPromptService(str(temp_dirs['prompts']), str(temp_dirs['history']))
    
    @pytest.fixture
    def history_processor(self, temp_dirs):
        """创建历史处理器 / Create history processor"""
        return HistoryProcessor(str(temp_dirs['history']))
    
    @pytest.fixture
    def mock_config_manager(self, temp_dirs):
        """创建模拟配置管理器 / Create mock config manager"""
        config = Mock()
        config.get_app_config.return_value = {
            'system_prompts': {
                'prompts_folder': str(temp_dirs['prompts']),
                'active_prompt': 'default'
            },
            'history_folder': str(temp_dirs['history'])
        }
        return config
    
    @pytest.fixture
    def prompt_manager(self, mock_config_manager, history_processor):
        """创建提示词管理器 / Create prompt manager"""
        return SystemPromptManager(mock_config_manager, history_processor)
    
    def test_prompt_service_basic_operations(self, prompt_service):
        """测试提示词服务基本操作 / Test prompt service basic operations"""
        # 测试创建提示词 / Test create prompt
        success = prompt_service.save_prompt_file("test_prompt", "Test content")
        assert success is True
        
        # 测试读取提示词 / Test read prompt
        content = prompt_service.load_prompt_file("test_prompt")
        assert "Test content" in content
        
        # 测试列出提示词 / Test list prompts
        prompts = prompt_service.list_prompt_files()
        assert "test_prompt" in prompts
        
        # 测试删除提示词 / Test delete prompt
        success = prompt_service.delete_prompt_file("test_prompt")
        assert success is True
        
        # 验证删除后不存在 / Verify doesn't exist after deletion
        with pytest.raises(PromptNotFoundError):
            prompt_service.load_prompt_file("test_prompt")
    
    def test_prompt_service_validation(self, prompt_service):
        """测试提示词服务验证 / Test prompt service validation"""
        # 测试空名称验证 / Test empty name validation
        with pytest.raises(PromptValidationError):
            prompt_service.validate_prompt_name("")
        
        # 测试非法字符验证 / Test illegal character validation
        with pytest.raises(PromptValidationError):
            prompt_service.validate_prompt_name("test<name>")
        
        # 测试空内容验证 / Test empty content validation
        with pytest.raises(PromptValidationError):
            prompt_service.save_prompt_file("test", "")
    
    def test_prompt_service_history_folder_creation(self, prompt_service, temp_dirs):
        """测试提示词服务历史文件夹创建 / Test prompt service history folder creation"""
        # 创建提示词 / Create prompt
        success = prompt_service.save_prompt_file("with_history", "Content with history")
        assert success is True
        
        # 验证历史文件夹被创建 / Verify history folder was created
        history_folder = temp_dirs['history'] / 'with_history'
        assert history_folder.exists()
        assert history_folder.is_dir()
    
    def test_history_processor_folder_switching(self, history_processor, temp_dirs):
        """测试历史处理器文件夹切换 / Test history processor folder switching"""
        # 创建测试历史文件夹和文件 / Create test history folder and file
        test_folder = temp_dirs['history'] / 'test_prompt'
        test_folder.mkdir()
        test_file = test_folder / 'test.txt'
        test_file.write_text("Test history content")
        
        # 切换到测试文件夹 / Switch to test folder
        history_processor.set_history_folder(str(test_folder))
        
        # 验证当前文件夹 / Verify current folder
        current_folder = history_processor.get_current_history_folder()
        assert 'test_prompt' in current_folder
        
        # 验证可以加载文件 / Verify can load files
        files = history_processor.load_history_files()
        assert len(files) >= 1
        assert any('test.txt' in f['name'] for f in files)
    
    def test_prompt_manager_integration(self, prompt_manager, temp_dirs):
        """测试提示词管理器集成 / Test prompt manager integration"""
        # 创建提示词 / Create prompt
        success = prompt_manager.create_prompt("integration_test", "Integration test content")
        assert success is True
        
        # 验证提示词文件存在 / Verify prompt file exists
        prompt_file = temp_dirs['prompts'] / 'integration_test.md'
        assert prompt_file.exists()
        
        # 验证历史文件夹存在 / Verify history folder exists
        history_folder = temp_dirs['history'] / 'integration_test'
        assert history_folder.exists()
        
        # 获取提示词内容 / Get prompt content
        content = prompt_manager.get_prompt("integration_test")
        assert "Integration test content" in content
        
        # 列出提示词 / List prompts
        prompts = prompt_manager.list_prompts()
        assert len(prompts) >= 1
        assert any(p['name'] == 'integration_test' for p in prompts)
    
    def test_end_to_end_workflow(self, prompt_manager, history_processor, temp_dirs):
        """测试端到端工作流 / Test end-to-end workflow"""
        # 1. 创建提示词 / Create prompt
        success = prompt_manager.create_prompt("e2e_test", "End-to-end test prompt")
        assert success is True
        
        # 2. 在历史文件夹中添加文件 / Add file to history folder
        history_folder = temp_dirs['history'] / 'e2e_test'
        test_file = history_folder / 'example.txt'
        test_file.write_text("Example history content")
        
        # 3. 设置为激活提示词 / Set as active prompt
        success = prompt_manager.set_active_prompt("e2e_test")
        assert success is True
        
        # 4. 验证激活提示词 / Verify active prompt
        active = prompt_manager.get_active_prompt()
        assert active is not None
        assert active['name'] == 'e2e_test'
        assert "End-to-end test prompt" in active['content']
        
        # 5. 验证历史处理器切换到正确文件夹 / Verify history processor switched to correct folder
        current_folder = history_processor.get_current_history_folder()
        assert 'e2e_test' in current_folder
        
        # 6. 验证可以加载历史文件 / Verify can load history files
        files = history_processor.load_history_files()
        assert len(files) >= 1
        assert any('example.txt' in f['name'] for f in files)
        
        # 7. 更新提示词 / Update prompt
        success = prompt_manager.update_prompt("e2e_test", "Updated e2e test prompt")
        assert success is True
        
        # 8. 验证更新 / Verify update
        active = prompt_manager.get_active_prompt()
        assert "Updated e2e test prompt" in active['content']
        
        # 9. 删除提示词 / Delete prompt
        success = prompt_manager.delete_prompt("e2e_test")
        assert success is True
        
        # 10. 验证回退到默认提示词 / Verify fallback to default prompt
        active = prompt_manager.get_active_prompt()
        assert active['name'] == 'default'
    
    def test_error_scenarios(self, prompt_manager):
        """测试错误场景 / Test error scenarios"""
        # 测试创建重复提示词 / Test creating duplicate prompt
        prompt_manager.create_prompt("duplicate", "First content")
        success = prompt_manager.create_prompt("duplicate", "Second content")
        assert success is False
        
        # 测试获取不存在的提示词 / Test getting non-existent prompt
        with pytest.raises(PromptNotFoundError):
            prompt_manager.get_prompt("nonexistent")
        
        # 测试设置不存在的激活提示词 / Test setting non-existent active prompt
        success = prompt_manager.set_active_prompt("nonexistent")
        assert success is False
        
        # 测试更新不存在的提示词 / Test updating non-existent prompt
        success = prompt_manager.update_prompt("nonexistent", "New content")
        assert success is False
    
    def test_concurrent_operations(self, prompt_manager):
        """测试并发操作 / Test concurrent operations"""
        # 创建多个提示词 / Create multiple prompts
        for i in range(5):
            success = prompt_manager.create_prompt(f"concurrent_{i}", f"Content {i}")
            assert success is True
        
        # 验证所有提示词都被创建 / Verify all prompts were created
        prompts = prompt_manager.list_prompts()
        concurrent_prompts = [p for p in prompts if p['name'].startswith('concurrent_')]
        assert len(concurrent_prompts) == 5
        
        # 测试切换激活提示词 / Test switching active prompts
        for i in range(3):
            success = prompt_manager.set_active_prompt(f"concurrent_{i}")
            assert success is True
            
            active = prompt_manager.get_active_prompt()
            assert active['name'] == f"concurrent_{i}"