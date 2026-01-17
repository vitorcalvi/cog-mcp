# AGENTS.md

This document provides guidelines for AI coding agents working with the **cog-mcp** repository.

## Project Overview

cog-mcp is a TypeScript-based MCP (Model Context Protocol) server that provides semantic code search capabilities. It acts as a bridge between AI assistants (like Claude) and the cog-core Python backend.

## Build / Lint / Test Commands

### Installation

```bash
# Install dependencies
npm install

# Install TypeScript globally (if needed)
npm install -g typescript
```

### Running

```bash
# Start the MCP server
npm start

# Run with ts-node directly
npx ts-node dreams-mcp.ts
```

### Building

```bash
# Compile TypeScript
npm run build

# Type check without emitting
tsc --noEmit
```

## Code Style Guidelines

### TypeScript Conventions

| Type            | Convention       | Example              |
| --------------- | ---------------- | -------------------- |
| Variables       | camelCase        | `searchQuery`        |
| Functions       | camelCase        | `getFileStructure()` |
| Classes         | PascalCase       | `SymbolGraphBuilder` |
| Constants       | UPPER_SNAKE_CASE | `MAX_RESULTS`        |
| Interfaces      | PascalCase       | `SearchResult`       |
| Private methods | prefix with `_`  | `_executeQuery()`    |

### Imports

**Order**: External → Internal → Relative

```typescript
// External (npm packages)
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

// Internal (project modules)
import { SearchService } from './services/search.js';

// Relative
import { CONFIG } from './config.js';
```

### TypeScript Specific

- Use explicit types for function parameters and return values
- Prefer interfaces over type aliases for object shapes
- Use `unknown` instead of `any` when type is uncertain
- Optional properties: `?: Type` not `Type | undefined`

```typescript
interface SearchResult {
  file: string;
  symbol: string;
  codeSnippet: string;
  score: number;
}

async function searchMemory(
  query: string,
  limit: number = 5,
): Promise<SearchResult[]> {
  // ...
}
```

### Error Handling

- Use specific error types when possible
- Add context in error messages
- Return structured error responses for MCP

```typescript
try {
  const result = await executeQuery(query);
  return { content: [{ type: 'text', text: JSON.stringify(result) }] };
} catch (error) {
  return {
    isError: true,
    content: [
      {
        type: 'text',
        text: JSON.stringify({
          error: error instanceof Error ? error.message : 'Unknown error',
        }),
      },
    ],
  };
}
```

## Architecture

### Directory Structure

```
cog-mcp/
├── dreams-mcp.ts        # Main MCP server
├── package.json         # Dependencies
├── tsconfig.json        # TypeScript config
├── README.md            # Documentation
└── LICENSE              # MIT License
```

### Key Components

1. **Server Setup** - MCP protocol initialization
2. **Tool Handlers** - `search_memory`, `get_file_structure`, `generate_embedding`
3. **Python Bridge** - Executes cog-core via subprocess

### Tool Definitions

```typescript
{
  name: "search_memory",
  description: "Semantic search of the codebase using vector embeddings",
  inputSchema: {
    type: "object",
    properties: {
      query: { type: "string", description: "Search query" },
      limit: { type: "integer", default: 5, description: "Max results" }
    },
    required: ["query"]
  }
}
```

## Integration with cog-core

### Configuration

Set the Python core directory:

```typescript
const PYTHON_CORE_DIR = process.env.PYTHON_CORE_DIR || '/path/to/cog-core';
const PYTHON_CMD = 'uv run python'; // or "python"
```

### Execution Pattern

```typescript
async function executeInCore(pythonScript: string) {
  return new Promise((resolve, reject) => {
    const command = `cd ${PYTHON_CORE_DIR} && ${PYTHON_CMD} -c "${escapedScript}"`;

    exec(command, (error, stdout, stderr) => {
      if (error) {
        resolve({
          isError: true,
          content: [{ type: 'text', text: stderr }],
        });
      } else {
        resolve({ content: [{ type: 'text', text: stdout.trim() }] });
      }
    });
  });
}
```

## Common Tasks

### Adding a New Tool

1. Define the tool in `ListToolsRequestSchema` handler
2. Add handler in `CallToolRequestSchema` handler
3. Implement the tool logic (may call cog-core)
4. Test with MCP client

### Modifying Search Behavior

The search behavior is controlled by cog-core. To modify:

1. Edit `mlx_engine.py` in cog-core for embedding changes
2. Edit `indexer.py` for indexing behavior
3. Modify `dreams-mcp.ts` for response formatting

## Testing

### Manual Testing

```bash
# Start server
npx ts-node dreams-mcp.ts

# Test with MCP inspector
npx @modelcontextprotocol/inspector
```

### Automated Tests

Tests can be added using the MCP SDK's testing utilities:

```typescript
import { MCPTestClient } from '@modelcontextprotocol/sdk/testing.js';

// Example test structure
describe('cog-mcp', () => {
  let client: MCPTestClient;

  beforeEach(() => {
    client = new MCPTestClient('cog-mcp');
  });

  it('should list available tools', async () => {
    const tools = await client.listTools();
    expect(tools).toContainEqual(
      expect.objectContaining({ name: 'search_memory' }),
    );
  });
});
```

## Debugging

### Common Issues

| Issue                      | Solution                                  |
| -------------------------- | ----------------------------------------- |
| Python not found           | Ensure `PYTHON_CORE_DIR` is set correctly |
| Embedding generation fails | Check MLX/MPS availability                |
| Search returns empty       | Run `indexer.py` to populate vector DB    |

### Debug Mode

```bash
# Enable verbose logging
DEBUG=* npx ts-node dreams-mcp.ts
```

## Best Practices

1. **Keep tools focused** - Each tool should do one thing well
2. **Handle errors gracefully** - Return structured error responses
3. **Use TypeScript types** - Leverage the type system for safety
4. **Document tool schemas** - Clear descriptions help AI assistants
5. **Test with real codebases** - Ensure search results are relevant

## Related Documentation

- [cog-core README](https://github.com/vitorcalvi/cog-core)
- [MCP Protocol Spec](https://modelcontextprotocol.io)
- [Nomic Embeddings](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5)
