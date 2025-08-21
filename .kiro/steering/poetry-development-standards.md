# Poetry开发规范 / Poetry Development Standards

## 项目管理 / Project Management

本项目使用**Poetry**作为Python包管理和虚拟环境管理工具。所有的依赖管理、构建和发布都应通过Poetry进行。

This project uses **Poetry** as the Python package management and virtual environment management tool. All dependency management, building, and publishing should be done through Poetry.

## 环境配置 / Environment Configuration

### Poetry安装 / Poetry Installation
```bash
# 安装Poetry / Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 或使用pip安装 / Or install via pip
pip install poetry
```

### 项目初始化 / Project Initialization
```bash
# 初始化新项目 / Initialize new project
poetry init

# 或从现有项目安装依赖 / Or install dependencies from existing project
poetry install
```

## 依赖管理规范 / Dependency Management Standards

### 添加依赖 / Adding Dependencies
```bash
# 添加生产依赖 / Add production dependency
poetry add requests

# 添加开发依赖 / Add development dependency
poetry add --group dev pytest black flake8

# 添加测试依赖 / Add test dependencies
poetry add --group test pytest pytest-cov pytest-mock
```

### pyproject.toml配置示例 / pyproject.toml Configuration Example
```toml
[tool.poetry]
name = "your-project-name"
version = "0.1.0"
description = "项目描述 / Project description"
authors = ["Your Name <your.email@example.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.8"
requests = "^2.28.0"
fastapi = "^0.95.0"

[tool.poetry.group.dev.dependencies]
black = "^23.0.0"
flake8 = "^6.0.0"
mypy = "^1.0.0"
pre-commit = "^3.0.0"

[tool.poetry.group.test.dependencies]
pytest = "^7.0.0"
pytest-cov = "^4.0.0"
pytest-mock = "^3.10.0"
pytest-asyncio = "^0.21.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

## 虚拟环境管理 / Virtual Environment Management

### 虚拟环境操作 / Virtual Environment Operations
```bash
# 激活虚拟环境 / Activate virtual environment
poetry shell

# 在虚拟环境中运行命令 / Run command in virtual environment
poetry run python script.py

# 查看虚拟环境信息 / Show virtual environment info
poetry env info

# 查看虚拟环境路径 / Show virtual environment path
poetry env info --path
```

### 环境变量配置 / Environment Variables Configuration
```bash
# 设置Poetry在项目目录创建虚拟环境 / Configure Poetry to create venv in project directory
poetry config virtualenvs.in-project true

# 设置虚拟环境路径 / Set virtual environment path
poetry config virtualenvs.path ~/.cache/pypoetry/virtualenvs
```

## 测试运行规范 / Testing Standards

### 测试环境要求 / Testing Environment Requirements
- **所有测试必须在Poetry管理的虚拟环境中运行** / All tests must run in Poetry-managed virtual environment
- 使用pytest作为测试框架 / Use pytest as testing framework
- 测试覆盖率要求达到80%以上 / Test coverage should be above 80%

### 测试命令 / Testing Commands
```bash
# 运行所有测试 / Run all tests
poetry run pytest

# 运行测试并生成覆盖率报告 / Run tests with coverage report
poetry run pytest --cov=src --cov-report=html --cov-report=term

# 运行特定测试文件 / Run specific test file
poetry run pytest tests/test_specific.py

# 运行带标记的测试 / Run tests with specific markers
poetry run pytest -m "unit"

# 详细输出模式 / Verbose output mode
poetry run pytest -v

# 并行运行测试 / Run tests in parallel
poetry run pytest -n auto
```

### 测试配置 / Test Configuration
在`pyproject.toml`中配置pytest：
Configure pytest in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html:htmlcov",
    "--cov-fail-under=80"
]
markers = [
    "unit: 单元测试 / Unit tests",
    "integration: 集成测试 / Integration tests",
    "slow: 慢速测试 / Slow tests"
]
```

## 代码质量工具 / Code Quality Tools

### 代码格式化 / Code Formatting
```bash
# 使用Black格式化代码 / Format code with Black
poetry run black src tests

# 检查代码格式 / Check code format
poetry run black --check src tests
```

### 代码检查 / Code Linting
```bash
# 使用flake8检查代码 / Lint code with flake8
poetry run flake8 src tests

# 使用mypy进行类型检查 / Type checking with mypy
poetry run mypy src
```

### 预提交钩子 / Pre-commit Hooks
```bash
# 安装预提交钩子 / Install pre-commit hooks
poetry run pre-commit install

# 运行预提交检查 / Run pre-commit checks
poetry run pre-commit run --all-files
```

## 开发工作流 / Development Workflow

### 日常开发流程 / Daily Development Process
1. **激活虚拟环境** / Activate virtual environment
   ```bash
   poetry shell
   ```

2. **安装/更新依赖** / Install/update dependencies
   ```bash
   poetry install
   ```

3. **运行测试** / Run tests
   ```bash
   poetry run pytest
   ```

4. **代码格式化和检查** / Format and lint code
   ```bash
   poetry run black src tests
   poetry run flake8 src tests
   ```

5. **提交代码前检查** / Pre-commit checks
   ```bash
   poetry run pre-commit run --all-files
   ```

### 构建和发布 / Build and Publish
```bash
# 构建项目 / Build project
poetry build

# 发布到PyPI / Publish to PyPI
poetry publish

# 发布到私有仓库 / Publish to private repository
poetry publish -r private-repo
```

## 最佳实践 / Best Practices

### 依赖版本管理 / Dependency Version Management
- 使用语义化版本约束 / Use semantic versioning constraints
- 定期更新依赖版本 / Regularly update dependencies
- 锁定关键依赖的具体版本 / Pin critical dependency versions

```bash
# 更新依赖 / Update dependencies
poetry update

# 更新特定依赖 / Update specific dependency
poetry update requests

# 显示过时的依赖 / Show outdated dependencies
poetry show --outdated
```

### 环境隔离 / Environment Isolation
- 每个项目使用独立的虚拟环境 / Use separate virtual environment for each project
- 不要在全局环境中安装项目依赖 / Don't install project dependencies globally
- 使用`.python-version`文件指定Python版本 / Use `.python-version` file to specify Python version

### 测试最佳实践 / Testing Best Practices
- 所有测试必须能够在CI/CD环境中运行 / All tests must be runnable in CI/CD environment
- 使用测试数据库和模拟对象 / Use test databases and mock objects
- 编写单元测试、集成测试和端到端测试 / Write unit, integration, and end-to-end tests

---

遵循这些规范将确保项目的依赖管理、环境隔离和测试执行的一致性和可靠性。

Following these standards ensures consistency and reliability in project dependency management, environment isolation, and test execution.