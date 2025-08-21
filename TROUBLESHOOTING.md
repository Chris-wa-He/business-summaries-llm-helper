# 故障排除指南 / Troubleshooting Guide

本文档提供了案例总结生成器常见问题的解决方案和故障排除步骤。

This document provides solutions and troubleshooting steps for common issues with the Case Summary Generator.

## 目录 / Table of Contents

1. [安装和环境问题 / Installation and Environment Issues](#安装和环境问题--installation-and-environment-issues)
2. [AWS配置问题 / AWS Configuration Issues](#aws配置问题--aws-configuration-issues)
3. [模型调用问题 / Model Invocation Issues](#模型调用问题--model-invocation-issues)
4. [文件读取问题 / File Reading Issues](#文件读取问题--file-reading-issues)
5. [界面和交互问题 / UI and Interaction Issues](#界面和交互问题--ui-and-interaction-issues)
6. [性能问题 / Performance Issues](#性能问题--performance-issues)
7. [测试问题 / Testing Issues](#测试问题--testing-issues)

## 安装和环境问题 / Installation and Environment Issues

### Poetry安装失败 / Poetry Installation Failed

**问题描述 / Problem Description:**
```bash
curl: command not found
# 或者 / or
Permission denied
```

**解决方案 / Solution:**
```bash
# 方法1：使用pip安装 / Method 1: Install using pip
pip install poetry

# 方法2：使用homebrew (macOS) / Method 2: Use homebrew (macOS)
brew install poetry

# 方法3：手动下载安装脚本 / Method 3: Manually download installation script
wget https://install.python-poetry.org/install-poetry.py
python install-poetry.py
```

### 依赖安装失败 / Dependency Installation Failed

**问题描述 / Problem Description:**
```bash
poetry install
# 报错：Package not found / Error: Package not found
```

**解决方案 / Solution:**
```bash
# 清理缓存 / Clear cache
poetry cache clear pypi --all

# 更新Poetry / Update Poetry
poetry self update

# 重新安装依赖 / Reinstall dependencies
poetry install --no-cache

# 如果仍有问题，删除虚拟环境重建 / If still issues, remove and recreate virtual environment
poetry env remove python
poetry install
```

### Python版本不兼容 / Python Version Incompatible

**问题描述 / Problem Description:**
```bash
The current project's Python requirement (>=3.8) is not compatible with some of the required packages.
```

**解决方案 / Solution:**
```bash
# 检查Python版本 / Check Python version
python --version

# 安装Python 3.8+ / Install Python 3.8+
# macOS:
brew install python@3.8

# Ubuntu:
sudo apt update
sudo apt install python3.8

# 指定Python版本 / Specify Python version
poetry env use python3.8
poetry install
```

## AWS配置问题 / AWS Configuration Issues

### AWS凭证未配置 / AWS Credentials Not Configured

**问题描述 / Problem Description:**
```
NoCredentialsError: Unable to locate credentials
```

**解决方案 / Solution:**

#### 方法1：配置AWS CLI / Method 1: Configure AWS CLI
```bash
# 安装AWS CLI / Install AWS CLI
pip install awscli

# 配置凭证 / Configure credentials
aws configure
# 输入Access Key ID, Secret Access Key, Region, Output format

# 或使用SSO / Or use SSO
aws configure sso
```

#### 方法2：使用环境变量 / Method 2: Use Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1
```

#### 方法3：修改config.yaml / Method 3: Modify config.yaml
```yaml
aws:
  auth_method: "ak_sk"
  access_key_id: "your-access-key"
  secret_access_key: "your-secret-key"
  region: "us-east-1"
```

### AWS区域不支持Bedrock / AWS Region Does Not Support Bedrock

**问题描述 / Problem Description:**
```
InvalidRegionError: Bedrock is not available in region 'ap-southeast-1'
```

**解决方案 / Solution:**
```bash
# 检查Bedrock支持的区域 / Check Bedrock supported regions
aws bedrock list-foundation-models --region us-east-1

# 更新config.yaml中的区域 / Update region in config.yaml
aws:
  region: "us-east-1"  # 或其他支持Bedrock的区域 / or other Bedrock-supported region
```

**支持Bedrock的区域 / Bedrock Supported Regions:**
- us-east-1 (N. Virginia)
- us-west-2 (Oregon)
- eu-west-1 (Ireland)
- ap-southeast-1 (Singapore)
- ap-northeast-1 (Tokyo)

### AWS权限不足 / Insufficient AWS Permissions

**问题描述 / Problem Description:**
```
AccessDeniedException: User is not authorized to perform: bedrock:ListFoundationModels
```

**解决方案 / Solution:**

确保您的AWS用户或角色具有以下权限：
Ensure your AWS user or role has the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:ListFoundationModels",
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "*"
        }
    ]
}
```

## 模型调用问题 / Model Invocation Issues

### 模型不可用 / Model Not Available

**问题描述 / Problem Description:**
```
ModelNotAvailableError: Model 'anthropic.claude-3-sonnet' is not available
```

**解决方案 / Solution:**
```bash
# 检查可用模型 / Check available models
aws bedrock list-foundation-models --region us-east-1

# 在应用中刷新模型列表 / Refresh model list in application
# 点击界面上的"刷新模型"按钮 / Click "Refresh Models" button in UI
```

### 模型调用超时 / Model Invocation Timeout

**问题描述 / Problem Description:**
```
TimeoutError: Model invocation timed out after 60 seconds
```

**解决方案 / Solution:**
1. **检查网络连接 / Check Network Connection**
2. **减少输入长度 / Reduce Input Length**
3. **降低max_tokens设置 / Lower max_tokens Setting**
4. **重试请求 / Retry Request**

### 模型响应格式错误 / Model Response Format Error

**问题描述 / Problem Description:**
```
ResponseFormatError: Unable to parse model response
```

**解决方案 / Solution:**
1. **检查系统提示词格式 / Check System Prompt Format**
2. **验证输入内容编码 / Verify Input Content Encoding**
3. **尝试不同的模型 / Try Different Models**

## 文件读取问题 / File Reading Issues

### 历史文件夹不存在 / History Folder Not Found

**问题描述 / Problem Description:**
```
HistoryProcessingError: History folder not found: ./history_references
```

**解决方案 / Solution:**
```bash
# 创建历史文件夹 / Create history folder
mkdir -p history_references

# 复制示例文件 / Copy example files
cp -r history_references_example/* history_references/

# 或修改config.yaml中的路径 / Or modify path in config.yaml
history_folder: "/path/to/your/history/files"
```

### 文件编码问题 / File Encoding Issues

**问题描述 / Problem Description:**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte
```

**解决方案 / Solution:**
```bash
# 转换文件编码为UTF-8 / Convert file encoding to UTF-8
iconv -f GBK -t UTF-8 filename.txt > filename_utf8.txt

# 或使用Python脚本转换 / Or use Python script to convert
python -c "
import codecs
with codecs.open('filename.txt', 'r', 'gbk') as f:
    content = f.read()
with codecs.open('filename_utf8.txt', 'w', 'utf-8') as f:
    f.write(content)
"
```

### 文件权限问题 / File Permission Issues

**问题描述 / Problem Description:**
```
PermissionError: [Errno 13] Permission denied: 'history_references/case.txt'
```

**解决方案 / Solution:**
```bash
# 修改文件权限 / Change file permissions
chmod 644 history_references/*.txt
chmod 755 history_references/

# 或修改所有者 / Or change owner
sudo chown -R $USER:$USER history_references/
```

## 界面和交互问题 / UI and Interaction Issues

### Gradio界面无法访问 / Gradio Interface Not Accessible

**问题描述 / Problem Description:**
- 浏览器显示"无法访问此网站" / Browser shows "This site can't be reached"
- 连接被拒绝 / Connection refused

**解决方案 / Solution:**
```bash
# 检查端口是否被占用 / Check if port is in use
lsof -i :7860

# 使用不同端口 / Use different port
poetry run python src/main.py --port 8080

# 允许外部访问 / Allow external access
poetry run python src/main.py --host 0.0.0.0

# 检查防火墙设置 / Check firewall settings
sudo ufw allow 7860
```

### 界面加载缓慢 / UI Loading Slowly

**问题描述 / Problem Description:**
- 界面响应缓慢 / UI responds slowly
- 模型列表加载时间长 / Model list takes long to load

**解决方案 / Solution:**
1. **启用模型缓存 / Enable Model Caching**
```yaml
# config.yaml
advanced:
  enable_model_cache: true
  cache_ttl_minutes: 60
```

2. **减少历史文件数量 / Reduce History Files**
3. **优化网络连接 / Optimize Network Connection**

### 生成结果显示异常 / Generation Results Display Issues

**问题描述 / Problem Description:**
- 中文显示乱码 / Chinese characters display as garbled text
- 格式混乱 / Format is messy

**解决方案 / Solution:**
1. **检查浏览器编码设置 / Check Browser Encoding Settings**
2. **清除浏览器缓存 / Clear Browser Cache**
3. **尝试不同浏览器 / Try Different Browser**

## 性能问题 / Performance Issues

### 内存使用过高 / High Memory Usage

**问题描述 / Problem Description:**
```
MemoryError: Unable to allocate memory
```

**解决方案 / Solution:**
1. **减少max_tokens设置 / Reduce max_tokens Setting**
```yaml
app:
  max_tokens: 2000  # 从4000减少到2000 / Reduce from 4000 to 2000
```

2. **限制历史文件大小 / Limit History File Size**
```yaml
advanced:
  max_file_size_mb: 5  # 限制单文件5MB / Limit single file to 5MB
  max_history_files: 50  # 限制文件数量 / Limit number of files
```

3. **清理系统内存 / Clean System Memory**
```bash
# Linux
sudo sync && sudo sysctl vm.drop_caches=3

# macOS
sudo purge
```

### 响应时间过长 / Response Time Too Long

**问题描述 / Problem Description:**
- 生成总结耗时超过2分钟 / Summary generation takes over 2 minutes

**解决方案 / Solution:**
1. **优化输入内容 / Optimize Input Content**
   - 减少历史参考信息长度 / Reduce history reference length
   - 简化案例描述 / Simplify case description

2. **调整模型参数 / Adjust Model Parameters**
```yaml
app:
  max_tokens: 2000
  temperature: 0.5  # 降低温度可能提高速度 / Lower temperature may improve speed
```

3. **选择更快的模型 / Choose Faster Models**
   - 使用Nova Micro而不是Claude 3.5 Sonnet / Use Nova Micro instead of Claude 3.5 Sonnet

## 测试问题 / Testing Issues

### 测试运行失败 / Test Execution Failed

**问题描述 / Problem Description:**
```bash
poetry run pytest
# 多个测试失败 / Multiple test failures
```

**解决方案 / Solution:**
```bash
# 清理测试缓存 / Clear test cache
poetry run pytest --cache-clear

# 重新安装测试依赖 / Reinstall test dependencies
poetry install --with test

# 运行特定测试 / Run specific tests
poetry run pytest tests/unit/ -v

# 跳过集成测试 / Skip integration tests
poetry run pytest tests/unit/ tests/integration/test_basic_integration.py -v
```

### 测试覆盖率不足 / Insufficient Test Coverage

**问题描述 / Problem Description:**
```
FAIL Required test coverage of 80% not reached. Total coverage: 45%
```

**解决方案 / Solution:**
1. **临时降低覆盖率要求 / Temporarily Lower Coverage Requirement**
```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = [
    "--cov-fail-under=40"  # 临时降低到40% / Temporarily lower to 40%
]
```

2. **运行不检查覆盖率的测试 / Run Tests Without Coverage Check**
```bash
poetry run pytest --no-cov
```

## 日志和调试 / Logging and Debugging

### 启用详细日志 / Enable Verbose Logging

```yaml
# config.yaml
logging:
  level: "DEBUG"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/app.log"
```

### 查看日志文件 / View Log Files

```bash
# 创建日志目录 / Create log directory
mkdir -p logs

# 实时查看日志 / View logs in real-time
tail -f logs/app.log

# 搜索错误日志 / Search error logs
grep -i error logs/app.log
```

## 获取帮助 / Getting Help

### 收集诊断信息 / Collect Diagnostic Information

运行以下命令收集系统信息：
Run the following commands to collect system information:

```bash
# 系统信息 / System information
python --version
poetry --version
aws --version

# 依赖信息 / Dependency information
poetry show

# AWS配置 / AWS configuration
aws configure list
aws sts get-caller-identity

# 测试连接 / Test connection
aws bedrock list-foundation-models --region us-east-1
```

### 常用调试命令 / Common Debugging Commands

```bash
# 检查配置文件 / Check configuration file
poetry run python -c "
from src.config.config_manager import ConfigManager
config = ConfigManager('config.yaml')
print('Config loaded successfully')
print(f'History folder: {config.get_history_folder()}')
"

# 测试历史文件读取 / Test history file reading
poetry run python -c "
from src.processors.history_processor import HistoryProcessor
processor = HistoryProcessor('./history_references')
files = processor.load_history_files()
print(f'Loaded {len(files)} history files')
"

# 测试AWS连接 / Test AWS connection
poetry run python -c "
from src.clients.bedrock_client import BedrockClient
from src.config.config_manager import ConfigManager
config = ConfigManager('config.yaml')
client = BedrockClient(config.get_aws_credentials(), config.get_aws_region())
models = client.list_foundation_models()
print(f'Found {len(models)} models')
"
```

### 联系支持 / Contact Support

如果以上解决方案都无法解决您的问题，请：
If none of the above solutions resolve your issue, please:

1. **收集诊断信息** / Collect diagnostic information
2. **查看日志文件** / Check log files
3. **创建GitHub Issue** / Create GitHub Issue
4. **提供详细的错误信息和复现步骤** / Provide detailed error information and reproduction steps

---

**注意 / Note:** 本指南会持续更新，如果您遇到新的问题或有改进建议，欢迎提交Issue或Pull Request。

This guide is continuously updated. If you encounter new issues or have improvement suggestions, please submit an Issue or Pull Request.
