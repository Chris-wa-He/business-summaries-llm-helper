#!/bin/bash
# 生产环境部署脚本 / Production Environment Deployment Script

set -e  # 遇到错误立即退出 / Exit on error

# 颜色定义 / Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数 / Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查系统要求 / Check system requirements
check_requirements() {
    log_info "检查系统要求... / Checking system requirements..."
    
    # 检查Python版本 / Check Python version
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 未安装 / Python 3 is not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
        log_error "需要Python 3.8或更高版本，当前版本: $PYTHON_VERSION / Python 3.8+ required, current: $PYTHON_VERSION"
        exit 1
    fi
    log_success "Python版本检查通过: $PYTHON_VERSION / Python version check passed: $PYTHON_VERSION"
    
    # 检查Poetry / Check Poetry
    if ! command -v poetry &> /dev/null; then
        log_warning "Poetry未安装，正在安装... / Poetry not found, installing..."
        curl -sSL https://install.python-poetry.org | python3 -
        export PATH="$HOME/.local/bin:$PATH"
    fi
    log_success "Poetry检查通过 / Poetry check passed"
    
    # 检查AWS CLI / Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_warning "AWS CLI未安装，请手动安装 / AWS CLI not found, please install manually"
    else
        log_success "AWS CLI检查通过 / AWS CLI check passed"
    fi
}

# 环境变量验证 / Environment variable validation
validate_environment() {
    log_info "验证环境变量... / Validating environment variables..."
    
    # 检查必要的环境变量 / Check required environment variables
    if [[ -z "${DEPLOYMENT_ENV:-}" ]]; then
        export DEPLOYMENT_ENV="production"
        log_warning "DEPLOYMENT_ENV未设置，使用默认值: production / DEPLOYMENT_ENV not set, using default: production"
    fi
    
    if [[ -z "${AWS_REGION:-}" ]]; then
        export AWS_REGION="us-east-1"
        log_warning "AWS_REGION未设置，使用默认值: us-east-1 / AWS_REGION not set, using default: us-east-1"
    fi
    
    log_success "环境变量验证完成 / Environment validation completed"
}

# 安装依赖 / Install dependencies
install_dependencies() {
    log_info "安装项目依赖... / Installing project dependencies..."
    
    # 配置Poetry / Configure Poetry
    poetry config virtualenvs.in-project true
    
    # 安装依赖 / Install dependencies
    poetry install --only main
    
    log_success "依赖安装完成 / Dependencies installed successfully"
}

# 配置文件设置 / Configuration setup
setup_configuration() {
    log_info "设置配置文件... / Setting up configuration files..."
    
    # 检查配置文件 / Check configuration file
    if [[ ! -f "config.yaml" ]]; then
        if [[ -f "config.yaml.example" ]]; then
            cp config.yaml.example config.yaml
            log_warning "已从示例创建配置文件，请检查并修改 / Configuration file created from example, please review and modify"
        else
            log_error "配置文件不存在 / Configuration file not found"
            exit 1
        fi
    fi
    
    # 创建必要的目录 / Create necessary directories
    mkdir -p logs
    mkdir -p system_prompts
    mkdir -p history_references
    mkdir -p personalized_prompts
    mkdir -p backups
    
    log_success "配置设置完成 / Configuration setup completed"
}

# AWS连接测试 / AWS connection test
test_aws_connection() {
    log_info "测试AWS连接... / Testing AWS connection..."
    
    # 测试AWS凭证 / Test AWS credentials
    if poetry run python -c "
import boto3
try:
    session = boto3.Session()
    sts = session.client('sts')
    identity = sts.get_caller_identity()
    print(f'AWS连接成功，用户: {identity.get(\"Arn\", \"Unknown\")}')
except Exception as e:
    print(f'AWS连接失败: {e}')
    exit(1)
"; then
        log_success "AWS连接测试通过 / AWS connection test passed"
    else
        log_error "AWS连接测试失败 / AWS connection test failed"
        exit 1
    fi
    
    # 测试Bedrock访问 / Test Bedrock access
    if poetry run python -c "
import boto3
try:
    session = boto3.Session()
    bedrock = session.client('bedrock', region_name='${AWS_REGION}')
    models = bedrock.list_foundation_models()
    print(f'Bedrock访问成功，可用模型数: {len(models.get(\"modelSummaries\", []))}')
except Exception as e:
    print(f'Bedrock访问失败: {e}')
    exit(1)
"; then
        log_success "Bedrock访问测试通过 / Bedrock access test passed"
    else
        log_error "Bedrock访问测试失败 / Bedrock access test failed"
        exit 1
    fi
}

# 运行测试 / Run tests
run_tests() {
    log_info "运行测试套件... / Running test suite..."
    
    # 安装测试依赖 / Install test dependencies
    poetry install --with test
    
    # 运行测试 / Run tests
    if poetry run pytest tests/ -v --tb=short; then
        log_success "所有测试通过 / All tests passed"
    else
        log_error "测试失败 / Tests failed"
        exit 1
    fi
}

# 健康检查 / Health check
health_check() {
    log_info "执行健康检查... / Performing health check..."
    
    # 运行健康检查脚本 / Run health check script
    if poetry run python scripts/health_check.py; then
        log_success "健康检查通过 / Health check passed"
    else
        log_error "健康检查失败 / Health check failed"
        exit 1
    fi
}

# 启动应用 / Start application
start_application() {
    log_info "启动应用... / Starting application..."
    
    # 设置生产环境变量 / Set production environment variables
    export PYTHONPATH="${PWD}/src:${PYTHONPATH:-}"
    export LOG_LEVEL="${LOG_LEVEL:-INFO}"
    
    # 启动应用 / Start application
    log_success "应用启动命令: poetry run python src/main.py / Application start command: poetry run python src/main.py"
    log_info "使用以下命令启动应用 / Use the following command to start the application:"
    echo "poetry run python src/main.py --host 0.0.0.0 --port 8080"
}

# 主函数 / Main function
main() {
    log_info "开始部署案例总结生成器 v2.0.0 / Starting deployment of Case Summary Generator v2.0.0"
    log_info "部署环境: ${DEPLOYMENT_ENV} / Deployment environment: ${DEPLOYMENT_ENV}"
    
    check_requirements
    validate_environment
    install_dependencies
    setup_configuration
    test_aws_connection
    
    # 可选的测试运行 / Optional test run
    if [[ "${RUN_TESTS:-true}" == "true" ]]; then
        run_tests
    else
        log_warning "跳过测试运行 / Skipping test run"
    fi
    
    health_check
    start_application
    
    log_success "部署完成！/ Deployment completed!"
    log_info "应用已准备就绪，可以启动服务 / Application is ready to start"
}

# 脚本入口 / Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi