"""
系统提示词管理器 / System Prompt Manager

提供统一的系统提示词管理接口，协调提示词的创建、读取、更新、删除操作，
管理提示词与历史参考文件夹的关联关系。

Provides unified system prompt management interface, coordinates prompt
creation, reading, updating, deletion operations, and manages the
association between prompts and history reference folders.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
from time import time
from src.services.system_prompt_service import SystemPromptService
from src.exceptions.system_prompt_exceptions import (
    SystemPromptError,
    PromptNotFoundError,
    PromptValidationError,
    PromptStorageError,
)


class SystemPromptManager:
    """系统提示词管理器类 / System Prompt Manager Class"""

    def __init__(self, config_manager, history_processor):
        """
        初始化系统提示词管理器 / Initialize System Prompt Manager

        Args:
            config_manager: 配置管理器实例 / Configuration manager instance
            history_processor: 历史处理器实例 / History processor instance
        """
        self.config_manager = config_manager
        self.history_processor = history_processor

        # 从配置中获取路径 / Get paths from configuration
        app_config = config_manager.get_app_config()
        system_prompts_config = app_config.get("system_prompts", {})

        self.prompts_folder = system_prompts_config.get(
            "prompts_folder", "./system_prompts"
        )
        self.active_prompt = system_prompts_config.get("active_prompt", "default")

        # 获取历史参考文件夹基础路径 / Get history reference folder base path
        self.history_base_folder = app_config.get(
            "history_folder", "./history_references"
        )

        # 初始化系统提示词服务 / Initialize system prompt service
        self.prompt_service = SystemPromptService(
            self.prompts_folder, self.history_base_folder
        )

        # 初始化缓存 / Initialize cache
        self._content_cache = {}  # 内容缓存 / Content cache
        self._list_cache = {}  # 列表缓存 / List cache
        self._cache_ttl = 300  # 缓存过期时间（5分钟） / Cache TTL (5 minutes)

        # 确保默认提示词存在 / Ensure default prompt exists
        self._ensure_default_prompt()

    def create_prompt(self, name: str, content: str) -> bool:
        """
        创建新的系统提示词 / Create new system prompt

        Args:
            name: 提示词名称 / Prompt name
            content: 提示词内容 / Prompt content

        Returns:
            bool: 创建是否成功 / Whether creation was successful
        """
        try:
            # 检查是否已存在 / Check if already exists
            try:
                existing_content = self.prompt_service.load_prompt_file(name)
                if existing_content is not None:
                    return False  # 已存在，不允许覆盖 / Already exists, don't allow overwrite
            except PromptNotFoundError:
                pass  # 文件不存在，可以创建 / File doesn't exist, can create

            # 创建提示词文件 / Create prompt file
            success = self.prompt_service.save_prompt_file(name, content)
            if success:
                # 清理列表缓存 / Clear list cache
                self._list_cache.clear()
            return success

        except (PromptValidationError, PromptStorageError) as e:
            print(f"创建提示词失败 / Failed to create prompt: {e}")
            return False
        except Exception as e:
            print(f"创建提示词失败 / Failed to create prompt: {e}")
            return False

    def get_prompt(self, name: str) -> Optional[str]:
        """
        获取指定名称的提示词内容 / Get prompt content by name

        Args:
            name: 提示词名称 / Prompt name

        Returns:
            Optional[str]: 提示词内容，如果不存在则返回None / Prompt content, None if doesn't exist

        Raises:
            PromptNotFoundError: 提示词不存在 / Prompt not found
        """
        # 检查缓存 / Check cache
        if name in self._content_cache:
            cache_entry = self._content_cache[name]
            if time() - cache_entry["time"] < self._cache_ttl:
                return cache_entry["content"]

        # 从文件加载 / Load from file
        try:
            content = self.prompt_service.load_prompt_file(name)

            # 缓存结果 / Cache result
            self._content_cache[name] = {"content": content, "time": time()}

            return content
        except PromptNotFoundError:
            return None

    def update_prompt(self, name: str, content: str) -> bool:
        """
        更新现有的系统提示词 / Update existing system prompt

        Args:
            name: 提示词名称 / Prompt name
            content: 新的提示词内容 / New prompt content

        Returns:
            bool: 更新是否成功 / Whether update was successful
        """
        try:
            # 检查提示词是否存在 / Check if prompt exists
            try:
                self.prompt_service.load_prompt_file(name)
            except PromptNotFoundError:
                return False  # 提示词不存在 / Prompt doesn't exist

            # 更新提示词文件 / Update prompt file
            success = self.prompt_service.save_prompt_file(name, content)
            if success:
                # 清理缓存中的该项 / Clear this item from cache
                self._content_cache.pop(name, None)
            return success

        except Exception as e:
            print(f"更新提示词失败 / Failed to update prompt: {e}")
            return False

    def delete_prompt(self, name: str) -> bool:
        """
        删除系统提示词 / Delete system prompt

        Args:
            name: 提示词名称 / Prompt name

        Returns:
            bool: 删除是否成功 / Whether deletion was successful
        """
        try:
            # 不允许删除默认提示词 / Don't allow deleting default prompt
            if name == "default":
                return False

            # 如果要删除的是当前激活的提示词，切换到默认提示词 / If deleting active prompt, switch to default
            if name == self.active_prompt:
                self.set_active_prompt("default")

            # 删除提示词文件 / Delete prompt file
            success = self.prompt_service.delete_prompt_file(name)
            if success:
                # 清理缓存中的该项和列表缓存 / Clear this item from cache and list cache
                self._content_cache.pop(name, None)
                self._list_cache.clear()
            return success

        except Exception as e:
            print(f"删除提示词失败 / Failed to delete prompt: {e}")
            return False

    def list_prompts(self) -> List[Dict[str, Any]]:
        """
        列出所有可用的系统提示词 / List all available system prompts

        Returns:
            List[Dict[str, Any]]: 提示词信息列表 / List of prompt information
        """
        try:
            # 检查缓存 / Check cache
            if "prompt_list" in self._list_cache:
                cache_entry = self._list_cache["prompt_list"]
                if time() - cache_entry["time"] < self._cache_ttl:
                    return cache_entry["data"]

            # 从文件系统获取 / Get from file system
            prompt_names = self.prompt_service.list_prompt_files()
            prompts = []

            for name in prompt_names:
                prompt_info = {
                    "name": name,
                    "is_active": name == self.active_prompt,
                    "history_folder": self.get_prompt_history_folder(name),
                }
                prompts.append(prompt_info)

            # 缓存结果 / Cache result
            self._list_cache["prompt_list"] = {"data": prompts, "time": time()}

            return prompts

        except Exception as e:
            print(f"列出提示词失败 / Failed to list prompts: {e}")
            return []

    def set_active_prompt(self, name: str) -> bool:
        """
        设置激活的系统提示词 / Set active system prompt

        Args:
            name: 提示词名称 / Prompt name

        Returns:
            bool: 设置是否成功 / Whether setting was successful
        """
        try:
            # 检查提示词是否存在 / Check if prompt exists
            try:
                self.prompt_service.load_prompt_file(name)
            except PromptNotFoundError:
                return False  # 提示词不存在 / Prompt doesn't exist

            # 更新激活的提示词 / Update active prompt
            self.active_prompt = name

            # 切换历史处理器的文件夹 / Switch history processor folder
            history_folder = self.get_prompt_history_folder(name)
            if hasattr(self.history_processor, "set_history_folder"):
                self.history_processor.set_history_folder(history_folder)

            return True

        except Exception as e:
            print(f"设置激活提示词失败 / Failed to set active prompt: {e}")
            return False

    def get_active_prompt(self) -> Optional[Dict[str, str]]:
        """
        获取当前激活的系统提示词信息 / Get current active system prompt information

        Returns:
            Optional[Dict[str, str]]: 激活提示词信息 / Active prompt information
        """
        try:
            try:
                content = self.get_prompt(self.active_prompt)
            except PromptNotFoundError:
                # 如果激活的提示词不存在，回退到默认提示词 / If active prompt doesn't exist, fallback to default
                self.active_prompt = "default"
                try:
                    content = self.get_prompt("default")
                except PromptNotFoundError:
                    return None

            if content is not None:
                return {
                    "name": self.active_prompt,
                    "content": content,
                    "history_folder": self.get_prompt_history_folder(
                        self.active_prompt
                    ),
                }

            return None

        except Exception as e:
            print(f"获取激活提示词失败 / Failed to get active prompt: {e}")
            return None

    def get_prompt_history_folder(self, name: str) -> str:
        """
        获取指定提示词对应的历史参考文件夹路径 / Get history reference folder path for specified prompt

        Args:
            name: 提示词名称 / Prompt name

        Returns:
            str: 历史文件夹路径 / History folder path
        """
        sanitized_name = self.prompt_service.sanitize_folder_name(name)
        return str(Path(self.history_base_folder) / sanitized_name)

    def _ensure_default_prompt(self):
        """
        确保默认提示词存在 / Ensure default prompt exists
        """
        try:
            # 检查默认提示词是否存在 / Check if default prompt exists
            try:
                self.prompt_service.load_prompt_file("default")
            except PromptNotFoundError:
                # 创建默认提示词 / Create default prompt
                default_content = """你是一个专业的案例总结助手。请根据提供的历史参考信息和新的案例输入，生成一个结构化、专业的案例总结。

需要按照历史参考的结构进行总结，在必要的地方以数据进行量化说明，总结确保简练明了。

请保持总结的客观性和专业性。"""

                self.prompt_service.save_prompt_file("default", default_content)

        except Exception as e:
            print(f"创建默认提示词失败 / Failed to create default prompt: {e}")

    def _invalidate_cache(self):
        """
        清理所有缓存 / Clear all caches
        """
        self._content_cache.clear()
        self._list_cache.clear()
