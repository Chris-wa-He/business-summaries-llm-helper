"""
系统提示词服务单元测试 / System Prompt Service Unit Tests
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.services.system_prompt_service import SystemPromptService


class TestSystemPromptService:
    """系统提示词服务测试类 / System Prompt Service Test Class"""
    
    def setup_method(self):
        """测试前设置 / Setup before each test"""
        # 创建临时目录 / Create temporary directories
        self.temp_dir = tempfile.mkdtemp()
        self.prompts_folder = Path(self.temp_dir) / "prompts"
        self.history_folder = Path(self.temp_dir) / "history"
        
        # 初始化服务 / Initialize service
        self.service = SystemPromptService(
            str(self.prompts_folder),
            str(self.history_folder)
        )
    
    def teardown_method(self):
        """测试后清理 / Cleanup after each test"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_init_creates_folders(self):
        """测试初始化时创建文件夹 / Test folder creation during initialization"""
        assert self.prompts_folder.exists()
        assert self.history_folder.exists()
    
    def test_validate_prompt_name_valid(self):
        """测试有效提示词名称验证 / Test valid prompt name validation"""
        assert self.service.validate_prompt_name("test_prompt")
        assert self.service.validate_prompt_name("技术分析")
        assert self.service.validate_prompt_name("Business Case 123")
    
    def test_validate_prompt_name_invalid(self):
        """测试无效提示词名称验证 / Test invalid prompt name validation"""
        from src.exceptions.system_prompt_exceptions import PromptValidationError
        
        with pytest.raises(PromptValidationError):
            self.service.validate_prompt_name("")
        with pytest.raises(PromptValidationError):
            self.service.validate_prompt_name("   ")
        with pytest.raises(PromptValidationError):
            self.service.validate_prompt_name("test<>prompt")
        with pytest.raises(PromptValidationError):
            self.service.validate_prompt_name("test/prompt")
        with pytest.raises(PromptValidationError):
            self.service.validate_prompt_name("a" * 101)  # Too long
    
    def test_sanitize_folder_name(self):
        """测试文件夹名称清理 / Test folder name sanitization"""
        assert self.service.sanitize_folder_name("test prompt") == "test_prompt"
        assert self.service.sanitize_folder_name("test<>prompt") == "test__prompt"
        assert self.service.sanitize_folder_name("  test  ") == "test"
        assert self.service.sanitize_folder_name("test/\\prompt") == "test__prompt"
    
    def test_save_and_load_prompt_file(self):
        """测试保存和加载提示词文件 / Test saving and loading prompt file"""
        name = "test_prompt"
        content = "这是一个测试提示词内容"
        
        # 保存文件 / Save file
        assert self.service.save_prompt_file(name, content)
        
        # 验证文件存在 / Verify file exists
        file_path = self.prompts_folder / f"{name}.md"
        assert file_path.exists()
        
        # 加载文件 / Load file
        loaded_content = self.service.load_prompt_file(name)
        assert loaded_content == content
    
    def test_load_nonexistent_prompt_file(self):
        """测试加载不存在的提示词文件 / Test loading non-existent prompt file"""
        from src.exceptions.system_prompt_exceptions import PromptNotFoundError
        
        with pytest.raises(PromptNotFoundError):
            self.service.load_prompt_file("nonexistent")
    
    def test_delete_prompt_file(self):
        """测试删除提示词文件 / Test deleting prompt file"""
        name = "test_prompt"
        content = "测试内容"
        
        # 先保存文件 / Save file first
        assert self.service.save_prompt_file(name, content)
        
        # 验证文件存在 / Verify file exists
        file_path = self.prompts_folder / f"{name}.md"
        assert file_path.exists()
        
        # 删除文件 / Delete file
        assert self.service.delete_prompt_file(name)
        assert not file_path.exists()
    
    def test_delete_nonexistent_prompt_file(self):
        """测试删除不存在的提示词文件 / Test deleting non-existent prompt file"""
        result = self.service.delete_prompt_file("nonexistent")
        assert not result
    
    def test_list_prompt_files(self):
        """测试列出提示词文件 / Test listing prompt files"""
        # 初始状态应该为空 / Initial state should be empty
        assert self.service.list_prompt_files() == []
        
        # 创建几个提示词文件 / Create several prompt files
        prompts = ["prompt1", "prompt2", "技术分析"]
        for prompt in prompts:
            self.service.save_prompt_file(prompt, f"内容 {prompt}")
        
        # 验证列表 / Verify list
        listed_prompts = self.service.list_prompt_files()
        assert len(listed_prompts) == 3
        assert "prompt1" in listed_prompts
        assert "prompt2" in listed_prompts
        assert "技术分析" in listed_prompts
    
    def test_create_history_folder(self):
        """测试创建历史文件夹 / Test creating history folder"""
        prompt_name = "test_prompt"
        
        # 创建历史文件夹 / Create history folder
        folder_path = self.service.create_history_folder(prompt_name)
        
        # 验证文件夹存在 / Verify folder exists
        assert folder_path
        assert Path(folder_path).exists()
        assert Path(folder_path).is_dir()
    
    def test_save_prompt_creates_history_folder(self):
        """测试保存提示词时自动创建历史文件夹 / Test automatic history folder creation when saving prompt"""
        name = "test_prompt"
        content = "测试内容"
        
        # 保存提示词 / Save prompt
        assert self.service.save_prompt_file(name, content)
        
        # 验证历史文件夹被创建 / Verify history folder was created
        history_folder = self.history_folder / name
        assert history_folder.exists()
        assert history_folder.is_dir()
    
    def test_format_and_extract_prompt_content(self):
        """测试提示词内容格式化和提取 / Test prompt content formatting and extraction"""
        name = "test_prompt"
        original_content = "这是原始提示词内容\n包含多行"
        
        # 保存并重新加载 / Save and reload
        assert self.service.save_prompt_file(name, original_content)
        loaded_content = self.service.load_prompt_file(name)
        
        # 验证内容一致 / Verify content consistency
        assert loaded_content == original_content
    
    def test_sanitize_folder_name_with_special_cases(self):
        """测试特殊情况下的文件夹名称清理 / Test folder name sanitization with special cases"""
        # 空名称应该生成默认名称 / Empty name should generate default name
        result = self.service.sanitize_folder_name("")
        assert result.startswith("prompt_")
        
        # 只有特殊字符的名称 / Name with only special characters
        result = self.service.sanitize_folder_name("<<<>>>")
        assert result.startswith("prompt_")
        
        # 包含点的名称 / Name with dots
        result = self.service.sanitize_folder_name(".test.")
        assert result == "test"