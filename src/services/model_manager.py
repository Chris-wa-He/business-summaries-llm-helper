"""
模型管理器 / Model Manager

负责管理可用模型列表和模型相关操作
Responsible for managing available model list and model-related operations
"""

import logging
from typing import Dict, List, Any, Optional
from src.clients.bedrock_client import BedrockClient, ModelInvocationError


class ModelManager:
    """模型管理器 / Model Manager"""

    def __init__(self, bedrock_client: BedrockClient, config: Dict[str, Any]):
        """
        初始化模型管理器 / Initialize model manager

        Args:
            bedrock_client: Bedrock客户端实例 / Bedrock client instance
            config: 配置信息 / Configuration information
        """
        self.bedrock_client = bedrock_client
        self.config = config
        self.logger = logging.getLogger(__name__)

        # 缓存的模型列表 / Cached model list
        self._cached_models: Optional[List[Dict[str, Any]]] = None
        self._categorized_models: Optional[Dict[str, List[Dict[str, Any]]]] = None

        # 默认模型配置 / Default model configuration
        self.default_models = {
            "claude": "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "nova": "amazon.nova-pro-v1:0",
            "deepseek": "deepseek.deepseek-v2.5",
            "openai": "openai.gpt-4o-2024-08-06",
        }

    def refresh_available_models(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        刷新可用模型列表 / Refresh available models list

        Returns:
            按类别分组的模型字典 / Dictionary of models grouped by category

        Raises:
            ModelInvocationError: 获取模型列表失败 / Failed to get model list
        """
        try:
            self.logger.info("开始刷新可用模型列表 / Starting to refresh available models list")

            # 从API获取模型列表 / Get model list from API
            models = self.bedrock_client.list_foundation_models()

            # 缓存模型列表 / Cache model list
            self._cached_models = models

            # 按类别分组 / Group by category
            self._categorized_models = self.bedrock_client.filter_models_by_provider(
                models
            )

            # 为每个模型添加显示名称 / Add display name for each model
            for category, category_models in self._categorized_models.items():
                for model in category_models:
                    model["displayName"] = self.bedrock_client.get_model_display_name(
                        model["modelId"]
                    )

            self.logger.info(
                f"成功刷新模型列表，共 {len(models)} 个模型 / Successfully refreshed model list, {len(models)} models total"
            )

            return self._categorized_models

        except Exception as e:
            self.logger.error(f"刷新模型列表失败: {e} / Failed to refresh model list: {e}")
            # 如果刷新失败，返回配置文件中的默认模型 / If refresh fails, return default models from config
            return self._get_fallback_models()

    def get_models_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        按四个类别获取模型：Claude、Nova、DeepSeek、OpenAI / Get models by four categories

        Returns:
            按类别分组的模型字典 / Dictionary of models grouped by category
        """
        if self._categorized_models is None:
            # 如果没有缓存，尝试刷新 / If no cache, try to refresh
            try:
                return self.refresh_available_models()
            except Exception as e:
                self.logger.warning(
                    f"无法获取实时模型列表，使用配置文件默认值: {e} / Cannot get real-time model list, using config defaults: {e}"
                )
                return self._get_fallback_models()

        return self._categorized_models

    def get_supported_models_only(self) -> List[Dict[str, Any]]:
        """
        仅获取支持的四类模型 / Get only the four supported model types

        Returns:
            支持的模型列表 / List of supported models
        """
        categorized = self.get_models_by_category()

        supported_models = []
        for category_models in categorized.values():
            supported_models.extend(category_models)

        return supported_models

    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        获取特定模型的详细信息 / Get detailed info for specific model

        Args:
            model_id: 模型ID / Model ID

        Returns:
            模型信息字典或None / Model info dictionary or None
        """
        supported_models = self.get_supported_models_only()

        for model in supported_models:
            if model.get("modelId") == model_id:
                return model

        return None

    def is_model_available(self, model_id: str) -> bool:
        """
        检查模型是否可用 / Check if model is available

        Args:
            model_id: 模型ID / Model ID

        Returns:
            是否可用 / Whether available
        """
        return self.get_model_info(model_id) is not None

    def get_default_model(self) -> str:
        """
        获取默认模型ID / Get default model ID

        Returns:
            默认模型ID / Default model ID
        """
        # 优先使用Claude 3.5 Sonnet / Prefer Claude 3.5 Sonnet
        preferred_models = [
            "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "anthropic.claude-3-sonnet-20240229-v1:0",
            "amazon.nova-pro-v1:0",
            "deepseek.deepseek-v2.5",
        ]

        # 检查首选模型是否可用 / Check if preferred models are available
        for model_id in preferred_models:
            if self.is_model_available(model_id):
                return model_id

        # 如果首选模型都不可用，返回任何可用的模型 / If no preferred models available, return any available model
        supported_models = self.get_supported_models_only()
        if supported_models:
            return supported_models[0]["modelId"]

        # 最后的备选方案 / Last fallback
        return "anthropic.claude-3-5-sonnet-20241022-v2:0"

    def get_models_for_ui(self) -> List[Dict[str, str]]:
        """
        获取用于UI显示的模型列表 / Get model list for UI display

        Returns:
            UI模型列表 / UI model list
        """
        categorized = self.get_models_by_category()
        ui_models = []

        # 按类别顺序添加模型 / Add models in category order
        category_order = ["claude", "nova", "deepseek", "openai"]
        category_labels = {
            "claude": "Claude (Anthropic)",
            "nova": "Nova (Amazon)",
            "deepseek": "DeepSeek",
            "openai": "OpenAI",
        }

        for category in category_order:
            if category in categorized and categorized[category]:
                # 添加类别分隔符 / Add category separator
                ui_models.append(
                    {
                        "value": f"---{category}---",
                        "label": f"--- {category_labels[category]} ---",
                        "disabled": True,
                    }
                )

                # 添加该类别的模型 / Add models in this category
                for model in categorized[category]:
                    ui_models.append(
                        {
                            "value": model["modelId"],
                            "label": f"  {model.get('displayName', model['modelId'])}",
                            "disabled": False,
                        }
                    )

        return ui_models

    def _get_fallback_models(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取备选模型列表（从配置文件） / Get fallback model list (from config file)

        Returns:
            备选模型字典 / Fallback models dictionary
        """
        config_models = self.config.get("models", {})
        fallback_models = {"claude": [], "nova": [], "deepseek": [], "openai": []}

        # 转换配置文件格式为标准格式 / Convert config format to standard format
        for category, models in config_models.items():
            if category in fallback_models and isinstance(models, list):
                for model_config in models:
                    if isinstance(model_config, dict) and "id" in model_config:
                        fallback_models[category].append(
                            {
                                "modelId": model_config["id"],
                                "displayName": model_config.get(
                                    "name", model_config["id"]
                                ),
                                "modelName": model_config.get(
                                    "name", model_config["id"]
                                ),
                            }
                        )

        self.logger.info("使用配置文件中的备选模型列表 / Using fallback model list from config file")
        return fallback_models

    def validate_model_access(self, model_id: str) -> bool:
        """
        验证模型访问权限 / Validate model access permissions

        Args:
            model_id: 模型ID / Model ID

        Returns:
            是否有访问权限 / Whether has access permission
        """
        try:
            # 尝试调用模型进行简单测试 / Try to call model for simple test
            messages = self.bedrock_client.format_messages("test")
            self.bedrock_client.converse(
                model_id=model_id, messages=messages, max_tokens=10, temperature=0.1
            )
            return True
        except Exception as e:
            self.logger.warning(
                f"模型 {model_id} 访问验证失败: {e} / Model {model_id} access validation failed: {e}"
            )
            return False
