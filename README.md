# 案例总结生成器 / Case Summary Generator

基于历史总结信息的案例总结生成应用，使用Gradio构建用户界面，集成AWS Bedrock上的多种大语言模型。

A case summary generation application based on historical summary information, built with Gradio UI and integrated with multiple large language models on AWS Bedrock.

## 功能特性 / Features

- 🎯 基于历史参考信息生成专业案例总结 / Generate professional case summaries based on historical references
- 🤖 支持多种AI模型：Claude、Nova、DeepSeek、OpenAI / Support multiple AI models: Claude, Nova, DeepSeek, OpenAI
- 🌐 直观的Web界面，基于Gradio构建 / Intuitive web interface built with Gradio
- ⚙️ 灵活的配置管理系统 / Flexible configuration management system
- 🔐 支持多种AWS认证方式 / Support multiple AWS authentication methods

## 环境要求 / Requirements

- Python 3.8+
- Poetry (包管理器 / Package manager)
- AWS账户和Bedrock访问权限 / AWS account with Bedrock access

## 安装和设置 / Installation and Setup

### 1. 克隆项目 / Clone the project
```bash
git clone <repository-url>
cd case-summary-generator
```

### 2. 安装依赖 / Install dependencies
```bash
# 安装Poetry (如果尚未安装) / Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# 安装项目依赖 / Install project dependencies
poetry install
```

### 3. 配置应用 / Configure Application

#### 创建配置文件 / Create Configuration File
```bash
# 复制配置模板 / Copy configuration template
cp config.yaml.example config.yaml
```

#### 配置AWS凭证 / Configure AWS Credentials

**方式1: 使用AWS Profile (推荐 / Recommended)**
```bash
# 配置AWS CLI
aws configure sso
# 或使用传统方式 / Or use traditional method
aws configure
```

然后在 `config.yaml` 中设置：
```yaml
aws:
  auth_method: "profile"
  profile_name: "default"  # 或您的profile名称
  region: "us-east-1"
```

**方式2: 使用Access Key**
在 `config.yaml` 文件中设置：
```yaml
aws:
  auth_method: "ak_sk"
  access_key_id: "your-access-key"
  secret_access_key: "your-secret-key"
  region: "us-east-1"
```

⚠️ **安全提醒**: `config.yaml` 文件包含敏感信息，已在 `.gitignore` 中排除，不会上传到代码仓库。

### 4. 准备历史参考文件 / Prepare history reference files
创建 `history_references/` 目录并放置您的历史总结文件：
```bash
# 创建历史参考文件目录 / Create history references directory
mkdir -p history_references

# 复制示例文件作为参考 / Copy example files as reference
cp -r history_references_example/* history_references/
```

目录结构示例 / Directory structure example:
```
history_references/
├── category1/
│   ├── case_001.txt
│   └── case_002.md
└── category2/
    └── case_003.txt
```

**注意**: `history_references/` 目录包含业务敏感信息，已在 `.gitignore` 中排除，不会上传到代码仓库。
**Note**: The `history_references/` directory contains business-sensitive information and is excluded in `.gitignore`, so it won't be uploaded to the code repository.

#### 历史文件设置详细说明 / Detailed History Files Setup

**支持的文件格式 / Supported File Formats:**
- `.txt` - 纯文本文件 / Plain text files
- `.md` - Markdown文件 / Markdown files  
- `.markdown` - Markdown文件 / Markdown files

**文件组织建议 / File Organization Recommendations:**
- 按类别分组（技术问题、业务案例、客户服务等）/ Group by category (technical issues, business cases, customer service, etc.)
- 使用描述性的文件名 / Use descriptive file names
- 推荐使用UTF-8编码 / Recommended to use UTF-8 encoding

**安全提醒 / Security Reminder:**
⚠️ 请确保不要将包含敏感业务信息的 `history_references/` 目录提交到公共代码仓库！
⚠️ Please ensure that you do not commit the `history_references/` directory containing sensitive business information to public code repositories!

## 使用方法 / Usage

### Web界面启动 / Web Interface Launch
```bash
# 启动Web应用 / Start web application
poetry run python src/main.py

# 自定义端口和主机 / Custom port and host
poetry run python src/main.py --host 0.0.0.0 --port 8080

# 创建公共链接 / Create public link
poetry run python src/main.py --share

# 启用调试模式 / Enable debug mode
poetry run python src/main.py --debug
```

### 命令行演示 / Command Line Demo
```bash
# 运行命令行演示 / Run CLI demo
poetry run python src/cli_demo.py
```

### 运行测试 / Run tests
```bash
# 运行所有测试 / Run all tests
poetry run pytest

# 运行测试并生成覆盖率报告 / Run tests with coverage report
poetry run pytest --cov=src --cov-report=html

# 运行特定测试 / Run specific tests
poetry run pytest tests/test_config/ -v
```

### 代码格式化 / Code formatting
```bash
# 格式化代码 / Format code
poetry run black src tests

# 检查代码风格 / Check code style
poetry run flake8 src tests

# 类型检查 / Type checking
poetry run mypy src
```

## 项目结构 / Project Structure

```
case-summary-generator/
├── src/                        # 源代码 / Source code
│   ├── config/                 # 配置管理 / Configuration management
│   │   └── config_manager.py   # 配置管理器 / Configuration manager
│   ├── clients/                # 客户端 / Clients
│   │   └── bedrock_client.py   # AWS Bedrock客户端 / AWS Bedrock client
│   ├── processors/             # 数据处理器 / Data processors
│   │   └── history_processor.py # 历史信息处理器 / History processor
│   ├── services/               # 业务服务 / Business services
│   │   ├── app_controller.py   # 应用控制器 / Application controller
│   │   ├── model_manager.py    # 模型管理器 / Model manager
│   │   └── prompt_builder.py   # Prompt构建器 / Prompt builder
│   ├── ui/                     # 用户界面 / User interface
│   │   └── gradio_interface.py # Gradio界面 / Gradio interface
│   ├── main.py                 # 应用入口 / Application entry
│   └── cli_demo.py             # 命令行演示 / CLI demo
├── tests/                      # 测试代码 / Test code
│   ├── unit/                   # 单元测试 / Unit tests
│   ├── integration/            # 集成测试 / Integration tests
│   └── e2e/                    # 端到端测试 / End-to-end tests
├── history_references/         # 历史参考文件 / History reference files
├── config.yaml                 # 配置文件 / Configuration file
├── pyproject.toml              # Poetry配置 / Poetry configuration
└── README.md                   # 项目说明 / Project documentation
```

## 配置说明 / Configuration

### config.yaml 配置文件 / Configuration File
```yaml
# AWS配置 / AWS Configuration
aws:
  auth_method: "profile"  # "profile" 或 "ak_sk"
  profile_name: "default"
  region: "us-east-1"

# 模型配置 / Model Configuration
models:
  claude:
    - id: "anthropic.claude-3-5-sonnet-20241022-v2:0"
      name: "Claude 3.5 Sonnet"
  nova:
    - id: "amazon.nova-pro-v1:0"
      name: "Nova Pro"

# 系统提示词 / System Prompt
system_prompt: |
  你是一个专业的案例总结助手。请根据提供的历史参考信息和新的案例输入，生成一个结构化、专业的案例总结。

# 历史参考文件夹 / History Reference Folder
history_folder: "./history_references"

# 应用设置 / Application Settings
app:
  title: "案例总结生成器 / Case Summary Generator"
  max_tokens: 4000
  temperature: 0.7
```

## 支持的模型 / Supported Models

应用严格限制只支持以下四类模型：
The application strictly supports only the following four types of models:

- **Claude (Anthropic)**: Claude 3 Sonnet, Claude 3 Haiku, Claude 3.5 Sonnet
- **Nova (Amazon)**: Nova Pro, Nova Lite, Nova Micro
- **DeepSeek**: DeepSeek V2.5, DeepSeek V3
- **OpenAI**: GPT-4o, GPT-4 (如果在Bedrock中可用 / if available in Bedrock)

## 故障排除 / Troubleshooting

### AWS凭证问题 / AWS Credentials Issues
```bash
# 检查AWS配置 / Check AWS configuration
aws sts get-caller-identity

# 重新配置AWS凭证 / Reconfigure AWS credentials
aws configure

# 检查Bedrock访问权限 / Check Bedrock access permissions
aws bedrock list-foundation-models --region us-east-1
```

### 依赖问题 / Dependency Issues
```bash
# 重新安装依赖 / Reinstall dependencies
poetry install --no-cache

# 更新依赖 / Update dependencies
poetry update
```

### 测试问题 / Testing Issues
```bash
# 清理测试缓存 / Clear test cache
poetry run pytest --cache-clear

# 运行特定测试模块 / Run specific test module
poetry run pytest tests/test_config/test_config_manager.py -v
```

## 开发指南 / Development Guide

### 开发环境设置 / Development Environment Setup
```bash
# 激活虚拟环境 / Activate virtual environment
poetry shell

# 安装开发依赖 / Install development dependencies
poetry install --with dev,test

# 安装预提交钩子 / Install pre-commit hooks
poetry run pre-commit install
```

### 代码质量检查 / Code Quality Checks
```bash
# 运行所有质量检查 / Run all quality checks
poetry run black src tests
poetry run flake8 src tests
poetry run mypy src
poetry run pytest --cov=src
```

### 添加新功能 / Adding New Features
1. 在相应的模块中添加功能代码 / Add feature code in appropriate module
2. 编写单元测试 / Write unit tests
3. 更新配置文件（如需要）/ Update configuration (if needed)
4. 运行测试确保通过 / Run tests to ensure they pass
5. 更新文档 / Update documentation

## 架构说明 / Architecture

应用采用分层架构设计：
The application uses a layered architecture design:

- **UI层 / UI Layer**: Gradio界面，处理用户交互 / Gradio interface, handles user interaction
- **控制层 / Controller Layer**: AppController，协调各组件 / AppController, coordinates components
- **服务层 / Service Layer**: 业务逻辑处理 / Business logic processing
- **客户端层 / Client Layer**: AWS Bedrock集成 / AWS Bedrock integration
- **配置层 / Configuration Layer**: 配置管理和验证 / Configuration management and validation

## 许可证 / License

[添加许可证信息 / Add license information]

## 贡献 / Contributing

欢迎提交问题和拉取请求！
Issues and pull requests are welcome!