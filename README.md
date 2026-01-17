# cog-mcp

<p align="center">
  <img src="https://img.shields.io/badge/MCP-Server-blue?style=for-the-badge&logo=microsoftazure" alt="MCP Server">
  <img src="https://img.shields.io/badge/Apple-Silicon-000?style=for-the-badge&logo=apple" alt="Apple Silicon">
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript" alt="TypeScript">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
  <a href="https://opencode.cafe"><img src="https://img.shields.io/badge/OpenCode-Cafe-orange?style=for-the-badge" alt="OpenCode Cafe"></a>
</p>

<p align="center">
  <strong>MCP Server for semantic code search with Metal GPU acceleration</strong>
</p>

---

## What is cog-mcp?

**cog-mcp** is a Model Context Protocol (MCP) server that provides AI assistants with semantic code search capabilities powered by Apple Silicon's Metal Performance Shaders (MPS). It bridges your codebase to intelligent search tools that understand code by meaning, not just text matching.

### Why cog-mcp?

Traditional code search finds exact text matches. cog-mcp understands **what code does**, not just **what it says**.

| Search Type     | Example Query                  | Result                                              |
| --------------- | ------------------------------ | --------------------------------------------------- |
| **Traditional** | "find `login` function"        | Files containing "login"                            |
| **cog-mcp**     | "find authentication handling" | All auth-related code: login, validate, permissions |

---

## Key Features

- 🔍 **Semantic Code Search** - Search code by meaning, not just keywords
- ⚡ **Metal GPU Acceleration** - Leverages Apple Silicon M1/M2/M3 for fast embeddings
- 🌳 **Tree-sitter Integration** - Deep code structure analysis
- 🧠 **RAG Pipeline** - Retrieval-augmented generation for code understanding
- 🔌 **MCP Protocol** - Standard Model Context Protocol server

---

## Tools Provided

| Tool                 | Description                                         | Returns                                                |
| -------------------- | --------------------------------------------------- | ------------------------------------------------------ |
| `search_memory`      | Semantic search of codebase using vector embeddings | JSON with matching code snippets and similarity scores |
| `get_file_structure` | Analyze code structure (classes/functions)          | JSON with extracted symbols                            |
| `generate_embedding` | Generate Nomic embeddings using local Metal GPU     | Raw embedding vector                                   |

### Example Usage

```json
{
  "tool": "search_memory",
  "arguments": {
    "query": "authentication and authorization handling",
    "limit": 10
  }
}
```

Returns relevant code snippets ranked by semantic similarity:

```json
[
  {
    "file": "auth.ts",
    "symbol": "validateToken",
    "code_snippet": "function validateToken(token: string): boolean { ... }",
    "score": 0.92
  }
]
```

---

## Installation

### Prerequisites

- macOS with Apple Silicon (M1/M2/M3)
- Node.js 18+
- [cog-core](https://github.com/vitorcalvi/cog-core) Python backend installed

### Quick Install

```bash
# Clone the repository
git clone https://github.com/vitorcalvi/cog-mcp.git
cd cog-mcp

# Install dependencies
npm install
```

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cog": {
      "command": "npx",
      "args": ["ts-node", "/path/to/cog-mcp/dreams-mcp.ts"],
      "env": {
        "PYTHON_CORE_DIR": "/path/to/cog-core"
      }
    }
  }
}
```

### Environment Variables

| Variable          | Description                   | Required |
| ----------------- | ----------------------------- | -------- |
| `PYTHON_CORE_DIR` | Path to cog-core installation | Yes      |

---

## Architecture

```
┌─────────────────┐      MCP Protocol       ┌─────────────────┐
│  Claude Desktop │  ◄──────────────────►   │    cog-mcp      │
│  / AI Assistant │                         │   (TypeScript)  │
└─────────────────┘                         └────────┬────────┘
                                                      │
                                              ┌───────▼───────┐
                                              │   Python Core │
                                              │  (cog-core)   │
                                              │               │
                                              │ • Nomic Embed │
                                              │ • LanceDB     │
                                              │ • Tree-sitter │
                                              └───────────────┘
```

---

## Requirements

- macOS with Apple Silicon (M1/M2/M3)
- Node.js 18+
- TypeScript 5.x
- [cog-core](https://github.com/vitorcalvi/cog-core) Python backend

---

## Dependencies

| Package                     | Purpose                     |
| --------------------------- | --------------------------- |
| `@modelcontextprotocol/sdk` | MCP protocol implementation |
| `typescript`                | TypeScript compilation      |
| `ts-node`                   | TypeScript execution        |

---

## Development

### Running Locally

```bash
# Start the MCP server
npm start
```

### Building

```bash
# Compile TypeScript
npm run build
```

---

## How It Works

1. **Query Received** - MCP request comes from Claude/AI assistant
2. **Python Execution** - cog-mcp executes Python code in cog-core
3. **Vector Search** - Query embedded via Nomic, compared to indexed code
4. **Results Returned** - Top matching code snippets returned with similarity scores

---

## Related Projects

| Project           | Description                        | Link                                             |
| ----------------- | ---------------------------------- | ------------------------------------------------ |
| **cog-core**      | Python backend with MLX embeddings | [GitHub](https://github.com/vitorcalvi/cog-core) |
| **OpenCode Cafe** | MCP server marketplace             | [opencode.cafe](https://www.opencode.cafe)       |

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  Made with ⚙️ by <a href="https://github.com/vitorcalvi">vitorcalvi</a>
</p>
