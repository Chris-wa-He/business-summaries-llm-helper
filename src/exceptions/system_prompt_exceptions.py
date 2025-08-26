"""
系统提示词异常类 / System Prompt Exception Classes

定义系统提示词管理相关的异常体系
Define exception hierarchy for system prompt management
"""


class SystemPromptError(Exception):
    """系统提示词基础异常 / Base system prompt exception"""

    pass


class PromptNotFoundError(SystemPromptError):
    """提示词未找到异常 / Prompt not found exception"""

    pass


class PromptValidationError(SystemPromptError):
    """提示词验证异常 / Prompt validation exception"""

    pass


class PromptStorageError(SystemPromptError):
    """提示词存储异常 / Prompt storage exception"""

    pass


class HistoryFolderError(SystemPromptError):
    """历史文件夹操作异常 / History folder operation exception"""

    pass
