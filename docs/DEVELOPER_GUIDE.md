# 系统提示词管理开发者指南 / System Prompt Management Developer Guide

## 架构概述 / Architecture Overview

系统提示词管理功能采用分层架构设计，包含以下核心组件：

The system prompt management feature uses a layered architecture design with the following core components:

```
UI Layer (Gradio)
    ↓
Controller Layer (SystemPromptManager)
    ↓
Service Layer (SystemPromptService)
    ↓
Storage Layer (File System)
```

## 核心组件 / Core Components

### 1. SystemPromptService

**位置**: `src/services/system_prompt_service.py`  
**职责**: 处理提示词文件的底层存储操作

#### 主要方法 / Main Methods:

```python
class SystemPromptService:
    def save_prompt_file(self, name: str, content: str) -> bool
    def load_prompt_file(self, name: str) -> Optional[str]
    def delete_prompt_file(self, name: str) -> bool
    def list_prompt_files(self) -> List[str]
    def create_history_folder(self, prompt_name: str) -> str
    def validate_prompt_name(self, name: str) -> bool
    def validate_prompt_content(self, content: str) -> bool
```

#### 使用示例 / Usage Example:

```python
from src.services.system_prompt_service import SystemPromptService

# 初始化服务
service = SystemPromptService(
    prompts_folder="./system_prompts",
    history_base_folder="./history_references"
)

# 创建提示词
success = service.save_prompt_file("technical", "你是技术专家...")
if success:
    print("提示词创建成功")

# 读取提示词
content = service.load_prompt_file("technical")
print(f"提示词内容: {content}")
```

### 2. SystemPromptManager

**位置**: `src/services/system_prompt_manager.py`  
**职责**: 提供统一的提示词管理接口，协调各组件

#### 主要方法 / Main Methods:

```python
class SystemPromptManager:
    def create_prompt(self, name: str, content: str) -> bool
    def get_prompt(self, name: str) -> Optional[str]
    def update_prompt(self, name: str, content: str) -> bool
    def delete_prompt(self, name: str) -> bool
    def list_prompts(self) -> List[Dict[str, Any]]
    def set_active_prompt(self, name: str) -> bool
    def get_active_prompt(self) -> Optional[Dict[str, str]]
```

#### 使用示例 / Usage Example:

```python
from src.services.system_prompt_manager import SystemPromptManager

# 初始化管理器
manager = SystemPromptManager(config_manager, history_processor)

# 创建提示词
success = manager.create_prompt("business", "你是商业分析师...")

# 设置激活提示词
manager.set_active_prompt("business")

# 获取当前激活的提示词
active = manager.get_active_prompt()
print(f"当前激活: {active['name']}")
```

### 3. PromptUIComponents

**位置**: `src/ui/prompt_ui_components.py`  
**职责**: 提供Gradio UI组件和交互处理

#### 主要方法 / Main Methods:

```python
class PromptUIComponents:
    def create_prompt_selector(self) -> gr.Dropdown
    def create_prompt_editor(self) -> gr.Textbox
    def create_prompt_management_panel(self) -> gr.Column
    def handle_prompt_creation(self, name: str, content: str) -> str
    def handle_prompt_selection(self, prompt_name: str) -> Tuple[str, str]
```

#### 使用示例 / Usage Example:

```python
from src.ui.prompt_ui_components import PromptUIComponents

# 初始化UI组件
ui_components = PromptUIComponents(prompt_manager)

# 创建UI组件
selector = ui_components.create_prompt_selector()
editor = ui_components.create_prompt_editor()
panel = ui_components.create_prompt_management_panel()
```

## 数据流 / Data Flow

### 创建提示词流程 / Prompt Creation Flow

```
User Input (UI)
    ↓
PromptUIComponents.handle_prompt_creation()
    ↓
SystemPromptManager.create_prompt()
    ↓
SystemPromptService.save_prompt_file()
    ↓
File System (save .md file)
    ↓
SystemPromptService.create_history_folder()
    ↓
File System (create directory)
```

### 切换提示词流程 / Prompt Switching Flow

```
User Selection (UI)
    ↓
PromptUIComponents.handle_prompt_selection()
    ↓
SystemPromptManager.set_active_prompt()
    ↓
HistoryProcessor.set_history_folder()
    ↓
Update UI State
```

## 缓存机制 / Caching Mechanism

### 缓存类型 / Cache Types

1. **内容缓存 / Content Cache**: 缓存提示词内容，TTL 5分钟
2. **列表缓存 / List Cache**: 缓存提示词列表，TTL 5分钟

### 缓存实现 / Cache Implementation

```python
class SystemPromptManager:
    def __init__(self):
        self._content_cache = {}  # {name: {content, time}}
        self._list_cache = {}     # {key: {data, time}}
        self._cache_ttl = 300     # 5 minutes
    
    def _is_cache_valid(self, cache_entry):
        return time() - cache_entry['time'] < self._cache_ttl
```

### 缓存失效策略 / Cache Invalidation Strategy

- **创建提示词**: 清理列表缓存
- **更新提示词**: 清理特定内容缓存
- **删除提示词**: 清理内容缓存和列表缓存

## 安全机制 / Security Mechanisms

### 输入验证 / Input Validation

```python
def validate_prompt_name(self, name: str) -> bool:
    # 检查空值
    if not name or not name.strip():
        raise PromptValidationError("名称不能为空")
    
    # 检查长度
    if len(name.strip()) > 100:
        raise PromptValidationError("名称过长")
    
    # 检查路径遍历
    if '..' in name or '/' in name or '\\' in name:
        raise PromptValidationError("名称包含非法字符")
    
    # 检查保留名称
    reserved_names = {'CON', 'PRN', 'AUX', 'NUL'}
    if name.upper() in reserved_names:
        raise PromptValidationError("不能使用保留名称")
```

### 文件路径安全 / File Path Security

```python
def validate_file_path_security(self, file_path: Path) -> bool:
    resolved_path = file_path.resolve()
    base_path = self.prompts_folder.resolve()
    
    if not str(resolved_path).startswith(str(base_path)):
        raise PromptStorageError("路径超出允许范围")
```

## 异常处理 / Exception Handling

### 异常层次结构 / Exception Hierarchy

```python
SystemPromptError (基础异常)
├── PromptNotFoundError (提示词未找到)
├── PromptValidationError (验证失败)
├── PromptStorageError (存储错误)
└── HistoryFolderError (历史文件夹错误)
```

### 异常处理示例 / Exception Handling Example

```python
try:
    manager.create_prompt(name, content)
except PromptValidationError as e:
    print(f"验证失败: {e}")
except PromptStorageError as e:
    print(f"存储失败: {e}")
except SystemPromptError as e:
    print(f"系统错误: {e}")
```

## 扩展开发 / Extension Development

### 添加新的验证规则 / Adding New Validation Rules

```python
class CustomSystemPromptService(SystemPromptService):
    def validate_prompt_content(self, content: str) -> bool:
        super().validate_prompt_content(content)
        
        # 添加自定义验证
        if "禁用词" in content:
            raise PromptValidationError("内容包含禁用词")
        
        return True
```

### 自定义UI组件 / Custom UI Components

```python
class CustomPromptUIComponents(PromptUIComponents):
    def create_advanced_editor(self):
        return gr.Code(
            language="markdown",
            label="高级编辑器",
            lines=20
        )
```

### 集成外部存储 / External Storage Integration

```python
class CloudSystemPromptService(SystemPromptService):
    def save_prompt_file(self, name: str, content: str) -> bool:
        # 保存到云存储
        cloud_storage.upload(f"prompts/{name}.md", content)
        return super().save_prompt_file(name, content)
```

## 测试指南 / Testing Guide

### 单元测试 / Unit Tests

```python
def test_create_prompt():
    manager = SystemPromptManager(mock_config, mock_history)
    success = manager.create_prompt("test", "测试内容")
    assert success is True
    
    content = manager.get_prompt("test")
    assert content == "测试内容"
```

### 集成测试 / Integration Tests

```python
def test_prompt_history_integration():
    manager = SystemPromptManager(config, history_processor)
    manager.create_prompt("integration_test", "集成测试")
    manager.set_active_prompt("integration_test")
    
    # 验证历史处理器被调用
    expected_folder = manager.get_prompt_history_folder("integration_test")
    history_processor.set_history_folder.assert_called_with(expected_folder)
```

### 端到端测试 / End-to-End Tests

```python
def test_complete_workflow():
    # 创建 -> 切换 -> 更新 -> 删除
    manager = create_test_manager()
    
    # 创建
    assert manager.create_prompt("e2e_test", "端到端测试")
    
    # 切换
    assert manager.set_active_prompt("e2e_test")
    
    # 更新
    assert manager.update_prompt("e2e_test", "更新内容")
    
    # 删除
    assert manager.delete_prompt("e2e_test")
```

## 性能优化 / Performance Optimization

### 缓存优化 / Cache Optimization

```python
# 预加载常用提示词
def preload_common_prompts(self):
    common_prompts = ["default", "technical", "business"]
    for prompt_name in common_prompts:
        self.get_prompt(prompt_name)  # 触发缓存
```

### 批量操作 / Batch Operations

```python
def batch_create_prompts(self, prompts_data: List[Tuple[str, str]]):
    results = []
    for name, content in prompts_data:
        try:
            success = self.create_prompt(name, content)
            results.append((name, success))
        except Exception as e:
            results.append((name, False, str(e)))
    return results
```

## 配置管理 / Configuration Management

### 配置结构 / Configuration Structure

```yaml
system_prompts:
  prompts_folder: "./system_prompts"
  active_prompt: "default"
  auto_create_history_folders: true
  prompt_file_extension: ".md"
  cache_ttl: 300  # 缓存过期时间（秒）
  max_prompt_size: 50000  # 最大提示词大小
```

### 配置读取 / Configuration Reading

```python
def load_prompt_config(self):
    app_config = self.config_manager.get_app_config()
    prompt_config = app_config.get('system_prompts', {})
    
    self.prompts_folder = prompt_config.get('prompts_folder', './system_prompts')
    self.active_prompt = prompt_config.get('active_prompt', 'default')
    self.cache_ttl = prompt_config.get('cache_ttl', 300)
```

## 部署注意事项 / Deployment Considerations

### 文件权限 / File Permissions

```bash
# 确保提示词文件夹有正确权限
chmod 755 system_prompts/
chmod 644 system_prompts/*.md

# 确保历史文件夹有正确权限
chmod -R 755 history_references/
```

### 备份策略 / Backup Strategy

```bash
# 定期备份提示词文件
tar -czf system_prompts_backup_$(date +%Y%m%d).tar.gz system_prompts/

# 备份配置文件
cp config.yaml config.yaml.backup
```

### 监控指标 / Monitoring Metrics

- 提示词创建/更新/删除次数
- 缓存命中率
- 文件操作错误率
- 响应时间统计

---

更多技术细节请参考源代码注释和测试用例。

For more technical details, please refer to source code comments and test cases.
