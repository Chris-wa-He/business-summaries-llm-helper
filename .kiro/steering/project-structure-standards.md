# 项目结构规范 / Project Structure Standards

## 标准项目结构 / Standard Project Structure

使用Poetry管理的Python项目应遵循以下目录结构：

Python projects managed with Poetry should follow this directory structure:

```
project-root/
├── pyproject.toml              # Poetry配置文件 / Poetry configuration
├── poetry.lock                 # 依赖锁定文件 / Dependency lock file
├── README.md                   # 项目说明文档 / Project documentation
├── .gitignore                  # Git忽略文件 / Git ignore file
├── .python-version             # Python版本指定 / Python version specification
├── .env.example                # 环境变量示例 / Environment variables example
├── .env.test                   # 测试环境变量 / Test environment variables
├── .pre-commit-config.yaml     # 预提交钩子配置 / Pre-commit hooks config
├── src/                        # 源代码目录 / Source code directory
│   ├── __init__.py
│   ├── main.py                 # 应用入口 / Application entry point
│   ├── config/                 # 配置模块 / Configuration module
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── models/                 # 数据模型 / Data models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/               # 业务逻辑服务 / Business logic services
│   │   ├── __init__.py
│   │   └── user_service.py
│   ├── repositories/           # 数据访问层 / Data access layer
│   │   ├── __init__.py
│   │   └── user_repository.py
│   ├── api/                    # API接口 / API interfaces
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── user_routes.py
│   │   └── dependencies.py
│   └── utils/                  # 工具函数 / Utility functions
│       ├── __init__.py
│       └── helpers.py
├── tests/                      # 测试目录 / Test directory
│   ├── __init__.py
│   ├── conftest.py             # pytest配置 / pytest configuration
│   ├── factories.py            # 测试数据工厂 / Test data factories
│   ├── unit/                   # 单元测试 / Unit tests
│   │   ├── __init__.py
│   │   ├── test_models/
│   │   ├── test_services/
│   │   └── test_utils/
│   ├── integration/            # 集成测试 / Integration tests
│   │   ├── __init__.py
│   │   ├── test_api/
│   │   └── test_database/
│   └── e2e/                    # 端到端测试 / End-to-end tests
│       ├── __init__.py
│       └── test_workflows/
├── docs/                       # 文档目录 / Documentation directory
│   ├── api.md
│   ├── deployment.md
│   └── development.md
├── scripts/                    # 脚本目录 / Scripts directory
│   ├── setup.sh
│   ├── test.sh
│   └── deploy.sh
└── docker/                     # Docker配置 / Docker configuration
    ├── Dockerfile
    └── docker-compose.yml
```

## pyproject.toml配置模板 / pyproject.toml Configuration Template

```toml
[tool.poetry]
name = "your-project-name"
version = "0.1.0"
description = "项目描述 / Project description"
authors = ["Your Name <your.email@example.com>"]
readme = "README.md"
packages = [{include = "src"}]

[tool.poetry.dependencies]
python = "^3.8"
fastapi = "^0.95.0"
uvicorn = "^0.21.0"
sqlalchemy = "^2.0.0"
alembic = "^1.10.0"
pydantic = "^1.10.0"
python-dotenv = "^1.0.0"

[tool.poetry.group.dev.dependencies]
black = "^23.0.0"
flake8 = "^6.0.0"
mypy = "^1.0.0"
pre-commit = "^3.0.0"
isort = "^5.12.0"

[tool.poetry.group.test.dependencies]
pytest = "^7.0.0"
pytest-cov = "^4.0.0"
pytest-mock = "^3.10.0"
pytest-asyncio = "^0.21.0"
httpx = "^0.24.0"
factory-boy = "^3.2.0"

[tool.poetry.scripts]
start = "src.main:main"
dev = "uvicorn src.main:app --reload"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

# Black配置 / Black configuration
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  # 排除目录 / Exclude directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

# isort配置 / isort configuration
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["src"]

# mypy配置 / mypy configuration
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

# pytest配置 / pytest configuration
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

# 覆盖率配置 / Coverage configuration
[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/venv/*",
    "*/.venv/*",
    "*/migrations/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError"
]
```

## 开发环境设置脚本 / Development Environment Setup Scripts

### setup.sh - 环境初始化脚本 / Environment initialization script
```bash
#!/bin/bash
# 项目环境初始化脚本 / Project environment initialization script

echo "正在初始化项目环境... / Initializing project environment..."

# 检查Poetry是否安装 / Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry未安装，正在安装... / Poetry not found, installing..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# 配置Poetry / Configure Poetry
echo "配置Poetry... / Configuring Poetry..."
poetry config virtualenvs.in-project true

# 安装依赖 / Install dependencies
echo "安装项目依赖... / Installing project dependencies..."
poetry install

# 安装预提交钩子 / Install pre-commit hooks
echo "安装预提交钩子... / Installing pre-commit hooks..."
poetry run pre-commit install

# 创建环境变量文件 / Create environment variables file
if [ ! -f .env ]; then
    echo "创建环境变量文件... / Creating environment variables file..."
    cp .env.example .env
fi

echo "环境初始化完成！/ Environment initialization completed!"
echo "运行 'poetry shell' 激活虚拟环境 / Run 'poetry shell' to activate virtual environment"
```

### test.sh - 测试运行脚本 / Test execution script
```bash
#!/bin/bash
# 测试运行脚本 / Test execution script

echo "开始运行测试... / Starting test execution..."

# 激活虚拟环境并运行测试 / Activate virtual environment and run tests
poetry run pytest -v --cov=src --cov-report=html --cov-report=term-missing

# 检查测试结果 / Check test results
if [ $? -eq 0 ]; then
    echo "所有测试通过！/ All tests passed!"
    echo "覆盖率报告已生成在 htmlcov/ 目录 / Coverage report generated in htmlcov/ directory"
else
    echo "测试失败！/ Tests failed!"
    exit 1
fi
```

### lint.sh - 代码质量检查脚本 / Code quality check script
```bash
#!/bin/bash
# 代码质量检查脚本 / Code quality check script

echo "开始代码质量检查... / Starting code quality checks..."

# 代码格式化 / Code formatting
echo "运行Black格式化... / Running Black formatting..."
poetry run black src tests

# 导入排序 / Import sorting
echo "运行isort排序... / Running isort sorting..."
poetry run isort src tests

# 代码检查 / Code linting
echo "运行flake8检查... / Running flake8 linting..."
poetry run flake8 src tests

# 类型检查 / Type checking
echo "运行mypy类型检查... / Running mypy type checking..."
poetry run mypy src

echo "代码质量检查完成！/ Code quality checks completed!"
```

## Git配置 / Git Configuration

### .gitignore模板 / .gitignore Template
```gitignore
# Python相关 / Python related
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Poetry相关 / Poetry related
poetry.lock

# 虚拟环境 / Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# 测试相关 / Testing related
.coverage
htmlcov/
.tox/
.pytest_cache/
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/

# IDE相关 / IDE related
.vscode/
.idea/
*.swp
*.swo
*~

# 数据库 / Database
*.db
*.sqlite3

# 日志文件 / Log files
*.log

# 临时文件 / Temporary files
.DS_Store
Thumbs.db
```

### .pre-commit-config.yaml配置 / Pre-commit configuration
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## 最佳实践 / Best Practices

### 代码组织原则 / Code Organization Principles
1. **单一职责原则** / Single Responsibility Principle
   - 每个模块只负责一个功能 / Each module handles only one functionality
   - 保持类和函数的职责单一 / Keep classes and functions focused

2. **依赖注入** / Dependency Injection
   - 使用依赖注入提高可测试性 / Use dependency injection for better testability
   - 避免硬编码依赖关系 / Avoid hardcoded dependencies

3. **配置管理** / Configuration Management
   - 使用环境变量管理配置 / Use environment variables for configuration
   - 分离开发、测试、生产环境配置 / Separate dev, test, production configurations

### 开发工作流 / Development Workflow
1. **功能开发** / Feature Development
   ```bash
   # 创建功能分支 / Create feature branch
   git checkout -b feature/new-feature
   
   # 开发过程中频繁运行测试 / Run tests frequently during development
   poetry run pytest
   
   # 提交前运行完整检查 / Run full checks before commit
   poetry run pre-commit run --all-files
   ```

2. **代码审查** / Code Review
   - 确保所有测试通过 / Ensure all tests pass
   - 检查代码覆盖率 / Check code coverage
   - 验证代码风格一致性 / Verify code style consistency

---

遵循这些项目结构规范，确保项目的可维护性、可扩展性和团队协作效率。

Following these project structure standards ensures project maintainability, scalability, and team collaboration efficiency.