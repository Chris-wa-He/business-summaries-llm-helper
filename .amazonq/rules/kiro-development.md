# Project Development Execution Guide

## Project Structure Overview
- **`.kiro/specs/`** - Project specification documents directory
  - Contains project requirements documentation
  - Design documents and architecture specifications
  - Task breakdown documentation
- **`.kiro/steering/`** - Project governance standards directory
  - Contains development standards and guidelines
  - Code style guides
  - Quality control requirements

## Development Execution Workflow

### 1. Documentation Understanding Phase
- Carefully read all documents in the `.kiro/specs/` directory
- Understand project requirements, technical architecture, and design solutions
- Familiarize yourself with development standards in the `.kiro/steering/` directory

### 2. Task Execution Phase
- Strictly follow the task list order in `task.md`
- Before executing each task, confirm:
  - Task objectives and acceptance criteria
  - Related technical requirements and constraints
  - Whether prerequisite tasks have been completed

### 3. Task Completion Standards
After completing each task, you must:
- 🧪 Ensure code passes basic tests
- 🔬 Write and run comprehensive unit tests to validate functionality
- 📋 Verify compliance with project specification requirements
- ✅ Mark task status as "Completed" in `task.md`

### 4. Code Quality Requirements
- Follow coding standards defined in `.kiro/steering/`
- Maintain code readability and maintainability
- Add necessary comments and documentation
- Ensure error handling and edge case coverage

### 5. Strict Implementation Constraints
**CRITICAL REQUIREMENT**: When implementing code, you must:
- ⚠️ **Strictly adhere to requirements and design documents** - Only implement what is explicitly specified
- 🚫 **Do NOT add any functionality not mentioned in requirements** - No additional features or enhancements
- 🎯 **Focus solely on documented specifications** - Avoid any creative interpretations or assumptions
- 📋 **Implement exactly what is requested** - No extra conveniences, utilities, or "nice-to-have" features
- 🔒 **No arbitrary extensions or associations** - Do not add related functionality that seems logical but isn't specified

**Violation of these constraints will result in implementation rejection and rework requirement.**

### 6. Progress Management
- Execute tasks sequentially, do not skip ahead
- Record and report blocking issues promptly
- Regularly update task completion status
- Maintain continuous development momentum

## Output Requirements
- Provide concise completion reports after each task
- Explain implemented functionality and technical details
- Indicate the next task to be executed
- If issues arise, provide detailed problem descriptions and suggested solutions

## Project Completion Criteria
When all tasks in `task.md` are marked as "Completed", the project development phase is finished. At this point, conduct final code review and prepare for project delivery.