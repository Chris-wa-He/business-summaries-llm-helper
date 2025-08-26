"""
系统提示词服务 / System Prompt Service

处理系统提示词文件的底层存储操作，包括文件的创建、读取、更新、删除，
以及自动管理对应的历史参考文件夹。

Handles low-level storage operations for system prompt files, including
file creation, reading, updating, deletion, and automatic management
of corresponding history reference folders.
"""

import os
import re
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from src.exceptions.system_prompt_exceptions import (
    PromptNotFoundError,
    PromptValidationError,
    PromptStorageError,
    HistoryFolderError,
)


class SystemPromptService:
    """系统提示词服务类 / System Prompt Service Class"""

    def __init__(self, prompts_folder: str, history_base_folder: str):
        """
        初始化系统提示词服务 / Initialize System Prompt Service

        Args:
            prompts_folder: 提示词存储文件夹路径 / Prompts storage folder path
            history_base_folder: 历史参考文件基础文件夹路径 / History reference base folder path
        """
        self.prompts_folder = Path(prompts_folder)
        self.history_base_folder = Path(history_base_folder)
        self.prompt_file_extension = ".md"

        # 确保文件夹存在 / Ensure folders exist
        self.prompts_folder.mkdir(parents=True, exist_ok=True)
        self.history_base_folder.mkdir(parents=True, exist_ok=True)

    def save_prompt_file(self, name: str, content: str) -> bool:
        """
        保存提示词文件 / Save prompt file

        Args:
            name: 提示词名称 / Prompt name
            content: 提示词内容 / Prompt content

        Returns:
            bool: 保存是否成功 / Whether save was successful

        Raises:
            PromptValidationError: 名称验证失败 / Name validation failed
            PromptStorageError: 文件存储失败 / File storage failed
        """
        try:
            # 验证和清理文件名 / Validate and sanitize filename
            self.validate_prompt_name(name)
            self.validate_prompt_content(content)

            sanitized_name = self.sanitize_folder_name(name)
            file_path = (
                self.prompts_folder / f"{sanitized_name}{self.prompt_file_extension}"
            )

            # 安全检查 / Security checks
            self.validate_file_path_security(file_path)
            self.check_file_permissions(file_path, "write")

            # 创建格式化的文件内容 / Create formatted file content
            formatted_content = self._format_prompt_content(name, content)

            # 写入文件 / Write file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(formatted_content)

            # 自动创建对应的历史文件夹 / Automatically create corresponding history folder
            self.create_history_folder(name)

            return True

        except (PromptValidationError, HistoryFolderError):
            raise
        except Exception as e:
            raise PromptStorageError(
                f"保存提示词文件失败: {e} / Failed to save prompt file: {e}"
            )

    def load_prompt_file(self, name: str) -> Optional[str]:
        """
        加载提示词文件内容 / Load prompt file content

        Args:
            name: 提示词名称 / Prompt name

        Returns:
            Optional[str]: 提示词内容，如果文件不存在则返回None / Prompt content, None if file doesn't exist

        Raises:
            PromptNotFoundError: 提示词文件不存在 / Prompt file not found
            PromptStorageError: 文件读取失败 / File reading failed
        """
        try:
            sanitized_name = self.sanitize_folder_name(name)
            file_path = (
                self.prompts_folder / f"{sanitized_name}{self.prompt_file_extension}"
            )

            # 安全检查 / Security checks
            self.validate_file_path_security(file_path)

            if not file_path.exists():
                raise PromptNotFoundError(
                    f"提示词文件不存在: {name} / Prompt file not found: {name}"
                )

            self.check_file_permissions(file_path, "read")

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 提取实际的提示词内容 / Extract actual prompt content
            return self._extract_prompt_content(content)

        except PromptNotFoundError:
            raise
        except Exception as e:
            raise PromptStorageError(
                f"加载提示词文件失败: {e} / Failed to load prompt file: {e}"
            )

    def delete_prompt_file(self, name: str) -> bool:
        """
        删除提示词文件 / Delete prompt file

        Args:
            name: 提示词名称 / Prompt name

        Returns:
            bool: 删除是否成功 / Whether deletion was successful
        """
        try:
            sanitized_name = self.sanitize_folder_name(name)
            file_path = (
                self.prompts_folder / f"{sanitized_name}{self.prompt_file_extension}"
            )

            # 安全检查 / Security checks
            self.validate_file_path_security(file_path)

            if file_path.exists():
                self.check_file_permissions(
                    file_path, "write"
                )  # 删除需要写权限 / Delete requires write permission
                file_path.unlink()
                return True

            return False

        except Exception as e:
            print(f"删除提示词文件失败 / Failed to delete prompt file: {e}")
            return False

    def list_prompt_files(self) -> List[str]:
        """
        列出所有提示词文件 / List all prompt files

        Returns:
            List[str]: 提示词名称列表 / List of prompt names
        """
        try:
            prompt_files = []

            for file_path in self.prompts_folder.glob(f"*{self.prompt_file_extension}"):
                # 从文件名中提取提示词名称 / Extract prompt name from filename
                name = file_path.stem
                prompt_files.append(name)

            return sorted(prompt_files)

        except Exception as e:
            print(f"列出提示词文件失败 / Failed to list prompt files: {e}")
            return []

    def create_history_folder(self, prompt_name: str) -> str:
        """
        为提示词创建对应的历史参考文件夹 / Create corresponding history reference folder for prompt

        Args:
            prompt_name: 提示词名称 / Prompt name

        Returns:
            str: 创建的历史文件夹路径 / Created history folder path
        """
        try:
            sanitized_name = self.sanitize_folder_name(prompt_name)
            history_folder = self.history_base_folder / sanitized_name
            history_folder.mkdir(parents=True, exist_ok=True)
            return str(history_folder)

        except Exception as e:
            print(f"创建历史文件夹失败 / Failed to create history folder: {e}")
            return ""

    def validate_prompt_name(self, name: str) -> bool:
        """
        验证提示词名称的合法性 / Validate prompt name legality

        Args:
            name: 提示词名称 / Prompt name

        Returns:
            bool: 名称是否合法 / Whether name is valid

        Raises:
            PromptValidationError: 名称验证失败 / Name validation failed
        """
        if not name or not name.strip():
            raise PromptValidationError("提示词名称不能为空 / Prompt name cannot be empty")

        # 检查长度限制 / Check length limit
        if len(name.strip()) > 100:
            raise PromptValidationError(
                "提示词名称过长（最多100个字符） / Prompt name too long (max 100 characters)"
            )

        # 检查路径遍历攻击 / Check for path traversal attacks
        if ".." in name or "/" in name or "\\" in name:
            raise PromptValidationError(
                "提示词名称不能包含路径分隔符 / Prompt name cannot contain path separators"
            )

        # 检查是否包含非法字符 / Check for illegal characters
        illegal_chars = r'[<>:"/\\|?*\x00-\x1f]'
        if re.search(illegal_chars, name):
            raise PromptValidationError(
                "提示词名称包含非法字符 / Prompt name contains illegal characters"
            )

        # 检查保留名称 / Check reserved names
        reserved_names = {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        }
        if name.upper() in reserved_names:
            raise PromptValidationError(
                "提示词名称不能使用系统保留名称 / Prompt name cannot use system reserved names"
            )

        return True

    def sanitize_folder_name(self, name: str) -> str:
        """
        清理文件夹名称，移除或替换非法字符 / Sanitize folder name, remove or replace illegal characters

        Args:
            name: 原始名称 / Original name

        Returns:
            str: 清理后的名称 / Sanitized name
        """
        # 移除首尾空格 / Remove leading/trailing spaces
        sanitized = name.strip()

        # 替换非法字符为下划线 / Replace illegal characters with underscores
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", sanitized)

        # 替换多个连续空格为单个下划线 / Replace multiple consecutive spaces with single underscore
        sanitized = re.sub(r"\s+", "_", sanitized)

        # 移除首尾的点和下划线 / Remove leading/trailing dots and underscores
        sanitized = sanitized.strip("._")

        # 如果名称为空，使用默认名称 / If name is empty, use default name
        if not sanitized:
            sanitized = f"prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return sanitized

    def _format_prompt_content(self, name: str, content: str) -> str:
        """
        格式化提示词文件内容 / Format prompt file content

        Args:
            name: 提示词名称 / Prompt name
            content: 提示词内容 / Prompt content

        Returns:
            str: 格式化后的文件内容 / Formatted file content
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        formatted_content = f"""# 系统提示词: {name}

## 创建时间 / Created Time
{timestamp}

## 最后修改时间 / Last Modified
{timestamp}

## 提示词内容 / Prompt Content
{content.strip()}

## 使用说明 / Usage Notes
此提示词用于指导AI模型的行为和响应风格。
This prompt is used to guide the AI model's behavior and response style.
"""

        return formatted_content

    def _extract_prompt_content(self, file_content: str) -> str:
        """
        从文件内容中提取实际的提示词内容 / Extract actual prompt content from file content

        Args:
            file_content: 文件内容 / File content

        Returns:
            str: 提取的提示词内容 / Extracted prompt content
        """
        try:
            # 查找提示词内容部分 / Find prompt content section
            content_start = file_content.find("## 提示词内容 / Prompt Content")
            if content_start == -1:
                # 如果没有找到标记，返回整个内容 / If marker not found, return entire content
                return file_content.strip()

            # 找到内容开始位置 / Find content start position
            content_start = file_content.find("\n", content_start) + 1

            # 查找下一个标题或文件结尾 / Find next heading or end of file
            content_end = file_content.find("\n## ", content_start)
            if content_end == -1:
                content_end = len(file_content)

            # 提取并清理内容 / Extract and clean content
            content = file_content[content_start:content_end].strip()
            return content

        except Exception:
            # 如果解析失败，返回整个文件内容 / If parsing fails, return entire file content
            return file_content.strip()

    def validate_prompt_content(self, content: str) -> bool:
        """
        验证提示词内容的合法性 / Validate prompt content legality

        Args:
            content: 提示词内容 / Prompt content

        Returns:
            bool: 内容是否合法 / Whether content is valid

        Raises:
            PromptValidationError: 内容验证失败 / Content validation failed
        """
        if not content or not content.strip():
            raise PromptValidationError("提示词内容不能为空 / Prompt content cannot be empty")

        # 检查内容长度限制 / Check content length limit
        if len(content.strip()) > 50000:
            raise PromptValidationError(
                "提示词内容过长（最多50000个字符） / Prompt content too long (max 50000 characters)"
            )

        # 检查是否包含控制字符 / Check for control characters
        if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", content):
            raise PromptValidationError(
                "提示词内容包含非法控制字符 / Prompt content contains illegal control characters"
            )

        return True

    def validate_file_path_security(self, file_path: Path) -> bool:
        """
        验证文件路径的安全性，防止路径遍历攻击 / Validate file path security, prevent path traversal attacks

        Args:
            file_path: 文件路径 / File path

        Returns:
            bool: 路径是否安全 / Whether path is secure

        Raises:
            PromptStorageError: 路径不安全 / Path is not secure
        """
        try:
            # 解析绝对路径 / Resolve absolute path
            resolved_path = file_path.resolve()
            base_path = self.prompts_folder.resolve()

            # 检查路径是否在允许的基础目录内 / Check if path is within allowed base directory
            if not str(resolved_path).startswith(str(base_path)):
                raise PromptStorageError("文件路径超出允许范围 / File path outside allowed range")

            return True

        except Exception as e:
            if isinstance(e, PromptStorageError):
                raise
            raise PromptStorageError(f"路径验证失败 / Path validation failed: {e}")

    def check_file_permissions(self, file_path: Path, operation: str = "read") -> bool:
        """
        检查文件权限 / Check file permissions

        Args:
            file_path: 文件路径 / File path
            operation: 操作类型 ('read', 'write', 'delete') / Operation type

        Returns:
            bool: 是否有权限 / Whether has permission

        Raises:
            PromptStorageError: 权限不足 / Insufficient permissions
        """
        try:
            if operation == "write":
                # 检查目录写权限 / Check directory write permission
                parent_dir = file_path.parent
                if not parent_dir.exists():
                    parent_dir.mkdir(parents=True, exist_ok=True)
                if not os.access(parent_dir, os.W_OK):
                    raise PromptStorageError(
                        f"目录写入权限不足 / Insufficient write permission: {parent_dir}"
                    )

            elif operation == "read":
                if file_path.exists() and not os.access(file_path, os.R_OK):
                    raise PromptStorageError(
                        f"文件读取权限不足 / Insufficient read permission: {file_path}"
                    )

            return True

        except Exception as e:
            if isinstance(e, PromptStorageError):
                raise
            raise PromptStorageError(f"权限检查失败 / Permission check failed: {e}")
