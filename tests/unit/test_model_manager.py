"""
模型管理器单元测试 / Model Manager Unit Tests

测试模型管理器的各项功能
Test various functions of model manager
"""

import pytest
from unittest.mock import Mock, MagicMock

from src.services.model_manager import ModelManager
from src.clients.bedrock_client import BedrockClient, ModelInvocationError


class TestModelManager:
    """ModelManager测试类 / ModelManager test class"""
    
    def setup_method(self):
        """测试方法设置 / Test method setup"""
        self.mock_bedrock_client = Mock(spec=BedrockClient)
        self.config = {
            'models': {
                'claude': [
                    {'id': 'anthropic.claude-3-sonnet-20240229-v1:0', 'name': 'Claude 3 Sonnet'},
                    {'id': 'anthropic.claude-3-haiku-20240307-v1:0', 'name': 'Claude 3 Haiku'}
                ],
                'nova': [
                    {'id': 'amazon.nova-pro-v1:0', 'name': 'Nova Pro'}
                ],
                'deepseek': [
                    {'id': 'deepseek.deepseek-v2.5', 'name': 'DeepSeek V2.5'}
                ],
                'openai': [
                    {'id': 'openai.gpt-4o-2024-08-06', 'name': 'GPT-4o'}
                ]
            }
        }
        
        # 模拟API返回的模型列表 / Mock API returned model list
        self.mock_api_models = [
            {'modelId': 'anthropic.claude-3-5-sonnet-20241022-v2:0', 'modelName': 'Claude 3.5 Sonnet'},
            {'modelId': 'amazon.nova-pro-v1:0', 'modelName': 'Nova Pro'},
            {'modelId': 'deepseek.deepseek-v2.5', 'modelName': 'DeepSeek V2.5'}
        ]
        
        # 模拟按提供商分类的模型 / Mock models categorized by provider
        self.mock_categorized_models = {
            'claude': [{'modelId': 'anthropic.claude-3-5-sonnet-20241022-v2:0', 'modelName': 'Claude 3.5 Sonnet'}],
            'nova': [{'modelId': 'amazon.nova-pro-v1:0', 'modelName': 'Nova Pro'}],
            'deepseek': [{'modelId': 'deepseek.deepseek-v2.5', 'modelName': 'DeepSeek V2.5'}],
            'openai': []
        }
    
    def test_init(self):
        """测试初始化 / Test initialization"""
        manager = ModelManager(self.mock_bedrock_client, self.config)
        
        assert manager.bedrock_client == self.mock_bedrock_client
        assert manager.config == self.config
        assert manager._cached_models is None
        assert manager._categorized_models is None
    
    def test_refresh_available_models_success(self):
        """测试成功刷新模型列表 / Test successful model list refresh"""
        # 设置mock返回值 / Setup mock return values
        self.mock_bedrock_client.list_foundation_models.return_value = self.mock_api_models
        self.mock_bedrock_client.filter_models_by_provider.return_value = self.mock_categorized_models
        self.mock_bedrock_client.get_model_display_name.side_effect = lambda x: f"Display {x}"
        
        manager = ModelManager(self.mock_bedrock_client, self.config)
        result = manager.refresh_available_models()
        
        # 验证结果 / Verify result
        assert result == self.mock_categorized_models
        assert manager._cached_models == self.mock_api_models
        assert manager._categorized_models == self.mock_categorized_models
        
        # 验证每个模型都添加了displayName / Verify displayName added to each model
        for category_models in result.values():
            for model in category_models:
                assert 'displayName' in model
    
    def test_refresh_available_models_failure(self):
        """测试刷新模型列表失败 / Test model list refresh failure"""
        # 设置mock抛出异常 / Setup mock to throw exception
        self.mock_bedrock_client.list_foundation_models.side_effect = ModelInvocationError("API Error")
        
        manager = ModelManager(self.mock_bedrock_client, self.config)
        result = manager.refresh_available_models()
        
        # 应该返回配置文件中的备选模型 / Should return fallback models from config
        assert 'claude' in result
        assert 'nova' in result
        assert len(result['claude']) > 0  # 应该有配置文件中的模型 / Should have models from config
    
    def test_get_models_by_category_with_cache(self):
        """测试从缓存获取模型分类 / Test getting model categories from cache"""
        manager = ModelManager(self.mock_bedrock_client, self.config)
        manager._categorized_models = self.mock_categorized_models
        
        result = manager.get_models_by_category()
        
        assert result == self.mock_categorized_models
        # 不应该调用API / Should not call API
        self.mock_bedrock_client.list_foundation_models.assert_not_called()
    
    def test_get_models_by_category_without_cache(self):
        """测试无缓存时获取模型分类 / Test getting model categories without cache"""
        # 设置mock返回值 / Setup mock return values
        self.mock_bedrock_client.list_foundation_models.return_value = self.mock_api_models
        self.mock_bedrock_client.filter_models_by_provider.return_value = self.mock_categorized_models
        self.mock_bedrock_client.get_model_display_name.side_effect = lambda x: f"Display {x}"
        
        manager = ModelManager(self.mock_bedrock_client, self.config)
        result = manager.get_models_by_category()
        
        assert result == self.mock_categorized_models
        # 应该调用API刷新 / Should call API to refresh
        self.mock_bedrock_client.list_foundation_models.assert_called_once()
    
    def test_get_supported_models_only(self):
        """测试获取仅支持的模型 / Test getting only supported models"""
        manager = ModelManager(self.mock_bedrock_client, self.config)
        manager._categorized_models = self.mock_categorized_models
        
        result = manager.get_supported_models_only()
        
        # 应该包含所有类别的模型 / Should include models from all categories
        expected_count = sum(len(models) for models in self.mock_categorized_models.values())
        assert len(result) == expected_count
    
    def test_get_model_info_found(self):
        """测试获取存在的模型信息 / Test getting existing model info"""
        manager = ModelManager(self.mock_bedrock_client, self.config)
        manager._categorized_models = self.mock_categorized_models
        
        model_id = 'anthropic.claude-3-5-sonnet-20241022-v2:0'
        result = manager.get_model_info(model_id)
        
        assert result is not None
        assert result['modelId'] == model_id
    
    def test_get_model_info_not_found(self):
        """测试获取不存在的模型信息 / Test getting non-existing model info"""
        manager = ModelManager(self.mock_bedrock_client, self.config)
        manager._categorized_models = self.mock_categorized_models
        
        result = manager.get_model_info('non-existent-model')
        
        assert result is None
    
    def test_is_model_available_true(self):
        """测试模型可用性检查（可用）/ Test model availability check (available)"""
        manager = ModelManager(self.mock_bedrock_client, self.config)
        manager._categorized_models = self.mock_categorized_models
        
        result = manager.is_model_available('anthropic.claude-3-5-sonnet-20241022-v2:0')
        
        assert result is True
    
    def test_is_model_available_false(self):
        """测试模型可用性检查（不可用）/ Test model availability check (not available)"""
        manager = ModelManager(self.mock_bedrock_client, self.config)
        manager._categorized_models = self.mock_categorized_models
        
        result = manager.is_model_available('non-existent-model')
        
        assert result is False
    
    def test_get_default_model_preferred_available(self):
        """测试获取默认模型（首选可用）/ Test getting default model (preferred available)"""
        manager = ModelManager(self.mock_bedrock_client, self.config)
        manager._categorized_models = self.mock_categorized_models
        
        result = manager.get_default_model()
        
        # 应该返回首选的Claude 3.5 Sonnet / Should return preferred Claude 3.5 Sonnet
        assert result == 'anthropic.claude-3-5-sonnet-20241022-v2:0'
    
    def test_get_default_model_fallback(self):
        """测试获取默认模型（备选）/ Test getting default model (fallback)"""
        # 设置没有首选模型的情况 / Setup scenario without preferred models
        categorized_models = {
            'claude': [],
            'nova': [{'modelId': 'amazon.nova-pro-v1:0'}],
            'deepseek': [],
            'openai': []
        }
        
        manager = ModelManager(self.mock_bedrock_client, self.config)
        manager._categorized_models = categorized_models
        
        result = manager.get_default_model()
        
        # 应该返回可用的模型 / Should return available model
        assert result == 'amazon.nova-pro-v1:0'
    
    def test_get_models_for_ui(self):
        """测试获取UI显示的模型列表 / Test getting model list for UI display"""
        manager = ModelManager(self.mock_bedrock_client, self.config)
        manager._categorized_models = self.mock_categorized_models
        
        result = manager.get_models_for_ui()
        
        # 验证结果结构 / Verify result structure
        assert isinstance(result, list)
        assert len(result) > 0
        
        # 应该包含分类分隔符 / Should include category separators
        separator_count = sum(1 for item in result if item.get('disabled', False))
        assert separator_count > 0
        
        # 应该包含实际模型 / Should include actual models
        model_count = sum(1 for item in result if not item.get('disabled', False))
        assert model_count > 0
    
    def test_get_fallback_models(self):
        """测试获取备选模型列表 / Test getting fallback model list"""
        manager = ModelManager(self.mock_bedrock_client, self.config)
        
        result = manager._get_fallback_models()
        
        # 验证结构 / Verify structure
        assert 'claude' in result
        assert 'nova' in result
        assert 'deepseek' in result
        assert 'openai' in result
        
        # 验证配置文件中的模型被正确转换 / Verify config models are correctly converted
        assert len(result['claude']) == 2  # 配置文件中有2个Claude模型 / 2 Claude models in config
        assert result['claude'][0]['modelId'] == 'anthropic.claude-3-sonnet-20240229-v1:0'
    
    def test_validate_model_access_success(self):
        """测试模型访问验证成功 / Test successful model access validation"""
        # 设置mock成功调用 / Setup mock successful call
        self.mock_bedrock_client.format_messages.return_value = [{'role': 'user', 'content': [{'text': 'test'}]}]
        self.mock_bedrock_client.converse.return_value = "test response"
        
        manager = ModelManager(self.mock_bedrock_client, self.config)
        
        result = manager.validate_model_access('test-model-id')
        
        assert result is True
        self.mock_bedrock_client.converse.assert_called_once()
    
    def test_validate_model_access_failure(self):
        """测试模型访问验证失败 / Test model access validation failure"""
        # 设置mock抛出异常 / Setup mock to throw exception
        self.mock_bedrock_client.format_messages.return_value = [{'role': 'user', 'content': [{'text': 'test'}]}]
        self.mock_bedrock_client.converse.side_effect = ModelInvocationError("Access denied")
        
        manager = ModelManager(self.mock_bedrock_client, self.config)
        
        result = manager.validate_model_access('test-model-id')
        
        assert result is False
