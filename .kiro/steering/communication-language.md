# 项目沟通语言规范 / Project Communication Language Guidelines

## 沟通语言 / Communication Language

在本项目的所有沟通交流中，请使用**中文**作为主要沟通语言。这包括但不限于：

In all communications within this project, please use **Chinese** as the primary communication language. This includes but is not limited to:

- 需求讨论和澄清 / Requirements discussion and clarification
- 设计文档和技术方案 / Design documents and technical proposals  
- 代码审查和反馈 / Code reviews and feedback
- 问题报告和解决方案 / Issue reports and solutions
- 项目进度和状态更新 / Project progress and status updates
- 团队协作和会议讨论 / Team collaboration and meeting discussions

## 代码规范 / Code Standards

### 编程语言 / Programming Language
- 代码实现使用对应的编程语言（如JavaScript、Python、Java等）
- Code implementation should use the appropriate programming language (JavaScript, Python, Java, etc.)

### 注释规范 / Comment Standards
- 所有代码注释采用**中英双语**形式
- All code comments should be written in **bilingual format (Chinese and English)**

#### 注释格式示例 / Comment Format Examples

**JavaScript/TypeScript:**
```javascript
// 用户认证服务 / User authentication service
class AuthService {
  /**
   * 验证用户登录凭据 / Validate user login credentials
   * @param {string} username - 用户名 / Username
   * @param {string} password - 密码 / Password
   * @returns {boolean} 验证结果 / Validation result
   */
  validateCredentials(username, password) {
    // 检查用户名格式 / Check username format
    if (!this.isValidUsername(username)) {
      return false;
    }
    
    // 验证密码强度 / Validate password strength
    return this.checkPasswordStrength(password);
  }
}
```

**Python:**
```python
# 数据处理工具类 / Data processing utility class
class DataProcessor:
    def process_data(self, raw_data):
        """
        处理原始数据 / Process raw data
        
        Args:
            raw_data: 原始数据 / Raw data input
            
        Returns:
            处理后的数据 / Processed data
        """
        # 数据清洗 / Data cleaning
        cleaned_data = self._clean_data(raw_data)
        
        # 数据转换 / Data transformation
        return self._transform_data(cleaned_data)
```

## 文档规范 / Documentation Standards

- 技术文档和设计文档使用中文编写 / Technical and design documents should be written in Chinese
- README文件可以提供中英双语版本 / README files may provide bilingual versions
- API文档和接口说明使用中文，但保留英文的技术术语 / API documentation should be in Chinese while preserving English technical terms

## 变量和函数命名 / Variable and Function Naming

- 变量名、函数名、类名等使用英文命名（遵循各语言的命名规范）/ Use English for variable names, function names, class names (following language-specific naming conventions)
- 常量和配置项可以使用有意义的英文名称 / Constants and configuration items should use meaningful English names

示例 / Example:
```javascript
// 正确 / Correct
const MAX_RETRY_COUNT = 3;
const userService = new UserService();
const isAuthenticated = checkUserAuth();

// 避免 / Avoid
const 最大重试次数 = 3;
const 用户服务 = new UserService();
```

---

此steering规则将确保项目团队在沟通中使用统一的语言标准，同时保持代码的国际化和可维护性。

This steering rule ensures the project team uses consistent language standards in communication while maintaining code internationalization and maintainability.