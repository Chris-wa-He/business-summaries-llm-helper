# 开发者指南 / Developer Guide

## 架构概述 / Architecture Overview

交互式内容优化功能采用分层架构设计，主要包含以下组件：

The Interactive Content Refinement feature uses a layered architecture design, mainly including the following components:

```
UI Layer (Gradio Interface)
    ↓
Controller Layer (RefinementController)
    ↓
Service Layer (ConversationService, VersionService, ModificationService)
    ↓
Storage Layer (ConversationStore, VersionStore)
```

## 核心组件 / Core Components

### 1. RefinementController

优化控制器，协调所有交互式优化功能。

Refinement controller that coordinates all interactive refinement functions.

```python
from src.services.refinement_controller import RefinementController

# 初始化控制器
controller = RefinementController(app_controller)

# 启动优化会话
session_id = await controller.start_refinement_session(content, user_id)

# 处理用户消息
result = await controller.process_user_message(message, session_id)
```

### 2. ConversationService

对话服务，管理用户与AI的对话会话。

Conversation service that manages user-AI conversation sessions.

```python
from src.services.conversation_service import ConversationService

service = ConversationService()

# 创建会话
session_id = service.create_session(user_id, initial_content)

# 添加消息
service.add_message(session_id, message)

# 获取对话历史
history = service.get_conversation_history(session_id)
```

### 3. VersionService

版本服务，管理内容版本和历史记录。

Version service that manages content versions and history.

```python
from src.services.version_service import VersionService

service = VersionService()

# 创建版本
version_id = service.create_version(session_id, content, modification_type)

# 获取版本列表
versions = service.get_version_list(session_id)

# 版本回退
content = service.revert_to_version(session_id, version_id)
```

### 4. ModificationService

修改服务，处理内容修改请求。

Modification service that handles content modification requests.

```python
from src.services.modification_service import ModificationService

service = ModificationService(bedrock_client)

# 处理修改请求
result = await service.process_modification_request(
    user_request, current_content, context
)
```

## 数据模型 / Data Models

### ConversationMessage

```python
@dataclass
class ConversationMessage:
    id: str
    session_id: str
    sender: str  # 'user' or 'ai'
    content: str
    timestamp: datetime
    message_type: str
    metadata: Dict[str, Any]
```

### ContentVersion

```python
@dataclass
class ContentVersion:
    id: str
    session_id: str
    content: str
    version_number: int
    parent_version_id: Optional[str]
    modification_type: str
    created_at: datetime
    metadata: Dict[str, Any]
```

## API接口 / API Interfaces

### 启动优化会话 / Start Refinement Session

```python
async def start_refinement_session(
    initial_content: str, 
    user_id: str
) -> str:
    """
    启动新的优化会话
    Start a new refinement session
    
    Args:
        initial_content: 初始内容
        user_id: 用户ID
        
    Returns:
        session_id: 会话ID
    """
```

### 处理用户消息 / Process User Message

```python
async def process_user_message(
    message: str, 
    session_id: str
) -> Dict[str, Any]:
    """
    处理用户修改请求
    Process user modification request
    
    Args:
        message: 用户消息
        session_id: 会话ID
        
    Returns:
        result: 处理结果，包含修改后的内容和AI响应
    """
```

### 获取版本历史 / Get Version History

```python
def get_version_history(session_id: str) -> List[Dict]:
    """
    获取会话的版本历史
    Get version history for a session
    
    Args:
        session_id: 会话ID
        
    Returns:
        versions: 版本列表
    """
```

## 扩展开发 / Extension Development

### 添加新的修改类型 / Add New Modification Types

1. 在`ModificationType`枚举中添加新类型：

```python
class ModificationType(Enum):
    CUSTOM_TYPE = "custom_type"
```

2. 在`ModificationService`中实现处理逻辑：

```python
async def handle_custom_modification(self, content: str, instruction: str) -> str:
    # 实现自定义修改逻辑
    pass
```

### 自定义存储后端 / Custom Storage Backend

实现存储接口：

```python
class CustomConversationStore:
    def save_session(self, session: ConversationSession) -> bool:
        # 实现自定义存储逻辑
        pass
    
    def load_session(self, session_id: str) -> Optional[ConversationSession]:
        # 实现自定义加载逻辑
        pass
```

### 添加新的UI组件 / Add New UI Components

在Gradio界面中添加组件：

```python
def create_custom_refinement_component(self):
    with gr.Column():
        custom_input = gr.Textbox(label="自定义输入")
        custom_button = gr.Button("自定义操作")
        
        custom_button.click(
            fn=self.handle_custom_operation,
            inputs=[custom_input],
            outputs=[self.output_area]
        )
```

## 测试指南 / Testing Guide

### 单元测试 / Unit Tests

```python
import pytest
from src.services.conversation_service import ConversationService

class TestConversationService:
    def test_create_session(self):
        service = ConversationService()
        session_id = service.create_session("user_1", "test content")
        assert session_id is not None
```

### 集成测试 / Integration Tests

```python
@pytest.mark.asyncio
async def test_refinement_workflow():
    controller = RefinementController(mock_app_controller)
    
    # 启动会话
    session_id = await controller.start_refinement_session("content", "user")
    
    # 处理消息
    result = await controller.process_user_message("modify request", session_id)
    
    assert result['success'] is True
```

### 性能测试 / Performance Tests

```python
def test_performance_benchmark():
    validator = InputValidator()
    
    start_time = time.time()
    for i in range(100):
        validator.validate_user_message(f"test message {i}")
    end_time = time.time()
    
    assert (end_time - start_time) < 1.0  # 应在1秒内完成
```

## 配置管理 / Configuration Management

### 环境配置 / Environment Configuration

```yaml
# config.yaml
interactive_refinement:
  max_sessions_per_user: 5
  session_timeout: 3600
  max_versions_per_session: 50
  enable_personalization: true
  
  # 性能配置
  performance:
    max_concurrent_requests: 10
    cache_ttl: 1800
    
  # 安全配置
  security:
    input_validation: true
    max_message_length: 2000
```

### 运行时配置 / Runtime Configuration

```python
from src.config.config_manager import ConfigManager

config = ConfigManager()
refinement_config = config.get_refinement_config()

max_sessions = refinement_config.get('max_sessions_per_user', 5)
```

## 部署指南 / Deployment Guide

### 环境要求 / Environment Requirements

- Python 3.8+
- Poetry for dependency management
- AWS Bedrock access
- Sufficient memory for concurrent sessions

### 部署步骤 / Deployment Steps

1. **安装依赖** / Install Dependencies
```bash
poetry install
```

2. **配置环境** / Configure Environment
```bash
cp config.yaml.example config.yaml
# 编辑配置文件
```

3. **运行测试** / Run Tests
```bash
poetry run pytest
```

4. **启动应用** / Start Application
```bash
poetry run python src/main.py
```

### 监控和日志 / Monitoring and Logging

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('refinement.log'),
        logging.StreamHandler()
    ]
)
```

## 最佳实践 / Best Practices

### 代码规范 / Code Standards

1. **遵循PEP 8代码风格** / Follow PEP 8 code style
2. **使用类型注解** / Use type annotations
3. **编写文档字符串** / Write docstrings
4. **保持函数简洁** / Keep functions concise

### 错误处理 / Error Handling

```python
try:
    result = await process_modification(request)
except ValidationError as e:
    logger.warning(f"Validation failed: {e}")
    return {"success": False, "error": "Invalid input"}
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return {"success": False, "error": "Internal error"}
```

### 性能优化 / Performance Optimization

1. **使用异步处理** / Use asynchronous processing
2. **实现智能缓存** / Implement smart caching
3. **优化数据库查询** / Optimize database queries
4. **监控内存使用** / Monitor memory usage

## 故障排除 / Troubleshooting

### 常见问题 / Common Issues

**问题：会话创建失败**
**Issue: Session creation fails**

解决方案：检查存储权限和磁盘空间
Solution: Check storage permissions and disk space

**问题：AI响应缓慢**
**Issue: Slow AI responses**

解决方案：检查AWS Bedrock连接和配额
Solution: Check AWS Bedrock connection and quotas

**问题：版本历史丢失**
**Issue: Version history lost**

解决方案：检查存储配置和备份机制
Solution: Check storage configuration and backup mechanisms

### 调试技巧 / Debugging Tips

1. **启用详细日志** / Enable verbose logging
2. **使用调试模式** / Use debug mode
3. **检查网络连接** / Check network connectivity
4. **验证配置文件** / Validate configuration files

## 贡献指南 / Contributing Guide

### 开发流程 / Development Workflow

1. Fork项目仓库 / Fork the repository
2. 创建功能分支 / Create feature branch
3. 编写代码和测试 / Write code and tests
4. 提交Pull Request / Submit Pull Request
5. 代码审查 / Code review

### 代码提交规范 / Commit Standards

```
feat: 添加新功能
fix: 修复bug
docs: 更新文档
test: 添加测试
refactor: 重构代码
```

更多详细信息请参考项目README和源代码注释。

For more detailed information, please refer to the project README and source code comments.