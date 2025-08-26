"""
系统提示词UI组件 / System Prompt UI Components

提供系统提示词管理的用户界面组件
Provides user interface components for system prompt management
"""

import gradio as gr
from typing import Tuple, List, Optional, Dict, Any
import logging


class PromptUIComponents:
    """系统提示词UI组件 / System Prompt UI Components"""

    def __init__(self, prompt_manager):
        """
        初始化提示词UI组件 / Initialize prompt UI components

        Args:
            prompt_manager: 系统提示词管理器实例 / System prompt manager instance
        """
        self.prompt_manager = prompt_manager
        self.logger = logging.getLogger(__name__)

    def create_prompt_selector(self) -> gr.Dropdown:
        """
        创建提示词选择器 / Create prompt selector

        Returns:
            gr.Dropdown: 提示词选择下拉框 / Prompt selection dropdown
        """
        prompts = self.prompt_manager.list_prompts()
        choices = [prompt["name"] for prompt in prompts]

        active_prompt = self.prompt_manager.get_active_prompt()
        value = (
            active_prompt["name"]
            if active_prompt
            else (choices[0] if choices else None)
        )

        return gr.Dropdown(
            choices=choices,
            value=value,
            label="系统提示词 / System Prompt",
            info="选择要使用的系统提示词 / Select system prompt to use",
            interactive=True,
        )

    def create_prompt_editor(self) -> gr.Textbox:
        """
        创建提示词编辑器 / Create prompt editor

        Returns:
            gr.Textbox: 提示词编辑文本框 / Prompt editor textbox
        """
        active_prompt = self.prompt_manager.get_active_prompt()
        value = active_prompt["content"] if active_prompt else ""

        return gr.Textbox(
            value=value,
            label="提示词内容 / Prompt Content",
            placeholder="请输入系统提示词内容... / Enter system prompt content...",
            lines=8,
            max_lines=15,
            interactive=True,
        )

    def create_prompt_management_panel(self) -> gr.Column:
        """
        创建提示词管理面板 / Create prompt management panel

        Returns:
            gr.Column: 提示词管理面板 / Prompt management panel
        """
        with gr.Column() as panel:
            with gr.Row():
                new_prompt_btn = gr.Button(
                    "新建提示词 / New Prompt", variant="primary", size="sm"
                )
                save_prompt_btn = gr.Button(
                    "保存提示词 / Save Prompt", variant="secondary", size="sm"
                )
                delete_prompt_btn = gr.Button(
                    "删除提示词 / Delete Prompt", variant="stop", size="sm"
                )

            status_text = gr.Textbox(
                label="状态 / Status", interactive=False, visible=False
            )

        return panel, new_prompt_btn, save_prompt_btn, delete_prompt_btn, status_text

    def create_new_prompt_dialog(
        self,
    ) -> Tuple[gr.Column, gr.Textbox, gr.Textbox, gr.Button, gr.Button]:
        """
        创建新建提示词对话框 / Create new prompt dialog

        Returns:
            Tuple: 对话框组件元组 / Dialog components tuple
        """
        with gr.Column(visible=False) as dialog:
            gr.Markdown("### 新建系统提示词 / Create New System Prompt")
            name_input = gr.Textbox(
                label="提示词名称 / Prompt Name",
                placeholder="请输入提示词名称... / Enter prompt name...",
                interactive=True,
            )
            content_input = gr.Textbox(
                label="提示词内容 / Prompt Content",
                placeholder="请输入系统提示词内容... / Enter system prompt content...",
                lines=6,
                interactive=True,
            )
            with gr.Row():
                create_btn = gr.Button("创建 / Create", variant="primary")
                cancel_btn = gr.Button("取消 / Cancel", variant="secondary")

        return dialog, name_input, content_input, create_btn, cancel_btn

    def handle_prompt_selection(self, prompt_name: str) -> Tuple[str, str]:
        """
        处理提示词选择事件 / Handle prompt selection event

        Args:
            prompt_name: 选中的提示词名称 / Selected prompt name

        Returns:
            Tuple[str, str]: (提示词内容, 状态信息) / (prompt content, status message)
        """
        try:
            if not prompt_name:
                return "", "请选择一个提示词 / Please select a prompt"

            success = self.prompt_manager.set_active_prompt(prompt_name)
            if success:
                prompt_content = self.prompt_manager.get_prompt(prompt_name)
                if prompt_content:
                    self.logger.info(
                        f"已切换到提示词: {prompt_name} / Switched to prompt: {prompt_name}"
                    )
                    return (
                        prompt_content,
                        f"已切换到提示词: {prompt_name} / Switched to prompt: {prompt_name}",
                    )
                else:
                    return (
                        "",
                        f"无法加载提示词内容: {prompt_name} / Cannot load prompt content: {prompt_name}",
                    )
            else:
                return (
                    "",
                    f"切换提示词失败: {prompt_name} / Failed to switch prompt: {prompt_name}",
                )

        except Exception as e:
            error_msg = f"切换提示词时发生错误: {e} / Error switching prompt: {e}"
            self.logger.error(error_msg)
            return "", error_msg

    def handle_prompt_creation(
        self, name: str, content: str
    ) -> Tuple[str, gr.Column, gr.Dropdown]:
        """
        处理提示词创建事件 / Handle prompt creation event

        Args:
            name: 提示词名称 / Prompt name
            content: 提示词内容 / Prompt content

        Returns:
            Tuple: (状态信息, 对话框状态, 更新的选择器) / (status message, dialog state, updated selector)
        """
        try:
            if not name or not name.strip():
                return (
                    "提示词名称不能为空 / Prompt name cannot be empty",
                    gr.Column(visible=True),
                    gr.Dropdown(),
                )

            if not content or not content.strip():
                return (
                    "提示词内容不能为空 / Prompt content cannot be empty",
                    gr.Column(visible=True),
                    gr.Dropdown(),
                )

            success = self.prompt_manager.create_prompt(name.strip(), content.strip())
            if success:
                # 更新选择器选项 / Update selector options
                updated_selector = self.create_prompt_selector()
                success_msg = f"成功创建提示词: {name} / Successfully created prompt: {name}"
                self.logger.info(success_msg)
                return success_msg, gr.Column(visible=False), updated_selector
            else:
                return (
                    f"创建提示词失败: {name} / Failed to create prompt: {name}",
                    gr.Column(visible=True),
                    gr.Dropdown(),
                )

        except Exception as e:
            error_msg = f"创建提示词时发生错误: {e} / Error creating prompt: {e}"
            self.logger.error(error_msg)
            return error_msg, gr.Column(visible=True), gr.Dropdown()

    def handle_prompt_update(self, name: str, content: str) -> str:
        """
        处理提示词更新事件 / Handle prompt update event

        Args:
            name: 提示词名称 / Prompt name
            content: 新的提示词内容 / New prompt content

        Returns:
            str: 状态信息 / Status message
        """
        try:
            if not name:
                return "没有选中的提示词 / No prompt selected"

            if not content or not content.strip():
                return "提示词内容不能为空 / Prompt content cannot be empty"

            success = self.prompt_manager.update_prompt(name, content.strip())
            if success:
                success_msg = f"成功更新提示词: {name} / Successfully updated prompt: {name}"
                self.logger.info(success_msg)
                return success_msg
            else:
                return f"更新提示词失败: {name} / Failed to update prompt: {name}"

        except Exception as e:
            error_msg = f"更新提示词时发生错误: {e} / Error updating prompt: {e}"
            self.logger.error(error_msg)
            return error_msg

    def handle_prompt_deletion(self, name: str) -> Tuple[str, gr.Dropdown]:
        """
        处理提示词删除事件 / Handle prompt deletion event

        Args:
            name: 要删除的提示词名称 / Prompt name to delete

        Returns:
            Tuple: (状态信息, 更新的选择器) / (status message, updated selector)
        """
        try:
            if not name:
                return "没有选中的提示词 / No prompt selected", gr.Dropdown()

            success = self.prompt_manager.delete_prompt(name)
            if success:
                # 更新选择器选项 / Update selector options
                updated_selector = self.create_prompt_selector()
                success_msg = f"成功删除提示词: {name} / Successfully deleted prompt: {name}"
                self.logger.info(success_msg)
                return success_msg, updated_selector
            else:
                return (
                    f"删除提示词失败: {name} / Failed to delete prompt: {name}",
                    gr.Dropdown(),
                )

        except Exception as e:
            error_msg = f"删除提示词时发生错误: {e} / Error deleting prompt: {e}"
            self.logger.error(error_msg)
            return error_msg, gr.Dropdown()

    def refresh_prompt_selector(self) -> gr.Dropdown:
        """
        刷新提示词选择器 / Refresh prompt selector

        Returns:
            gr.Dropdown: 更新的提示词选择器 / Updated prompt selector
        """
        return self.create_prompt_selector()
