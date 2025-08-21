"""
客户端模块单元测试 / Clients Module Unit Tests

测试客户端模块的各项功能
Test various functions of clients module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import boto3
from botocore.exceptions import ClientError

from src.clients.bedrock_client import BedrockClient, ModelInvocationError


class TestBedrockClient:
    """BedrockClient测试类 / BedrockClient test class"""
    
    def setup_method(self):
        """测试方法设置 / Test method setup"""
        self.mock_session = Mock(spec=boto3.Session)
        self.mock_bedrock_client = Mock()
        self.mock_bedrock_runtime_client = Mock()
        
        # 设置session.client返回mock客户端 / Setup session.client to return mock clients
        def mock_client(service_name):
            if service_name == 'bedrock':
                return self.mock_bedrock_client
            elif service_name == 'bedrock-runtime':
                return self.mock_bedrock_runtime_client
            return Mock()
        
        self.mock_session.client.side_effect = mock_client
        
    def test_initialize_clients_success(self):
        """测试成功初始化客户端 / Test successful client initialization"""
        client = BedrockClient(self.mock_session)
        
        assert client.bedrock_client == self.mock_bedrock_client
        assert client.bedrock_runtime_client == self.mock_bedrock_runtime_client
        assert self.mock_session.client.call_count == 2
    
    def test_initialize_clients_failure(self):
        """测试客户端初始化失败 / Test client initialization failure"""
        self.mock_session.client.side_effect = Exception("Connection failed")
        
        with pytest.raises(ModelInvocationError, match="无法初始化Bedrock客户端"):
            BedrockClient(self.mock_session)
    
    def test_list_foundation_models_success(self):
        """测试成功获取模型列表 / Test successful model list retrieval"""
        # 模拟API响应 / Mock API response
        mock_models = [
            {'modelId': 'anthropic.claude-3-sonnet-20240229-v1:0', 'modelName': 'Claude 3 Sonnet'},
            {'modelId': 'amazon.nova-pro-v1:0', 'modelName': 'Nova Pro'},
            {'modelId': 'deepseek.deepseek-v2.5', 'modelName': 'DeepSeek V2.5'},
            {'modelId': 'unsupported.model-v1:0', 'modelName': 'Unsupported Model'}  # 不支持的模型
        ]
        
        self.mock_bedrock_client.list_foundation_models.return_value = {
            'modelSummaries': mock_models
        }
        
        client = BedrockClient(self.mock_session)
        models = client.list_foundation_models()
        
        # 应该只返回支持的模型 / Should only return supported models
        assert len(models) == 3
        model_ids = [model['modelId'] for model in models]
        assert 'anthropic.claude-3-sonnet-20240229-v1:0' in model_ids
        assert 'amazon.nova-pro-v1:0' in model_ids
        assert 'deepseek.deepseek-v2.5' in model_ids
        assert 'unsupported.model-v1:0' not in model_ids
    
    def test_list_foundation_models_client_error(self):
        """测试获取模型列表时的客户端错误 / Test client error when getting model list"""
        self.mock_bedrock_client.list_foundation_models.side_effect = ClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
            'ListFoundationModels'
        )
        
        client = BedrockClient(self.mock_session)
        
        with pytest.raises(ModelInvocationError, match="AWS API错误: AccessDenied"):
            client.list_foundation_models()
    
    def test_filter_models_by_provider(self):
        """测试按提供商筛选模型 / Test filtering models by provider"""
        models = [
            {'modelId': 'anthropic.claude-3-sonnet-20240229-v1:0'},
            {'modelId': 'anthropic.claude-3-haiku-20240307-v1:0'},
            {'modelId': 'amazon.nova-pro-v1:0'},
            {'modelId': 'amazon.nova-lite-v1:0'},
            {'modelId': 'deepseek.deepseek-v2.5'},
            {'modelId': 'openai.gpt-4o-2024-08-06'}
        ]
        
        client = BedrockClient(self.mock_session)
        categorized = client.filter_models_by_provider(models)
        
        assert len(categorized['claude']) == 2
        assert len(categorized['nova']) == 2
        assert len(categorized['deepseek']) == 1
        assert len(categorized['openai']) == 1
        
        # 验证分类正确 / Verify correct categorization
        claude_ids = [model['modelId'] for model in categorized['claude']]
        assert 'anthropic.claude-3-sonnet-20240229-v1:0' in claude_ids
        assert 'anthropic.claude-3-haiku-20240307-v1:0' in claude_ids
    
    def test_is_supported_model(self):
        """测试模型支持检查 / Test model support checking"""
        client = BedrockClient(self.mock_session)
        
        # 支持的模型 / Supported models
        assert client.is_supported_model('anthropic.claude-3-sonnet-20240229-v1:0') is True
        assert client.is_supported_model('amazon.nova-pro-v1:0') is True
        assert client.is_supported_model('deepseek.deepseek-v2.5') is True
        assert client.is_supported_model('openai.gpt-4o-2024-08-06') is True
        
        # 不支持的模型 / Unsupported models
        assert client.is_supported_model('meta.llama2-70b-chat-v1') is False
        assert client.is_supported_model('ai21.j2-ultra-v1') is False
        assert client.is_supported_model('cohere.command-text-v14') is False
    
    def test_get_model_display_name(self):
        """测试获取模型显示名称 / Test getting model display name"""
        client = BedrockClient(self.mock_session)
        
        # Claude系列 / Claude series
        assert client.get_model_display_name('anthropic.claude-3-sonnet-20240229-v1:0') == "Claude 3 Sonnet"
        assert client.get_model_display_name('anthropic.claude-3-haiku-20240307-v1:0') == "Claude 3 Haiku"
        assert client.get_model_display_name('anthropic.claude-3-5-sonnet-20241022-v2:0') == "Claude 3.5 Sonnet"
        
        # Nova系列 / Nova series
        assert client.get_model_display_name('amazon.nova-pro-v1:0') == "Nova Pro"
        assert client.get_model_display_name('amazon.nova-lite-v1:0') == "Nova Lite"
        
        # DeepSeek系列 / DeepSeek series
        assert client.get_model_display_name('deepseek.deepseek-v2.5') == "DeepSeek V2.5"
        
        # OpenAI系列 / OpenAI series
        assert client.get_model_display_name('openai.gpt-4o-2024-08-06') == "GPT-4o"
        
        # 未知模型返回原ID / Unknown model returns original ID
        assert client.get_model_display_name('unknown.model-v1:0') == "unknown.model-v1:0"
    
    def test_converse_success(self):
        """测试成功的模型对话 / Test successful model conversation"""
        # 模拟API响应 / Mock API response
        mock_response = {
            'output': {
                'message': {
                    'content': [
                        {
                            'text': '这是模型的响应内容'
                        }
                    ]
                }
            }
        }
        
        self.mock_bedrock_runtime_client.converse.return_value = mock_response
        
        client = BedrockClient(self.mock_session)
        messages = client.format_messages("测试用户输入")
        
        result = client.converse(
            model_id='anthropic.claude-3-sonnet-20240229-v1:0',
            messages=messages,
            system_prompt='你是助手',
            max_tokens=1000,
            temperature=0.5
        )
        
        assert result == '这是模型的响应内容'
        
        # 验证API调用参数 / Verify API call parameters
        call_args = self.mock_bedrock_runtime_client.converse.call_args
        assert call_args[1]['modelId'] == 'anthropic.claude-3-sonnet-20240229-v1:0'
        assert call_args[1]['inferenceConfig']['maxTokens'] == 1000
        assert call_args[1]['inferenceConfig']['temperature'] == 0.5
        assert call_args[1]['system'][0]['text'] == '你是助手'
    
    def test_converse_without_system_prompt(self):
        """测试不带系统提示词的对话 / Test conversation without system prompt"""
        mock_response = {
            'output': {
                'message': {
                    'content': [
                        {
                            'text': '响应内容'
                        }
                    ]
                }
            }
        }
        
        self.mock_bedrock_runtime_client.converse.return_value = mock_response
        
        client = BedrockClient(self.mock_session)
        messages = client.format_messages("测试输入")
        
        result = client.converse(
            model_id='anthropic.claude-3-sonnet-20240229-v1:0',
            messages=messages
        )
        
        assert result == '响应内容'
        
        # 验证没有系统提示词 / Verify no system prompt
        call_args = self.mock_bedrock_runtime_client.converse.call_args
        assert 'system' not in call_args[1]
    
    def test_converse_empty_response(self):
        """测试空响应处理 / Test empty response handling"""
        mock_response = {
            'output': {
                'message': {
                    'content': []
                }
            }
        }
        
        self.mock_bedrock_runtime_client.converse.return_value = mock_response
        
        client = BedrockClient(self.mock_session)
        messages = client.format_messages("测试输入")
        
        with pytest.raises(ModelInvocationError, match="模型响应为空"):
            client.converse(
                model_id='anthropic.claude-3-sonnet-20240229-v1:0',
                messages=messages
            )
    
    def test_converse_client_error(self):
        """测试对话时的客户端错误 / Test client error during conversation"""
        self.mock_bedrock_runtime_client.converse.side_effect = ClientError(
            {'Error': {'Code': 'ValidationException', 'Message': 'Invalid model ID'}},
            'Converse'
        )
        
        client = BedrockClient(self.mock_session)
        messages = client.format_messages("测试输入")
        
        with pytest.raises(ModelInvocationError, match="AWS API错误: ValidationException"):
            client.converse(
                model_id='invalid-model-id',
                messages=messages
            )
    
    def test_format_messages(self):
        """测试消息格式化 / Test message formatting"""
        client = BedrockClient(self.mock_session)
        
        user_prompt = "这是用户的输入内容"
        messages = client.format_messages(user_prompt)
        
        expected = [
            {
                'role': 'user',
                'content': [
                    {
                        'text': user_prompt
                    }
                ]
            }
        ]
        
        assert messages == expected
