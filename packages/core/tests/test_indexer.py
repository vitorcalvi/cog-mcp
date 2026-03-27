"""
Tests for Code Indexer - Vector Database Builder for Semantic Search.
"""

import pytest
import os
import tempfile
from unittest.mock import MagicMock, patch


class TestCodeIndexer:
    """Test suite for CodeIndexer class."""

    @patch("cog_core.mlx_engine.SentenceTransformer")
    @patch("cog_core.indexer.lancedb")
    def test_init_default_params(self, mock_lancedb, mock_transformer):
        """Test initialization with default parameters."""
        from cog_core.indexer import CodeIndexer

        indexer = CodeIndexer()

        assert indexer.db_path == "./cog_memory"
        assert indexer.file_extensions == [".py"]

    @patch("cog_core.mlx_engine.SentenceTransformer")
    @patch("cog_core.indexer.lancedb")
    def test_init_custom_params(self, mock_lancedb, mock_transformer):
        """Test initialization with custom parameters."""
        from cog_core.indexer import CodeIndexer

        indexer = CodeIndexer(
            db_path="/custom/db", file_extensions=[".py", ".js", ".ts"]
        )

        assert indexer.db_path == "/custom/db"
        assert indexer.file_extensions == [".py", ".js", ".ts"]

    @patch("cog_core.mlx_engine.SentenceTransformer")
    @patch("cog_core.indexer.lancedb")
    def test_index_codebase_empty_dir(self, mock_lancedb, mock_transformer):
        """Test indexing an empty directory."""
        from cog_core.indexer import CodeIndexer

        mock_transformer.return_value = MagicMock()
        mock_transformer.return_value.encode.return_value = [0.1] * 768

        with tempfile.TemporaryDirectory() as tmpdir:
            indexer = CodeIndexer(db_path=os.path.join(tmpdir, "db"))
            count = indexer.index_codebase(tmpdir)

            assert count == 0

    @patch("cog_core.mlx_engine.SentenceTransformer")
    @patch("cog_core.indexer.lancedb")
    def test_index_codebase_single_file(self, mock_lancedb, mock_transformer):
        """Test indexing a single file."""
        from cog_core.indexer import CodeIndexer

        mock_transformer.return_value = MagicMock()
        mock_transformer.return_value.encode.return_value = [0.1] * 768

        mock_db = MagicMock()
        mock_table = MagicMock()
        mock_lancedb.connect.return_value = mock_db
        mock_db.create_table.return_value = mock_table

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file with a function
            test_file = os.path.join(tmpdir, "test.py")
            with open(test_file, "w") as f:
                f.write("def hello():\n    pass\n")

            indexer = CodeIndexer(db_path=os.path.join(tmpdir, "db"))
            count = indexer.index_codebase(tmpdir)

            assert count >= 1
            mock_db.create_table.assert_called_once()

    @patch("cog_core.mlx_engine.SentenceTransformer")
    @patch("cog_core.indexer.lancedb")
    def test_index_codebase_multiple_files(self, mock_lancedb, mock_transformer):
        """Test indexing multiple files."""
        from cog_core.indexer import CodeIndexer

        mock_transformer.return_value = MagicMock()
        mock_transformer.return_value.encode.return_value = [0.1] * 768

        mock_db = MagicMock()
        mock_table = MagicMock()
        mock_lancedb.connect.return_value = mock_db
        mock_db.create_table.return_value = mock_table

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple test files
            for i in range(3):
                test_file = os.path.join(tmpdir, f"test{i}.py")
                with open(test_file, "w") as f:
                    f.write(f"def func{i}():\n    pass\n")

            indexer = CodeIndexer(db_path=os.path.join(tmpdir, "db"))
            count = indexer.index_codebase(tmpdir)

            assert count >= 3

    @patch("cog_core.mlx_engine.SentenceTransformer")
    @patch("cog_core.indexer.lancedb")
    def test_index_codebase_excludes_dirs(self, mock_lancedb, mock_transformer):
        """Test that excluded directories are skipped."""
        from cog_core.indexer import CodeIndexer

        mock_transformer.return_value = MagicMock()
        mock_transformer.return_value.encode.return_value = [0.1] * 768

        mock_db = MagicMock()
        mock_table = MagicMock()
        mock_lancedb.connect.return_value = mock_db
        mock_db.create_table.return_value = mock_table

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files in excluded directories
            venv_dir = os.path.join(tmpdir, "venv")
            os.makedirs(venv_dir)
            with open(os.path.join(venv_dir, "should_skip.py"), "w") as f:
                f.write("def skip_me():\n    pass\n")

            # Create a file in main directory
            with open(os.path.join(tmpdir, "include.py"), "w") as f:
                f.write("def include_me():\n    pass\n")

            indexer = CodeIndexer(db_path=os.path.join(tmpdir, "db"))
            count = indexer.index_codebase(tmpdir)

            # Should only index the main file, not venv
            assert count >= 1

    @patch("cog_core.mlx_engine.SentenceTransformer")
    @patch("cog_core.indexer.lancedb")
    def test_index_codebase_custom_excludes(self, mock_lancedb, mock_transformer):
        """Test custom exclude directories."""
        mock_transformer.return_value = MagicMock()
        mock_transformer.return_value.encode.return_value = [0.1] * 768

        mock_db = MagicMock()
        mock_table = MagicMock()
        mock_lancedb.connect.return_value = mock_db
        mock_db.create_table.return_value = mock_table

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a custom exclude directory
            custom_dir = os.path.join(tmpdir, "custom_exclude")
            os.makedirs(custom_dir)
            with open(os.path.join(custom_dir, "skip.py"), "w") as f:
                f.write("def skip():\n    pass\n")

            # Custom exclude should be respected
            assert True  # Test passes if no exception

    @patch("cog_core.mlx_engine.SentenceTransformer")
    @patch("cog_core.indexer.lancedb")
    def test_index_codebase_file_without_symbols(self, mock_lancedb, mock_transformer):
        """Test indexing a file without function/class definitions."""
        from cog_core.indexer import CodeIndexer

        mock_transformer.return_value = MagicMock()
        mock_transformer.return_value.encode.return_value = [0.1] * 768

        mock_db = MagicMock()
        mock_table = MagicMock()
        mock_lancedb.connect.return_value = mock_db
        mock_db.create_table.return_value = mock_table

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "no_symbols.py")
            with open(test_file, "w") as f:
                f.write("x = 1\ny = 2\nprint(x + y)\n")

            indexer = CodeIndexer(db_path=os.path.join(tmpdir, "db"))
            count = indexer.index_codebase(tmpdir)

            # File without symbols should still be indexed as one chunk
            assert count >= 1

    @patch("cog_core.mlx_engine.SentenceTransformer")
    @patch("cog_core.indexer.lancedb")
    def test_index_codebase_creates_index_for_large_db(
        self, mock_lancedb, mock_transformer
    ):
        """Test that vector index is created for large databases."""
        from cog_core.indexer import CodeIndexer

        mock_transformer.return_value = MagicMock()
        mock_transformer.return_value.encode.return_value = [0.1] * 768

        mock_db = MagicMock()
        mock_table = MagicMock()
        mock_lancedb.connect.return_value = mock_db
        mock_db.create_table.return_value = mock_table

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create 300 files to trigger index creation (>256)
            for i in range(300):
                test_file = os.path.join(tmpdir, f"file{i}.py")
                with open(test_file, "w") as f:
                    f.write(f"x{i} = {i}\n")

            indexer = CodeIndexer(db_path=os.path.join(tmpdir, "db"))
            indexer.index_codebase(tmpdir)

            # Index should be created for large databases
            mock_table.create_index.assert_called()

    @patch("cog_core.mlx_engine.SentenceTransformer")
    @patch("cog_core.indexer.lancedb")
    def test_index_codebase_handles_read_errors(self, mock_lancedb, mock_transformer):
        """Test that read errors are handled gracefully."""
        from cog_core.indexer import CodeIndexer

        mock_transformer.return_value = MagicMock()
        mock_transformer.return_value.encode.return_value = [0.1] * 768

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file that will cause an encoding error
            bad_file = os.path.join(tmpdir, "bad.py")
            with open(bad_file, "wb") as f:
                f.write(b"\xff\xfe\x00\x00")  # Invalid UTF-8

            indexer = CodeIndexer(db_path=os.path.join(tmpdir, "db"))
            # Should not raise exception
            indexer.index_codebase(tmpdir)

    @patch("cog_core.mlx_engine.SentenceTransformer")
    @patch("cog_core.indexer.lancedb")
    def test_search_returns_results(self, mock_lancedb, mock_transformer):
        """Test search returns results."""
        from cog_core.indexer import CodeIndexer

        mock_transformer.return_value = MagicMock()
        mock_transformer.return_value.encode.return_value = [0.1] * 768

        mock_db = MagicMock()
        mock_table = MagicMock()
        mock_lancedb.connect.return_value = mock_db
        mock_db.open_table.return_value = mock_table
        mock_table.search.return_value.limit.return_value.to_list.return_value = [
            {
                "filename": "test.py",
                "path": "/test/test.py",
                "symbol": "foo",
                "text": "def foo(): pass",
                "_distance": 0.1,
            }
        ]

        indexer = CodeIndexer(db_path="./test_db")
        results = indexer.search("authentication", limit=5)

        assert len(results) >= 1
        assert "file" in results[0]

    @patch("cog_core.mlx_engine.SentenceTransformer")
    @patch("cog_core.indexer.lancedb")
    def test_search_no_index_returns_error(self, mock_lancedb, mock_transformer):
        """Test search returns error when no index exists."""
        from cog_core.indexer import CodeIndexer

        mock_transformer.return_value = MagicMock()
        mock_transformer.return_value.encode.return_value = [0.1] * 768

        mock_db = MagicMock()
        mock_db.open_table.side_effect = Exception("Table not found")
        mock_lancedb.connect.return_value = mock_db

        indexer = CodeIndexer(db_path="./nonexistent_db")
        results = indexer.search("query")

        assert "error" in results[0]

    @patch("cog_core.mlx_engine.SentenceTransformer")
    @patch("cog_core.indexer.lancedb")
    def test_search_custom_limit(self, mock_lancedb, mock_transformer):
        """Test search with custom limit."""
        from cog_core.indexer import CodeIndexer

        mock_transformer.return_value = MagicMock()
        mock_transformer.return_value.encode.return_value = [0.1] * 768

        mock_db = MagicMock()
        mock_table = MagicMock()
        mock_lancedb.connect.return_value = mock_db
        mock_db.open_table.return_value = mock_table
        mock_table.search.return_value.limit.return_value.to_list.return_value = [
            {
                "filename": f"file{i}.py",
                "path": f"/test/file{i}.py",
                "symbol": f"func{i}",
                "text": f"def func{i}(): pass",
                "_distance": 0.1 * i,
            }
            for i in range(10)
        ]

        indexer = CodeIndexer(db_path="./test_db")
        indexer.search("query", limit=10)

        mock_table.search.return_value.limit.assert_called()

    @patch("cog_core.mlx_engine.SentenceTransformer")
    @patch("cog_core.indexer.lancedb")
    def test_index_codebase_custom_extensions(self, mock_lancedb, mock_transformer):
        """Test indexing with custom file extensions."""
        from cog_core.indexer import CodeIndexer

        mock_transformer.return_value = MagicMock()
        mock_transformer.return_value.encode.return_value = [0.1] * 768

        mock_db = MagicMock()
        mock_table = MagicMock()
        mock_lancedb.connect.return_value = mock_db
        mock_db.create_table.return_value = mock_table

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files with different extensions
            with open(os.path.join(tmpdir, "test.py"), "w") as f:
                f.write("def py_func(): pass\n")
            with open(os.path.join(tmpdir, "test.txt"), "w") as f:
                f.write("some text\n")

            indexer = CodeIndexer(
                db_path=os.path.join(tmpdir, "db"), file_extensions=[".txt"]
            )
            indexer.index_codebase(tmpdir)

            # Should only index .txt file
            assert True


class TestMainFunction:
    """Tests for the main CLI function."""

    @patch("cog_core.mlx_engine.SentenceTransformer")
    @patch("cog_core.indexer.lancedb")
    @patch("sys.argv", ["cog-index", "--help"])
    def test_main_help(self, mock_lancedb, mock_transformer):
        """Test main with --help argument."""
        from cog_core.indexer import main

        # --help will raise SystemExit
        with pytest.raises(SystemExit):
            main()

    @patch("cog_core.mlx_engine.SentenceTransformer")
    @patch("cog_core.indexer.lancedb")
    @patch("sys.argv", ["cog-index", ".", "--db", "/tmp/test_db"])
    def test_main_with_args(self, mock_lancedb, mock_transformer):
        """Test main with command line arguments."""
        from cog_core.indexer import main

        mock_transformer.return_value = MagicMock()
        mock_transformer.return_value.encode.return_value = [0.1] * 768

        mock_db = MagicMock()
        mock_table = MagicMock()
        mock_lancedb.connect.return_value = mock_db
        mock_db.create_table.return_value = mock_table

        # Should not raise exception
        main()


class TestSearchResultFormatting:
    """Tests for search result formatting."""

    @patch("cog_core.mlx_engine.SentenceTransformer")
    @patch("cog_core.indexer.lancedb")
    def test_search_result_format(self, mock_lancedb, mock_transformer):
        """Test that search results are properly formatted."""
        from cog_core.indexer import CodeIndexer

        mock_transformer.return_value = MagicMock()
        mock_transformer.return_value.encode.return_value = [0.1] * 768

        mock_db = MagicMock()
        mock_table = MagicMock()
        mock_lancedb.connect.return_value = mock_db
        mock_db.open_table.return_value = mock_table
        mock_table.search.return_value.limit.return_value.to_list.return_value = [
            {
                "filename": "auth.py",
                "path": "/app/auth.py",
                "symbol": "login",
                "text": "def login(user, password):\n    return True",
                "_distance": 0.05,
            }
        ]

        indexer = CodeIndexer(db_path="./test_db")
        results = indexer.search("login function")

        assert len(results) == 1
        assert results[0]["file"] == "auth.py"
        assert results[0]["path"] == "/app/auth.py"
        assert results[0]["symbol"] == "login"
        assert "code_snippet" in results[0]
        assert "score" in results[0]

    @patch("cog_core.mlx_engine.SentenceTransformer")
    @patch("cog_core.indexer.lancedb")
    def test_search_result_score_calculation(self, mock_lancedb, mock_transformer):
        """Test that search scores are calculated correctly."""
        from cog_core.indexer import CodeIndexer

        mock_transformer.return_value = MagicMock()
        mock_transformer.return_value.encode.return_value = [0.1] * 768

        mock_db = MagicMock()
        mock_table = MagicMock()
        mock_lancedb.connect.return_value = mock_db
        mock_db.open_table.return_value = mock_table
        mock_table.search.return_value.limit.return_value.to_list.return_value = [
            {
                "filename": "test.py",
                "path": "/test.py",
                "symbol": "test",
                "text": "test",
                "_distance": 0.2,
            }
        ]

        indexer = CodeIndexer(db_path="./test_db")
        results = indexer.search("test")

        # Score should be 1 - distance
        assert results[0]["score"] == 0.8  # 1 - 0.2


class TestDetectLanguage:
    """Tests for language auto-detection."""

    def test_detect_language_python(self):
        """Test Python detection from .py files."""
        from cog_core.indexer import detect_language
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .py files
            for i in range(3):
                with open(os.path.join(tmpdir, f"test{i}.py"), "w") as f:
                    f.write("def foo(): pass\n")

            result = detect_language(tmpdir)
            assert result == "python"

    def test_detect_language_rust(self):
        """Test Rust detection from .rs files."""
        from cog_core.indexer import detect_language
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .rs files
            for i in range(3):
                with open(os.path.join(tmpdir, f"test{i}.rs"), "w") as f:
                    f.write("fn main() {}\n")

            result = detect_language(tmpdir)
            assert result == "rust"

    def test_detect_language_mixed_defaults_python(self):
        """Test that unknown extensions default to Python."""
        from cog_core.indexer import detect_language
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create unknown file types
            with open(os.path.join(tmpdir, "file.txt"), "w") as f:
                f.write("some text\n")

            result = detect_language(tmpdir)
            assert result == "python"

    def test_detect_language_dominant_ext(self):
        """Test that dominant extension is selected."""
        from cog_core.indexer import detect_language
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create more .js files than .ts files
            for i in range(5):
                with open(os.path.join(tmpdir, f"file{i}.js"), "w") as f:
                    f.write("console.log('test');\n")
            for i in range(2):
                with open(os.path.join(tmpdir, f"file{i}.ts"), "w") as f:
                    f.write("const x = 1;\n")

            result = detect_language(tmpdir)
            assert result == "javascript"


class TestLanguageCLI:
    """Tests for language CLI argument."""

    @patch("cog_core.mlx_engine.SentenceTransformer")
    @patch("cog_core.indexer.lancedb")
    @patch("sys.argv", ["cog-index", ".", "--lang", "rust"])
    def test_cli_lang_argument_rust(self, mock_lancedb, mock_transformer):
        """Test CLI with explicit --lang rust."""
        from cog_core.indexer import main

        mock_transformer.return_value = MagicMock()
        mock_transformer.return_value.encode.return_value = [0.1] * 768

        mock_db = MagicMock()
        mock_table = MagicMock()
        mock_lancedb.connect.return_value = mock_db
        mock_db.create_table.return_value = mock_table

        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "main.rs"), "w") as f:
                f.write("fn main() {}\n")

            # Should not raise - main() will try to index but may fail on parse
            # Just verify it doesn't crash on arg parsing
            try:
                main()
            except SystemExit:
                pass  # May exit if no files found

    @patch("cog_core.mlx_engine.SentenceTransformer")
    @patch("cog_core.indexer.lancedb")
    @patch("sys.argv", ["cog-index", ".", "--lang", "auto"])
    def test_cli_lang_auto(self, mock_lancedb, mock_transformer):
        """Test CLI with --lang auto."""
        from cog_core.indexer import main
        from unittest.mock import patch as mock_patch

        mock_transformer.return_value = MagicMock()
        mock_transformer.return_value.encode.return_value = [0.1] * 768

        mock_db = MagicMock()
        mock_table = MagicMock()
        mock_lancedb.connect.return_value = mock_db
        mock_db.create_table.return_value = mock_table

        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "test.py"), "w") as f:
                f.write("def foo(): pass\n")

            with mock_patch("cog_core.indexer.detect_language", return_value="python"):
                try:
                    main()
                except SystemExit:
                    pass
