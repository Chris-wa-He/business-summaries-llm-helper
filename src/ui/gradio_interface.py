"""
Gradio用户界面 / Gradio User Interface

基于Gradio构建的Web用户界面
Web user interface built with Gradio
"""

import gradio as gr
import logging
from typing import Optional, Tuple, List
from src.services.app_controller import AppController, CaseSummaryError
from src.ui.prompt_ui_components import PromptUIComponents


class GradioInterface:
    """Gradio界面类 / Gradio Interface Class"""

    def __init__(self, app_controller: AppController):
        """
        初始化Gradio界面 / Initialize Gradio interface

        Args:
            app_controller: 应用控制器实例 / App controller instance
        """
        self.app_controller = app_controller
        self.logger = logging.getLogger(__name__)

        # 初始化提示词UI组件 / Initialize prompt UI components
        self.prompt_ui = PromptUIComponents(app_controller)

        # 获取应用配置 / Get app configuration
        self.app_config = app_controller.get_app_config()

        # 界面组件 / Interface components
        self.interface = None

    def create_interface(self) -> gr.Blocks:
        """
        创建Gradio界面 / Create Gradio interface

        Returns:
            Gradio Blocks界面 / Gradio Blocks interface
        """
        with gr.Blocks(
            title=self.app_config.get("title", "案例总结生成器"), theme=gr.themes.Soft()
        ) as interface:
            # 标题 / Title
            gr.Markdown(
                f"# {self.app_config.get('title', '案例总结生成器 / Case Summary Generator')}"
            )

            with gr.Row():
                with gr.Column(scale=2):
                    # 案例输入区域 / Case input area
                    case_input = gr.Textbox(
                        label="案例输入 / Case Input",
                        placeholder="请输入需要总结的案例内容... / Please enter the case content to summarize...",
                        lines=8,
                        max_lines=15,
                    )

                    # 系统提示词管理 / System prompt management
                    with gr.Group():
                        gr.Markdown("### 系统提示词管理 / System Prompt Management")

                        # 提示词选择器 / Prompt selector
                        prompt_selector = self.prompt_ui.create_prompt_selector()

                        # 提示词编辑器 / Prompt editor
                        prompt_editor = self.prompt_ui.create_prompt_editor()

                        # 提示词管理面板 / Prompt management panel
                        (
                            management_panel,
                            new_btn,
                            save_btn,
                            delete_btn,
                            status_text,
                        ) = self.prompt_ui.create_prompt_management_panel()

                        # 新建提示词对话框 / New prompt dialog
                        (
                            new_dialog,
                            name_input,
                            content_input,
                            create_btn,
                            cancel_btn,
                        ) = self.prompt_ui.create_new_prompt_dialog()

                with gr.Column(scale=1):
                    # 模型选择 / Model selection
                    model_dropdown = gr.Dropdown(
                        label="选择模型 / Select Model",
                        choices=[],
                        value=None,
                        interactive=True,
                    )

                    # 控制按钮 / Control buttons
                    with gr.Row():
                        generate_btn = gr.Button(
                            "生成总结 / Generate Summary", variant="primary"
                        )
                        refresh_btn = gr.Button(
                            "刷新模型 / Refresh Models", variant="secondary"
                        )

                    # 状态显示 / Status display
                    status_text = gr.Textbox(
                        label="状态 / Status",
                        value="就绪 / Ready",
                        interactive=False,
                        lines=2,
                    )

            # 输出区域 / Output area
            with gr.Row():
                output_text = gr.Textbox(
                    label="生成的案例总结 / Generated Case Summary",
                    lines=12,
                    max_lines=20,
                    interactive=False,
                )

            # 事件绑定 / Event binding

            # 生成总结事件 / Generate summary event
            generate_btn.click(
                fn=self._generate_summary,
                inputs=[case_input, model_dropdown, prompt_editor],
                outputs=[output_text, status_text],
            )

            # 刷新模型事件 / Refresh models event
            refresh_btn.click(
                fn=self._refresh_models, outputs=[model_dropdown, status_text]
            )

            # 提示词管理事件 / Prompt management events

            # 提示词选择事件 / Prompt selection event
            prompt_selector.change(
                fn=self.prompt_ui.handle_prompt_selection,
                inputs=[prompt_selector],
                outputs=[prompt_editor, status_text],
            )

            # 新建提示词事件 / New prompt events
            new_btn.click(fn=lambda: gr.Column(visible=True), outputs=[new_dialog])

            create_btn.click(
                fn=self.prompt_ui.handle_prompt_creation,
                inputs=[name_input, content_input],
                outputs=[status_text, new_dialog, prompt_selector],
            )

            cancel_btn.click(fn=lambda: gr.Column(visible=False), outputs=[new_dialog])

            # 保存提示词事件 / Save prompt event
            save_btn.click(
                fn=self._save_current_prompt,
                inputs=[prompt_selector, prompt_editor],
                outputs=[status_text],
            )

            # 删除提示词事件 / Delete prompt event
            delete_btn.click(
                fn=self.prompt_ui.handle_prompt_deletion,
                inputs=[prompt_selector],
                outputs=[status_text, prompt_selector],
            )

            # 界面加载时初始化模型列表 / Initialize model list on interface load
            interface.load(
                fn=self._initialize_models, outputs=[model_dropdown, status_text]
            )

        self.interface = interface
        return interface

    def _generate_summary(
        self, case_input: str, model_id: str, prompt_content: str
    ) -> Tuple[str, str]:
        """
        生成案例总结 / Generate case summary

        Args:
            case_input: 案例输入 / Case input
            model_id: 模型ID / Model ID
            prompt_content: 提示词内容 / Prompt content

        Returns:
            (总结结果, 状态信息) / (Summary result, status message)
        """
        try:
            # 验证输入 / Validate input
            if not case_input or not case_input.strip():
                return "", "❌ 错误：案例输入不能为空 / Error: Case input cannot be empty"

            if not model_id:
                return "", "❌ 错误：请选择一个模型 / Error: Please select a model"

            # 更新状态 / Update status
            status = "🔄 正在生成总结... / Generating summary..."

            # 调用应用控制器生成总结 / Call app controller to generate summary
            summary = self.app_controller.process_case_summary(
                case_input=case_input,
                model_id=model_id,
                custom_system_prompt=prompt_content.strip()
                if prompt_content.strip()
                else None,
            )

            return summary, "✅ 总结生成成功 / Summary generated successfully"

        except CaseSummaryError as e:
            error_msg = f"❌ 生成失败: {str(e)} / Generation failed: {str(e)}"
            self.logger.error(f"案例总结生成失败: {e}")
            return "", error_msg
        except Exception as e:
            error_msg = f"❌ 未知错误: {str(e)} / Unknown error: {str(e)}"
            self.logger.error(f"未知错误: {e}")
            return "", error_msg

    def _refresh_models(self) -> Tuple[gr.Dropdown, str]:
        """
        刷新模型列表 / Refresh model list

        Returns:
            (更新的下拉列表, 状态信息) / (Updated dropdown, status message)
        """
        try:
            # 刷新模型 / Refresh models
            self.app_controller.refresh_models()

            # 获取UI模型列表 / Get UI model list
            ui_models = self.app_controller.get_models_for_ui()

            # 转换为Gradio格式 / Convert to Gradio format
            choices = []
            for model in ui_models:
                if not model.get("disabled", False):
                    choices.append((model["label"], model["value"]))

            # 获取默认模型 / Get default model
            default_model = self.app_controller.get_default_model()

            return (
                gr.Dropdown(choices=choices, value=default_model),
                "✅ 模型列表已刷新 / Model list refreshed",
            )

        except Exception as e:
            error_msg = f"❌ 刷新失败: {str(e)} / Refresh failed: {str(e)}"
            self.logger.error(f"模型刷新失败: {e}")
            return gr.Dropdown(choices=[]), error_msg

    def _save_current_prompt(self, prompt_name: str, prompt_content: str) -> str:
        """
        保存当前提示词 / Save current prompt

        Args:
            prompt_name: 提示词名称 / Prompt name
            prompt_content: 提示词内容 / Prompt content

        Returns:
            状态信息 / Status message
        """
        return self.prompt_ui.handle_prompt_update(prompt_name, prompt_content)

    def _initialize_models(self) -> Tuple[gr.Dropdown, str]:
        """
        初始化模型列表 / Initialize model list

        Returns:
            (初始化的下拉列表, 状态信息) / (Initialized dropdown, status message)
        """
        try:
            # 初始化模型 / Initialize models
            self.app_controller.initialize_models()

            # 获取UI模型列表 / Get UI model list
            ui_models = self.app_controller.get_models_for_ui()

            # 转换为Gradio格式 / Convert to Gradio format
            choices = []
            for model in ui_models:
                if not model.get("disabled", False):
                    choices.append((model["label"], model["value"]))

            # 获取默认模型 / Get default model
            default_model = self.app_controller.get_default_model()

            return (
                gr.Dropdown(choices=choices, value=default_model),
                "✅ 模型初始化完成 / Model initialization completed",
            )

        except Exception as e:
            error_msg = f"❌ 初始化失败: {str(e)} / Initialization failed: {str(e)}"
            self.logger.error(f"模型初始化失败: {e}")
            return gr.Dropdown(choices=[]), error_msg

    def launch(
        self,
        server_name: str = "127.0.0.1",
        server_port: int = 7860,
        share: bool = False,
        debug: bool = False,
    ) -> None:
        """
        启动Gradio界面 / Launch Gradio interface

        Args:
            server_name: 服务器地址 / Server address
            server_port: 服务器端口 / Server port
            share: 是否创建公共链接 / Whether to create public link
            debug: 是否启用调试模式 / Whether to enable debug mode
        """
        if self.interface is None:
            self.create_interface()

        self.logger.info(
            f"启动Gradio界面: {server_name}:{server_port} / Launching Gradio interface: {server_name}:{server_port}"
        )

        self.interface.launch(
            server_name=server_name,
            server_port=server_port,
            share=share,
            debug=debug,
            show_error=True,
        )
