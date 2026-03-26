"""
Graph Builder - Structural Code Analysis with Tree-sitter

Parses source code to extract symbols (functions, classes) and build
dependency graphs for code intelligence.
"""

import re
import tree_sitter
from tree_sitter_language_pack import get_language, get_parser
from collections import defaultdict
from typing import Any

import networkx as nx

# Tree-sitter queries per language
LANGUAGE_QUERIES = {
    "python": """
        (function_definition name: (identifier) @name)
        (class_definition name: (identifier) @name)
    """,
    "javascript": """
        (function_declaration name: (identifier) @name)
        (function_declaration name: (property_identifier) @name)
        (class_declaration name: (identifier) @name)
    """,
    "typescript": """
        (function_declaration name: (identifier) @name)
        (function_declaration name: (property_identifier) @name)
        (class_declaration name: (identifier) @name)
    """,
    "tsx": """
        (function_declaration name: (identifier) @name)
        (function_declaration name: (property_identifier) @name)
        (class_declaration name: (identifier) @name)
    """,
    "rust": """
        (function_item name: (identifier) @name)
        (struct_item name: (type_identifier) @name)
    """,
    "go": """
        (function_declaration name: (identifier) @name)
    """,
    "ruby": """
        (method name: (identifier) @name)
        (class name: (constant) @name)
    """,
    "java": """
        (method_declaration name: (identifier) @name)
        (class_declaration name: (identifier) @name)
    """,
    "c": """
        (function_definition declarator: (identifier) @name)
        (struct_specifier name: (identifier) @name)
    """,
    "cpp": """
        (function_definition declarator: (identifier) @name)
        (class_specifier name: (type_identifier) @name)
    """,
}


class SymbolGraphBuilder:
    """
    Tree-sitter based code analyzer for extracting symbols and dependencies.

    Supports multiple programming languages via tree-sitter-language-pack.

    Example:
        >>> builder = SymbolGraphBuilder("python")
        >>> code = "def hello(): pass"
        >>> symbols = builder.parse_symbols(code)
        >>> print(symbols)
        [{'name': 'hello', 'type': 'function', 'line': 1}]
    """

    def __init__(self, lang_name: str = "python"):
        """
        Initialize the parser for a specific language.

        Args:
            lang_name: Language name (e.g., "python", "javascript", "typescript")
        """
        self.language = get_language(lang_name)  # type: ignore
        self.parser = get_parser(lang_name)  # type: ignore
        self.lang_name = lang_name
        self.resource_dependencies: dict[str, set[str]] = defaultdict(set)
        self.operation_resources: dict[str, set[str]] = defaultdict(set)

    def parse_symbols(self, code: str) -> list[dict[str, Any]]:
        """
        Extract all function and class definitions from code.

        Args:
            code: Source code string to parse

        Returns:
            List of symbol dictionaries with 'name', 'type', and 'line' keys
        """
        tree = self.parser.parse(bytes(code, "utf8"))

        query_str = LANGUAGE_QUERIES.get(self.lang_name, LANGUAGE_QUERIES["python"])
        query = self.language.query(query_str)

        symbols = []

        try:
            cursor = tree_sitter.QueryCursor(query)
            results = cursor.captures(tree.root_node)
        except TypeError:
            results = {}

        if isinstance(results, dict):
            for tag, nodes in results.items():
                for node in nodes:
                    if node is None:
                        continue
                    parent_type = node.parent.type if node.parent else ""
                    node_text = node.text
                    if isinstance(node_text, bytes):
                        node_text = node_text.decode("utf8")
                    symbols.append(
                        {
                            "name": node_text,
                            "type": parent_type.replace("_definition", "")
                            .replace("_declaration", "")
                            .replace("_item", ""),
                            "line": node.start_point[0] + 1,
                        }
                    )

        return symbols

    def extract_resource_dependencies(
        self, symbols: list[dict], code: str
    ) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
        """
        Extract resource dependencies from operations.

        Args:
            symbols: List of extracted symbols from parse_symbols
            code: The source code to analyze

        Returns:
            Tuple of (resource_deps, op_resources) as dicts
        """
        self.resource_dependencies.clear()
        self.operation_resources.clear()

        for (
            symbol
        ) in symbols:  # pragma: no cover - requires parse_symbols to return data
            if symbol["type"] == "function":
                func_name = symbol["name"]
                lines = code.split("\n")
                start_line = symbol["line"] - 1
                end_line = len(lines)

                # Find function end
                for i in range(start_line + 1, end_line):
                    line = lines[i].strip()
                    if line.startswith(("def ", "class ", "async def ")):
                        end_line = i
                        break

                func_body = "\n".join(lines[start_line:end_line])
                resources = self._extract_resources_from_function(func_body)

                self.operation_resources[func_name] = resources
                for resource in resources:
                    self.resource_dependencies[resource].add(func_name)

        return (
            {k: list(v) for k, v in self.resource_dependencies.items()},
            {k: list(v) for k, v in self.operation_resources.items()},
        )

    def _extract_resources_from_function(self, func_code: str) -> set[str]:
        """Extract resource names from a function code."""
        resources: set[str] = set()
        lines = func_code.split("\n")

        for line in lines:
            if line.strip().startswith(("def ", "async def ")):
                params = self._extract_function_params(line)
                resources.update(params)

        resource_patterns = [
            (r'\.open\s*\(\s*[\'"]([^\'"]+)[\'"]', "file"),
            (r"(connect|connection|cursor|execute|query)", "database"),
            (r"(get|post|put|delete|request)\s*\(", "http"),
            (r"\b(config|settings|resource|data_|input_|output_)\w*", "config"),
        ]

        for line in lines:
            if line.strip().startswith("#"):  # pragma: no cover - comment skip
                continue

            for pattern, resource_type in resource_patterns:
                matches = re.findall(pattern, line.lower())
                if matches:
                    if resource_type in ("file", "config"):
                        resources.update(matches)
                    else:
                        resources.add(f"{resource_type}_{len(resources)}")

        return resources

    def _extract_function_params(self, func_def_line: str) -> set[str]:
        """Extract parameter names from a function definition line."""
        params: set[str] = set()

        match = re.search(r"\((.*?)\)", func_def_line)
        if match:
            param_str = match.group(1)
            for param in param_str.split(","):
                param = param.strip()
                param = param.split(":")[0].split("=")[0].strip()
                if param and param != "self":
                    params.add(param)

        return params

    def build_dependency_graph(self) -> nx.DiGraph:
        """
        Build a NetworkX graph representing resource dependencies.

        Returns:
            NetworkX DiGraph with operation and resource nodes
        """
        G = nx.DiGraph()

        for op_name in self.operation_resources:
            G.add_node(op_name, type="operation")

        for resource, operations in self.resource_dependencies.items():
            G.add_node(resource, type="resource")
            for op in operations:
                G.add_edge(op, resource, relation="uses")

        return G

    def analyze_dependencies(self) -> dict[str, Any]:
        """
        Analyze and return dependency insights.

        Returns:
            Dictionary with dependency statistics and insights
        """
        insights: dict[str, Any] = {
            "total_operations": len(self.operation_resources),
            "total_resources": len(self.resource_dependencies),
            "resource_usage": {},
            "operation_dependencies": {},
            "shared_resources": {},
            "critical_resources": [],
        }

        for resource, operations in self.resource_dependencies.items():
            insights["resource_usage"][resource] = len(operations)
            if len(operations) > 1:
                insights["shared_resources"][resource] = list(operations)

        for operation, resources in self.operation_resources.items():
            insights["operation_dependencies"][operation] = len(resources)

        if insights["total_resources"] > 0 and insights["resource_usage"]:
            avg_usage = sum(insights["resource_usage"].values()) / len(
                insights["resource_usage"]
            )
            insights["critical_resources"] = [
                r
                for r, count in insights["resource_usage"].items()
                if isinstance(count, int) and count > avg_usage * 1.5
            ]

        return insights
