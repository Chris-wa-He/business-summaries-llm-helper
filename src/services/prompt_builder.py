"""
Prompt构建器 / Prompt Builder

负责构建和格式化用于LLM的提示词
Responsible for building and formatting prompts for LLM
"""

import logging
from typing import Optional


class PromptBuilder:
    """Prompt构建器 / Prompt Builder"""

    def __init__(self):
        """初始化Prompt构建器 / Initialize Prompt Builder"""
        self.logger = logging.getLogger(__name__)
        self.max_prompt_length = 32000  # 最大prompt长度限制 / Maximum prompt length limit

    def build_prompt(
        self, case_input: str, history_reference: str, system_prompt: str
    ) -> str:
        """
        构建完整的提示词 / Build complete prompt

        Args:
            case_input: 案例输入内容 / Case input content
            history_reference: 历史参考信息 / History reference information
            system_prompt: 系统提示词 / System prompt

        Returns:
            构建好的完整提示词 / Built complete prompt
        """
        try:
            # 格式化历史参考信息 / Format history reference information
            formatted_history = self.format_history_reference(history_reference)

            # 构建完整的用户提示词 / Build complete user prompt
            user_prompt_parts = []

            # 添加历史参考信息 / Add history reference information
            if formatted_history.strip():
                user_prompt_parts.append("## 历史参考信息 / Historical Reference Information")
                user_prompt_parts.append(formatted_history)
                user_prompt_parts.append("")  # 空行分隔 / Empty line separator

            # 添加案例输入 / Add case input
            user_prompt_parts.append("## 需要总结的案例 / Case to Summarize")
            user_prompt_parts.append(case_input.strip())
            user_prompt_parts.append("")  # 空行分隔 / Empty line separator

            # 添加输出要求 / Add output requirements
            user_prompt_parts.append("## 输出要求 / Output Requirements")
            if formatted_history.strip():
                user_prompt_parts.append("请根据上述历史参考信息和案例内容，生成一个结构化、专业的案例总结。")
                user_prompt_parts.append(
                    "Please generate a structured and professional case summary based on the above historical reference information and case content."
                )
            else:
                user_prompt_parts.append("请根据案例内容，生成一个结构化、专业的案例总结。")
                user_prompt_parts.append(
                    "Please generate a structured and professional case summary based on the case content."
                )

            user_prompt = "\n".join(user_prompt_parts)

            # 检查长度并截断如果需要 / Check length and truncate if needed
            user_prompt = self._ensure_prompt_length(user_prompt, system_prompt)

            self.logger.debug(
                f"构建的用户提示词长度: {len(user_prompt)} 字符 / Built user prompt length: {len(user_prompt)} characters"
            )

            return user_prompt

        except Exception as e:
            self.logger.error(f"构建提示词失败: {e} / Failed to build prompt: {e}")
            # 返回基础提示词 / Return basic prompt
            return f"## 需要总结的案例 / Case to Summarize\n\n{case_input}\n\n## 输出要求 / Output Requirements\n\n请生成案例总结。"

    def format_history_reference(self, history: str) -> str:
        """
        格式化历史参考信息 / Format history reference information

        Args:
            history: 原始历史参考信息 / Raw history reference information

        Returns:
            格式化后的历史参考信息 / Formatted history reference information
        """
        if not history or not history.strip():
            return ""

        # 清理和格式化历史信息 / Clean and format history information
        lines = history.split("\n")
        formatted_lines = []

        for line in lines:
            line = line.strip()
            if line:
                formatted_lines.append(line)
            elif formatted_lines and formatted_lines[-1] != "":
                # 保留单个空行作为段落分隔 / Keep single empty line as paragraph separator
                formatted_lines.append("")

        # 移除末尾的空行 / Remove trailing empty lines
        while formatted_lines and formatted_lines[-1] == "":
            formatted_lines.pop()

        formatted_history = "\n".join(formatted_lines)

        # 如果历史信息太长，进行智能截断 / If history is too long, perform intelligent truncation
        if len(formatted_history) > 15000:  # 历史信息最大长度 / Maximum history length
            formatted_history = self._truncate_history_intelligently(formatted_history)

        return formatted_history

    def _ensure_prompt_length(self, user_prompt: str, system_prompt: str) -> str:
        """
        确保提示词长度在限制范围内 / Ensure prompt length is within limits

        Args:
            user_prompt: 用户提示词 / User prompt
            system_prompt: 系统提示词 / System prompt

        Returns:
            调整后的用户提示词 / Adjusted user prompt
        """
        total_length = len(user_prompt) + len(system_prompt)

        if total_length <= self.max_prompt_length:
            return user_prompt

        # 需要截断用户提示词 / Need to truncate user prompt
        available_length = (
            self.max_prompt_length - len(system_prompt) - 500
        )  # 保留500字符缓冲 / Reserve 500 characters buffer

        if available_length < 1000:  # 如果可用长度太短 / If available length is too short
            self.logger.warning(
                "系统提示词过长，可能影响用户输入 / System prompt too long, may affect user input"
            )
            available_length = 1000

        # 智能截断用户提示词 / Intelligently truncate user prompt
        truncated_prompt = self._truncate_prompt_intelligently(
            user_prompt, available_length
        )

        self.logger.warning(
            f"提示词被截断，原长度: {len(user_prompt)}, 截断后: {len(truncated_prompt)} / Prompt truncated, original: {len(user_prompt)}, after: {len(truncated_prompt)}"
        )

        return truncated_prompt

    def _truncate_history_intelligently(self, history: str) -> str:
        """
        智能截断历史信息 / Intelligently truncate history information

        Args:
            history: 原始历史信息 / Original history information

        Returns:
            截断后的历史信息 / Truncated history information
        """
        lines = history.split("\n")

        # 优先保留标题和重要信息 / Prioritize keeping headers and important information
        important_lines = []
        content_lines = []

        for line in lines:
            line = line.strip()
            if (
                line.startswith("#")
                or "重要" in line
                or "关键" in line
                or "important" in line.lower()
                or "key" in line.lower()
            ):
                important_lines.append(line)
            elif line:
                content_lines.append(line)

        # 构建截断后的历史信息 / Build truncated history
        truncated_lines = important_lines.copy()

        # 添加部分内容行，直到达到长度限制 / Add content lines until length limit
        current_length = len("\n".join(truncated_lines))
        target_length = 12000  # 历史信息截断目标长度 / Target length for history truncation

        for line in content_lines:
            if current_length + len(line) + 1 > target_length:
                break
            truncated_lines.append(line)
            current_length += len(line) + 1

        # 添加截断提示 / Add truncation notice
        if len(truncated_lines) < len(lines):
            truncated_lines.append("")
            truncated_lines.append(
                "... (历史信息已截断以适应长度限制) / (History truncated to fit length limit) ..."
            )

        return "\n".join(truncated_lines)

    def _truncate_prompt_intelligently(self, prompt: str, max_length: int) -> str:
        """
        智能截断提示词 / Intelligently truncate prompt

        Args:
            prompt: 原始提示词 / Original prompt
            max_length: 最大长度 / Maximum length

        Returns:
            截断后的提示词 / Truncated prompt
        """
        if len(prompt) <= max_length:
            return prompt

        lines = prompt.split("\n")

        # 查找关键部分 / Find key sections
        case_section_start = -1
        requirements_section_start = -1

        for i, line in enumerate(lines):
            if "需要总结的案例" in line or "Case to Summarize" in line:
                case_section_start = i
            elif "输出要求" in line or "Output Requirements" in line:
                requirements_section_start = i

        # 优先保留案例内容和输出要求 / Prioritize keeping case content and output requirements
        essential_lines = []

        if case_section_start >= 0:
            if requirements_section_start >= 0:
                # 保留案例部分和输出要求 / Keep case section and output requirements
                essential_lines = lines[case_section_start:]
            else:
                # 只保留案例部分 / Only keep case section
                essential_lines = lines[case_section_start:]
        else:
            # 如果找不到关键部分，保留后半部分 / If key sections not found, keep latter half
            essential_lines = lines[len(lines) // 2 :]

        # 从essential_lines开始，逐行添加直到达到长度限制 / Add lines from essential_lines until length limit
        truncated_lines = []
        current_length = 0

        for line in essential_lines:
            if (
                current_length + len(line) + 1 > max_length - 100
            ):  # 保留100字符缓冲 / Reserve 100 characters buffer
                break
            truncated_lines.append(line)
            current_length += len(line) + 1

        # 如果还有空间，尝试添加历史信息的开头部分 / If there's still space, try to add beginning of history
        if current_length < max_length * 0.8 and case_section_start > 0:
            history_lines = lines[:case_section_start]
            for line in history_lines:
                if current_length + len(line) + 1 > max_length - 100:
                    break
                truncated_lines.insert(-len(essential_lines), line)
                current_length += len(line) + 1

        return "\n".join(truncated_lines)

    def create_system_message_format(self, system_prompt: str) -> str:
        """
        创建系统消息格式 / Create system message format

        Args:
            system_prompt: 系统提示词 / System prompt

        Returns:
            格式化的系统消息 / Formatted system message
        """
        if not system_prompt or not system_prompt.strip():
            # 使用默认系统提示词 / Use default system prompt
            system_prompt = """你是一个专业的案例总结助手。请根据提供的历史参考信息和新的案例输入，生成一个结构化、专业的案例总结。

总结应该包含：
1. 案例概述
2. 关键要点
3. 分析结论
4. 建议措施

请保持总结的客观性和专业性。"""

        return system_prompt.strip()

    def validate_prompt_components(self, case_input: str, system_prompt: str) -> bool:
        """
        验证提示词组件 / Validate prompt components

        Args:
            case_input: 案例输入 / Case input
            system_prompt: 系统提示词 / System prompt

        Returns:
            验证结果 / Validation result
        """
        if not case_input or not case_input.strip():
            self.logger.error("案例输入不能为空 / Case input cannot be empty")
            return False

        if len(case_input.strip()) < 10:
            self.logger.warning(
                "案例输入内容过短，可能影响总结质量 / Case input too short, may affect summary quality"
            )

        if not system_prompt or not system_prompt.strip():
            self.logger.warning(
                "系统提示词为空，将使用默认提示词 / System prompt empty, will use default prompt"
            )

        return True
