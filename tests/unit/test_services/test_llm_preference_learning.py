"""
LLM偏好学习引擎单元测试 / LLM Preference Learning Engine Unit Tests
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from src.services.llm_preference_learning import LLMBasedPreferenceLearning
from src.clients.bedrock_client import BedrockClient


class TestLLMBasedPreferenceLearning:
    """LLM偏好学习引擎测试类 / LLM Preference Learning Engine Test Class"""
    
    def setup_method(self):
        """测试前设置 / Setup before each test"""
        self.mock_bedrock_client = Mock(spec=BedrockClient)
        self.preference_learning = LLMBasedPreferenceLearning(self.mock_bedrock_client)
        
    def test_init(self):
        """测试初始化 / Test initialization"""
        assert self.preference_learning.bedrock_client == self.mock_bedrock_client
        assert self.preference_learning.preference_prompt_template is not None
        assert len(self.preference_learning.preference_prompt_template) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_and_update_preference_success(self):
        """测试成功分析和更新偏好 / Test successful preference analysis and update"""
        # 准备测试数据
        user_id = "test_user"
        prompt_name = "test_prompt"
        interaction_data = {
            'modification_type': 'content_addition',
            'user_satisfaction': 0.8,
            'feedback_text': 'Please add more details'
        }
        
        # Mock LLM响应
        mock_llm_response = '{"preference_analysis": {"dominant_modification_types": ["content_addition"]}, "personalized_prompt": "详细的提示词"}'
        
        self.mock_bedrock_client.converse = AsyncMock(return_value=mock_llm_response)
        
        # 执行测试
        result = await self.preference_learning.analyze_and_update_preference(
            user_id, prompt_name, interaction_data
        )
        
        # 验证结果
        assert result['success'] is True
        assert 'preference_analysis' in result
        assert 'update_timestamp' in result
        
        # 验证方法调用
        self.mock_bedrock_client.converse.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_and_update_preference_llm_error(self):
        """测试LLM调用错误 / Test LLM call error"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        interaction_data = {'modification_type': 'content_addition'}
        
        # Mock LLM错误
        self.mock_bedrock_client.converse = AsyncMock(side_effect=Exception("LLM调用失败"))
        
        result = await self.preference_learning.analyze_and_update_preference(
            user_id, prompt_name, interaction_data
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_collect_interaction_history(self):
        """测试收集交互历史 / Test collect interaction history"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        
        result = self.preference_learning.collect_interaction_history(user_id, prompt_name)
        
        assert isinstance(result, list)
        # 当前实现返回模拟数据
        assert len(result) > 0
    
    def test_load_current_preference(self):
        """测试加载当前偏好 / Test load current preference"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        
        result = self.preference_learning.load_current_preference(user_id, prompt_name)
        
        assert isinstance(result, dict)
        assert 'summary' in result
    
    def test_format_interaction_history(self):
        """测试格式化交互历史 / Test format interaction history"""
        interaction_history = [
            {
                'timestamp': '2025-08-29T15:30:00',
                'modification_type': 'content_addition',
                'user_request': 'Add more details',
                'satisfaction_score': 0.8
            },
            {
                'timestamp': '2025-08-29T15:35:00',
                'modification_type': 'style_adjustment',
                'user_request': 'Make it more formal',
                'satisfaction_score': 0.7
            }
        ]
        
        result = self.preference_learning.format_interaction_history(interaction_history)
        
        assert isinstance(result, str)
        assert 'content_addition' in result
        assert 'style_adjustment' in result
        assert 'Add more details' in result
        assert 'Make it more formal' in result
    
    def test_format_interaction_history_empty(self):
        """测试格式化空交互历史 / Test format empty interaction history"""
        result = self.preference_learning.format_interaction_history([])
        
        assert result == "暂无交互历史"
    
    def test_format_user_feedback(self):
        """测试格式化用户反馈 / Test format user feedback"""
        interaction_data = {
            'satisfaction_score': 0.8,
            'modification_success': True,
            'user_comments': 'Good improvement',
            'preferred_style': 'formal'
        }
        
        result = self.preference_learning.format_user_feedback(interaction_data)
        
        assert isinstance(result, str)
        assert '0.8' in result
        assert 'Good improvement' in result
        assert 'formal' in result
    
    def test_format_user_feedback_empty(self):
        """测试格式化空用户反馈 / Test format empty user feedback"""
        result = self.preference_learning.format_user_feedback({})
        
        assert result == "暂无反馈信息"
    
    def test_parse_llm_response_json(self):
        """测试解析JSON格式的LLM响应 / Test parse JSON format LLM response"""
        json_response = '{"preference_analysis": {"dominant_types": ["content_addition"]}, "personalized_prompt": "详细的案例总结"}'
        
        result = self.preference_learning.parse_llm_response(json_response)
        
        assert isinstance(result, dict)
        assert 'preference_analysis' in result
        assert 'personalized_prompt' in result
        assert result['preference_analysis']['dominant_types'] == ["content_addition"]
    
    def test_parse_llm_response_text(self):
        """测试解析文本格式的LLM响应 / Test parse text format LLM response"""
        text_response = "用户喜欢详细的信息。"
        
        result = self.preference_learning.parse_llm_response(text_response)
        
        assert isinstance(result, dict)
        assert 'preference_analysis' in result
        assert 'personalized_prompt' in result
        assert 'raw_response' in result['preference_analysis']
    
    @pytest.mark.asyncio
    async def test_save_preference_update(self):
        """测试保存偏好更新 / Test save preference update"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        preference_data = {
            'analysis': '偏好分析',
            'update_timestamp': datetime.now().isoformat()
        }
        
        result = await self.preference_learning.save_preference_update(
            user_id, prompt_name, preference_data
        )
        
        # 当前实现总是返回True
        assert result is True
    
    def test_get_preference_learning_statistics(self):
        """测试获取偏好学习统计信息 / Test get preference learning statistics"""
        user_id = "test_user"
        
        result = self.preference_learning.get_preference_learning_statistics(user_id)
        
        assert isinstance(result, dict)
        assert 'total_analyses' in result
        assert 'successful_analyses' in result
        assert 'learning_confidence' in result
        assert result['total_analyses'] == 0  # 当前实现返回默认值