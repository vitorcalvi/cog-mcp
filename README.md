# Cog

Semantic code search for AI assistants. Powered by Nomic embeddings on Apple Silicon.

## What it does

- **Search code by meaning** - Find functions that "handle authentication" not just keyword matches
- **Analyze structure** - Extract functions, classes, and dependencies from any file
- **Generate embeddings** - 768-dim vectors on Metal GPU (M1/M2/M3)

## Requirements

- macOS with Apple Silicon
- Python 3.12+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/)

## Install

```bash
git clone https://github.com/vitorcalvi/cog.git
cd cog

# Python engine
cd packages/core && uv sync

# MCP server
cd ../mcp && npm install && npm run build
```

## Index your code

```bash
cd packages/core
uv run cog-index ./your/project
```

### Supported languages

Cog auto-detects language from file extension. Supported: **Python, JavaScript, TypeScript, TSX, Rust, Go, Ruby, Java, C, C++**

```bash
# Auto-detect (default)
uv run cog-index ./your/project

# Force specific language
uv run cog-index ./your/project --lang rust
```

## Connect to OpenCode

Edit `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "cog": {
      "type": "local",
      "command": ["node", "/ABSOLUTE/PATH/TO/cog/packages/mcp/dist/index.js"],
      "environment": {
        "COG_CORE_DIR": "/ABSOLUTE/PATH/TO/cog/packages/core",
        "COG_DB_PATH": "/ABSOLUTE/PATH/TO/cog/packages/core/cog_memory"
      },
      "enabled": true
    }
  }
}
```

Replace `/ABSOLUTE/PATH/TO` with your actual path.

## Use in OpenCode

```
> Search my codebase for user authentication
> Analyze the structure of src/api.py
> Find database connection functions
```

## Tools

| Tool | Description |
|------|-------------|
| `search_code` | Semantic search - finds code by meaning |
| `analyze_structure` | Extract functions and classes from a file |
| `generate_embedding` | Get 768-dim vector for any text |

## Test it works

| Package | Tests | Coverage |
|---------|-------|----------|
| Python Core | 60 | 100% |
| TypeScript MCP | 35 | 98.7% |

Run tests:
```bash
cd packages/core
uv run pytest
cd packages/mcp
npm test
```

## License

MIT © [Vitor Calvi](https://github.com/vitorcalvi)
