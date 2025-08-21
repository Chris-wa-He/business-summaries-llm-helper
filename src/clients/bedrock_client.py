"""
AWS Bedrock客户端 / AWS Bedrock Client

负责与AWS Bedrock服务进行交互
Responsible for interacting with AWS Bedrock service
"""

import json
import logging
from typing import Dict, List, Any, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class ModelInvocationError(Exception):
    """模型调用错误 / Model invocation error"""
    pass


class BedrockClient:
    """AWS Bedrock客户端 / AWS Bedrock Client"""
    
    def __init__(self, session: boto3.Session):
        """
        初始化Bedrock客户端 / Initialize Bedrock client
        
        Args:
            session: boto3会话对象 / boto3 session object
        """
        self.session = session
        self.logger = logging.getLogger(__name__)
        self.bedrock_client = None
        self.bedrock_runtime_client = None
        self._initialize_clients()
        
        # 支持的模型提供商 / Supported model providers
        self.supported_providers = {
            'anthropic',  # Claude系列
            'amazon',     # Nova系列
            'deepseek',   # DeepSeek系列
            'openai'      # OpenAI系列
        }
    
    def _initialize_clients(self):
        """初始化Bedrock客户端 / Initialize Bedrock clients"""
        try:
            self.bedrock_client = self.session.client('bedrock')
            self.bedrock_runtime_client = self.session.client('bedrock-runtime')
            self.logger.info("Bedrock客户端初始化成功 / Bedrock clients initialized successfully")
        except Exception as e:
            self.logger.error(f"Bedrock客户端初始化失败: {e} / Failed to initialize Bedrock clients: {e}")
            raise ModelInvocationError(f"无法初始化Bedrock客户端: {e} / Cannot initialize Bedrock client: {e}")
    
    def list_foundation_models(self) -> List[Dict[str, Any]]:
        """
        通过API获取可用的基础模型列表 / Get available foundation models via API
        
        Returns:
            模型列表 / List of models
            
        Raises:
            ModelInvocationError: 获取模型列表失败 / Failed to get model list
        """
        try:
            response = self.bedrock_client.list_foundation_models()
            models = response.get('modelSummaries', [])
            
            # 获取inference profiles / Get inference profiles
            inference_profiles = {}
            try:
                profiles_response = self.bedrock_client.list_inference_profiles()
                profiles = profiles_response.get('inferenceProfileSummaries', [])
                for profile in profiles:
                    profile_models = profile.get('models', [])
                    for model in profile_models:
                        model_arn = model.get('modelArn', '')
                        # 从ARN中提取模型ID
                        if '::foundation-model/' in model_arn:
                            model_id = model_arn.split('::foundation-model/')[-1]
                            inference_profiles[model_id] = profile.get('inferenceProfileId', '')
            except Exception as e:
                self.logger.warning(f"获取inference profiles失败: {e} / Failed to get inference profiles: {e}")
            
            # 筛选支持的模型 / Filter supported models
            supported_models = []
            for model in models:
                model_id = model.get('modelId', '')
                if self.is_supported_model(model_id):
                    # 检查模型是否支持ON_DEMAND或INFERENCE_PROFILE
                    inference_types = model.get('inferenceTypesSupported', [])
                    if 'ON_DEMAND' in inference_types or 'INFERENCE_PROFILE' in inference_types:
                        # 如果有inference profile，优先使用inference profile ID
                        if model_id in inference_profiles:
                            model_copy = model.copy()
                            model_copy['originalModelId'] = model_id
                            model_copy['modelId'] = inference_profiles[model_id]
                            model_copy['useInferenceProfile'] = True
                            supported_models.append(model_copy)
                        else:
                            model['useInferenceProfile'] = False
                            supported_models.append(model)
                    else:
                        self.logger.debug(f"跳过不支持的推理类型的模型: {model_id} / Skipping model with unsupported inference types: {model_id}")
            
            self.logger.info(f"获取到 {len(supported_models)} 个支持的模型 / Retrieved {len(supported_models)} supported models")
            return supported_models
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            self.logger.error(f"获取模型列表失败 - AWS错误: {error_code} / Failed to get model list - AWS error: {error_code}")
            raise ModelInvocationError(f"AWS API错误: {error_code} / AWS API error: {error_code}")
        except Exception as e:
            self.logger.error(f"获取模型列表失败: {e} / Failed to get model list: {e}")
            raise ModelInvocationError(f"获取模型列表失败: {e} / Failed to get model list: {e}")
    
    def get_inference_profile_for_model(self, model_id: str) -> Optional[str]:
        """
        获取模型的推理配置文件ID / Get inference profile ID for model
        
        Args:
            model_id: 模型ID / Model ID
            
        Returns:
            推理配置文件ID或None / Inference profile ID or None
        """
        try:
            # 获取推理配置文件列表 / Get inference profiles list
            response = self.bedrock_client.list_inference_profiles()
            profiles = response.get('inferenceProfileSummaries', [])
            
            # 查找包含指定模型的推理配置文件 / Find inference profile containing the specified model
            for profile in profiles:
                profile_id = profile.get('inferenceProfileId', '')
                models = profile.get('models', [])
                
                # 检查是否有匹配的模型 / Check if there's a matching model
                for model in models:
                    model_arn = model.get('modelArn', '')
                    if model_id in model_arn:
                        self.logger.info(f"找到模型 {model_id} 的推理配置文件: {profile_id} / Found inference profile for model {model_id}: {profile_id}")
                        return profile_id
            
            self.logger.warning(f"未找到模型 {model_id} 的推理配置文件 / No inference profile found for model {model_id}")
            return None
            
        except Exception as e:
            self.logger.warning(f"获取推理配置文件失败: {e} / Failed to get inference profiles: {e}")
            return None
    
    def filter_models_by_provider(self, models: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        按指定的四类提供商筛选模型 / Filter models by the four specified providers
        
        Args:
            models: 模型列表 / List of models
            
        Returns:
            按提供商分类的模型字典 / Dictionary of models categorized by provider
        """
        categorized_models = {
            'claude': [],
            'nova': [],
            'deepseek': [],
            'openai': []
        }
        
        for model in models:
            model_id = model.get('modelId', '').lower()
            
            if 'anthropic.claude' in model_id:
                categorized_models['claude'].append(model)
            elif 'amazon.nova' in model_id:
                categorized_models['nova'].append(model)
            elif 'deepseek' in model_id:
                categorized_models['deepseek'].append(model)
            elif 'openai' in model_id:
                categorized_models['openai'].append(model)
        
        return categorized_models
    
    def is_supported_model(self, model_id: str) -> bool:
        """
        检查模型是否属于支持的四类 / Check if model belongs to supported four types
        
        Args:
            model_id: 模型ID / Model ID
            
        Returns:
            是否支持 / Whether supported
        """
        model_id_lower = model_id.lower()
        
        # 检查是否属于支持的四类模型 / Check if belongs to supported four model types
        supported_patterns = [
            'anthropic.claude',  # Claude系列
            'amazon.nova',       # Nova系列
            'deepseek',          # DeepSeek系列
            'openai'             # OpenAI系列
        ]
        
        return any(pattern in model_id_lower for pattern in supported_patterns)
    
    def get_model_display_name(self, model_id: str) -> str:
        """
        获取模型的显示名称 / Get model display name
        
        Args:
            model_id: 模型ID或推理配置文件ID / Model ID or inference profile ID
            
        Returns:
            显示名称 / Display name
        """
        # 如果是inference profile ID，提取原始模型ID
        original_model_id = model_id
        if model_id.startswith('us.'):
            # 从inference profile ID中提取模型ID
            # 例如: us.anthropic.claude-3-7-sonnet-20250219-v1:0 -> anthropic.claude-3-7-sonnet-20250219-v1:0
            original_model_id = model_id[3:]  # 去掉 'us.' 前缀
        
        model_id_lower = original_model_id.lower()
        
        # Claude系列 - 使用更智能的模式匹配 / Claude series - using smarter pattern matching
        if 'anthropic.claude' in model_id_lower:
            return self._get_claude_display_name(original_model_id)
        
        # Nova系列 / Nova series
        elif 'amazon.nova' in model_id_lower:
            return self._get_nova_display_name(original_model_id)
        
        # DeepSeek系列 / DeepSeek series
        elif 'deepseek' in model_id_lower:
            return self._get_deepseek_display_name(original_model_id)
        
        # OpenAI系列 / OpenAI series
        elif 'openai' in model_id_lower:
            return self._get_openai_display_name(original_model_id)
        
        # 其他模型，尝试从模型ID中提取友好名称 / Other models, try to extract friendly name from model ID
        return self._extract_friendly_name(original_model_id)
    
    def _get_claude_display_name(self, model_id: str) -> str:
        """获取Claude模型的显示名称 / Get Claude model display name"""
        model_id_lower = model_id.lower()
        
        # 具体版本匹配 / Specific version matching
        if 'claude-3-sonnet-20240229' in model_id_lower:
            if ':28k' in model_id_lower:
                return "Claude 3 Sonnet (28K)"
            elif ':200k' in model_id_lower:
                return "Claude 3 Sonnet (200K)"
            else:
                return "Claude 3 Sonnet"
        elif 'claude-3-haiku-20240307' in model_id_lower:
            if ':48k' in model_id_lower:
                return "Claude 3 Haiku (48K)"
            elif ':200k' in model_id_lower:
                return "Claude 3 Haiku (200K)"
            else:
                return "Claude 3 Haiku"
        elif 'claude-3-opus-20240229' in model_id_lower:
            if ':12k' in model_id_lower:
                return "Claude 3 Opus (12K)"
            elif ':28k' in model_id_lower:
                return "Claude 3 Opus (28K)"
            elif ':200k' in model_id_lower:
                return "Claude 3 Opus (200K)"
            else:
                return "Claude 3 Opus"
        elif 'claude-3-5-sonnet-20240620' in model_id_lower:
            return "Claude 3.5 Sonnet (June)"
        elif 'claude-3-5-sonnet-20241022' in model_id_lower:
            return "Claude 3.5 Sonnet (Oct)"
        elif 'claude-3-5-haiku' in model_id_lower:
            return "Claude 3.5 Haiku"
        elif 'claude-3-7-sonnet' in model_id_lower:
            return "Claude 3.7 Sonnet"
        elif 'claude-opus-4-1' in model_id_lower:
            return "Claude Opus 4.1"
        elif 'claude-opus-4' in model_id_lower:
            return "Claude Opus 4"
        elif 'claude-sonnet-4' in model_id_lower:
            return "Claude Sonnet 4"
        elif 'claude-instant' in model_id_lower:
            if ':100k' in model_id_lower:
                return "Claude Instant (100K)"
            else:
                return "Claude Instant"
        elif 'claude-v2' in model_id_lower:
            if ':1:200k' in model_id_lower:
                return "Claude v2.1 (200K)"
            elif ':1:18k' in model_id_lower:
                return "Claude v2.1 (18K)"
            elif ':1' in model_id_lower and model_id_lower.endswith(':1'):
                return "Claude v2.1"
            elif ':0:100k' in model_id_lower:
                return "Claude v2.0 (100K)"
            elif ':0:18k' in model_id_lower:
                return "Claude v2.0 (18K)"
            elif model_id_lower.endswith('claude-v2'):
                return "Claude v2.0"
            else:
                return "Claude v2"
        
        # 通用Claude模式匹配 / Generic Claude pattern matching
        elif 'claude-5' in model_id_lower:
            return "Claude 5"
        elif 'claude-4' in model_id_lower:
            if 'sonnet' in model_id_lower:
                return "Claude 4 Sonnet"
            elif 'haiku' in model_id_lower:
                return "Claude 4 Haiku"
            elif 'opus' in model_id_lower:
                return "Claude 4 Opus"
            else:
                return "Claude 4"
        elif 'claude-3' in model_id_lower:
            if 'sonnet' in model_id_lower:
                return "Claude 3 Sonnet"
            elif 'haiku' in model_id_lower:
                return "Claude 3 Haiku"
            elif 'opus' in model_id_lower:
                return "Claude 3 Opus"
            else:
                return "Claude 3"
        
        # 默认Claude名称 / Default Claude name
        return "Claude"
    
    def _get_nova_display_name(self, model_id: str) -> str:
        """获取Nova模型的显示名称 / Get Nova model display name"""
        model_id_lower = model_id.lower()
        
        if 'nova-pro' in model_id_lower:
            if ':24k' in model_id_lower:
                return "Nova Pro (24K)"
            elif ':300k' in model_id_lower:
                return "Nova Pro (300K)"
            else:
                return "Nova Pro"
        elif 'nova-lite' in model_id_lower:
            if ':24k' in model_id_lower:
                return "Nova Lite (24K)"
            elif ':300k' in model_id_lower:
                return "Nova Lite (300K)"
            else:
                return "Nova Lite"
        elif 'nova-micro' in model_id_lower:
            if ':24k' in model_id_lower:
                return "Nova Micro (24K)"
            elif ':128k' in model_id_lower:
                return "Nova Micro (128K)"
            else:
                return "Nova Micro"
        elif 'nova-premier' in model_id_lower:
            if ':8k' in model_id_lower:
                return "Nova Premier (8K)"
            elif ':20k' in model_id_lower:
                return "Nova Premier (20K)"
            elif ':1000k' in model_id_lower:
                return "Nova Premier (1000K)"
            elif ':mm' in model_id_lower:
                return "Nova Premier (MM)"
            else:
                return "Nova Premier"
        elif 'nova-canvas' in model_id_lower:
            return "Nova Canvas (Image)"
        elif 'nova-reel' in model_id_lower:
            if 'v1:1' in model_id_lower:
                return "Nova Reel v1.1 (Video)"
            else:
                return "Nova Reel (Video)"
        elif 'nova-sonic' in model_id_lower:
            return "Nova Sonic (Audio)"
        
        # 通用Nova模式匹配 / Generic Nova pattern matching
        return "Nova " + model_id_lower.split('nova-')[-1].split(':')[0].title()
    
    def _get_deepseek_display_name(self, model_id: str) -> str:
        """获取DeepSeek模型的显示名称 / Get DeepSeek model display name"""
        model_id_lower = model_id.lower()
        
        if 'v2.5' in model_id_lower:
            return "DeepSeek V2.5"
        elif 'v3' in model_id_lower:
            return "DeepSeek V3"
        elif 'r1' in model_id_lower:
            return "DeepSeek R1"
        elif 'r2' in model_id_lower:
            return "DeepSeek R2"
        
        # 通用DeepSeek模式匹配 / Generic DeepSeek pattern matching
        return "DeepSeek"
    
    def _get_openai_display_name(self, model_id: str) -> str:
        """获取OpenAI模型的显示名称 / Get OpenAI model display name"""
        model_id_lower = model_id.lower()
        
        if 'gpt-4o' in model_id_lower:
            return "GPT-4o"
        elif 'gpt-4' in model_id_lower:
            return "GPT-4"
        elif 'gpt-5' in model_id_lower:
            return "GPT-5"
        
        # 通用OpenAI模式匹配 / Generic OpenAI pattern matching
        return "GPT"
    
    def _extract_friendly_name(self, model_id: str) -> str:
        """从模型ID中提取友好名称 / Extract friendly name from model ID"""
        # 移除提供商前缀 / Remove provider prefix
        parts = model_id.split('.')
        if len(parts) > 1:
            name_part = parts[-1]
            # 移除版本后缀 / Remove version suffix
            name_part = name_part.split(':')[0]
            # 转换为标题格式 / Convert to title case
            return name_part.replace('-', ' ').title()
        
        return model_id
    
    def converse(self, 
                model_id: str, 
                messages: List[Dict[str, Any]], 
                system_prompt: Optional[str] = None,
                max_tokens: int = 4000,
                temperature: float = 0.7) -> str:
        """
        使用Converse API调用模型 / Use Converse API to invoke model
        
        Args:
            model_id: 模型ID或推理配置文件ID / Model ID or inference profile ID
            messages: 消息列表 / Message list
            system_prompt: 系统提示词 / System prompt
            max_tokens: 最大token数 / Maximum tokens
            temperature: 温度参数 / Temperature parameter
            
        Returns:
            模型响应内容 / Model response content
            
        Raises:
            ModelInvocationError: 模型调用失败 / Model invocation failed
        """
        try:
            # 构建请求参数 / Build request parameters
            request_params = {
                'modelId': model_id,
                'messages': messages,
                'inferenceConfig': {
                    'maxTokens': max_tokens,
                    'temperature': temperature
                }
            }
            
            # 添加系统提示词 / Add system prompt
            if system_prompt and system_prompt.strip():
                request_params['system'] = [
                    {
                        'text': system_prompt.strip()
                    }
                ]
            
            self.logger.debug(f"调用模型: {model_id} / Invoking model: {model_id}")
            
            # 调用Converse API / Call Converse API
            response = self.bedrock_runtime_client.converse(**request_params)
            return self._parse_converse_response(response)
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            self.logger.error(f"模型调用失败 - AWS错误: {error_code}: {error_message} / Model invocation failed - AWS error: {error_code}: {error_message}")
            raise ModelInvocationError(f"AWS API错误: {error_code} - {error_message} / AWS API error: {error_code} - {error_message}")
        except Exception as e:
            self.logger.error(f"模型调用失败: {e} / Model invocation failed: {e}")
            raise ModelInvocationError(f"模型调用失败: {e} / Model invocation failed: {e}")
    
    def _parse_converse_response(self, response: Dict[str, Any]) -> str:
        """
        解析Converse API响应 / Parse Converse API response
        
        Args:
            response: API响应 / API response
            
        Returns:
            响应文本内容 / Response text content
            
        Raises:
            ModelInvocationError: 响应解析失败 / Response parsing failed
        """
        output = response.get('output', {})
        message = output.get('message', {})
        content = message.get('content', [])
        
        if content and len(content) > 0:
            text_content = content[0].get('text', '')
            self.logger.debug(f"模型响应长度: {len(text_content)} 字符 / Model response length: {len(text_content)} characters")
            return text_content
        else:
            raise ModelInvocationError("模型响应为空 / Model response is empty")
    
    def _get_cross_region_inference_profile(self, model_id: str) -> Optional[str]:
        """
        获取跨区域推理配置文件 / Get cross-region inference profile
        
        Args:
            model_id: 模型ID / Model ID
            
        Returns:
            跨区域推理配置文件ID或None / Cross-region inference profile ID or None
        """
        # 常见的跨区域推理配置文件映射 / Common cross-region inference profile mappings
        cross_region_profiles = {
            'anthropic.claude-3-5-sonnet-20241022-v2:0': 'us.anthropic.claude-3-5-sonnet-20241022-v2:0',
            'anthropic.claude-3-5-sonnet-20240620-v1:0': 'us.anthropic.claude-3-5-sonnet-20240620-v1:0',
            'anthropic.claude-3-5-haiku-20241022-v1:0': 'us.anthropic.claude-3-5-haiku-20241022-v1:0',
            'anthropic.claude-3-opus-20240229-v1:0': 'us.anthropic.claude-3-opus-20240229-v1:0',
            'anthropic.claude-3-sonnet-20240229-v1:0': 'us.anthropic.claude-3-sonnet-20240229-v1:0',
            'anthropic.claude-3-haiku-20240307-v1:0': 'us.anthropic.claude-3-haiku-20240307-v1:0',
            'anthropic.claude-3-7-sonnet-20250219-v1:0': 'us.anthropic.claude-3-7-sonnet-20250219-v1:0',
            'anthropic.claude-opus-4-20250514-v1:0': 'us.anthropic.claude-opus-4-20250514-v1:0',
            'anthropic.claude-sonnet-4-20250514-v1:0': 'us.anthropic.claude-sonnet-4-20250514-v1:0',
            'deepseek.r1-v1:0': 'us.deepseek.r1-v1:0',
            'meta.llama3-1-8b-instruct-v1:0': 'us.meta.llama3-1-8b-instruct-v1:0',
            'meta.llama3-1-70b-instruct-v1:0': 'us.meta.llama3-1-70b-instruct-v1:0',
            'meta.llama3-2-11b-instruct-v1:0': 'us.meta.llama3-2-11b-instruct-v1:0',
            'meta.llama3-2-90b-instruct-v1:0': 'us.meta.llama3-2-90b-instruct-v1:0',
            'meta.llama3-3-70b-instruct-v1:0': 'us.meta.llama3-3-70b-instruct-v1:0'
        }
        
        cross_region_profile = cross_region_profiles.get(model_id)
        if cross_region_profile:
            self.logger.info(f"找到跨区域推理配置文件: {model_id} -> {cross_region_profile} / Found cross-region inference profile: {model_id} -> {cross_region_profile}")
        
        return cross_region_profile
    
    def format_messages(self, user_prompt: str) -> List[Dict[str, Any]]:
        """
        格式化消息为Converse API格式 / Format messages for Converse API
        
        Args:
            user_prompt: 用户提示词 / User prompt
            
        Returns:
            格式化的消息列表 / Formatted message list
        """
        return [
            {
                'role': 'user',
                'content': [
                    {
                        'text': user_prompt
                    }
                ]
            }
        ]
