#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例总结生成器主程序 / Case Summary Generator Main Application

这是应用程序的入口点，负责初始化所有组件并启动Gradio界面。
This is the application entry point, responsible for initializing all components and starting the Gradio interface.
"""

import sys
import logging
import argparse
from pathlib import Path

# 添加src目录到Python路径 / Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from services.app_controller import AppController, CaseSummaryError
from ui.gradio_interface import GradioInterface


def setup_logging(debug: bool = False):
    """
    设置日志配置 / Setup logging configuration
    
    Args:
        debug: 是否启用调试模式 / Whether to enable debug mode
    """
    level = logging.DEBUG if debug else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('case_summary_generator.log', encoding='utf-8')
        ]
    )


def parse_arguments():
    """
    解析命令行参数 / Parse command line arguments
    
    Returns:
        解析后的参数 / Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='案例总结生成器 / Case Summary Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config.yaml',
        help='配置文件路径 / Configuration file path (default: config.yaml)'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='服务器地址 / Server host (default: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=7860,
        help='服务器端口 / Server port (default: 7860)'
    )
    
    parser.add_argument(
        '--share',
        action='store_true',
        help='创建公共链接 / Create public link'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式 / Enable debug mode'
    )
    
    return parser.parse_args()


def main():
    """
    主函数 / Main function
    """
    # 解析命令行参数 / Parse command line arguments
    args = parse_arguments()
    
    # 设置日志 / Setup logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    
    logger.info("启动案例总结生成器 / Starting Case Summary Generator")
    
    try:
        # 初始化应用控制器 / Initialize app controller
        logger.info("初始化应用控制器 / Initializing app controller")
        app_controller = AppController(args.config)
        
        # 检查初始化状态 / Check initialization status
        is_initialized, status_message = app_controller.get_initialization_status()
        if not is_initialized:
            logger.error(f"应用控制器初始化失败: {status_message} / App controller initialization failed: {status_message}")
            sys.exit(1)
        
        logger.info(f"应用控制器初始化成功: {status_message} / App controller initialized successfully: {status_message}")
        
        # 创建Gradio界面 / Create Gradio interface
        logger.info("创建Gradio界面 / Creating Gradio interface")
        gradio_interface = GradioInterface(app_controller)
        gradio_interface.create_interface()
        
        # 启动界面 / Launch interface
        logger.info(f"启动Web界面: http://{args.host}:{args.port} / Launching web interface: http://{args.host}:{args.port}")
        
        gradio_interface.launch(
            server_name=args.host,
            server_port=args.port,
            share=args.share,
            debug=args.debug
        )
        
    except CaseSummaryError as e:
        logger.error(f"应用启动失败: {e} / Application startup failed: {e}")
        print(f"❌ 应用启动失败: {e}")
        print(f"❌ Application startup failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("用户中断应用 / User interrupted application")
        print("\n👋 应用已停止 / Application stopped")
    except Exception as e:
        logger.error(f"未知错误: {e} / Unknown error: {e}")
        print(f"❌ 未知错误: {e}")
        print(f"❌ Unknown error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()