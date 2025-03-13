# Claude Code MCP 服务器和客户端示例

本文档展示如何使用 Claude Code Python Edition 作为 MCP（Model Context Protocol）服务器，并通过 MCP 客户端与之通信。

## 什么是 MCP？

MCP（Model Context Protocol）是一种协议，允许 AI 模型与外部工具和资源进行交互。通过 MCP，AI 模型可以：

- 执行工具函数（如文件操作、系统命令等）
- 访问资源（如文件内容、系统信息等）
- 与用户交互

## 启动 Claude Code MCP 服务器

### 方法1：直接使用 serve 命令

现在，您可以直接使用 `serve` 命令启动 Claude Code MCP 服务器：

```bash
python claude.py serve --host 127.0.0.1 --port 8000
```

参数说明：
- `--host`：服务器绑定的地址（默认为 127.0.0.1）
- `--port`：服务器监听的端口（默认为 8000）
- `--dev`：启用开发模式，提供额外的日志信息
- `--dependencies`：安装额外的 Python 依赖（例如，`--dependencies "fastapi>=0.95.0" "uvicorn>=0.22.0"`）
- `--env-file`：环境变量文件的路径

服务器启动后，您可以访问 `http://127.0.0.1:8000` 查看服务器状态和配置信息。

### 方法2：使用 claude_code/mcp_server.py

您也可以直接运行 MCP 服务器脚本：

```bash
python -m claude_code.mcp_server
```

## 连接到 Claude Code MCP 服务器

有几种方法可以连接到 Claude Code MCP 服务器：

### 1. 使用内置的 mcp-client 命令

Claude Code 提供了一个内置的 MCP 客户端：

```bash
python claude.py mcp-client claude_code/mcp_server.py --model claude-3-5-sonnet-20241022
```

参数说明：
- 第一个参数是服务器脚本的路径
- `--model`：指定使用的 Claude 模型

### 2. 使用内置的 mcp-multi-agent 命令

如果您需要多个 AI 代理协同工作，可以使用多代理客户端：

```bash
python claude.py mcp-multi-agent claude_code/mcp_server.py --config agent_config.json
```

参数说明：
- 第一个参数是服务器脚本的路径 
- `--config`：代理配置文件的路径（可选）

### 3. 使用自定义 MCP 客户端

您可以使用 MCP 客户端库创建自己的客户端。请参考 `examples/mcp_client_example.py` 获取示例。

## 可用的工具和资源

Claude Code MCP 服务器提供以下工具：

- `View`：读取文件内容
- `Edit`：编辑文件
- `Replace`：替换或创建文件
- `ListDirectory`：列出目录内容
- `MakeDirectory`：创建新目录
- `GetServerMetrics`：获取服务器指标和统计信息
- `RegisterClient`：注册客户端连接
- `GetConfiguration`：获取配置信息
- `ResetServerMetrics`：重置服务器指标跟踪

以及以下资源：

- `file://path`：获取文件内容
- `filesystem://path`：列出目录内容
- `system://info`：获取系统信息
- `config://json`：获取配置信息（JSON 格式）
- `metrics://json`：获取指标信息（JSON 格式）

## 示例：使用 Claude Desktop 与 MCP 服务器连接

您可以将 Claude Code MCP 服务器与 Claude Desktop 进行集成：

1. 启动 Claude Code MCP 服务器：
   ```bash
   python claude.py serve
   ```

2. 在 Claude Desktop 中：
   - 打开设置
   - 导航到"Model Context Protocol"部分
   - 点击"Add New Server"
   - 使用以下设置：
     - Name: Claude Code Tools
     - Type: Local Process
     - Command: python
     - Arguments: claude.py serve
     - Working Directory: /path/to/claude-code-directory
   - 点击保存并连接到服务器

3. 现在您可以在 Claude Desktop 中使用 Claude Code 提供的所有工具和资源。

## 排障

如果遇到连接问题：

1. 确认服务器正在运行（访问 http://localhost:8000）
2. 检查服务器日志是否有错误信息
3. 确保没有防火墙阻止连接
4. 尝试使用不同的端口（使用 `--port` 参数）

## 依赖

使用 MCP 服务器和客户端需要以下依赖：

- Python 3.8+
- fastapi
- uvicorn
- aiohttp
- fastmcp

您可以使用以下命令安装依赖：

```bash
pip install fastapi uvicorn aiohttp fastmcp
``` 