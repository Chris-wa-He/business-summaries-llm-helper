"""
Gradio用户界面 / Gradio User Interface

基于Gradio构建的Web用户界面
Web user interface built with Gradio
"""

import gradio as gr
import logging
from typing import Optional, Tuple, List

try:
    from services.app_controller import AppController
    from services.refinement_controller import RefinementController
except ImportError:
    from src.services.app_controller import AppController
    from src.services.refinement_controller import RefinementController


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
        
        # 初始化优化控制器 / Initialize refinement controller
        self.refinement_controller = RefinementController(app_controller)
        
        # 当前优化会话ID / Current refinement session ID
        self.current_session_id = None

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

            # 主要功能区域 / Main functional area
            with gr.Row():
                # 左侧：输入区域 / Left: Input area
                with gr.Column(scale=1):
                    # 案例输入区域 / Case input area
                    case_input = gr.Textbox(
                        label="案例输入 / Case Input",
                        placeholder="请输入需要总结的案例内容... / Please enter the case content to summarize...",
                        lines=8,
                        max_lines=15,
                    )
                    
                    # 模型选择 / Model selection
                    model_dropdown = gr.Dropdown(
                        label="选择模型 / Select Model",
                        choices=[],
                        value=None,
                        interactive=True,
                    )
                    
                    # 系统提示词选择器 / System prompt selector
                    prompt_selector = gr.Dropdown(
                        label="选择系统提示词 / Select System Prompt",
                        choices=self._get_prompt_choices(),
                        value=self._get_active_prompt_name(),
                        interactive=True,
                    )
                    
                    # 提示词编辑器 / Prompt editor
                    prompt_editor = gr.Textbox(
                        label="系统提示词内容 / System Prompt Content",
                        value=self._get_default_system_prompt(),
                        lines=5,
                        max_lines=10,
                    )
                    
                    # 控制按钮 / Control buttons
                    with gr.Row():
                        generate_btn = gr.Button(
                            "🚀 生成案例总结 / Generate Case Summary", 
                            variant="primary"
                        )
                        refresh_btn = gr.Button("🔄 刷新模型 / Refresh Models")
                
                # 右侧：结果显示区域 / Right: Results display area
                with gr.Column(scale=2):
                    # 状态显示 / Status display
                    status_text = gr.Textbox(
                        label="状态 / Status",
                        value="就绪 / Ready",
                        interactive=False,
                        lines=2,
                    )
                    
                    # 结果显示区域 / Results display area
                    output_text = gr.Textbox(
                        label="生成的案例总结 / Generated Case Summary",
                        lines=12,
                        max_lines=20,
                        interactive=False,
                    )
                    
                    # 交互优化区域 / Interactive refinement area
                    with gr.Group():
                        gr.Markdown("### 💬 交互优化 / Interactive Refinement")
                        
                        # 简化的聊天区域
                        chat_display = gr.Textbox(
                            label="对话记录 / Chat Record",
                            lines=8,
                            interactive=False,
                            placeholder="对话记录将在这里显示... / Chat records will be displayed here..."
                        )
                        
                        # 用户输入 / User input
                        with gr.Row():
                            user_input = gr.Textbox(
                                placeholder="请描述您希望的修改... / Describe your desired changes...",
                                container=False,
                                scale=4,
                                show_label=False
                            )
                            send_btn = gr.Button("发送 / Send", variant="primary", scale=1)
                        
                        # 快捷操作 / Quick actions
                        with gr.Row():
                            add_detail_btn = gr.Button("➕ 添加细节", size="sm")
                            adjust_style_btn = gr.Button("🎨 调整风格", size="sm")
                            simplify_btn = gr.Button("✂️ 简化内容", size="sm")

            # 简化的事件处理函数 / Simplified event handlers
            def generate_summary(case_input, model_id, prompt_content):
                try:
                    if not case_input or not case_input.strip():
                        return "", "❌ 案例输入不能为空"
                    if not model_id:
                        return "", "❌ 请选择一个模型"
                    
                    # 重置优化会话 / Reset refinement session
                    self.current_session_id = None
                    
                    summary = self.app_controller.process_case_summary(
                        case_input=case_input,
                        model_id=model_id,
                        custom_system_prompt=prompt_content.strip() if prompt_content.strip() else None,
                    )
                    return summary, "✅ 生成成功"
                except Exception as e:
                    return "", f"❌ 错误: {str(e)}"
            
            def refresh_models():
                try:
                    # 检查应用控制器状态
                    if not self.app_controller.is_initialized:
                        return gr.Dropdown(choices=[]), "❌ 应用未初始化"
                    
                    self.app_controller.refresh_models()
                    ui_models = self.app_controller.get_models_for_ui()
                    
                    # 安全地构建选择列表
                    choices = []
                    for model in ui_models:
                        if isinstance(model, dict) and not model.get("disabled", False):
                            label = model.get("label", "Unknown")
                            value = model.get("value", "")
                            if label and value:
                                choices.append((label, value))
                    
                    default_model = self.app_controller.get_default_model()
                    return gr.Dropdown(choices=choices, value=default_model), "✅ 模型列表已刷新"
                except Exception as e:
                    self.logger.error(f"模型刷新失败: {e}")
                    return gr.Dropdown(choices=[]), f"❌ 刷新失败: {str(e)}"
            
            def update_prompt(prompt_name):
                try:
                    if prompt_name:
                        self.app_controller.set_active_prompt(prompt_name)
                        active_prompt = self.app_controller.get_active_prompt()
                        if active_prompt:
                            return active_prompt.get("content", "")
                    return self._get_default_system_prompt()
                except Exception as e:
                    return self._get_default_system_prompt()
            
            def chat_message(message, chat_record, current_model_id, case_input_value, output_value):
                if not message.strip():
                    return chat_record, "", gr.update()
                
                try:
                    # 如果没有活跃会话，创建一个 / Create session if none exists
                    if not self.current_session_id:
                        # 使用当前输出内容作为初始内容，案例输入作为原始上下文 / Use current output as initial content, case input as original context
                        initial_content = output_value if output_value else "暂无内容"
                        original_context = case_input_value if case_input_value else "暂无原始案例"
                        
                        self.current_session_id = self.refinement_controller.start_refinement_session(
                            initial_content=initial_content,
                            user_id="default_user",
                            original_context=original_context  # 传递原始案例输入
                        )
                    
                    # 使用传入的模型ID，如果为空则使用默认模型 / Use passed model ID, fallback to default if empty
                    model_id = current_model_id if current_model_id else self.app_controller.get_default_model()
                    
                    # 处理用户消息 / Process user message
                    result = self.refinement_controller.process_user_message(
                        message=message,
                        session_id=self.current_session_id,
                        model_id=model_id
                    )
                    
                    if result["success"]:
                        # 更新聊天记录 / Update chat record
                        new_record = chat_record + f"\n\n用户: {message}\n助手: {result['response']}"
                        
                        # 返回更新的聊天记录、清空输入框、更新输出内容 / Return updated chat, clear input, update output
                        return new_record, "", gr.update(value=result['modified_content'])
                    else:
                        # 错误处理 / Error handling
                        error_msg = result.get('error', '未知错误')
                        new_record = chat_record + f"\n\n用户: {message}\n助手: 抱歉，处理您的请求时出现错误：{error_msg}"
                        return new_record, "", gr.update()
                        
                except Exception as e:
                    self.logger.error(f"Chat message processing failed: {e}")
                    error_record = chat_record + f"\n\n用户: {message}\n助手: 抱歉，系统出现错误：{str(e)}"
                    return error_record, "", gr.update()
            
            def initialize_models():
                try:
                    # 检查应用控制器状态
                    if not self.app_controller.is_initialized:
                        return gr.Dropdown(choices=[]), "❌ 应用未初始化"
                    
                    # 初始化模型
                    self.app_controller.initialize_models()
                    ui_models = self.app_controller.get_models_for_ui()
                    
                    # 安全地构建选择列表
                    choices = []
                    for model in ui_models:
                        if isinstance(model, dict) and not model.get("disabled", False):
                            label = model.get("label", "Unknown")
                            value = model.get("value", "")
                            if label and value:
                                choices.append((label, value))
                    
                    # 获取默认模型
                    default_model = self.app_controller.get_default_model()
                    
                    # 确保默认模型在选择列表中
                    if default_model and not any(choice[1] == default_model for choice in choices):
                        choices.append((default_model, default_model))
                    
                    return gr.Dropdown(choices=choices, value=default_model), "✅ 模型初始化完成"
                    
                except Exception as e:
                    self.logger.error(f"模型初始化失败: {e}")
                    return gr.Dropdown(choices=[]), f"❌ 初始化失败: {str(e)}"
            
            # 事件绑定 / Event binding
            generate_btn.click(generate_summary, [case_input, model_dropdown, prompt_editor], [output_text, status_text])
            refresh_btn.click(refresh_models, outputs=[model_dropdown, status_text])
            prompt_selector.change(update_prompt, [prompt_selector], [prompt_editor])
            send_btn.click(chat_message, [user_input, chat_display, model_dropdown, case_input, output_text], [chat_display, user_input, output_text])
            add_detail_btn.click(lambda chat_record, model_id, case_val, output_val: chat_message("请添加更多细节和具体信息", chat_record, model_id, case_val, output_val), [chat_display, model_dropdown, case_input, output_text], [chat_display, user_input, output_text])
            adjust_style_btn.click(lambda chat_record, model_id, case_val, output_val: chat_message("请调整语言风格，使其更加专业", chat_record, model_id, case_val, output_val), [chat_display, model_dropdown, case_input, output_text], [chat_display, user_input, output_text])
            simplify_btn.click(lambda chat_record, model_id, case_val, output_val: chat_message("请简化内容，使其更加简洁明了", chat_record, model_id, case_val, output_val), [chat_display, model_dropdown, case_input, output_text], [chat_display, user_input, output_text])
            interface.load(initialize_models, outputs=[model_dropdown, status_text])

        return interface
    
    def _get_default_system_prompt(self) -> str:
        """
        获取默认系统提示词 / Get default system prompt
        
        Returns:
            默认系统提示词 / Default system prompt
        """
        try:
            # 尝试获取激活的系统提示词 / Try to get active system prompt
            active_prompt = self.app_controller.get_active_prompt()
            if active_prompt and active_prompt.get("content"):
                return active_prompt["content"]
            
            # 如果没有激活的提示词，使用配置中的默认提示词 / If no active prompt, use default from config
            return self.app_controller.config_manager.get_system_prompt()
        except Exception as e:
            self.logger.warning(f"获取系统提示词失败，使用默认值: {e} / Failed to get system prompt, using default: {e}")
            # 返回一个简单的默认提示词 / Return a simple default prompt
            return "你是一个专业的案例总结助手。请根据提供的历史参考信息和新的案例输入，生成一个结构化、专业的案例总结。"
    
    def _get_prompt_choices(self) -> List[Tuple[str, str]]:
        """获取提示词选择列表 / Get prompt choices list"""
        try:
            prompts = self.app_controller.get_available_prompts()
            choices = [(prompt.get("name", "Unknown"), prompt.get("name", "Unknown")) for prompt in prompts]
            if not choices:
                choices = [("default", "default")]
            return choices
        except Exception as e:
            self.logger.warning(f"获取提示词列表失败: {e}")
            return [("default", "default")]
    
    def _get_active_prompt_name(self) -> str:
        """获取当前激活的提示词名称 / Get active prompt name"""
        try:
            active_prompt = self.app_controller.get_active_prompt()
            if active_prompt:
                return active_prompt.get("name", "default")
            return "default"
        except Exception as e:
            self.logger.warning(f"获取激活提示词名称失败: {e}")
            return "default"

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

            # 调用应用控制器生成总结 / Call app controller to generate summary
            summary = self.app_controller.process_case_summary(
                case_input=case_input,
                model_id=model_id,
                custom_system_prompt=prompt_content.strip()
                if prompt_content.strip()
                else None,
            )

            return summary, "✅ 总结生成成功 / Summary generated successfully"

        except Exception as e:
            error_msg = f"❌ 生成失败: {str(e)} / Generation failed: {str(e)}"
            self.logger.error(f"案例总结生成失败: {e}")
            return "", error_msg

    def _refresh_models(self) -> Tuple[List[Tuple[str, str]], str]:
        """
        刷新模型列表 / Refresh model list

        Returns:
            (更新的选项列表, 状态信息) / (Updated choices list, status message)
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

            return choices, "✅ 模型列表已刷新 / Model list refreshed"

        except Exception as e:
            error_msg = f"❌ 刷新失败: {str(e)} / Refresh failed: {str(e)}"
            self.logger.error(f"模型刷新失败: {e}")
            return [], error_msg

    def _refresh_models_simple(self) -> str:
        """
        简化的模型刷新方法 / Simplified model refresh method

        Returns:
            状态信息 / Status message
        """
        try:
            # 刷新模型 / Refresh models
            self.app_controller.refresh_models()
            return "✅ 模型列表已刷新，请重新选择模型 / Model list refreshed, please reselect model"
        except Exception as e:
            error_msg = f"❌ 刷新失败: {str(e)} / Refresh failed: {str(e)}"
            self.logger.error(f"模型刷新失败: {e}")
            return error_msg

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
            self.interface = self.create_interface()

        self.logger.info(
            f"启动Gradio界面: {server_name}:{server_port} / Launching Gradio interface: {server_name}:{server_port}"
        )

        self.interface.launch(
            server_name=server_name,
            server_port=server_port,
            share=share
        )