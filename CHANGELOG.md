# 变更日志 / Changelog

本文档记录了项目的所有重要变更。

This document records all important changes to the project.

## [v1.1.0] - 2025-08-25

### 🎉 新增功能 / New Features

#### 系统提示词管理 / System Prompt Management
- **多提示词支持**: 创建、编辑、删除和切换多个系统提示词
- **智能历史文件管理**: 每个提示词自动创建对应的历史参考文件夹
- **直观的Web界面**: 集成到Gradio界面的提示词管理组件
- **高性能缓存**: 内容缓存和列表缓存机制，提升响应速度
- **完善的安全检查**: 输入验证、路径安全和权限检查

#### 核心组件 / Core Components
- `SystemPromptService`: 提示词文件的底层存储操作
- `SystemPromptManager`: 统一的提示词管理接口
- `PromptUIComponents`: Gradio UI组件和交互处理

#### 配置管理增强 / Configuration Management Enhancement
- 新增 `system_prompts` 配置节
- 支持提示词文件夹、激活提示词等配置
- 保持向后兼容性，支持旧配置格式

### ⚡ 性能优化 / Performance Improvements
- **缓存机制**: 提示词内容和列表缓存，TTL 5分钟
- **批量操作**: 支持大规模提示词管理
- **延迟加载**: 按需加载提示词内容

### 🛡️ 安全增强 / Security Enhancements
- **输入验证**: 提示词名称和内容的严格验证
- **路径安全**: 防止路径遍历攻击
- **权限检查**: 文件读写权限验证
- **异常处理**: 完善的异常层次结构

### 📚 文档更新 / Documentation Updates
- 更新 README.md，添加系统提示词管理说明
- 新增用户使用指南 (`docs/SYSTEM_PROMPT_GUIDE.md`)
- 新增开发者文档 (`docs/DEVELOPER_GUIDE.md`)
- 更新配置文件示例 (`config.yaml.example`)

### 🧪 测试覆盖 / Test Coverage
- **91个测试用例**: 单元测试、集成测试、端到端测试
- **安全测试**: 17个专门的安全验证测试
- **性能基准测试**: 创建、读取、列表操作性能验证
- **兼容性测试**: 配置文件向后兼容性验证

### 📊 性能指标 / Performance Metrics
- 提示词创建: 平均 0.0006秒/个
- 提示词读取: 平均 0.0001秒/次
- 列表操作: 平均 0.0000秒/次
- 缓存效果: 273.8倍性能提升

### 🔧 技术改进 / Technical Improvements
- 代码格式化: 使用 Black 统一代码风格
- 异常处理: 5个专门的异常类型
- 双语支持: 中英双语错误消息和文档
- 模块化设计: 清晰的分层架构

### 📁 文件结构变更 / File Structure Changes
```
新增文件 / New Files:
├── src/services/system_prompt_manager.py
├── src/services/system_prompt_service.py
├── src/ui/prompt_ui_components.py
├── src/exceptions/system_prompt_exceptions.py
├── docs/SYSTEM_PROMPT_GUIDE.md
├── docs/DEVELOPER_GUIDE.md
├── docs/DOCUMENTATION_SUMMARY.md
├── config.yaml.example
└── tests/
    ├── unit/test_services/test_system_prompt_*
    ├── e2e/test_*
    ├── performance/test_benchmark.py
    └── compatibility/test_config_compatibility.py
```

### 🔄 向后兼容性 / Backward Compatibility
- ✅ 支持旧版本配置文件格式
- ✅ 现有功能保持不变
- ✅ API接口向后兼容
- ✅ 历史文件结构兼容

### 🚀 部署说明 / Deployment Notes
- Python 3.8+ 要求保持不变
- 新增配置项为可选，有默认值
- 自动创建必要的目录结构
- 无需数据迁移

---

## [v1.0.0] - 2025-08-24

### 🎉 初始发布 / Initial Release

#### 核心功能 / Core Features
- 基于历史参考信息的案例总结生成
- 支持多种AI模型（Claude、Nova、DeepSeek、OpenAI）
- Gradio Web用户界面
- 灵活的配置管理系统
- AWS Bedrock集成

#### 主要组件 / Main Components
- `ConfigManager`: 配置文件管理
- `BedrockClient`: AWS Bedrock客户端
- `HistoryProcessor`: 历史信息处理
- `ModelManager`: 模型管理
- `PromptBuilder`: 提示词构建
- `AppController`: 应用控制器
- `GradioInterface`: Web界面

#### 技术栈 / Technology Stack
- Python 3.8+
- Poetry 包管理
- Gradio 4.0+ Web界面
- AWS Bedrock AI服务
- pytest 测试框架

---

## 版本说明 / Version Notes

### 语义化版本 / Semantic Versioning
本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范：
- **主版本号**: 不兼容的API修改
- **次版本号**: 向下兼容的功能性新增
- **修订号**: 向下兼容的问题修正

### 发布周期 / Release Cycle
- **主要版本**: 每季度发布，包含重大功能更新
- **次要版本**: 每月发布，包含新功能和改进
- **修订版本**: 按需发布，主要修复bug

### 支持政策 / Support Policy
- **当前版本**: 完全支持和维护
- **前一版本**: 安全更新和关键bug修复
- **更早版本**: 不再维护，建议升级
