"""
Prompt导出导入管理器单元测试 / Prompt Export/Import Manager Unit Tests
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch

from src.services.prompt_export_import import PromptExportImportManager
from src.services.personalized_prompt_manager import PersonalizedPromptManager


class TestPromptExportImportManager:
    """Prompt导出导入管理器测试类 / Prompt Export/Import Manager Test Class"""
    
    def setup_method(self):
        """测试前设置 / Setup before each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.prompt_manager = PersonalizedPromptManager(self.temp_dir)
        self.export_import_manager = PromptExportImportManager(self.prompt_manager)
        
    def teardown_method(self):
        """测试后清理 / Cleanup after each test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """测试初始化 / Test initialization"""
        assert self.export_import_manager.prompt_manager == self.prompt_manager
        assert 'json' in self.export_import_manager.export_formats
        assert 'yaml' in self.export_import_manager.export_formats
    
    def test_export_user_prompts_no_data(self):
        """测试导出无数据的用户 / Test exporting user with no data"""
        export_config = {'format': 'json'}
        result = self.export_import_manager.export_user_prompts('nonexistent_user', export_config)
        
        assert result['success'] is False
        assert 'No personalized prompts found' in result['error']
    
    def test_export_user_prompts_success(self):
        """测试成功导出用户数据 / Test successful user data export"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        preference_analysis = {
            'analysis': 'User prefers detailed responses',
            'personalized_prompt': 'Please provide detailed explanations.'
        }
        
        # 创建测试数据
        self.prompt_manager.create_personalized_prompt_file(
            user_id, prompt_name, preference_analysis
        )
        
        export_config = {'format': 'json', 'include_history': True}
        result = self.export_import_manager.export_user_prompts(user_id, export_config)
        
        assert result['success'] is True
        assert 'filename' in result
        assert 'data' in result
        assert 'metadata' in result
        
        # 验证导出数据格式
        exported_data = json.loads(result['data'])
        assert 'metadata' in exported_data
        assert 'user_profile' in exported_data
        assert 'prompt_preferences' in exported_data
        assert user_id == exported_data['metadata']['user_id']
    
    def test_export_user_prompts_yaml_format(self):
        """测试YAML格式导出 / Test YAML format export"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        preference_analysis = {
            'analysis': 'Test analysis',
            'personalized_prompt': 'Test prompt'
        }
        
        # 创建测试数据
        self.prompt_manager.create_personalized_prompt_file(
            user_id, prompt_name, preference_analysis
        )
        
        export_config = {'format': 'yaml'}
        result = self.export_import_manager.export_user_prompts(user_id, export_config)
        
        assert result['success'] is True
        assert result['filename'].endswith('.yaml')
        assert 'metadata:' in result['data']  # YAML格式特征
    
    def test_import_user_prompts_invalid_data(self):
        """测试导入无效数据 / Test importing invalid data"""
        invalid_data = {'invalid': 'data'}
        import_config = {'merge_strategy': 'replace'}
        
        result = self.export_import_manager.import_user_prompts(invalid_data, import_config)
        
        assert result['success'] is False
        assert 'Invalid import data' in result['error']
    
    def test_import_user_prompts_success(self):
        """测试成功导入数据 / Test successful data import"""
        user_id = "test_user"
        
        # 准备有效的导入数据
        import_data = {
            'metadata': {
                'user_id': user_id,
                'export_version': '1.0',
                'export_timestamp': '2024-01-01T00:00:00'
            },
            'user_profile': {
                'user_id': user_id,
                'total_prompts': 1
            },
            'prompt_preferences': {
                'test_prompt': [{
                    'version': '20240101_000000',
                    'content': 'Test prompt content',
                    'created_at': '2024-01-01T00:00:00'
                }]
            }
        }
        
        import_config = {
            'merge_strategy': 'replace',
            'validate_integrity': False,
            'backup_existing': False
        }
        
        result = self.export_import_manager.import_user_prompts(import_data, import_config)
        
        assert result['success'] is True
        assert result['total_items'] == 1
        assert result['successful_items'] == 1
        assert result['failed_items'] == 0
    
    def test_validate_import_data_valid(self):
        """测试验证有效的导入数据 / Test validating valid import data"""
        valid_data = {
            'metadata': {'user_id': 'test_user', 'export_version': '1.0'},
            'user_profile': {'user_id': 'test_user'},
            'prompt_preferences': {}
        }
        
        result = self.export_import_manager._validate_import_data(valid_data)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
    
    def test_validate_import_data_invalid(self):
        """测试验证无效的导入数据 / Test validating invalid import data"""
        invalid_data = {
            'metadata': {},  # 缺少user_id
            'user_profile': {}
            # 缺少prompt_preferences
        }
        
        result = self.export_import_manager._validate_import_data(invalid_data)
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
        assert any('user_id' in error for error in result['errors'])
        assert any('prompt_preferences' in error for error in result['errors'])
    
    def test_verify_data_integrity_no_hash(self):
        """测试验证无hash的数据完整性 / Test verifying data integrity without hash"""
        import_data = {
            'metadata': {},
            'user_profile': {},
            'prompt_preferences': {}
        }
        
        result = self.export_import_manager._verify_data_integrity(import_data)
        
        assert result['valid'] is True
    
    def test_verify_data_integrity_valid_hash(self):
        """测试验证有效hash的数据完整性 / Test verifying data integrity with valid hash"""
        user_data = {
            'profile': {'user_id': 'test_user'},
            'prompts': {'test_prompt': []}
        }
        
        # 计算正确的hash
        expected_hash = self.export_import_manager._calculate_data_hash(user_data)
        
        import_data = {
            'metadata': {'data_integrity_hash': expected_hash},
            'user_profile': user_data['profile'],
            'prompt_preferences': user_data['prompts']
        }
        
        result = self.export_import_manager._verify_data_integrity(import_data)
        
        assert result['valid'] is True
    
    def test_verify_data_integrity_invalid_hash(self):
        """测试验证无效hash的数据完整性 / Test verifying data integrity with invalid hash"""
        import_data = {
            'metadata': {'data_integrity_hash': 'invalid_hash'},
            'user_profile': {'user_id': 'test_user'},
            'prompt_preferences': {}
        }
        
        result = self.export_import_manager._verify_data_integrity(import_data)
        
        assert result['valid'] is False
        assert 'hash mismatch' in result['error']
    
    def test_calculate_data_hash(self):
        """测试计算数据hash / Test calculating data hash"""
        data1 = {'key': 'value', 'number': 123}
        data2 = {'key': 'value', 'number': 123}
        data3 = {'key': 'different', 'number': 123}
        
        hash1 = self.export_import_manager._calculate_data_hash(data1)
        hash2 = self.export_import_manager._calculate_data_hash(data2)
        hash3 = self.export_import_manager._calculate_data_hash(data3)
        
        assert hash1 == hash2  # 相同数据应该有相同hash
        assert hash1 != hash3  # 不同数据应该有不同hash
        assert len(hash1) == 32  # MD5 hash长度
    
    def test_collect_user_data_empty(self):
        """测试收集空用户数据 / Test collecting empty user data"""
        user_data = self.export_import_manager._collect_user_data(
            'nonexistent_user', None, True
        )
        
        assert user_data['profile']['user_id'] == 'nonexistent_user'
        assert user_data['profile']['total_prompts'] == 0
        assert len(user_data['prompts']) == 0
    
    def test_collect_user_data_with_prompts(self):
        """测试收集包含prompt的用户数据 / Test collecting user data with prompts"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        preference_analysis = {
            'analysis': 'Test analysis',
            'personalized_prompt': 'Test prompt'
        }
        
        # 创建测试数据
        self.prompt_manager.create_personalized_prompt_file(
            user_id, prompt_name, preference_analysis
        )
        
        user_data = self.export_import_manager._collect_user_data(user_id, None, True)
        
        assert user_data['profile']['user_id'] == user_id
        assert user_data['profile']['total_prompts'] == 1
        assert prompt_name in user_data['prompts']
        assert len(user_data['prompts'][prompt_name]) == 1
    
    def test_format_export_data_json(self):
        """测试JSON格式化导出数据 / Test JSON format export data"""
        data = {'key': 'value', 'number': 123}
        
        formatted = self.export_import_manager._format_export_data(data, 'json')
        
        assert isinstance(formatted, str)
        parsed = json.loads(formatted)
        assert parsed == data
    
    def test_format_export_data_yaml(self):
        """测试YAML格式化导出数据 / Test YAML format export data"""
        data = {'key': 'value', 'number': 123}
        
        formatted = self.export_import_manager._format_export_data(data, 'yaml')
        
        assert isinstance(formatted, str)
        assert 'key: value' in formatted
        assert 'number: 123' in formatted
    
    def test_format_export_data_unsupported_format(self):
        """测试不支持的格式 / Test unsupported format"""
        data = {'key': 'value'}
        
        with pytest.raises(ValueError, match="Unsupported export format"):
            self.export_import_manager._format_export_data(data, 'xml')
    
    def test_backup_existing_prompts_no_data(self):
        """测试备份不存在的用户数据 / Test backing up non-existent user data"""
        result = self.export_import_manager._backup_existing_prompts('nonexistent_user')
        
        assert result['success'] is False
    
    def test_import_prompt_data_success(self):
        """测试成功导入prompt数据 / Test successful prompt data import"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        prompt_data = [{
            'version': '20240101_000000',
            'content': 'Test prompt content',
            'created_at': '2024-01-01T00:00:00'
        }]
        
        result = self.export_import_manager._import_prompt_data(
            user_id, prompt_name, prompt_data, 'replace'
        )
        
        assert result['success'] is True
        assert result['prompt_name'] == prompt_name
        assert result['imported_count'] == 1
        
        # 验证文件是否创建
        user_dir = Path(self.temp_dir) / user_id
        assert user_dir.exists()
        prompt_files = list(user_dir.glob(f"*{prompt_name}*.md"))
        assert len(prompt_files) == 1