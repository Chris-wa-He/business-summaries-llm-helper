"""
配置管理器 / Configuration Manager

负责加载、解析和验证应用配置文件
Responsible for loading, parsing and validating application configuration files
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound

# 配置自定义异常 / Configuration custom exceptions
class ConfigurationError(Exception):
    """配置错误 / Configuration error"""
    pass


class AWSCredentialsError(ConfigurationError):
    """AWS凭证错误 / AWS credentials error"""
    pass


class ConfigManager:
    """配置管理器 / Configuration Manager"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器 / Initialize configuration manager
        
        Args:
            config_path: 配置文件路径 / Configuration file path
        """
        self.config_path = config_path or "config.yaml"
        self.config_data: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件 / Load configuration file
        
        Returns:
            配置数据字典 / Configuration data dictionary
            
        Raises:
            ConfigurationError: 配置文件加载或解析失败 / Configuration file loading or parsing failed
        """
        try:
            config_path = Path(self.config_path)
            
            # 如果配置文件不存在，创建默认配置 / If config file doesn't exist, create default config
            if not config_path.exists():
                self.logger.warning(f"配置文件不存在，创建默认配置: {config_path} / Config file not found, creating default config: {config_path}")
                self._create_default_config()
            
            # 读取配置文件 / Read configuration file
            with open(config_path, 'r', encoding='utf-8') as file:
                self.config_data = yaml.safe_load(file) or {}
                
            # 验证配置 / Validate configuration
            self._validate_config()
            
            self.logger.info(f"配置文件加载成功: {config_path} / Configuration loaded successfully: {config_path}")
            return self.config_data
            
        except yaml.YAMLError as e:
            raise ConfigurationError(f"配置文件解析失败 / Configuration file parsing failed: {e}")
        except Exception as e:
            raise ConfigurationError(f"配置文件加载失败 / Configuration file loading failed: {e}")
    
    def get_aws_credentials(self) -> Dict[str, str]:
        """
        获取AWS凭证配置 / Get AWS credentials configuration
        
        Returns:
            AWS凭证字典 / AWS credentials dictionary
        """
        aws_config = self.config_data.get('aws', {})
        
        credentials = {
            'auth_method': aws_config.get('auth_method', 'profile'),
            'region': aws_config.get('region', 'us-east-1')
        }
        
        # 根据认证方式添加相应凭证 / Add appropriate credentials based on auth method
        if credentials['auth_method'] == 'ak_sk':
            credentials.update({
                'access_key_id': aws_config.get('access_key_id', ''),
                'secret_access_key': aws_config.get('secret_access_key', '')
            })
        elif credentials['auth_method'] == 'profile':
            credentials['profile_name'] = aws_config.get('profile_name', 'default')
            
        return credentials
    
    def get_system_prompt(self) -> str:
        """
        获取系统提示词 / Get system prompt
        
        Returns:
            系统提示词字符串 / System prompt string
        """
        return self.config_data.get('system_prompt', self._get_default_system_prompt())
    
    def get_history_folder(self) -> str:
        """
        获取历史参考文件夹路径 / Get history reference folder path
        
        Returns:
            历史文件夹路径 / History folder path
        """
        return self.config_data.get('history_folder', './history_references')
    
    def get_models_config(self) -> Dict[str, List[Dict[str, str]]]:
        """
        获取模型配置 / Get models configuration
        
        Returns:
            模型配置字典 / Models configuration dictionary
        """
        return self.config_data.get('models', self._get_default_models())
    
    def get_app_config(self) -> Dict[str, Any]:
        """
        获取应用配置 / Get application configuration
        
        Returns:
            应用配置字典 / Application configuration dictionary
        """
        default_app_config = {
            'title': '案例总结生成器 / Case Summary Generator',
            'max_tokens': 4000,
            'temperature': 0.7
        }
        return self.config_data.get('app', default_app_config)
    
    def _create_default_config(self) -> None:
        """
        创建默认配置文件 / Create default configuration file
        """
        default_config = {
            'aws': {
                'auth_method': 'profile',
                'profile_name': 'default',
                'access_key_id': '',
                'secret_access_key': '',
                'region': 'us-east-1'
            },
            'models': self._get_default_models(),
            'system_prompt': self._get_default_system_prompt(),
            'history_folder': './history_references',
            'app': {
                'title': '案例总结生成器 / Case Summary Generator',
                'max_tokens': 4000,
                'temperature': 0.7
            }
        }
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(default_config, file, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            self.logger.info(f"默认配置文件已创建: {self.config_path} / Default configuration file created: {self.config_path}")
        except Exception as e:
            raise ConfigurationError(f"创建默认配置文件失败 / Failed to create default configuration file: {e}")
    
    def _validate_config(self) -> None:
        """
        验证配置文件的必要字段 / Validate required fields in configuration
        
        Raises:
            ConfigurationError: 配置验证失败 / Configuration validation failed
        """
        required_sections = ['aws', 'models', 'system_prompt', 'history_folder', 'app']
        
        for section in required_sections:
            if section not in self.config_data:
                raise ConfigurationError(f"缺少必要配置节: {section} / Missing required configuration section: {section}")
        
        # 验证AWS配置 / Validate AWS configuration
        aws_config = self.config_data['aws']
        auth_method = aws_config.get('auth_method')
        
        if auth_method not in ['profile', 'ak_sk']:
            raise ConfigurationError(f"无效的AWS认证方式: {auth_method} / Invalid AWS auth method: {auth_method}")
        
        if auth_method == 'ak_sk':
            if not aws_config.get('access_key_id') or not aws_config.get('secret_access_key'):
                raise ConfigurationError("使用ak_sk认证方式时，access_key_id和secret_access_key不能为空 / access_key_id and secret_access_key cannot be empty when using ak_sk auth method")
        
        # 验证模型配置 / Validate models configuration
        models = self.config_data.get('models', {})
        if not models:
            raise ConfigurationError("模型配置不能为空 / Models configuration cannot be empty")
        
        # 验证应用配置 / Validate app configuration
        app_config = self.config_data.get('app', {})
        max_tokens = app_config.get('max_tokens')
        temperature = app_config.get('temperature')
        
        if max_tokens and (not isinstance(max_tokens, int) or max_tokens <= 0):
            raise ConfigurationError("max_tokens必须是正整数 / max_tokens must be a positive integer")
        
        if temperature and (not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2):
            raise ConfigurationError("temperature必须在0-2之间 / temperature must be between 0-2")
    
    def _get_default_system_prompt(self) -> str:
        """
        获取默认系统提示词 / Get default system prompt
        
        Returns:
            默认系统提示词 / Default system prompt
        """
        return """你是一个专业的案例总结助手。请根据提供的历史参考信息和新的案例输入，生成一个结构化、专业的案例总结。

总结应该包含：
1. 案例概述
2. 关键要点
3. 分析结论
4. 建议措施

请保持总结的客观性和专业性。"""
    
    def _get_default_models(self) -> Dict[str, List[Dict[str, str]]]:
        """
        获取默认模型配置 / Get default models configuration
        
        Returns:
            默认模型配置 / Default models configuration
        """
        return {
            'claude': [
                {
                    'id': 'anthropic.claude-3-sonnet-20240229-v1:0',
                    'name': 'Claude 3 Sonnet'
                },
                {
                    'id': 'anthropic.claude-3-haiku-20240307-v1:0',
                    'name': 'Claude 3 Haiku'
                }
            ],
            'nova': [
                {
                    'id': 'amazon.nova-pro-v1:0',
                    'name': 'Nova Pro'
                },
                {
                    'id': 'amazon.nova-lite-v1:0',
                    'name': 'Nova Lite'
                }
            ],
            'deepseek': [
                {
                    'id': 'deepseek.deepseek-v2.5',
                    'name': 'DeepSeek V2.5'
                }
            ],
            'openai': [
                {
                    'id': 'openai.gpt-4o-2024-08-06',
                    'name': 'GPT-4o'
                }
            ]
        }
    
    def validate_aws_credentials(self) -> bool:
        """
        验证AWS凭证 / Validate AWS credentials
        
        Returns:
            验证结果 / Validation result
            
        Raises:
            AWSCredentialsError: AWS凭证验证失败 / AWS credentials validation failed
        """
        try:
            credentials = self.get_aws_credentials()
            
            # 根据认证方式创建session / Create session based on auth method
            if credentials['auth_method'] == 'profile':
                self.logger.info(f"使用AWS Profile: {credentials['profile_name']} / Using AWS Profile: {credentials['profile_name']}")
                session = boto3.Session(
                    profile_name=credentials['profile_name'],
                    region_name=credentials['region']
                )
            else:  # ak_sk
                session = boto3.Session(
                    aws_access_key_id=credentials['access_key_id'],
                    aws_secret_access_key=credentials['secret_access_key'],
                    region_name=credentials['region']
                )
            
            # 尝试获取caller identity来验证凭证 / Try to get caller identity to validate credentials
            sts_client = session.client('sts')
            response = sts_client.get_caller_identity()
            
            self.logger.info(f"AWS凭证验证成功，账户ID: {response.get('Account')} / AWS credentials validated successfully, Account ID: {response.get('Account')}")
            return True
            
        except ProfileNotFound as e:
            raise AWSCredentialsError(f"AWS Profile未找到: {credentials.get('profile_name')} / AWS Profile not found: {credentials.get('profile_name')}")
        except NoCredentialsError:
            raise AWSCredentialsError("AWS凭证未配置或无效 / AWS credentials not configured or invalid")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'InvalidUserID.NotFound':
                raise AWSCredentialsError("AWS Access Key ID无效 / Invalid AWS Access Key ID")
            elif error_code == 'SignatureDoesNotMatch':
                raise AWSCredentialsError("AWS Secret Access Key无效 / Invalid AWS Secret Access Key")
            else:
                raise AWSCredentialsError(f"AWS凭证验证失败: {e} / AWS credentials validation failed: {e}")
        except Exception as e:
            raise AWSCredentialsError(f"AWS凭证验证过程中发生错误: {e} / Error occurred during AWS credentials validation: {e}")
    
    def get_boto3_session(self) -> boto3.Session:
        """
        获取配置好的boto3 session / Get configured boto3 session
        
        Returns:
            boto3.Session对象 / boto3.Session object
            
        Raises:
            AWSCredentialsError: 凭证配置错误 / Credentials configuration error
        """
        credentials = self.get_aws_credentials()
        
        try:
            if credentials['auth_method'] == 'profile':
                self.logger.info(f"创建boto3 session，使用profile: {credentials['profile_name']} / Creating boto3 session with profile: {credentials['profile_name']}")
                session = boto3.Session(
                    profile_name=credentials['profile_name'],
                    region_name=credentials['region']
                )
            else:  # ak_sk
                session = boto3.Session(
                    aws_access_key_id=credentials['access_key_id'],
                    aws_secret_access_key=credentials['secret_access_key'],
                    region_name=credentials['region']
                )
            
            return session
            
        except Exception as e:
            raise AWSCredentialsError(f"创建boto3 session失败: {e} / Failed to create boto3 session: {e}")