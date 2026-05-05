<div align="center">

# 🎯 MockMaster

**API Mock Server Intelligent Manager**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)]()
[![Tests](https://img.shields.io/badge/Tests-23%20passing-success.svg)]()

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="english"></a>
## 🇺🇸 English

### 🎉 Project Introduction

**MockMaster** is a lightweight, zero-dependency CLI tool for rapid API mock server creation, management, and switching. Built with pure Python 3.8+, it requires no external packages - just Python standard library.

**Why MockMaster?**
- 🚀 **Zero Dependencies** - No pip install hell, works out of the box
- ⚡ **Lightning Fast** - Start a mock server in seconds
- 📝 **Simple Config** - JSON/YAML configuration with intuitive syntax
- 🎭 **Dynamic Responses** - Template engine with random data generators
- 📊 **Request Logging** - Built-in HTTP traffic monitoring
- 🔄 **Project Management** - Manage multiple mock configurations

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🚀 **Quick Start** | Start mock server with single command |
| 📝 **Flexible Config** | JSON/YAML support with full feature parity |
| 🎭 **Templates** | Dynamic responses with `{{ random_uuid() }}`, `{{ now() }}`, etc. |
| 🔗 **Path Params** | Support for `/users/{id}` style routes |
| 🌐 **CORS** | Built-in cross-origin support for frontend dev |
| 📊 **Logging** | Request/response logging with statistics |
| 📦 **Projects** | Save, load, export, import, duplicate configurations |
| 🧪 **Testing** | 23 comprehensive unit tests, all passing |

### 🚀 Quick Start

#### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/MockMaster.git
cd MockMaster

# Install (optional - can also run directly)
pip install -e .
```

#### Create Your First Mock API

```bash
# Create a new project
mockmaster create --name my-api --port 8080

# Start the server
mockmaster start --project my-api
```

Or use a configuration file directly:

```bash
mockmaster start --config examples/sample-api.json --port 8080
```

#### Example Configuration (JSON)

```json
{
  "server": {
    "port": 8080,
    "host": "localhost",
    "cors": { "enabled": true }
  },
  "routes": [
    {
      "path": "/api/users",
      "methods": ["GET"],
      "response": {
        "status": 200,
        "headers": { "Content-Type": "application/json" },
        "body": {
          "users": [
            { "id": "{{ random_uuid() }}", "name": "Alice" },
            { "id": "{{ random_uuid() }}", "name": "Bob" }
          ]
        }
      }
    },
    {
      "path": "/api/users/{id}",
      "methods": ["GET"],
      "response": {
        "status": 200,
        "body": {
          "id": "{{ id }}",
          "name": "{{ random_choice(['Alice', 'Bob', 'Charlie']) }}"
        }
      }
    }
  ]
}
```

### 📖 Available Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{ random_uuid() }}` | Random UUID | `550e8400-e29b-41d4-a716-446655440000` |
| `{{ random_string(10) }}` | Random alphanumeric string | `aB3dE5fGh7` |
| `{{ random_email() }}` | Random email address | `user@example.com` |
| `{{ random_int(1, 100) }}` | Random integer | `42` |
| `{{ random_float(0.0, 1.0) }}` | Random float | `0.753` |
| `{{ random_bool() }}` | Random boolean | `true` |
| `{{ random_date() }}` | Random date | `2024-03-15` |
| `{{ random_datetime() }}` | Random ISO datetime | `2024-03-15T10:30:00+00:00` |
| `{{ random_choice(['a','b']) }}` | Random choice from list | `a` |
| `{{ lorem(20) }}` | Lorem ipsum text | `lorem ipsum dolor...` |
| `{{ now() }}` | Current timestamp | `2024-03-15T10:30:00+00:00` |
| `{{ today() }}` | Current date | `2024-03-15` |
| `{{ id }}` | Path parameter | (from URL) |

### 📚 CLI Commands

```bash
# Project management
mockmaster create --name <project> [--config <file>] [--port <port>]
mockmaster list                          # List all projects
mockmaster show <project>                # Show project details
mockmaster delete <project>              # Delete a project
mockmaster duplicate <source> <new>      # Duplicate project

# Server operations
mockmaster start --project <name>        # Start by project name
mockmaster start --config <file>         # Start by config file
mockmaster start --port 8080 --host 0.0.0.0

# Utilities
mockmaster validate <config-file>        # Validate configuration
mockmaster export <project> [--output]   # Export project
mockmaster import <file> [--name]        # Import project
```

### 📦 Project Structure

```
mockmaster/
├── mockmaster/          # Main package
│   ├── cli.py          # CLI entry point
│   ├── server.py       # HTTP mock server
│   ├── config.py       # Configuration parser
│   ├── templates.py    # Template engine
│   ├── storage.py      # Project management
│   ├── logger.py       # Request logging
│   └── utils.py        # Utilities
├── tests/              # Test suite
├── examples/           # Example configurations
├── setup.py            # Package setup
└── README.md           # Documentation
```

### 💡 Design Philosophy

MockMaster follows these principles:

1. **Zero Dependencies** - Only Python standard library
2. **Simplicity First** - Easy to learn, easy to use
3. **Developer Experience** - Clear error messages, helpful defaults
4. **Flexibility** - JSON/YAML, dynamic templates, path parameters
5. **Testing** - Comprehensive test coverage

### 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<a name="简体中文"></a>
## 🇨🇳 简体中文

### 🎉 项目介绍

**MockMaster** 是一个轻量级、零依赖的 CLI 工具，用于快速创建、管理和切换 API Mock 服务器。使用纯 Python 3.8+ 构建，无需任何外部包 - 仅使用 Python 标准库。

**为什么选择 MockMaster？**
- 🚀 **零依赖** - 无需 pip 安装，开箱即用
- ⚡ **极速启动** - 几秒钟内启动 Mock 服务器
- 📝 **简单配置** - JSON/YAML 配置，语法直观
- 🎭 **动态响应** - 支持随机数据生成器的模板引擎
- 📊 **请求日志** - 内置 HTTP 流量监控
- 🔄 **项目管理** - 管理多个 Mock 配置

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🚀 **快速启动** | 单条命令启动 Mock 服务器 |
| 📝 **灵活配置** | 支持 JSON/YAML，功能完全对等 |
| 🎭 **模板系统** | 动态响应，支持 `{{ random_uuid() }}`、`{{ now() }}` 等 |
| 🔗 **路径参数** | 支持 `/users/{id}` 风格的路由 |
| 🌐 **CORS** | 内置跨域支持，方便前端开发 |
| 📊 **日志记录** | 请求/响应日志与统计 |
| 📦 **项目管理** | 保存、加载、导出、导入、复制配置 |
| 🧪 **测试覆盖** | 23 个全面的单元测试，全部通过 |

### 🚀 快速开始

#### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/MockMaster.git
cd MockMaster

# 安装（可选 - 也可以直接运行）
pip install -e .
```

#### 创建你的第一个 Mock API

```bash
# 创建新项目
mockmaster create --name my-api --port 8080

# 启动服务器
mockmaster start --project my-api
```

或者直接使用配置文件：

```bash
mockmaster start --config examples/sample-api.json --port 8080
```

#### 配置示例（JSON）

```json
{
  "server": {
    "port": 8080,
    "host": "localhost",
    "cors": { "enabled": true }
  },
  "routes": [
    {
      "path": "/api/users",
      "methods": ["GET"],
      "response": {
        "status": 200,
        "headers": { "Content-Type": "application/json" },
        "body": {
          "users": [
            { "id": "{{ random_uuid() }}", "name": "Alice" },
            { "id": "{{ random_uuid() }}", "name": "Bob" }
          ]
        }
      }
    },
    {
      "path": "/api/users/{id}",
      "methods": ["GET"],
      "response": {
        "status": 200,
        "body": {
          "id": "{{ id }}",
          "name": "{{ random_choice(['Alice', 'Bob', 'Charlie']) }}"
        }
      }
    }
  ]
}
```

### 📖 可用模板变量

| 变量 | 描述 | 示例 |
|------|------|------|
| `{{ random_uuid() }}` | 随机 UUID | `550e8400-e29b-41d4-a716-446655440000` |
| `{{ random_string(10) }}` | 随机字母数字字符串 | `aB3dE5fGh7` |
| `{{ random_email() }}` | 随机邮箱地址 | `user@example.com` |
| `{{ random_int(1, 100) }}` | 随机整数 | `42` |
| `{{ random_float(0.0, 1.0) }}` | 随机浮点数 | `0.753` |
| `{{ random_bool() }}` | 随机布尔值 | `true` |
| `{{ random_date() }}` | 随机日期 | `2024-03-15` |
| `{{ random_datetime() }}` | 随机 ISO 时间戳 | `2024-03-15T10:30:00+00:00` |
| `{{ random_choice(['a','b']) }}` | 从列表中随机选择 | `a` |
| `{{ lorem(20) }}` | Lorem ipsum 文本 | `lorem ipsum dolor...` |
| `{{ now() }}` | 当前时间戳 | `2024-03-15T10:30:00+00:00` |
| `{{ today() }}` | 当前日期 | `2024-03-15` |
| `{{ id }}` | 路径参数 | （从 URL 获取） |

### 📚 CLI 命令

```bash
# 项目管理
mockmaster create --name <project> [--config <file>] [--port <port>]
mockmaster list                          # 列出所有项目
mockmaster show <project>                # 显示项目详情
mockmaster delete <project>              # 删除项目
mockmaster duplicate <source> <new>      # 复制项目

# 服务器操作
mockmaster start --project <name>        # 按项目名称启动
mockmaster start --config <file>         # 按配置文件启动
mockmaster start --port 8080 --host 0.0.0.0

# 工具
mockmaster validate <config-file>        # 验证配置
mockmaster export <project> [--output]   # 导出项目
mockmaster import <file> [--name]        # 导入项目
```

### 📦 项目结构

```
mockmaster/
├── mockmaster/          # 主包
│   ├── cli.py          # CLI 入口
│   ├── server.py       # HTTP Mock 服务器
│   ├── config.py       # 配置解析器
│   ├── templates.py    # 模板引擎
│   ├── storage.py      # 项目管理
│   ├── logger.py       # 请求日志
│   └── utils.py        # 工具函数
├── tests/              # 测试套件
├── examples/           # 配置示例
├── setup.py            # 包设置
└── README.md           # 文档
```

### 💡 设计理念

MockMaster 遵循以下原则：

1. **零依赖** - 仅使用 Python 标准库
2. **简洁优先** - 易学易用
3. **开发者体验** - 清晰的错误消息，合理的默认值
4. **灵活性** - JSON/YAML、动态模板、路径参数
5. **测试覆盖** - 全面的测试覆盖

### 🤝 贡献

欢迎贡献！请随时提交 Pull Request。

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

### 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

<a name="繁體中文"></a>
## 🇹