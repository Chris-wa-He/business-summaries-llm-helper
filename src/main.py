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
import warnings

# 捕获所有警告并记录到日志 / Capture all warnings and log them
logging.captureWarnings(True)

# 添加src目录到Python路径 / Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from services.app_controller import AppController
from ui.gradio_interface import GradioInterface


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    全局异常处理器 / Global exception handler
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger = logging.getLogger(__name__)
    logger.error(
        f"未处理的异常 / Unhandled exception: {exc_type.__name__}: {exc_value}",
        exc_info=(exc_type, exc_value, exc_traceback)
    )


# 设置全局异常处理器 / Set global exception handler
sys.excepthook = handle_exception


def setup_logging(debug: bool = False):
    """
    设置日志配置 / Setup logging configuration
    
    Args:
        debug: 是否启用调试模式 / Whether to enable debug mode
    """
    # 创建logs目录 / Create logs directory
    Path('logs').mkdir(exist_ok=True)
    
    log_level = logging.DEBUG if debug else logging.INFO
    
    # 配置日志格式 / Configure log format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器 / Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # 文件处理器 / File handler
    file_handler = logging.FileHandler('logs/app.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # 错误日志文件处理器 / Error log file handler
    error_handler = logging.FileHandler('logs/error.log', encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # 配置根日志器 / Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()  # 清除现有处理器 / Clear existing handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # 设置第三方库日志级别 / Set third-party library log levels
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    
    # 将所有第三方库错误也记录到文件 / Log all third-party library errors to file
    for logger_name in ['uvicorn', 'fastapi', 'starlette', 'gradio', 'uvicorn.error', 'uvicorn.access']:
        third_party_logger = logging.getLogger(logger_name)
        third_party_logger.setLevel(logging.DEBUG if debug else logging.ERROR)
        third_party_logger.addHandler(error_handler)
        third_party_logger.addHandler(file_handler)
        # 确保错误传播到根日志器
        third_party_logger.propagate = True


def parse_arguments():
    """
    解析命令行参数 / Parse command line arguments
    
    Returns:
        解析后的参数 / Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="案例总结生成器 / Case Summary Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="配置文件路径 / Configuration file path (default: config.yaml)"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="服务器主机地址 / Server host address (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="服务器端口 / Server port (default: 7860)"
    )
    
    parser.add_argument(
        "--share",
        action="store_true",
        help="创建公共链接 / Create public link"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式 / Enable debug mode"
    )
    
    return parser.parse_args()


def main():
    """
    主函数 / Main function
    """
    try:
        # 解析命令行参数 / Parse command line arguments
        args = parse_arguments()
        
        # 设置日志 / Setup logging
        setup_logging(debug=args.debug)
        logger = logging.getLogger(__name__)
        
        logger.info("启动案例总结生成器 / Starting Case Summary Generator")
        logger.info(f"配置文件: {args.config} / Config file: {args.config}")
        logger.info(f"日志文件: logs/app.log, logs/error.log / Log files: logs/app.log, logs/error.log")
        
        # 初始化应用控制器 / Initialize application controller
        logger.info("初始化应用控制器 / Initializing application controller")
        try:
            app_controller = AppController(args.config)
        except Exception as e:
            logger.error(f"应用控制器初始化失败: {e} / App controller initialization failed: {e}")
            logger.error("详细错误信息已记录到 logs/error.log / Detailed error logged to logs/error.log")
            raise
        
        # 检查初始化状态 / Check initialization status
        is_initialized, status_message = app_controller.get_initialization_status()
        if not is_initialized:
            logger.error(f"应用初始化失败: {status_message} / Application initialization failed: {status_message}")
            sys.exit(1)
        
        logger.info(f"应用初始化成功: {status_message} / Application initialized successfully: {status_message}")
        
        # 创建并启动Gradio界面 / Create and launch Gradio interface
        logger.info("创建Gradio界面 / Creating Gradio interface")
        try:
            gradio_interface = GradioInterface(app_controller)
        except Exception as e:
            logger.error(f"Gradio界面创建失败: {e} / Gradio interface creation failed: {e}")
            logger.error("详细错误信息已记录到 logs/error.log / Detailed error logged to logs/error.log")
            raise
        
        logger.info(f"启动Web服务器 / Starting web server")
        logger.info(f"主机: {args.host}, 端口: {args.port} / Host: {args.host}, Port: {args.port}")
        
        # 启动界面 / Launch interface
        try:
            gradio_interface.launch(
                server_name=args.host,
                server_port=args.port,
                share=args.share
            )
        except Exception as e:
            logger.error(f"Web服务器启动失败: {e} / Web server launch failed: {e}")
            logger.error("详细错误信息已记录到 logs/error.log / Detailed error logged to logs/error.log")
            raise
        
    except KeyboardInterrupt:
        logger.info("用户中断程序 / User interrupted the program")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序运行出错: {e} / Program execution error: {e}")
        logger.error("详细错误信息已记录到 logs/error.log / Detailed error logged to logs/error.log")
        if args.debug:
            import traceback
            logger.error(f"完整错误堆栈: {traceback.format_exc()} / Full error traceback: {traceback.format_exc()}")
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()