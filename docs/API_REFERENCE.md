# API参考文档 / API Reference

## 概述 / Overview

本文档描述了交互式内容优化功能的API接口和使用方法。

This document describes the API interfaces and usage methods for the Interactive Content Refinement feature.

## 核心API / Core APIs

### RefinementController

#### start_refinement_session

启动新的优化会话。

Start a new refinement session.

```python
async def start_refinement_session(
    initial_content: str, 
    user_id: str
) -> str
```

**参数 / Parameters:**
- `initial_content` (str): 初始内容 / Initial content
- `user_id` (str): 用户ID / User ID

**返回值 / Returns:**
- `str`: 会话ID / Session ID

**示例 / Example:**
```python
session_id = await controller.start_refinement_session(
    "这是初始的案例总结内容", 
    "user_123"
)
```

#### process_user_message

处理用户的修改请求消息。

Process user modification request message.

```python
async def process_user_message(
    message: str, 
    session_id: str
) -> Dict[str, Any]
```

**参数 / Parameters:**
- `message` (str): 用户消息 / User message
- `session_id` (str): 会话ID / Session ID

**返回值 / Returns:**
- `Dict[str, Any]`: 处理结果 / Processing result
  - `success` (bool): 是否成功 / Whether successful
  - `response` (str): AI响应 / AI response
  - `modified_content` (str): 修改后的内容 / Modified content
  - `modification_type` (str): 修改类型 / Modification type

**示例 / Example:**
```python
result = await controller.process_user_message(
    "请添加风险评估部分", 
    session_id
)
```

#### get_version_history

获取会话的版本历史。

Get version history for a session.

```python
def get_version_history(session_id: str) -> List[Dict]
```

**参数 / Parameters:**
- `session_id` (str): 会话ID / Session ID

**返回值 / Returns:**
- `List[Dict]`: 版本列表 / Version list
  - `id` (str): 版本ID / Version ID
  - `version_number` (int): 版本号 / Version number
  - `created_at` (str): 创建时间 / Creation time
  - `modification_type` (str): 修改类型 / Modification type

#### revert_to_version

回退到指定版本。

Revert to specified version.

```python
def revert_to_version(session_id: str, version_id: str) -> str
```

**参数 / Parameters:**
- `session_id` (str): 会话ID / Session ID
- `version_id` (str): 版本ID / Version ID

**返回值 / Returns:**
- `str`: 回退后的内容 / Content after reversion

### ConversationService

#### create_session

创建新的对话会话。

Create a new conversation session.

```python
def create_session(user_id: str, initial_content: str) -> str
```

#### add_message

添加消息到会话。

Add message to session.

```python
def add_message(session_id: str, message: ConversationMessage) -> None
```

#### get_conversation_history

获取对话历史。

Get conversation history.

```python
def get_conversation_history(session_id: str) -> List[ConversationMessage]
```

### VersionService

#### create_version

创建新版本。

Create new version.

```python
def create_version(
    session_id: str, 
    content: str, 
    modification_type: str
) -> str
```

#### get_version_list

获取版本列表。

Get version list.

```python
def get_version_list(session_id: str) -> List[ContentVersion]
```

#### compare_versions

对比两个版本。

Compare two versions.

```python
def compare_versions(version_id1: str, version_id2: str) -> VersionDiff
```

### InputValidator

#### validate_user_message

验证用户消息。

Validate user message.

```python
def validate_user_message(
    message: str, 
    max_length: int = 2000
) -> ValidationResult
```

**参数 / Parameters:**
- `message` (str): 用户消息 / User message
- `max_length` (int): 最大长度 / Maximum length

**返回值 / Returns:**
- `ValidationResult`: 验证结果 / Validation result
  - `is_valid` (bool): 是否有效 / Whether valid
  - `cleaned_data` (str): 清理后的数据 / Cleaned data
  - `errors` (List[str]): 错误列表 / Error list

### ErrorHandler

#### handle_error

处理错误。

Handle error.

```python
def handle_error(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]
```

**参数 / Parameters:**
- `error` (Exception): 异常对象 / Exception object
- `context` (Dict[str, Any]): 上下文信息 / Context information

**返回值 / Returns:**
- `Dict[str, Any]`: 错误处理结果 / Error handling result
  - `success` (bool): 处理是否成功 / Whether handling successful
  - `error_id` (str): 错误ID / Error ID
  - `user_message` (str): 用户友好的错误消息 / User-friendly error message

## 数据模型 / Data Models

### ConversationMessage

```python
@dataclass
class ConversationMessage:
    id: str                    # 消息ID / Message ID
    session_id: str           # 会话ID / Session ID
    sender: str               # 发送者 ('user' or 'ai')
    content: str              # 消息内容 / Message content
    timestamp: datetime       # 时间戳 / Timestamp
    message_type: str         # 消息类型 / Message type
    metadata: Dict[str, Any]  # 元数据 / Metadata
```

### ContentVersion

```python
@dataclass
class ContentVersion:
    id: str                          # 版本ID / Version ID
    session_id: str                  # 会话ID / Session ID
    content: str                     # 内容 / Content
    version_number: int              # 版本号 / Version number
    parent_version_id: Optional[str] # 父版本ID / Parent version ID
    modification_type: str           # 修改类型 / Modification type
    created_at: datetime            # 创建时间 / Creation time
    metadata: Dict[str, Any]        # 元数据 / Metadata
```

### ValidationResult

```python
@dataclass
class ValidationResult:
    is_valid: bool                    # 是否有效 / Whether valid
    cleaned_data: Optional[str]       # 清理后的数据 / Cleaned data
    errors: List[str]                # 错误列表 / Error list
    warnings: List[str]              # 警告列表 / Warning list
```

## 错误代码 / Error Codes

### 验证错误 / Validation Errors

- `VALIDATION_001`: 消息长度超出限制 / Message length exceeds limit
- `VALIDATION_002`: 检测到恶意内容 / Malicious content detected
- `VALIDATION_003`: 消息为空 / Message is empty

### 会话错误 / Session Errors

- `SESSION_001`: 会话不存在 / Session does not exist
- `SESSION_002`: 会话已过期 / Session has expired
- `SESSION_003`: 会话创建失败 / Session creation failed

### 版本错误 / Version Errors

- `VERSION_001`: 版本不存在 / Version does not exist
- `VERSION_002`: 版本创建失败 / Version creation failed
- `VERSION_003`: 版本回退失败 / Version reversion failed

### 系统错误 / System Errors

- `SYSTEM_001`: 内部服务器错误 / Internal server error
- `SYSTEM_002`: 服务不可用 / Service unavailable
- `SYSTEM_003`: 配置错误 / Configuration error

## 使用示例 / Usage Examples

### 完整工作流示例 / Complete Workflow Example

```python
from src.services.refinement_controller import RefinementController
from src.utils.input_validator import InputValidator

# 初始化组件
controller = RefinementController(app_controller)
validator = InputValidator()

# 1. 启动会话
session_id = await controller.start_refinement_session(
    "这是一个技术案例的初始总结内容。", 
    "user_123"
)

# 2. 验证用户输入
user_message = "请添加技术实现细节"
validation_result = validator.validate_user_message(user_message)

if validation_result.is_valid:
    # 3. 处理修改请求
    result = await controller.process_user_message(
        validation_result.cleaned_data, 
        session_id
    )
    
    if result['success']:
        print(f"AI响应: {result['response']}")
        print(f"修改后内容: {result['modified_content']}")
    else:
        print(f"处理失败: {result.get('error')}")

# 4. 查看版本历史
versions = controller.get_version_history(session_id)
for version in versions:
    print(f"版本 {version['version_number']}: {version['created_at']}")

# 5. 版本回退（如需要）
if len(versions) > 1:
    reverted_content = controller.revert_to_version(
        session_id, 
        versions[0]['id']
    )
    print(f"已回退到版本: {reverted_content}")
```

### 错误处理示例 / Error Handling Example

```python
from src.services.error_handler import RefinementErrorHandler

error_handler = RefinementErrorHandler()

try:
    result = await controller.process_user_message(message, session_id)
except Exception as e:
    error_result = error_handler.handle_error(e, {
        'session_id': session_id,
        'user_id': 'user_123',
        'operation': 'process_message'
    })
    
    print(f"错误ID: {error_result['error_id']}")
    print(f"用户消息: {error_result['user_message']}")
```

## 配置参数 / Configuration Parameters

### 会话配置 / Session Configuration

```yaml
conversation:
  max_sessions_per_user: 5      # 每用户最大会话数
  session_timeout: 3600         # 会话超时时间（秒）
  max_messages_per_session: 100 # 每会话最大消息数
```

### 版本配置 / Version Configuration

```yaml
version:
  max_versions_per_session: 50  # 每会话最大版本数
  auto_cleanup_enabled: true    # 自动清理启用
  milestone_retention_days: 30  # 里程碑保留天数
```

### 性能配置 / Performance Configuration

```yaml
performance:
  max_concurrent_modifications: 10  # 最大并发修改数
  cache_ttl: 3600                  # 缓存生存时间
  async_processing_enabled: true   # 异步处理启用
```

## 限制和约束 / Limits and Constraints

- 单次消息最大长度：2000字符 / Maximum message length: 2000 characters
- 每用户最大并发会话：5个 / Maximum concurrent sessions per user: 5
- 版本历史保留：50个版本 / Version history retention: 50 versions
- 会话超时：1小时 / Session timeout: 1 hour
- API调用频率限制：每分钟100次 / API call rate limit: 100 per minute