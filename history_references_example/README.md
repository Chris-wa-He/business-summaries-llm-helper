# 历史参考文件示例 / History Reference Files Example

这个目录包含了案例总结生成器的历史参考文件示例，展示了如何组织和格式化历史案例文件。

This directory contains example history reference files for the Case Summary Generator, demonstrating how to organize and format historical case files.

## 目录结构 / Directory Structure

```
history_references_example/
├── technical_issues/           # 技术问题类别 / Technical issues category
│   ├── login_failure_case.md   # 登录失败案例 / Login failure case
│   └── database_performance_issue.txt  # 数据库性能问题 / Database performance issue
├── business_cases/             # 业务案例类别 / Business cases category
│   └── customer_complaint_resolution.md  # 客户投诉处理案例 / Customer complaint resolution
└── README.md                   # 说明文档 / Documentation
```

## 文件格式要求 / File Format Requirements

### 支持的文件格式 / Supported File Formats
- `.txt` - 纯文本文件 / Plain text files
- `.md` - Markdown文件 / Markdown files
- `.markdown` - Markdown文件 / Markdown files

### 文件编码 / File Encoding
- 推荐使用UTF-8编码 / Recommended to use UTF-8 encoding
- 支持中文内容 / Supports Chinese content

## 内容组织建议 / Content Organization Recommendations

### 按类别分组 / Group by Category
将相似类型的案例放在同一个子目录中，例如：
Group similar types of cases in the same subdirectory, for example:

- `technical_issues/` - 技术问题 / Technical issues
- `business_cases/` - 业务案例 / Business cases
- `customer_service/` - 客户服务 / Customer service
- `project_management/` - 项目管理 / Project management

### 文件命名规范 / File Naming Convention
- 使用描述性的文件名 / Use descriptive file names
- 避免使用特殊字符 / Avoid special characters
- 可以使用中英文混合命名 / Can use mixed Chinese and English naming

## 案例内容结构建议 / Case Content Structure Recommendations

### 标准结构 / Standard Structure
每个案例文件建议包含以下部分：
Each case file should include the following sections:

1. **案例概述 / Case Overview** - 简要描述问题和解决方案
2. **问题描述 / Problem Description** - 详细的问题情况
3. **分析过程 / Analysis Process** - 问题分析和诊断过程
4. **解决方案 / Solution** - 采取的解决措施
5. **实施结果 / Implementation Results** - 解决效果和反馈
6. **经验教训 / Lessons Learned** - 总结和改进建议

### 格式示例 / Format Example

#### Markdown格式 / Markdown Format
```markdown
# 案例标题 / Case Title

## 案例概述 / Case Overview
简要描述...

## 问题描述 / Problem Description
详细描述问题...

## 解决方案 / Solution
1. 步骤一
2. 步骤二
3. 步骤三

## 结果 / Results
解决效果...
```

#### 文本格式 / Text Format
```
案例标题：
问题描述：
解决方案：
结果：
经验总结：
```

## 使用方法 / Usage Instructions

### 1. 复制示例文件 / Copy Example Files
```bash
# 复制示例目录到实际使用目录 / Copy example directory to actual usage directory
cp -r history_references_example/ history_references/
```

### 2. 自定义内容 / Customize Content
- 替换示例内容为您的实际案例 / Replace example content with your actual cases
- 根据需要调整目录结构 / Adjust directory structure as needed
- 添加更多案例文件 / Add more case files

### 3. 配置应用 / Configure Application
在 `config.yaml` 中设置历史文件夹路径：
Set the history folder path in `config.yaml`:

```yaml
history_folder: "./history_references"
```

## 最佳实践 / Best Practices

### 内容质量 / Content Quality
1. **详细记录** - 包含足够的细节信息 / Include sufficient detail
2. **结构化** - 使用清晰的章节结构 / Use clear section structure
3. **客观描述** - 避免主观判断，注重事实 / Avoid subjective judgments, focus on facts
4. **定期更新** - 及时添加新的案例 / Regularly add new cases

### 文件管理 / File Management
1. **版本控制** - 使用Git等工具管理文件版本 / Use Git for version control
2. **备份策略** - 定期备份重要案例文件 / Regular backup of important case files
3. **访问权限** - 合理设置文件访问权限 / Set appropriate file access permissions
4. **文件大小** - 单个文件建议不超过10MB / Single file should not exceed 10MB

### 隐私保护 / Privacy Protection
1. **敏感信息** - 移除或脱敏个人信息 / Remove or anonymize personal information
2. **商业机密** - 避免包含商业敏感信息 / Avoid including business sensitive information
3. **合规要求** - 确保符合相关法规要求 / Ensure compliance with relevant regulations

## 故障排除 / Troubleshooting

### 常见问题 / Common Issues

#### 文件无法读取 / File Cannot Be Read
- 检查文件编码是否为UTF-8 / Check if file encoding is UTF-8
- 确认文件扩展名是否支持 / Confirm if file extension is supported
- 验证文件路径是否正确 / Verify if file path is correct

#### 中文显示异常 / Chinese Display Issues
- 确保文件保存为UTF-8编码 / Ensure file is saved in UTF-8 encoding
- 检查系统环境变量设置 / Check system environment variable settings

#### 文件过大 / File Too Large
- 将大文件拆分为多个小文件 / Split large files into smaller ones
- 移除不必要的内容 / Remove unnecessary content
- 使用文件压缩 / Use file compression

如有其他问题，请参考主项目的故障排除指南。
For other issues, please refer to the main project's troubleshooting guide.
