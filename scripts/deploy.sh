#!/bin/bash
# 生产环境部署脚本 / Production Environment Deployment Script

set -e  # 遇到错误立即退出 / Exit on error

echo "🚀 开始部署案例总结生成器 / Starting Case Summary Generator deployment..."

# 检查环境 / Check environment
echo "📋 检查部署环境... / Checking deployment environment..."

# 检查Python版本 / Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python版本: $python_version / Python version: $python_version"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8, 1) else 1)"; then
    echo "❌ 错误: 需要Python 3.8.1或更高版本 / Error: Python 3.8.1 or higher required"
    exit 1
fi

# 检查Poetry / Check Poetry
if ! command -v poetry &> /dev/null; then
    echo "📦 安装Poetry... / Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "✅ Poetry版本: $(poetry --version) / Poetry version: $(poetry --version)"

# 配置Poetry / Configure Poetry
echo "⚙️ 配置Poetry... / Configuring Poetry..."
poetry config virtualenvs.in-project true

# 安装依赖 / Install dependencies
echo "📦 安装项目依赖... / Installing project dependencies..."
poetry install --only main

# 检查配置文件 / Check configuration file
echo "📝 检查配置文件... / Checking configuration file..."
if [ ! -f "config.yaml" ]; then
    echo "⚠️ 配置文件不存在，从模板创建... / Config file not found, creating from template..."
    cp config.yaml.example config.yaml
    echo "📝 请编辑 config.yaml 文件配置AWS凭证 / Please edit config.yaml to configure AWS credentials"
fi

# 创建必要目录 / Create necessary directories
echo "📁 创建必要目录... / Creating necessary directories..."
mkdir -p logs
mkdir -p history_references
mkdir -p system_prompts
mkdir -p backups

# 运行基础测试 / Run basic tests
echo "🧪 运行部署前测试... / Running pre-deployment tests..."
poetry run pytest tests/test_security.py -v --tb=short

if [ $? -ne 0 ]; then
    echo "❌ 测试失败，部署中止 / Tests failed, deployment aborted"
    exit 1
fi

echo "🎉 部署完成！/ Deployment completed!"
echo "📱 使用以下命令启动应用: / Use the following command to start the application:"
echo "poetry run python src/main.py"