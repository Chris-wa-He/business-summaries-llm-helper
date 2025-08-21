"""
应用控制器 / Application Controller

整合所有组件，提供统一的业务逻辑接口
Integrate all components and provide unified business logic interface
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from src.config.config_manager import ConfigManager, ConfigurationError, AWSCredentialsError
from src.processors.history_processor import HistoryProcessor, HistoryProcessingError
from src.services.prompt_builder import PromptBuilder
from src.clients.bedrock_client import BedrockClient, ModelInvocationError
from src.services.model_manager import ModelManager


class CaseSummaryError(Exception):
    """案例总结应用基础异常 / Base exception for case summary app"""
    pass


class AppController:
    """应用控制器 / Application Controller"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化应用控制器 / Initialize application controller
        
        Args:
            config_path: 配置文件路径 / Configuration file path
        """
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件 / Initialize components
        self.config_manager = ConfigManager(config_path)
        self.history_processor = None
        self.prompt_builder = PromptBuilder()
        self.bedrock_client = None
        self.model_manager = None
        
        # 应用状态 / Application state
        self.is_initialized = False
        self.available_models = {}
        
        # 初始化应用 / Initialize application
        self._initialize_app()
    
    def _initialize_app(self):
        """初始化应用 / Initialize application"""
        try:
            self.logger.info("开始初始化应用 / Starting application initialization")
            
            # 加载配置 / Load configuration
            self.config_manager.load_config()
            
            # 验证AWS凭证 / Validate AWS credentials
            self.config_manager.validate_aws_credentials()
            
            # 初始化历史处理器 / Initialize history processor
            history_folder = self.config_manager.get_history_folder()
            self.history_processor = HistoryProcessor(history_folder)
            
            # 初始化Bedrock客户端 / Initialize Bedrock client
            session = self.config_manager.get_boto3_session()
            self.bedrock_client = BedrockClient(session)
            
            # 初始化模型管理器 / Initialize model manager
            config_data = self.config_manager.config_data
            self.model_manager = ModelManager(self.bedrock_client, config_data)
            
            self.is_initialized = True
            self.logger.info("应用初始化成功 / Application initialized successfully")
            
        except Exception as e:
            self.logger.error(f"应用初始化失败: {e} / Application initialization failed: {e}")
            raise CaseSummaryError(f"应用初始化失败: {e} / Application initialization failed: {e}")
    
    def initialize_models(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        初始化并获取可用模型 / Initialize and get available models
        
        Returns:
            可用模型字典 / Available models dictionary
            
        Raises:
            CaseSummaryError: 模型初始化失败 / Model initialization failed
        """
        if not self.is_initialized:
            raise CaseSummaryError("应用未初始化 / Application not initialized")
        
        try:
            self.logger.info("开始初始化模型列表 / Starting model list initialization")
            
            # 刷新可用模型 / Refresh available models
            self.available_models = self.model_manager.refresh_available_models()
            
            self.logger.info(f"模型初始化完成，共 {sum(len(models) for models in self.available_models.values())} 个模型 / Model initialization completed, {sum(len(models) for models in self.available_models.values())} models total")
            
            return self.available_models
            
        except Exception as e:
            self.logger.error(f"模型初始化失败: {e} / Model initialization failed: {e}")
            raise CaseSummaryError(f"模型初始化失败: {e} / Model initialization failed: {e}")
    
    def process_case_summary(self, 
                           case_input: str, 
                           model_id: str, 
                           custom_system_prompt: Optional[str] = None) -> str:
        """
        处理案例总结请求 / Process case summary request
        
        Args:
            case_input: 案例输入内容 / Case input content
            model_id: 模型ID / Model ID
            custom_system_prompt: 自定义系统提示词 / Custom system prompt
            
        Returns:
            生成的案例总结 / Generated case summary
            
        Raises:
            CaseSummaryError: 处理失败 / Processing failed
        """
        if not self.is_initialized:
            raise CaseSummaryError("应用未初始化 / Application not initialized")
        
        try:
            self.logger.info(f"开始处理案例总结，模型: {model_id} / Starting case summary processing, model: {model_id}")
            
            # 验证输入 / Validate input
            if not self.validate_input(case_input):
                raise CaseSummaryError("输入验证失败 / Input validation failed")
            
            # 验证模型可用性 / Validate model availability
            if not self.model_manager.is_model_available(model_id):
                raise CaseSummaryError(f"模型不可用: {model_id} / Model not available: {model_id}")
            
            # 加载历史参考信息 / Load history reference information
            history_reference = self._load_history_reference(case_input)
            
            # 获取系统提示词 / Get system prompt
            system_prompt = custom_system_prompt or self.config_manager.get_system_prompt()
            
            # 构建提示词 / Build prompt
            user_prompt = self.prompt_builder.build_prompt(
                case_input=case_input,
                history_reference=history_reference,
                system_prompt=system_prompt
            )
            
            # 调用模型生成总结 / Call model to generate summary
            summary = self._generate_summary(model_id, user_prompt, system_prompt)
            
            self.logger.info("案例总结生成成功 / Case summary generated successfully")
            return summary
            
        except Exception as e:
            self.logger.error(f"案例总结处理失败: {e} / Case summary processing failed: {e}")
            raise CaseSummaryError(f"案例总结处理失败: {e} / Case summary processing failed: {e}")
    
    def validate_input(self, case_input: str) -> bool:
        """
        验证输入内容 / Validate input content
        
        Args:
            case_input: 案例输入 / Case input
            
        Returns:
            验证结果 / Validation result
        """
        if not case_input or not case_input.strip():
            self.logger.error("案例输入不能为空 / Case input cannot be empty")
            return False
        
        if len(case_input.strip()) < 5:
            self.logger.warning("案例输入内容过短 / Case input content too short")
            return False
        
        return True
    
    def refresh_models(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        刷新模型列表 / Refresh models list
        
        Returns:
            刷新后的模型字典 / Refreshed models dictionary
        """
        if not self.is_initialized:
            raise CaseSummaryError("应用未初始化 / Application not initialized")
        
        try:
            self.available_models = self.model_manager.refresh_available_models()
            self.logger.info("模型列表刷新成功 / Model list refreshed successfully")
            return self.available_models
        except Exception as e:
            self.logger.error(f"模型列表刷新失败: {e} / Model list refresh failed: {e}")
            raise CaseSummaryError(f"模型列表刷新失败: {e} / Model list refresh failed: {e}")
    
    def get_models_for_ui(self) -> List[Dict[str, str]]:
        """
        获取用于UI显示的模型列表 / Get model list for UI display
        
        Returns:
            UI模型列表 / UI model list
        """
        if not self.is_initialized:
            return []
        
        try:
            return self.model_manager.get_models_for_ui()
        except Exception as e:
            self.logger.error(f"获取UI模型列表失败: {e} / Failed to get UI model list: {e}")
            return []
    
    def get_default_model(self) -> str:
        """
        获取默认模型ID / Get default model ID
        
        Returns:
            默认模型ID / Default model ID
        """
        if not self.is_initialized:
            return 'anthropic.claude-3-5-sonnet-20241022-v2:0'
        
        try:
            return self.model_manager.get_default_model()
        except Exception as e:
            self.logger.error(f"获取默认模型失败: {e} / Failed to get default model: {e}")
            return 'anthropic.claude-3-5-sonnet-20241022-v2:0'
    
    def get_app_config(self) -> Dict[str, Any]:
        """
        获取应用配置 / Get application configuration
        
        Returns:
            应用配置字典 / Application configuration dictionary
        """
        if not self.is_initialized:
            return {
                'title': '案例总结生成器 / Case Summary Generator',
                'max_tokens': 4000,
                'temperature': 0.7
            }
        
        return self.config_manager.get_app_config()
    
    def _load_history_reference(self, case_input: str) -> str:
        """
        加载历史参考信息 / Load history reference information
        
        Args:
            case_input: 案例输入 / Case input
            
        Returns:
            历史参考信息 / History reference information
        """
        try:
            # 加载历史文件 / Load history files
            history_files = self.history_processor.load_history_files()
            
            if not history_files:
                self.logger.info("未找到历史参考文件 / No history reference files found")
                return ""
            
            # 处理历史内容 / Process history content
            history_content = self.history_processor.process_history_content(history_files)
            
            # 筛选相关历史信息 / Filter relevant history information
            relevant_history = self.history_processor.filter_relevant_history(case_input, history_content)
            
            return relevant_history
            
        except HistoryProcessingError as e:
            self.logger.warning(f"历史信息处理失败: {e} / History processing failed: {e}")
            return ""
        except Exception as e:
            self.logger.error(f"加载历史参考信息失败: {e} / Failed to load history reference: {e}")
            return ""
    
    def _generate_summary(self, model_id: str, user_prompt: str, system_prompt: str) -> str:
        """
        生成案例总结 / Generate case summary
        
        Args:
            model_id: 模型ID / Model ID
            user_prompt: 用户提示词 / User prompt
            system_prompt: 系统提示词 / System prompt
            
        Returns:
            生成的总结 / Generated summary
        """
        try:
            # 获取应用配置 / Get app configuration
            app_config = self.get_app_config()
            
            # 格式化消息 / Format messages
            messages = self.bedrock_client.format_messages(user_prompt)
            
            # 调用模型 / Call model
            summary = self.bedrock_client.converse(
                model_id=model_id,
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=app_config.get('max_tokens', 4000),
                temperature=app_config.get('temperature', 0.7)
            )
            
            return summary
            
        except ModelInvocationError as e:
            raise CaseSummaryError(f"模型调用失败: {e} / Model invocation failed: {e}")
        except Exception as e:
            raise CaseSummaryError(f"生成总结失败: {e} / Summary generation failed: {e}")
    
    def get_initialization_status(self) -> Tuple[bool, str]:
        """
        获取初始化状态 / Get initialization status
        
        Returns:
            (是否初始化成功, 状态信息) / (Whether initialized successfully, status message)
        """
        if self.is_initialized:
            return True, "应用初始化成功 / Application initialized successfully"
        else:
            return False, "应用未初始化或初始化失败 / Application not initialized or initialization failed"
