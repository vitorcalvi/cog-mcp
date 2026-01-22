import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { 
  CallToolRequestSchema, 
  ListToolsRequestSchema, 
  type CallToolResult 
} from "@modelcontextprotocol/sdk/types.js";
import { exec } from "child_process";


// --- CONFIGURATION ---
// The exact path to cog-core installation:
const PYTHON_CORE_DIR = "/Users/vitorcalvi/Desktop/cog-core";
// Using 'uv' to execute python within your managed environment
const PYTHON_CMD = "uv run python";

const server = new Server(
  { name: "dreams-intelligence", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "search_memory",
      description: "Semantic search of the codebase. Finds code by meaning (e.g. 'function that handles privacy').",
      inputSchema: {
        type: "object",
        properties: {
          query: { type: "string" },
          limit: { type: "integer", default: 5 }
        },
        required: ["query"]
      }
    },
    {
      name: "get_file_structure",
      description: "Analyze code structure (classes/functions) using your local Python graph builder.",
      inputSchema: {
        type: "object",
        properties: {
          file_path: { type: "string" }
        },
        required: ["file_path"]
      }
    },
    {
      name: "generate_embedding",
      description: "Generate Nomic embeddings using local M2 Max GPU.",
      inputSchema: {
        type: "object",
        properties: {
          text: { type: "string" }
        },
        required: ["text"]
      }
    }
  ]
}));

server.setRequestHandler(CallToolRequestSchema, async (request): Promise<CallToolResult> => {
  const { name, arguments: args } = request.params;

  // --- TOOL 1: MEMORY SEARCH (RAG) ---
  if (name === "search_memory") {
    const query = String(args?.query).replace(/'/g, "\\'");
    const limit = args?.limit || 5;

    const script = `
import json
import lancedb
from mlx_engine import DreamsMLXEngine

try:
    # 1. Connect (Auto-opens existing DB)
    db = lancedb.connect("./dreams_memory")
    tbl = db.open_table("codebase")
    
    # 2. Embed Query (M2 Max)
    engine = DreamsMLXEngine()
    q_vec = engine.get_embedding('${query}')
    
    # 3. Search (Vector Similarity)
    # limit result count
    results = tbl.search(q_vec).limit(${limit}).to_list()
    
    # 4. Cleanup output for JSON
    clean_results = []
    for r in results:
        clean_results.append({
            "file": r["filename"],
            "symbol": r["symbol"],
            "code_snippet": r["text"],
            "score": 1 - r["_distance"] # Convert distance to similarity score
        })
    print(json.dumps(clean_results))

except Exception as e:
    # Fail gracefully so agent knows what happened
    print(json.dumps({"error": str(e), "hint": "Run indexer.py first?"}))
`;
    return executeInCore(script);
  }

  // --- TOOL 2: FILE STRUCTURE (Tree-sitter) ---
  if (name === "get_file_structure") {
    const filePath = String(args?.file_path).replace(/'/g, "\\'").replace(/"/g, '\\"');
    const script = `
import json
import os
from graph_builder import SymbolGraphBuilder
try:
    if not os.path.exists('${filePath}'):
        print(json.dumps({"error": "File not found", "path": '${filePath}'}))
    else:
        with open('${filePath}', 'r', encoding='utf-8') as f:
            code = f.read()
        symbols = SymbolGraphBuilder().parse_symbols(code)
        print(json.dumps(symbols))
except Exception as e:
    print(json.dumps({"error": str(e), "type": str(type(e).__name__)}))
`;
    return executeInCore(script);
  }

  // --- TOOL 3: RAW EMBEDDING (Debug/Direct) ---
  if (name === "generate_embedding") {
    const text = String(args?.text).replace(/'/g, "\\'").replace(/"/g, '\\"');
    const script = `
import json
import numpy as np
from mlx_engine import DreamsMLXEngine
try:
    engine = DreamsMLXEngine()
    embedding = engine.get_embedding('${text}')
    # Convert numpy ndarray to list for JSON serialization
    embedding_list = embedding.tolist() if hasattr(embedding, 'tolist') else embedding
    print(json.dumps({"embedding": embedding_list, "dimensions": len(embedding_list)}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
`;
    return executeInCore(script);
  }

  throw new Error("Unknown tool");
});

 // Helper: Runs the python script INSIDE your core directory
 async function executeInCore(pythonScript: string): Promise<CallToolResult> {
   return new Promise((resolve) => {
     // Escape double quotes for the shell command
     const escapedScript = pythonScript.replace(/"/g, '\\"');
     
     // 1. CD into the core dir
     // 2. Run uv python with the script
     const command = `cd ${PYTHON_CORE_DIR} && ${PYTHON_CMD} -c "${escapedScript}"`;

     exec(command, (error, stdout, stderr) => {
       if (error) {
         resolve({
           content: [{ type: "text", text: `Execution Error: ${stderr || error.message}` }],
           isError: true
         } as CallToolResult);
       } else {
         // Attempt to return clean JSON, fallback to raw text if print failed
         const output = stdout.trim();
         resolve({ content: [{ type: "text", text: output }] } as CallToolResult);
       }
     });
   });
 }

const transport = new StdioServerTransport();
(async () => {
  await server.connect(transport);
})();
