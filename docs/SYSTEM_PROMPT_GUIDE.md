# 系统提示词管理用户指南 / System Prompt Management User Guide

## 概述 / Overview

系统提示词管理功能允许您创建、编辑和管理多个系统提示词，每个提示词都有对应的历史参考文件夹。这使您能够为不同的使用场景配置专门的AI行为模式。

The system prompt management feature allows you to create, edit, and manage multiple system prompts, each with its corresponding history reference folder. This enables you to configure specialized AI behavior patterns for different use cases.

## 核心概念 / Core Concepts

### 系统提示词 / System Prompts
系统提示词是指导AI模型行为和响应风格的指令。不同的提示词可以让AI扮演不同的角色，如技术专家、商业分析师、客服代表等。

System prompts are instructions that guide AI model behavior and response style. Different prompts can make AI play different roles, such as technical expert, business analyst, customer service representative, etc.

### 历史参考文件夹 / History Reference Folders
每个系统提示词都有对应的历史参考文件夹，用于存储相关的历史案例和参考资料。系统会根据当前激活的提示词自动切换到对应的历史文件夹。

Each system prompt has a corresponding history reference folder for storing related historical cases and reference materials. The system automatically switches to the corresponding history folder based on the currently active prompt.

## 功能详解 / Feature Details

### 1. 创建新提示词 / Creating New Prompts

#### 步骤 / Steps:
1. 启动Web应用 / Start the web application
2. 在界面中找到"新建提示词"按钮 / Find the "New Prompt" button in the interface
3. 点击按钮打开创建对话框 / Click the button to open the creation dialog
4. 输入提示词信息 / Enter prompt information:
   - **名称**: 提示词的唯一标识符 / **Name**: Unique identifier for the prompt
   - **内容**: 具体的提示词指令 / **Content**: Specific prompt instructions
5. 点击"创建"按钮 / Click the "Create" button
6. 系统自动创建对应的历史文件夹 / System automatically creates corresponding history folder

#### 命名规范 / Naming Conventions:
- 使用描述性名称，如 `technical_analysis`、`customer_service` / Use descriptive names like `technical_analysis`, `customer_service`
- 避免特殊字符和路径分隔符 / Avoid special characters and path separators
- 长度限制在100个字符以内 / Keep length within 100 characters

#### 示例提示词 / Example Prompts:

**技术分析专家 / Technical Analysis Expert:**
```
你是一个资深的技术分析专家，专门分析技术问题、系统架构和解决方案。

请根据历史技术案例，为新的技术问题提供：
1. 问题根因分析
2. 技术解决方案
3. 实施建议
4. 风险评估

保持技术准确性和实用性。
```

**商业分析师 / Business Analyst:**
```
你是一个专业的商业分析师，擅长分析商业案例、市场趋势和业务策略。

请基于历史商业案例，为新的商业问题提供：
1. 市场环境分析
2. 业务影响评估
3. 解决方案建议
4. 预期收益分析

确保分析客观、数据驱动。
```

### 2. 切换提示词 / Switching Prompts

#### 步骤 / Steps:
1. 在界面中找到提示词选择器 / Find the prompt selector in the interface
2. 点击下拉菜单查看所有可用提示词 / Click the dropdown menu to view all available prompts
3. 选择目标提示词 / Select the target prompt
4. 系统自动切换并更新界面 / System automatically switches and updates the interface
5. 历史参考文件夹自动切换到对应目录 / History reference folder automatically switches to corresponding directory

#### 切换效果 / Switching Effects:
- 当前激活提示词标记更新 / Current active prompt marker updates
- 提示词编辑器显示新内容 / Prompt editor displays new content
- 历史处理器切换到对应文件夹 / History processor switches to corresponding folder
- 后续生成的总结使用新提示词 / Subsequent summaries use the new prompt

### 3. 编辑提示词 / Editing Prompts

#### 步骤 / Steps:
1. 选择要编辑的提示词 / Select the prompt to edit
2. 在提示词编辑器中修改内容 / Modify content in the prompt editor
3. 点击"保存"按钮 / Click the "Save" button
4. 系统验证并保存更改 / System validates and saves changes

#### 编辑技巧 / Editing Tips:
- 保持提示词结构清晰 / Keep prompt structure clear
- 使用具体的指令和示例 / Use specific instructions and examples
- 定期测试提示词效果 / Regularly test prompt effectiveness
- 根据使用反馈优化内容 / Optimize content based on usage feedback

### 4. 删除提示词 / Deleting Prompts

#### 步骤 / Steps:
1. 选择要删除的提示词 / Select the prompt to delete
2. 点击"删除"按钮 / Click the "Delete" button
3. 确认删除操作 / Confirm the deletion operation
4. 系统删除提示词文件 / System deletes the prompt file

#### 注意事项 / Important Notes:
- 默认提示词不能删除 / Default prompt cannot be deleted
- 删除激活提示词会自动切换到默认提示词 / Deleting active prompt automatically switches to default
- 对应的历史文件夹不会自动删除 / Corresponding history folder is not automatically deleted

## 历史文件管理 / History File Management

### 文件夹结构 / Folder Structure
```
history_references/
├── default/                    # 默认提示词
│   ├── general_cases/
│   └── mixed_topics/
├── technical_analysis/         # 技术分析提示词
│   ├── performance_issues/
│   ├── security_problems/
│   └── architecture_reviews/
├── business_analysis/          # 商业分析提示词
│   ├── market_research/
│   ├── competitor_analysis/
│   └── strategy_planning/
└── customer_service/          # 客服提示词
    ├── complaint_handling/
    ├── product_support/
    └── service_improvement/
```

### 文件组织建议 / File Organization Recommendations

#### 按主题分类 / Categorize by Topic:
- 为每个提示词创建清晰的子目录结构 / Create clear subdirectory structure for each prompt
- 使用描述性的文件夹名称 / Use descriptive folder names
- 保持一致的命名规范 / Maintain consistent naming conventions

#### 文件格式支持 / Supported File Formats:
- `.txt` - 纯文本文件 / Plain text files
- `.md` - Markdown文件 / Markdown files
- `.markdown` - Markdown文件 / Markdown files

#### 内容质量 / Content Quality:
- 确保历史案例的相关性 / Ensure relevance of historical cases
- 定期更新和维护文件 / Regularly update and maintain files
- 移除过时或不准确的信息 / Remove outdated or inaccurate information

## 最佳实践 / Best Practices

### 1. 提示词设计 / Prompt Design

#### 结构化方法 / Structured Approach:
```
角色定义 + 任务描述 + 输出要求 + 质量标准

Role Definition + Task Description + Output Requirements + Quality Standards
```

#### 示例模板 / Example Template:
```
你是一个[角色]，专门处理[领域]的问题。

请根据提供的历史参考信息和新的案例输入，生成一个包含以下部分的总结：
1. [部分1]
2. [部分2]
3. [部分3]
4. [部分4]

要求：
- [要求1]
- [要求2]
- [要求3]
```

### 2. 历史文件管理 / History File Management

#### 定期维护 / Regular Maintenance:
- 每月检查文件相关性 / Monthly relevance check
- 更新过时信息 / Update outdated information
- 添加新的优质案例 / Add new quality cases
- 删除重复或低质量内容 / Remove duplicate or low-quality content

#### 版本控制 / Version Control:
- 对重要提示词进行备份 / Backup important prompts
- 记录重大修改的原因和日期 / Record reasons and dates for major changes
- 保留历史版本以便回滚 / Keep historical versions for rollback

### 3. 性能优化 / Performance Optimization

#### 缓存利用 / Cache Utilization:
- 系统自动缓存常用提示词 / System automatically caches frequently used prompts
- 避免频繁切换提示词 / Avoid frequent prompt switching
- 合理组织历史文件以提高加载速度 / Organize history files properly for faster loading

#### 文件大小控制 / File Size Control:
- 单个历史文件建议不超过50KB / Individual history files should not exceed 50KB
- 总历史文件夹大小建议控制在100MB以内 / Total history folder size should be within 100MB
- 使用摘要而非完整文档 / Use summaries rather than complete documents

## 故障排除 / Troubleshooting

### 常见问题 / Common Issues

#### 1. 提示词创建失败 / Prompt Creation Failed
**症状**: 点击创建按钮后显示错误信息  
**原因**: 名称包含非法字符或内容为空  
**解决**: 检查名称格式，确保内容不为空  

#### 2. 历史文件夹未自动创建 / History Folder Not Auto-Created
**症状**: 切换提示词后找不到对应文件夹  
**原因**: 文件系统权限不足或磁盘空间不足  
**解决**: 检查目录权限和磁盘空间  

#### 3. 提示词切换无效 / Prompt Switching Ineffective
**症状**: 选择提示词后界面未更新  
**原因**: 缓存问题或提示词文件损坏  
**解决**: 刷新页面或重新创建提示词  

#### 4. 性能缓慢 / Performance Issues
**症状**: 提示词操作响应缓慢  
**原因**: 历史文件过多或文件过大  
**解决**: 清理不必要的历史文件，优化文件结构  

### 日志查看 / Log Viewing
```bash
# 查看应用日志
tail -f logs/application.log

# 查看错误日志
grep "ERROR" logs/application.log
```

## 高级功能 / Advanced Features

### 1. 批量操作 / Batch Operations
- 通过配置文件批量导入提示词 / Batch import prompts via configuration file
- 使用脚本批量创建历史文件夹结构 / Use scripts to batch create history folder structure

### 2. 模板系统 / Template System
- 创建提示词模板以便快速复制 / Create prompt templates for quick copying
- 使用变量占位符实现动态内容 / Use variable placeholders for dynamic content

### 3. 集成开发 / Integration Development
- 通过API接口程序化管理提示词 / Programmatically manage prompts via API interface
- 与外部系统集成实现自动化工作流 / Integrate with external systems for automated workflows

---

如需更多帮助，请参考项目README文档或联系开发团队。

For more help, please refer to the project README documentation or contact the development team.
