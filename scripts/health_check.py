#!/usr/bin/env python3
"""
生产环境健康检查脚本 / Production Environment Health Check Script
"""

import sys
import os
import time
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def check_python_version():
    """检查Python版本 / Check Python version"""
    print("🐍 检查Python版本... / Checking Python version...")
    
    if sys.version_info < (3, 8, 1):
        print(f"❌ Python版本过低: {sys.version_info} / Python version too low: {sys.version_info}")
        return False
    
    print(f"✅ Python版本: {sys.version_info} / Python version: {sys.version_info}")
    return True

def check_dependencies():
    """检查依赖包 / Check dependencies"""
    print("📦 检查依赖包... / Checking dependencies...")
    
    required_packages = [
        'gradio',
        'boto3', 
        'yaml',
        'pathlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'yaml':
                import yaml
            else:
                __import__(package)
            print(f"✅ {package} 已安装 / {package} installed")
        except ImportError:
            print(f"❌ {package} 未安装 / {package} not installed")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_configuration():
    """检查配置文件 / Check configuration file"""
    print("📝 检查配置文件... / Checking configuration file...")
    
    config_file = Path("config.yaml")
    if not config_file.exists():
        print("❌ config.yaml 文件不存在 / config.yaml file does not exist")
        return False
    
    try:
        from config.config_manager import ConfigManager
        config = ConfigManager()
        config.load_config()
        print("✅ 配置文件格式正确 / Configuration file format is correct")
        return True
    except Exception as e:
        print(f"❌ 配置文件错误: {e} / Configuration file error: {e}")
        return False

def check_aws_connection():
    """检查AWS连接 / Check AWS connection"""
    print("☁️ 检查AWS连接... / Checking AWS connection...")
    
    try:
        from config.config_manager import ConfigManager
        
        config = ConfigManager()
        session = config.get_boto3_session()
        
        # 测试Bedrock连接 / Test Bedrock connection
        client = session.client('bedrock', region_name=config.get_aws_config()['region'])
        models = client.list_foundation_models()
        
        model_count = len(models.get('modelSummaries', []))
        print(f"✅ AWS Bedrock连接成功，发现 {model_count} 个模型 / AWS Bedrock connection successful, found {model_count} models")
        return True
        
    except Exception as e:
        print(f"❌ AWS连接失败: {e} / AWS connection failed: {e}")
        return False

def check_directories():
    """检查必要目录 / Check necessary directories"""
    print("📁 检查必要目录... / Checking necessary directories...")
    
    required_dirs = [
        'logs',
        'history_references', 
        'system_prompts',
        'backups'
    ]
    
    all_exist = True
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name} 目录存在 / {dir_name} directory exists")
        else:
            print(f"⚠️ {dir_name} 目录不存在，正在创建... / {dir_name} directory does not exist, creating...")
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ {dir_name} 目录已创建 / {dir_name} directory created")
            except Exception as e:
                print(f"❌ 创建 {dir_name} 目录失败: {e} / Failed to create {dir_name} directory: {e}")
                all_exist = False
    
    return all_exist

def check_system_resources():
    """检查系统资源 / Check system resources"""
    print("💻 检查系统资源... / Checking system resources...")
    
    # 检查磁盘空间 / Check disk space
    import shutil
    total, used, free = shutil.disk_usage(".")
    free_gb = free // (1024**3)
    
    if free_gb < 1:
        print(f"⚠️ 磁盘空间不足: {free_gb}GB / Insufficient disk space: {free_gb}GB")
        return False
    
    print(f"✅ 可用磁盘空间: {free_gb}GB / Available disk space: {free_gb}GB")
    return True

def run_basic_functionality_test():
    """运行基础功能测试 / Run basic functionality test"""
    print("🧪 运行基础功能测试... / Running basic functionality test...")
    
    try:
        from utils.input_validator import InputValidator
        from services.error_handler import RefinementErrorHandler
        
        # 测试输入验证 / Test input validation
        validator = InputValidator()
        result = validator.validate_user_message("健康检查测试消息")
        if not result.is_valid:
            print("❌ 输入验证测试失败 / Input validation test failed")
            return False
        
        # 测试错误处理 / Test error handling
        error_handler = RefinementErrorHandler()
        error_result = error_handler.handle_error(Exception("健康检查测试"), {"health_check": True})
        if "error_id" not in error_result:
            print("❌ 错误处理测试失败 / Error handling test failed")
            return False
        
        print("✅ 基础功能测试通过 / Basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ 基础功能测试失败: {e} / Basic functionality test failed: {e}")
        return False

def main():
    """主健康检查函数 / Main health check function"""
    print("🏥 开始系统健康检查... / Starting system health check...")
    print("=" * 50)
    
    checks = [
        ("Python版本检查", check_python_version),
        ("依赖包检查", check_dependencies),
        ("配置文件检查", check_configuration),
        ("AWS连接检查", check_aws_connection),
        ("目录结构检查", check_directories),
        ("系统资源检查", check_system_resources),
        ("基础功能测试", run_basic_functionality_test)
    ]
    
    passed_checks = 0
    total_checks = len(checks)
    
    for check_name, check_func in checks:
        try:
            if check_func():
                passed_checks += 1
            else:
                print(f"❌ {check_name} 失败 / {check_name} failed")
        except Exception as e:
            print(f"❌ {check_name} 异常: {e} / {check_name} exception: {e}")
        
        print("-" * 30)
    
    print("=" * 50)
    print(f"📊 健康检查结果: {passed_checks}/{total_checks} 通过 / Health check result: {passed_checks}/{total_checks} passed")
    
    if passed_checks == total_checks:
        print("🎉 系统健康检查全部通过！可以启动应用 / All health checks passed! Ready to start application")
        return 0
    else:
        print("⚠️ 部分健康检查失败，请检查上述错误 / Some health checks failed, please check the errors above")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)