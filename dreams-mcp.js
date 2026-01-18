"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
var index_js_1 = require("@modelcontextprotocol/sdk/server/index.js");
var stdio_js_1 = require("@modelcontextprotocol/sdk/server/stdio.js");
var types_js_1 = require("@modelcontextprotocol/sdk/types.js");
var child_process_1 = require("child_process");
// --- CONFIGURATION ---
// The exact path to cog-core installation:
var PYTHON_CORE_DIR = "/Users/vitorcalvi/Desktop/cog-core";
// Using 'uv' to execute python within your managed environment
var PYTHON_CMD = "uv run python";
var server = new index_js_1.Server({ name: "dreams-intelligence", version: "1.0.0" }, { capabilities: { tools: {} } });
server.setRequestHandler(types_js_1.ListToolsRequestSchema, function () { return __awaiter(void 0, void 0, void 0, function () {
    return __generator(this, function (_a) {
        return [2 /*return*/, ({
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
            })];
    });
}); });
server.setRequestHandler(types_js_1.CallToolRequestSchema, function (request) { return __awaiter(void 0, void 0, void 0, function () {
    var _a, name, args, query, limit, script, filePath, script, text, script;
    return __generator(this, function (_b) {
        _a = request.params, name = _a.name, args = _a.arguments;
        // --- TOOL 1: MEMORY SEARCH (RAG) ---
        if (name === "search_memory") {
            query = String(args === null || args === void 0 ? void 0 : args.query).replace(/'/g, "\\'");
            limit = (args === null || args === void 0 ? void 0 : args.limit) || 5;
            script = "\nimport json\nimport lancedb\nfrom mlx_engine import DreamsMLXEngine\n\ntry:\n    # 1. Connect (Auto-opens existing DB)\n    db = lancedb.connect(\"./dreams_memory\")\n    tbl = db.open_table(\"codebase\")\n    \n    # 2. Embed Query (M2 Max)\n    engine = DreamsMLXEngine()\n    q_vec = engine.get_embedding('".concat(query, "')\n    \n    # 3. Search (Vector Similarity)\n    # limit result count\n    results = tbl.search(q_vec).limit(").concat(limit, ").to_list()\n    \n    # 4. Cleanup output for JSON\n    clean_results = []\n    for r in results:\n        clean_results.append({\n            \"file\": r[\"filename\"],\n            \"symbol\": r[\"symbol\"],\n            \"code_snippet\": r[\"text\"],\n            \"score\": 1 - r[\"_distance\"] # Convert distance to similarity score\n        })\n    print(json.dumps(clean_results))\n\nexcept Exception as e:\n    # Fail gracefully so agent knows what happened\n    print(json.dumps({\"error\": str(e), \"hint\": \"Run indexer.py first?\"}))\n");
            return [2 /*return*/, executeInCore(script)];
        }
        // --- TOOL 2: FILE STRUCTURE (Tree-sitter) ---
        if (name === "get_file_structure") {
            filePath = String(args === null || args === void 0 ? void 0 : args.file_path);
            script = "\nimport json\nfrom graph_builder import SymbolGraphBuilder\ntry:\n    with open('".concat(filePath, "', 'r') as f:\n        code = f.read()\n    print(json.dumps(SymbolGraphBuilder().parse_symbols(code)))\nexcept Exception as e:\n    print(json.dumps({\"error\": str(e)}))\n");
            return [2 /*return*/, executeInCore(script)];
        }
        // --- TOOL 3: RAW EMBEDDING (Debug/Direct) ---
        if (name === "generate_embedding") {
            text = String(args === null || args === void 0 ? void 0 : args.text).replace(/'/g, "\\'");
            script = "\nimport json\nfrom mlx_engine import DreamsMLXEngine\ntry:\n    engine = DreamsMLXEngine()\n    print(json.dumps(engine.get_embedding('".concat(text, "'))) \nexcept Exception as e:\n    print(json.dumps({\"error\": str(e)}))\n");
            return [2 /*return*/, executeInCore(script)];
        }
        throw new Error("Unknown tool");
    });
}); });
// Helper: Runs the python script INSIDE your core directory
function executeInCore(pythonScript) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            return [2 /*return*/, new Promise(function (resolve) {
                    // Escape double quotes for the shell command
                    var escapedScript = pythonScript.replace(/"/g, '\\"');
                    // 1. CD into the core dir
                    // 2. Run uv python with the script
                    var command = "cd ".concat(PYTHON_CORE_DIR, " && ").concat(PYTHON_CMD, " -c \"").concat(escapedScript, "\"");
                    (0, child_process_1.exec)(command, function (error, stdout, stderr) {
                        if (error) {
                            resolve({
                                content: [{ type: "text", text: "Execution Error: ".concat(stderr || error.message) }],
                                isError: true
                            });
                        }
                        else {
                            // Attempt to return clean JSON, fallback to raw text if print failed
                            var output = stdout.trim();
                            resolve({ content: [{ type: "text", text: output }] });
                        }
                    });
                })];
        });
    });
}
var transport = new stdio_js_1.StdioServerTransport();
await server.connect(transport);
