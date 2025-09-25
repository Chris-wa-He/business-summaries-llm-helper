"""
增强的系统提示词管理器 / Enhanced System Prompt Manager

该模块扩展现有的系统提示词管理器，集成个性化功能。
This module extends the existing system prompt manager with personalized functionality.
"""

import logging
from typing import Optional, Dict, Any
from src.services.system_prompt_manager import SystemPromptManager
from src.services.personalized_prompt_manager import PersonalizedPromptManager
from src.services.llm_preference_learning import LLMBasedPreferenceLearning


class EnhancedSystemPromptManager:
    """增强的系统提示词管理器，集成个性化功能 / Enhanced System Prompt Manager with personalized functionality"""
    
    def __init__(self, config_manager, history_processor, bedrock_client):
        """
        初始化增强的系统提示词管理器
        Initialize enhanced system prompt manager
        
        Args:
            config_manager: 配置管理器 / Configuration manager
            history_processor: 历史处理器 / History processor
            bedrock_client: Bedrock客户端 / Bedrock client
        """
        self.base_manager = SystemPromptManager(config_manager, history_processor)
        self.personalized_manager = PersonalizedPromptManager()
        self.llm_learning = LLMBasedPreferenceLearning(bedrock_client)
        
    def get_effective_prompt(self, user_id: str, prompt_name: str) -> str:
        """
        获取有效的提示词（优先使用个性化版本）/ Get effective prompt (prioritize personalized version)
        
        Args:
            user_id: 用户ID / User ID
            prompt_name: 提示词名称 / Prompt name
            
        Returns:
            str: 有效的提示词内容 / Effective prompt content
        """
        try:
            # 1. 尝试加载个性化prompt
            personalized_prompt = self.personalized_manager.load_personalized_prompt(
                user_id, prompt_name
            )
            
            if personalized_prompt:
                logging.info(f"Using personalized prompt for {user_id}/{prompt_name}")
                return personalized_prompt
            
            # 2. 回退到基础系统提示词
            base_prompt = self.base_manager.get_prompt(prompt_name)
            if base_prompt:
                logging.info(f"Using base prompt for {prompt_name}")
                return base_prompt
            
            # 3. 使用默认提示词
            default_prompt = self.base_manager.get_active_prompt()
            if default_prompt:
                return default_prompt.get('content', '')
            
            return ""
            
        except Exception as e:
            logging.error(f"Failed to get effective prompt: {e}")
            # 出错时回退到基础提示词
            return self.base_manager.get_prompt(prompt_name) or ""
    
    async def update_preference_from_feedback(self, user_id: str, prompt_name: str, 
                                           feedback_data: Dict[str, Any]) -> bool:
        """
        根据用户反馈更新偏好 / Update preference based on user feedback
        
        Args:
            user_id: 用户ID / User ID
            prompt_name: 提示词名称 / Prompt name
            feedback_data: 反馈数据 / Feedback data
            
        Returns:
            bool: 更新是否成功 / Whether update was successful
        """
        try:
            # 调用LLM进行偏好分析和prompt生成
            result = await self.llm_learning.analyze_and_update_preference(
                user_id, prompt_name, feedback_data
            )
            
            if result['success']:
                logging.info(f"Updated personalized prompt for {user_id}/{prompt_name}")
                return True
            else:
                logging.error(f"Failed to update personalized prompt: {result.get('error')}")
                return False
                
        except Exception as e:
            logging.error(f"Error updating preference from feedback: {e}")
            return False
    
    def get_user_prompt_versions(self, user_id: str, prompt_name: str) -> list:
        """
        获取用户的个性化prompt版本列表 / Get user's personalized prompt version list
        
        Args:
            user_id: 用户ID / User ID
            prompt_name: 提示词名称 / Prompt name
            
        Returns:
            list: 版本信息列表 / Version information list
        """
        return self.personalized_manager.get_prompt_versions(user_id, prompt_name)
    
    def activate_user_prompt_version(self, user_id: str, prompt_name: str, version: str) -> bool:
        """
        激活用户的特定prompt版本 / Activate user's specific prompt version
        
        Args:
            user_id: 用户ID / User ID
            prompt_name: 提示词名称 / Prompt name
            version: 版本号 / Version number
            
        Returns:
            bool: 激活是否成功 / Whether activation was successful
        """
        return self.personalized_manager.activate_prompt_version(user_id, prompt_name, version)
    
    def has_personalized_prompt(self, user_id: str, prompt_name: str) -> bool:
        """
        检查用户是否有个性化prompt / Check if user has personalized prompt
        
        Args:
            user_id: 用户ID / User ID
            prompt_name: 提示词名称 / Prompt name
            
        Returns:
            bool: 是否存在个性化prompt / Whether personalized prompt exists
        """
        try:
            versions = self.personalized_manager.get_prompt_versions(user_id, prompt_name)
            return len(versions) > 0
        except Exception:
            return False
    
    # 代理基础管理器的方法 / Delegate base manager methods
    def create_prompt(self, name: str, content: str) -> bool:
        """创建基础提示词 / Create base prompt"""
        return self.base_manager.create_prompt(name, content)
    
    def get_prompt(self, name: str) -> Optional[str]:
        """获取基础提示词 / Get base prompt"""
        return self.base_manager.get_prompt(name)
    
    def update_prompt(self, name: str, content: str) -> bool:
        """更新基础提示词 / Update base prompt"""
        return self.base_manager.update_prompt(name, content)
    
    def delete_prompt(self, name: str) -> bool:
        """删除基础提示词 / Delete base prompt"""
        return self.base_manager.delete_prompt(name)
    
    def list_prompts(self) -> list:
        """列出所有基础提示词 / List all base prompts"""
        return self.base_manager.list_prompts()
    
    def set_active_prompt(self, name: str) -> bool:
        """设置激活的基础提示词 / Set active base prompt"""
        return self.base_manager.set_active_prompt(name)
    
    def get_active_prompt(self) -> Optional[Dict[str, str]]:
        """获取当前激活的基础提示词 / Get current active base prompt"""
        return self.base_manager.get_active_prompt()
    
    def get_prompt_history_folder(self, name: str) -> str:
        """获取提示词对应的历史文件夹 / Get prompt's corresponding history folder"""
        return self.base_manager.get_prompt_history_folder(name)