"""
个性化Prompt管理器单元测试 / Personalized Prompt Manager Unit Tests
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open
from datetime import datetime

from src.services.personalized_prompt_manager import PersonalizedPromptManager, PersonalizedPromptInfo


class TestPersonalizedPromptManager:
    """个性化Prompt管理器测试类 / Personalized Prompt Manager Test Class"""
    
    def setup_method(self):
        """测试前设置 / Setup before each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = PersonalizedPromptManager(self.temp_dir)
        
    def teardown_method(self):
        """测试后清理 / Cleanup after each test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_creates_base_directory(self):
        """测试初始化创建基础目录 / Test initialization creates base directory"""
        assert self.manager.base_path.exists()
        assert self.manager.base_path.is_dir()
    
    def test_create_personalized_prompt_file_success(self):
        """测试成功创建个性化prompt文件 / Test successful creation of personalized prompt file"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        preference_analysis = {
            'analysis': 'User prefers detailed explanations',
            'personalized_prompt': 'Please provide detailed and comprehensive responses.'
        }
        
        result = self.manager.create_personalized_prompt_file(
            user_id, prompt_name, preference_analysis
        )
        
        assert isinstance(result, PersonalizedPromptInfo)
        assert result.user_id == user_id
        assert result.prompt_name == prompt_name
        assert Path(result.file_path).exists()
        assert preference_analysis['personalized_prompt'] in result.content
    
    def test_create_personalized_prompt_file_creates_user_directory(self):
        """测试创建prompt文件时自动创建用户目录 / Test automatic user directory creation"""
        user_id = "new_user"
        prompt_name = "test_prompt"
        preference_analysis = {'analysis': 'test', 'personalized_prompt': 'test prompt'}
        
        user_dir = self.manager.base_path / user_id
        assert not user_dir.exists()
        
        self.manager.create_personalized_prompt_file(user_id, prompt_name, preference_analysis)
        
        assert user_dir.exists()
        assert user_dir.is_dir()
    
    def test_load_personalized_prompt_success(self):
        """测试成功加载个性化prompt / Test successful loading of personalized prompt"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        preference_analysis = {
            'analysis': 'User analysis',
            'personalized_prompt': 'Custom prompt content'
        }
        
        # 创建prompt文件
        self.manager.create_personalized_prompt_file(user_id, prompt_name, preference_analysis)
        
        # 加载prompt
        loaded_prompt = self.manager.load_personalized_prompt(user_id, prompt_name)
        
        assert loaded_prompt is not None
        assert 'Custom prompt content' in loaded_prompt
    
    def test_load_personalized_prompt_not_found(self):
        """测试加载不存在的prompt / Test loading non-existent prompt"""
        result = self.manager.load_personalized_prompt("nonexistent_user", "nonexistent_prompt")
        assert result is None
    
    def test_get_prompt_versions_empty(self):
        """测试获取空的版本列表 / Test getting empty version list"""
        versions = self.manager.get_prompt_versions("nonexistent_user", "test_prompt")
        assert versions == []
    
    def test_get_prompt_versions_with_files(self):
        """测试获取包含文件的版本列表 / Test getting version list with files"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        preference_analysis = {'analysis': 'test', 'personalized_prompt': 'test'}
        
        # 创建多个版本
        self.manager.create_personalized_prompt_file(user_id, prompt_name, preference_analysis)
        import time
        time.sleep(0.01)  # 小延迟确保文件名不同
        self.manager.create_personalized_prompt_file(user_id, prompt_name, preference_analysis)
        
        versions = self.manager.get_prompt_versions(user_id, prompt_name)
        
        assert len(versions) == 2
        assert all('version' in v for v in versions)
        assert all('file_path' in v for v in versions)
    
    def test_activate_prompt_version_success(self):
        """测试成功激活prompt版本 / Test successful prompt version activation"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        preference_analysis = {'analysis': 'test', 'personalized_prompt': 'test'}
        
        # 创建prompt文件
        prompt_info = self.manager.create_personalized_prompt_file(
            user_id, prompt_name, preference_analysis
        )
        
        # 激活版本
        result = self.manager.activate_prompt_version(user_id, prompt_name, prompt_info.version)
        
        assert result is True
        assert self.manager._get_active_prompt_file(user_id, prompt_name) == prompt_info.file_path
    
    def test_activate_prompt_version_not_found(self):
        """测试激活不存在的prompt版本 / Test activating non-existent prompt version"""
        result = self.manager.activate_prompt_version("test_user", "test_prompt", "nonexistent_version")
        assert result is False
    
    def test_delete_prompt_version_success(self):
        """测试成功删除prompt版本 / Test successful prompt version deletion"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        preference_analysis = {'analysis': 'test', 'personalized_prompt': 'test'}
        
        # 创建prompt文件
        prompt_info = self.manager.create_personalized_prompt_file(
            user_id, prompt_name, preference_analysis
        )
        
        # 确认文件存在
        assert Path(prompt_info.file_path).exists()
        
        # 删除版本
        result = self.manager.delete_prompt_version(user_id, prompt_name, prompt_info.version)
        
        assert result is True
        assert not Path(prompt_info.file_path).exists()
    
    def test_delete_prompt_version_not_found(self):
        """测试删除不存在的prompt版本 / Test deleting non-existent prompt version"""
        result = self.manager.delete_prompt_version("test_user", "test_prompt", "nonexistent_version")
        assert result is False
    
    def test_extract_prompt_content(self):
        """测试提取prompt内容 / Test extracting prompt content"""
        file_content = """# 个性化系统提示词 / Personalized System Prompt

## 基本信息 / Basic Information
- **用户ID**: test_user

## 个性化提示词 / Personalized Prompt
This is the personalized prompt content.
It spans multiple lines.

## 使用说明 / Usage Instructions
Some usage instructions here.
"""
        
        extracted = self.manager._extract_prompt_content(file_content)
        
        assert "This is the personalized prompt content." in extracted
        assert "It spans multiple lines." in extracted
        assert "使用说明" not in extracted
    
    def test_parse_prompt_file_info_success(self):
        """测试成功解析prompt文件信息 / Test successful parsing of prompt file info"""
        # 创建测试文件 - 使用正确的格式
        user_dir = self.manager.base_path / "test_user"
        user_dir.mkdir(exist_ok=True)
        test_file = user_dir / "test_user__test_prompt__v20240101_120000_123.md"
        test_file.write_text("test content")
        
        info = self.manager._parse_prompt_file_info(test_file)
        
        assert info is not None
        assert info['user_id'] == 'test_user'
        assert info['prompt_name'] == 'test_prompt'
        assert info['version'] == '20240101_120000_123'
        assert info['file_name'] == test_file.name
    
    def test_parse_prompt_file_info_invalid_format(self):
        """测试解析无效格式的文件信息 / Test parsing invalid format file info"""
        user_dir = self.manager.base_path / "test_user"
        user_dir.mkdir(exist_ok=True)
        test_file = user_dir / "invalid_filename.md"
        test_file.write_text("test content")
        
        info = self.manager._parse_prompt_file_info(test_file)
        
        assert info is None
    
    def test_update_active_prompt(self):
        """测试更新激活的prompt / Test updating active prompt"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        file_path = "/path/to/file.md"
        
        self.manager._update_active_prompt(user_id, prompt_name, file_path)
        
        assert self.manager.active_prompts[user_id][prompt_name] == file_path
    
    def test_get_active_prompt_file(self):
        """测试获取激活的prompt文件 / Test getting active prompt file"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        file_path = "/path/to/file.md"
        
        # 设置激活的prompt
        self.manager._update_active_prompt(user_id, prompt_name, file_path)
        
        # 获取激活的prompt文件
        active_file = self.manager._get_active_prompt_file(user_id, prompt_name)
        
        assert active_file == file_path
    
    def test_get_active_prompt_file_not_found(self):
        """测试获取不存在的激活prompt文件 / Test getting non-existent active prompt file"""
        active_file = self.manager._get_active_prompt_file("nonexistent_user", "nonexistent_prompt")
        assert active_file is None