#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令行演示程序 / Command Line Demo

用于测试核心功能的简化命令行界面
Simplified command line interface for testing core functionality
"""

import sys
import logging
from pathlib import Path

# 添加src目录到Python路径 / Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from services.app_controller import AppController, CaseSummaryError


def setup_logging():
    """设置日志配置 / Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main():
    """主函数 / Main function"""
    setup_logging()
    logger = logging.getLogger(__name__)

    print("🚀 案例总结生成器 - 命令行演示 / Case Summary Generator - CLI Demo")
    print("=" * 60)

    try:
        # 初始化应用控制器 / Initialize app controller
        print("📋 正在初始化应用... / Initializing application...")
        app_controller = AppController()

        # 检查初始化状态 / Check initialization status
        is_initialized, status_message = app_controller.get_initialization_status()
        if not is_initialized:
            print(f"❌ 初始化失败: {status_message}")
            return

        print(f"✅ {status_message}")

        # 初始化模型 / Initialize models
        print("🤖 正在加载模型列表... / Loading model list...")
        try:
            models = app_controller.initialize_models()
            model_count = sum(
                len(category_models) for category_models in models.values()
            )
            print(
                f"✅ 成功加载 {model_count} 个模型 / Successfully loaded {model_count} models"
            )

            # 显示可用模型 / Show available models
            print("\n📋 可用模型 / Available Models:")
            for category, category_models in models.items():
                if category_models:
                    print(f"  {category.upper()}:")
                    for model in category_models[:2]:  # 只显示前2个 / Only show first 2
                        display_name = model.get(
                            "displayName", model.get("modelId", "Unknown")
                        )
                        print(f"    - {display_name}")
                    if len(category_models) > 2:
                        print(
                            f"    ... 还有 {len(category_models) - 2} 个模型 / ... and {len(category_models) - 2} more"
                        )

        except Exception as e:
            print(f"⚠️  模型加载失败，使用默认配置: {e}")

        # 获取默认模型 / Get default model
        default_model = app_controller.get_default_model()
        print(f"\n🎯 默认模型: {default_model} / Default model: {default_model}")

        # 交互式演示 / Interactive demo
        print("\n" + "=" * 60)
        print("💡 演示案例总结生成 / Demo Case Summary Generation")
        print("=" * 60)

        # 示例案例 / Example case
        sample_case = """
用户反映在使用我们的在线购物平台时遇到了支付问题。具体表现为：
1. 在结算页面点击"确认支付"按钮后，页面长时间加载
2. 最终显示"支付超时"错误信息
3. 但是用户的银行账户已经被扣款
4. 订单状态显示为"待支付"

用户联系客服后，客服查询发现支付网关返回了成功状态，但订单系统没有收到确认信息。
这导致了订单状态不一致的问题。

需要分析问题原因并提供解决方案。
        """.strip()

        print("📝 示例案例输入:")
        print("-" * 40)
        print(sample_case)
        print("-" * 40)

        print(f"\n🔄 正在使用模型 {default_model} 生成总结...")

        try:
            # 生成总结 / Generate summary
            summary = app_controller.process_case_summary(
                case_input=sample_case, model_id=default_model
            )

            print("\n📄 生成的案例总结:")
            print("=" * 60)
            print(summary)
            print("=" * 60)
            print("\n✅ 演示完成！/ Demo completed!")

        except CaseSummaryError as e:
            print(f"\n❌ 总结生成失败: {e}")
            print("💡 请检查AWS凭证配置和网络连接")

    except CaseSummaryError as e:
        print(f"❌ 应用启动失败: {e}")
        print("💡 请检查配置文件和AWS凭证设置")
    except KeyboardInterrupt:
        print("\n👋 演示已停止")
    except Exception as e:
        print(f"❌ 未知错误: {e}")


if __name__ == "__main__":
    main()
