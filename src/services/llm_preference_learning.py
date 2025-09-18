"""
基于LLM的偏好学习模块 / LLM-based Preference Learning Module

使用LLM分析用户偏好并生成个性化提示词。
Uses LLM to analyze user preferences and generate personalized prompts.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..models.refinement_models import UserPreferenceProfile
from ..clients.bedrock_client import BedrockClient


logger = logging.getLogger(__name__)


class LLMBasedPreferenceLearning:
    """基于LLM的偏好学习引擎 / LLM-based Preference Learning Engine"""
    
    def __init__(self, bedrock_client: BedrockClient):
        """
        初始化偏好学习引擎 / Initialize preference learning engine
        
        Args:
            bedrock_client: Bedrock客户端实例 / Bedrock client instance
        """
        self.bedrock_client = bedrock_client
        self.preference_prompt_template = self._initialize_preference_prompt_template()
        
        logger.info("LLM偏好学习引擎初始化完成")
    
    def _initialize_preference_prompt_template(self) -> str:
        """
        初始化偏好分析提示词模板 / Initialize preference analysis prompt template
        
        Returns:
            提示词模板 / Prompt template
        """
        return """基于以下用户交互历史和反馈，分析用户在{prompt_name}场景下的生成偏好：

## 交互历史
{interaction_history}

## 用户反馈
{user_feedback}

## 当前偏好总结
{current_preference_summary}

请分析用户的偏好模式，并生成一个优化的系统提示词。

输出格式（JSON）：
{{
  "preference_analysis": {{
    "dominant_modification_types": ["类型1", "类型2"],
    "style_preferences": {{
      "formality_level": "formal/informal/balanced",
      "detail_level": "detailed/concise/moderate",
      "tone": "professional/friendly/authoritative"
    }},
    "content_structure_preferences": {{
      "preferred_sections": ["section1", "section2"],
      "paragraph_length": "short/medium/long"
    }}
  }},
  "personalized_prompt": "生成的个性化提示词内容"
}}"""
    
    def analyze_and_update_preference(self, user_id: str, prompt_name: str, 
                                          interaction_data: Dict) -> Dict[str, Any]:
        """
        分析用户交互并更新偏好 / Analyze user interaction and update preference
        
        Args:
            user_id: 用户ID / User ID
            prompt_name: 提示词名称 / Prompt name
            interaction_data: 交互数据 / Interaction data
            
        Returns:
            分析结果 / Analysis result
        """
        try:
            # 1. 收集用户交互历史
            interaction_history = self.collect_interaction_history(user_id, prompt_name)
            
            # 2. 获取当前偏好总结
            current_preference = self.load_current_preference(user_id, prompt_name)
            
            # 3. 构建LLM分析提示词
            analysis_prompt = self.preference_prompt_template.format(
                prompt_name=prompt_name,
                interaction_history=self.format_interaction_history(interaction_history),
                user_feedback=self.format_user_feedback(interaction_data),
                current_preference_summary=current_preference.get('summary', '暂无偏好记录')
            )
            
            # 4. 调用LLM进行偏好分析
            messages = self.bedrock_client.format_messages(analysis_prompt)
            llm_response = self.bedrock_client.converse(
                model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
                messages=messages,
                system_prompt="你是一个专业的用户偏好分析专家，擅长从用户行为中总结个性化需求。",
                max_tokens=2000,
                temperature=0.3
            )
            
            # 5. 解析LLM响应
            preference_analysis = self.parse_llm_response(llm_response)
            
            # 6. 保存偏好更新
            self.save_preference_update(user_id, prompt_name, {
                'analysis': preference_analysis,
                'update_timestamp': datetime.now().isoformat(),
                'interaction_data': interaction_data
            })
            
            logger.info(f"偏好分析完成: {user_id}/{prompt_name}")
            return {
                'success': True,
                'preference_analysis': preference_analysis,
                'update_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"偏好分析失败: {user_id}/{prompt_name}, 错误: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def collect_interaction_history(self, user_id: str, prompt_name: str) -> List[Dict]:
        """
        收集用户交互历史 / Collect user interaction history
        
        Args:
            user_id: 用户ID / User ID
            prompt_name: 提示词名称 / Prompt name
            
        Returns:
            交互历史列表 / Interaction history list
        """
        try:
            # 这里返回模拟数据，实际实现中会从存储中获取
            # 当前版本专注于基础框架
            return [
                {
                    "timestamp": datetime.now().isoformat(),
                    "modification_type": "content_addition",
                    "user_request": "添加更多技术细节",
                    "satisfaction_score": 0.8
                }
            ]
            
        except Exception as e:
            logger.error(f"收集交互历史失败: {user_id}/{prompt_name}, 错误: {e}")
            return []
    
    def load_current_preference(self, user_id: str, prompt_name: str) -> Dict[str, Any]:
        """
        加载当前偏好 / Load current preference
        
        Args:
            user_id: 用户ID / User ID
            prompt_name: 提示词名称 / Prompt name
            
        Returns:
            当前偏好信息 / Current preference info
        """
        try:
            # 这里返回默认偏好，实际实现中会从存储中加载
            return {
                'summary': '用户偏好专业、详细的技术说明',
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"加载当前偏好失败: {user_id}/{prompt_name}, 错误: {e}")
            return {}
    
    def format_interaction_history(self, history: List[Dict]) -> str:
        """
        格式化交互历史 / Format interaction history
        
        Args:
            history: 交互历史列表 / Interaction history list
            
        Returns:
            格式化的历史文本 / Formatted history text
        """
        try:
            if not history:
                return "暂无交互历史"
            
            formatted_lines = []
            for item in history[-10:]:  # 最近10条记录
                formatted_lines.append(
                    f"- {item.get('timestamp', 'N/A')}: "
                    f"{item.get('modification_type', 'unknown')} - "
                    f"{item.get('user_request', 'N/A')} "
                    f"(满意度: {item.get('satisfaction_score', 0.5)})"
                )
            
            return "\n".join(formatted_lines)
            
        except Exception as e:
            logger.error(f"格式化交互历史失败: {e}")
            return "格式化失败"
    
    def format_user_feedback(self, feedback_data: Dict) -> str:
        """
        格式化用户反馈 / Format user feedback
        
        Args:
            feedback_data: 反馈数据 / Feedback data
            
        Returns:
            格式化的反馈文本 / Formatted feedback text
        """
        try:
            feedback_lines = []
            
            if 'satisfaction_score' in feedback_data:
                feedback_lines.append(f"满意度评分: {feedback_data['satisfaction_score']}")
            
            if 'modification_success' in feedback_data:
                feedback_lines.append(f"修改成功: {feedback_data['modification_success']}")
            
            if 'user_comments' in feedback_data:
                feedback_lines.append(f"用户评论: {feedback_data['user_comments']}")
            
            if 'preferred_style' in feedback_data:
                feedback_lines.append(f"偏好风格: {feedback_data['preferred_style']}")
            
            return "\n".join(feedback_lines) if feedback_lines else "暂无反馈信息"
            
        except Exception as e:
            logger.error(f"格式化用户反馈失败: {e}")
            return "格式化失败"
    
    def parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        解析LLM响应 / Parse LLM response
        
        Args:
            response: LLM响应内容 / LLM response content
            
        Returns:
            解析后的偏好分析 / Parsed preference analysis
        """
        try:
            # 尝试解析JSON格式的响应
            if '{' in response and '}' in response:
                # 提取JSON部分
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                json_str = response[start_idx:end_idx]
                
                parsed_data = json.loads(json_str)
                return parsed_data
            
            # 如果不是JSON格式，返回基础解析
            return {
                'preference_analysis': {
                    'raw_response': response,
                    'parsed_at': datetime.now().isoformat()
                },
                'personalized_prompt': response[:500] + "..." if len(response) > 500 else response
            }
            
        except Exception as e:
            logger.error(f"解析LLM响应失败: {e}")
            return {
                'preference_analysis': {
                    'error': str(e),
                    'raw_response': response
                },
                'personalized_prompt': "解析失败，使用默认提示词"
            }
    
    def save_preference_update(self, user_id: str, prompt_name: str, 
                                   preference_data: Dict) -> bool:
        """
        保存偏好更新 / Save preference update
        
        Args:
            user_id: 用户ID / User ID
            prompt_name: 提示词名称 / Prompt name
            preference_data: 偏好数据 / Preference data
            
        Returns:
            保存是否成功 / Whether save was successful
        """
        try:
            # 这里是基础实现，实际中会保存到文件或数据库
            logger.info(f"保存偏好更新: {user_id}/{prompt_name}")
            return True
            
        except Exception as e:
            logger.error(f"保存偏好更新失败: {user_id}/{prompt_name}, 错误: {e}")
            return False
    
    def get_preference_learning_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        获取偏好学习统计信息 / Get preference learning statistics
        
        Args:
            user_id: 用户ID / User ID
            
        Returns:
            统计信息 / Statistics information
        """
        try:
            # 基础统计信息
            return {
                'total_analyses': 0,
                'successful_analyses': 0,
                'last_analysis': None,
                'active_prompts': [],
                'learning_confidence': 0.0
            }
            
        except Exception as e:
            logger.error(f"获取偏好学习统计失败: {user_id}, 错误: {e}")
            return {}