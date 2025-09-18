# 交互式内容优化功能使用指南 / Interactive Content Refinement User Guide

## 概述 / Overview

交互式内容优化功能允许用户通过聊天界面与AI进行多轮对话，对生成的案例总结进行精细化调整和优化。

The Interactive Content Refinement feature allows users to engage in multi-turn conversations with AI through a chat interface to fine-tune and optimize generated case summaries.

## 快速开始 / Quick Start

### 1. 启动优化会话 / Start Refinement Session

生成初始案例总结后，系统会自动显示交互式优化区域：

After generating an initial case summary, the system automatically displays the interactive refinement area:

- 聊天历史显示区域 / Chat history display area
- 用户输入框 / User input box
- 快捷建议按钮 / Quick suggestion buttons

### 2. 发送优化请求 / Send Refinement Requests

在输入框中描述您希望的修改：

Describe your desired changes in the input box:

```
请添加风险评估部分
Please add a risk assessment section

详细说明技术实现方案
Provide detailed technical implementation

调整语言风格使其更加正式
Adjust the language style to be more formal
```

### 3. 使用快捷建议 / Use Quick Suggestions

点击快捷按钮快速发送常用请求：

Click quick buttons to send common requests:

- **➕ 添加细节** / Add Details
- **🎨 调整风格** / Adjust Style  
- **🔄 重新组织** / Restructure
- **✂️ 简化内容** / Simplify Content

## 主要功能 / Main Features

### 聊天式交互 / Chat-style Interaction

- **多轮对话**：支持连续的修改请求和AI响应
- **上下文感知**：AI记住之前的对话内容
- **实时反馈**：即时显示修改结果

- **Multi-turn Conversation**: Supports continuous modification requests and AI responses
- **Context Awareness**: AI remembers previous conversation content
- **Real-time Feedback**: Instantly displays modification results

### 版本管理 / Version Management

- **自动版本创建**：每次修改自动创建新版本
- **版本历史查看**：查看所有修改历史
- **版本对比**：对比不同版本的差异
- **版本回退**：恢复到任意历史版本

- **Automatic Version Creation**: Automatically creates new versions with each modification
- **Version History View**: View all modification history
- **Version Comparison**: Compare differences between versions
- **Version Rollback**: Restore to any historical version

### 个性化学习 / Personalized Learning

- **偏好学习**：系统学习您的修改偏好
- **智能建议**：基于历史提供个性化建议
- **自适应优化**：随使用不断改进

- **Preference Learning**: System learns your modification preferences
- **Smart Suggestions**: Provides personalized suggestions based on history
- **Adaptive Optimization**: Continuously improves with usage

## 使用技巧 / Usage Tips

### 有效的修改请求 / Effective Modification Requests

**具体明确** / Be Specific:
```
✅ 好：在第二段后添加数据分析部分，包含具体数字
✅ Good: Add a data analysis section after the second paragraph, including specific numbers

❌ 避免：改进内容
❌ Avoid: Improve the content
```

**分步骤请求** / Step-by-step Requests:
```
✅ 好：先添加风险评估，然后调整语言风格
✅ Good: First add risk assessment, then adjust language style

❌ 避免：添加风险评估并调整语言风格同时重新组织结构
❌ Avoid: Add risk assessment and adjust language style while reorganizing structure
```

### 版本管理最佳实践 / Version Management Best Practices

1. **重要节点创建里程碑** / Create Milestones at Important Points
2. **定期检查版本历史** / Regularly Check Version History
3. **保留满意的版本** / Keep Satisfactory Versions
4. **使用描述性版本说明** / Use Descriptive Version Notes

### 个性化优化建议 / Personalization Optimization Tips

1. **提供明确反馈** / Provide Clear Feedback
2. **保持一致的偏好** / Maintain Consistent Preferences
3. **定期导出偏好数据** / Regularly Export Preference Data
4. **利用学习建议** / Utilize Learning Suggestions

## 故障排除 / Troubleshooting

### 常见问题 / Common Issues

**Q: AI没有理解我的修改请求**
**Q: AI didn't understand my modification request**

A: 尝试更具体地描述您的需求，或使用快捷建议按钮
A: Try to describe your needs more specifically, or use quick suggestion buttons

**Q: 版本历史显示为空**
**Q: Version history shows empty**

A: 确保已进行至少一次修改操作
A: Ensure at least one modification operation has been performed

**Q: 个性化建议不准确**
**Q: Personalized suggestions are inaccurate**

A: 需要更多交互数据来改进学习效果，继续使用系统
A: More interaction data is needed to improve learning effectiveness, continue using the system

### 错误处理 / Error Handling

如果遇到错误：
If you encounter errors:

1. 检查网络连接 / Check network connection
2. 刷新页面重试 / Refresh page and retry
3. 查看错误消息提示 / Check error message prompts
4. 联系技术支持 / Contact technical support

## 数据管理 / Data Management

### 导出偏好数据 / Export Preference Data

1. 进入个性化偏好管理页面 / Go to personalized preference management page
2. 选择导出格式（JSON/YAML）/ Select export format (JSON/YAML)
3. 点击"导出数据"按钮 / Click "Export Data" button
4. 保存导出文件 / Save exported file

### 导入偏好数据 / Import Preference Data

1. 准备符合格式的偏好数据文件 / Prepare preference data file in correct format
2. 选择导入策略（替换/合并/跳过现有）/ Select import strategy (replace/merge/skip existing)
3. 上传文件并确认导入 / Upload file and confirm import
4. 验证导入结果 / Verify import results

## 安全注意事项 / Security Considerations

- 不要在修改请求中包含敏感信息 / Don't include sensitive information in modification requests
- 定期备份重要的偏好数据 / Regularly backup important preference data
- 注意保护个人隐私信息 / Pay attention to protecting personal privacy information
- 使用安全的网络环境 / Use secure network environment

## 更多帮助 / Additional Help

- 查看开发者文档了解技术细节 / Check developer documentation for technical details
- 参考API文档进行集成开发 / Refer to API documentation for integration development
- 访问项目GitHub页面获取最新信息 / Visit project GitHub page for latest information