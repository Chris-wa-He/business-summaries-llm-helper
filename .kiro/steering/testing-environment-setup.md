# 测试环境配置规范 / Testing Environment Setup Standards

## 测试环境隔离 / Test Environment Isolation

所有测试必须在Poetry管理的虚拟环境中运行，确保测试环境的一致性和可重复性。

All tests must run in Poetry-managed virtual environments to ensure consistency and reproducibility of the test environment.

## 环境配置检查 / Environment Configuration Verification

### 虚拟环境验证 / Virtual Environment Verification
在运行测试前，确保正确的虚拟环境已激活：

Before running tests, ensure the correct virtual environment is activated:

```bash
# 检查当前Python路径 / Check current Python path
poetry run which python

# 验证Poetry环境 / Verify Poetry environment
poetry env info

# 确认依赖安装状态 / Confirm dependency installation status
poetry show
```

### 测试依赖安装 / Test Dependencies Installation
```bash
# 安装所有依赖（包括测试依赖）/ Install all dependencies (including test dependencies)
poetry install

# 仅安装测试相关依赖 / Install only test-related dependencies
poetry install --only test

# 安装开发和测试依赖 / Install development and test dependencies
poetry install --with dev,test
```

## 测试运行配置 / Test Execution Configuration

### 基础测试命令 / Basic Test Commands
```bash
# 标准测试运行 / Standard test execution
poetry run pytest

# 详细输出测试 / Verbose test output
poetry run pytest -v

# 显示测试覆盖率 / Show test coverage
poetry run pytest --cov=src

# 生成HTML覆盖率报告 / Generate HTML coverage report
poetry run pytest --cov=src --cov-report=html
```

### 测试环境变量 / Test Environment Variables
创建`.env.test`文件用于测试环境配置：

Create `.env.test` file for test environment configuration:

```bash
# 测试数据库配置 / Test database configuration
TEST_DATABASE_URL=sqlite:///test.db
TEST_REDIS_URL=redis://localhost:6379/1

# 测试API配置 / Test API configuration
TEST_API_BASE_URL=http://localhost:8000
TEST_API_KEY=test_api_key

# 日志级别 / Log level
LOG_LEVEL=DEBUG

# 测试模式标识 / Test mode identifier
TESTING=true
```

### pytest配置优化 / pytest Configuration Optimization
在`pyproject.toml`中配置测试环境：

Configure test environment in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
# 测试路径 / Test paths
testpaths = ["tests"]

# 测试文件模式 / Test file patterns
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

# 测试选项 / Test options
addopts = [
    "--strict-markers",
    "--strict-config",
    "--tb=short",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html:htmlcov",
    "--cov-fail-under=80",
    "--durations=10"
]

# 测试标记 / Test markers
markers = [
    "unit: 单元测试，快速执行 / Unit tests, fast execution",
    "integration: 集成测试，需要外部依赖 / Integration tests, requires external dependencies",
    "slow: 慢速测试，执行时间较长 / Slow tests, longer execution time",
    "database: 需要数据库的测试 / Tests requiring database",
    "network: 需要网络连接的测试 / Tests requiring network connection"
]

# 测试发现配置 / Test discovery configuration
minversion = "7.0"
```

## 测试数据管理 / Test Data Management

### 测试数据库配置 / Test Database Configuration
```python
# conftest.py - 测试配置文件 / Test configuration file
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def test_db():
    """
    创建测试数据库会话 / Create test database session
    """
    # 使用内存数据库进行测试 / Use in-memory database for testing
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # 创建表结构 / Create table structure
    from src.models import Base
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def setup_test_environment():
    """
    自动设置测试环境变量 / Automatically setup test environment variables
    """
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    yield
    # 清理环境变量 / Cleanup environment variables
    os.environ.pop("TESTING", None)
    os.environ.pop("DATABASE_URL", None)
```

### 测试数据工厂 / Test Data Factories
```python
# tests/factories.py - 测试数据工厂 / Test data factories
import factory
from src.models import User, Product

class UserFactory(factory.Factory):
    """
    用户测试数据工厂 / User test data factory
    """
    class Meta:
        model = User
    
    name = factory.Faker('name', locale='zh_CN')
    email = factory.Faker('email')
    age = factory.Faker('random_int', min=18, max=80)

class ProductFactory(factory.Factory):
    """
    产品测试数据工厂 / Product test data factory
    """
    class Meta:
        model = Product
    
    name = factory.Faker('word')
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    description = factory.Faker('text', max_nb_chars=200)
```

## 测试执行策略 / Test Execution Strategy

### 分层测试运行 / Layered Test Execution
```bash
# 仅运行单元测试 / Run only unit tests
poetry run pytest -m "unit"

# 运行集成测试 / Run integration tests
poetry run pytest -m "integration"

# 跳过慢速测试 / Skip slow tests
poetry run pytest -m "not slow"

# 运行特定模块测试 / Run specific module tests
poetry run pytest tests/test_user_service.py

# 并行运行测试 / Run tests in parallel
poetry run pytest -n auto
```

### 持续集成配置 / Continuous Integration Configuration
```yaml
# .github/workflows/test.yml
name: 测试流水线 / Test Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: 设置Python环境 / Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: 安装Poetry / Install Poetry
      uses: snok/install-poetry@v1
      with:
        version: latest
        virtualenvs-create: true
        virtualenvs-in-project: true
    
    - name: 安装依赖 / Install dependencies
      run: poetry install
    
    - name: 运行测试 / Run tests
      run: poetry run pytest --cov=src --cov-report=xml
    
    - name: 上传覆盖率报告 / Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## 测试环境监控 / Test Environment Monitoring

### 性能监控 / Performance Monitoring
```bash
# 测试执行时间分析 / Test execution time analysis
poetry run pytest --durations=0

# 内存使用监控 / Memory usage monitoring
poetry run pytest --memray

# 测试覆盖率详细报告 / Detailed coverage report
poetry run pytest --cov=src --cov-report=html --cov-report=term-missing
```

### 测试结果报告 / Test Result Reporting
```bash
# 生成JUnit格式报告 / Generate JUnit format report
poetry run pytest --junitxml=test-results.xml

# 生成HTML测试报告 / Generate HTML test report
poetry run pytest --html=test-report.html --self-contained-html
```

## 故障排除 / Troubleshooting

### 常见问题解决 / Common Issues Resolution

#### 虚拟环境问题 / Virtual Environment Issues
```bash
# 重建虚拟环境 / Rebuild virtual environment
poetry env remove python
poetry install

# 清理Poetry缓存 / Clear Poetry cache
poetry cache clear pypi --all
```

#### 依赖冲突解决 / Dependency Conflict Resolution
```bash
# 检查依赖冲突 / Check dependency conflicts
poetry check

# 更新锁定文件 / Update lock file
poetry lock --no-update

# 强制重新解析依赖 / Force dependency resolution
poetry lock
```

#### 测试环境清理 / Test Environment Cleanup
```bash
# 清理测试缓存 / Clear test cache
poetry run pytest --cache-clear

# 删除覆盖率文件 / Remove coverage files
rm -rf .coverage htmlcov/

# 清理临时测试文件 / Clean temporary test files
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

---

遵循这些测试环境配置规范，确保所有测试在一致、隔离的环境中运行，提高测试的可靠性和可重复性。

Following these test environment configuration standards ensures all tests run in a consistent, isolated environment, improving test reliability and reproducibility.