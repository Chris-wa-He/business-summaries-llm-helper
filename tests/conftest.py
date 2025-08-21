# -*- coding: utf-8 -*-
"""
pytest配置文件 / pytest configuration file

提供测试环境的全局配置和fixture定义。
Provides global configuration and fixture definitions for the test environment.
"""

import pytest
import os
import sys
from pathlib import Path

# 添加src目录到Python路径 / Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(autouse=True)
def setup_test_environment():
    """
    自动设置测试环境变量 / Automatically setup test environment variables
    """
    os.environ["TESTING"] = "true"
    yield
    # 清理环境变量 / Cleanup environment variables
    os.environ.pop("TESTING", None)


@pytest.fixture
def sample_config():
    """
    提供测试用的配置数据 / Provide test configuration data
    """
    return {
        "aws": {
            "auth_method": "profile",
            "profile_name": "test",
            "region": "us-east-1"
        },
        "system_prompt": "测试系统提示词 / Test system prompt",
        "history_folder": "./test_history",
        "app": {
            "title": "测试应用 / Test Application",
            "max_tokens": 1000,
            "temperature": 0.5
        }
    }