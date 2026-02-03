"""
Markdown Viewer with Mermaid support
Windows Desktop Application using PyQt6
"""

import sys
import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QTreeView,
    QVBoxLayout, QWidget, QToolBar, QFileDialog, QMessageBox
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QDir, QModelIndex
from PyQt6.QtGui import QAction, QFileSystemModel


class MarkdownViewer(QMainWindow):
    def __init__(self, file_path: str = None):
        super().__init__()
        self.setWindowTitle("Markdown Viewer")
        self.setGeometry(100, 100, 1400, 900)

        self.current_folder = None
        self.current_file = None

        self._setup_ui()
        self._setup_toolbar()
        self._load_template()

        # Open file if provided via command line
        if file_path:
            self.open_file(file_path)

    def _setup_ui(self):
        """Setup main UI with splitter layout"""
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left pane: File tree view
        self.tree_view = QTreeView()
        self.file_model = QFileSystemModel()
        self.file_model.setNameFilters(["*.md", "*.markdown"])
        self.file_model.setNameFilterDisables(False)
        self.tree_view.setModel(self.file_model)

        # Hide unnecessary columns (Size, Type, Date Modified)
        self.tree_view.setColumnHidden(1, True)
        self.tree_view.setColumnHidden(2, True)
        self.tree_view.setColumnHidden(3, True)

        self.tree_view.setHeaderHidden(True)
        self.tree_view.clicked.connect(self._on_file_clicked)
        self.tree_view.setMinimumWidth(250)

        # Right pane: Web view for markdown rendering
        self.web_view = QWebEngineView()
        self.web_view.setMinimumWidth(600)

        splitter.addWidget(self.tree_view)
        splitter.addWidget(self.web_view)
        splitter.setSizes([300, 1100])

        self.setCentralWidget(splitter)

    def _setup_toolbar(self):
        """Setup toolbar with actions"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Open folder action
        open_folder_action = QAction("📂 Open Folder", self)
        open_folder_action.setShortcut("Ctrl+O")
        open_folder_action.triggered.connect(self._open_folder)
        toolbar.addAction(open_folder_action)

        # Refresh action
        refresh_action = QAction("🔄 Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_current_file)
        toolbar.addAction(refresh_action)

    def _load_template(self):
        """Load HTML template for markdown rendering"""
        template_path = Path(__file__).parent / "template.html"
        if template_path.exists():
            self.template = template_path.read_text(encoding="utf-8")
        else:
            self.template = self._get_default_template()

        # Show welcome message
        self._render_markdown("# Welcome to Markdown Viewer\n\nOpen a folder to get started.")

    def _get_default_template(self):
        """Return default HTML template"""
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div id="content">{{CONTENT}}</div>
</body>
</html>"""

    def _open_folder(self):
        """Open folder dialog and set root path"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.current_folder = folder
            self.file_model.setRootPath(folder)
            self.tree_view.setRootIndex(self.file_model.index(folder))
            self.setWindowTitle(f"Markdown Viewer - {folder}")

    def _on_file_clicked(self, index: QModelIndex):
        """Handle file click in tree view"""
        file_path = self.file_model.filePath(index)

        if os.path.isfile(file_path) and file_path.lower().endswith(('.md', '.markdown')):
            self.current_file = file_path
            self._load_markdown_file(file_path)

    def _load_markdown_file(self, file_path: str):
        """Load and render markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self._render_markdown(content)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file:\n{e}")

    def _render_markdown(self, markdown_content: str):
        """Render markdown content in web view"""
        # Escape special characters for JavaScript
        escaped_content = markdown_content.replace('\\', '\\\\')
        escaped_content = escaped_content.replace('`', '\\`')
        escaped_content = escaped_content.replace('$', '\\$')

        template_path = Path(__file__).parent / "template.html"
        css_path = Path(__file__).parent / "style.css"

        # Read CSS content
        css_content = ""
        if css_path.exists():
            css_content = css_path.read_text(encoding="utf-8")

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>{css_content}</style>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
</head>
<body>
    <div id="content"></div>
    <script>
        // Configure mermaid
        mermaid.initialize({{ startOnLoad: false, theme: 'default' }});

        // Custom renderer for mermaid code blocks
        const renderer = new marked.Renderer();
        const originalCodeRenderer = renderer.code.bind(renderer);

        renderer.code = function(code, language) {{
            if (language === 'mermaid') {{
                return '<div class="mermaid">' + code + '</div>';
            }}
            return originalCodeRenderer(code, language);
        }};

        marked.setOptions({{
            renderer: renderer,
            gfm: true,
            breaks: true
        }});

        // Render markdown
        const markdown = `{escaped_content}`;
        document.getElementById('content').innerHTML = marked.parse(markdown);

        // Render mermaid diagrams
        mermaid.run({{
            querySelector: '.mermaid'
        }});
    </script>
</body>
</html>"""

        self.web_view.setHtml(html)

    def _refresh_current_file(self):
        """Refresh current file"""
        if self.current_file and os.path.exists(self.current_file):
            self._load_markdown_file(self.current_file)

    def open_file(self, file_path: str):
        """Open a specific markdown file"""
        file_path = os.path.abspath(file_path)

        if not os.path.exists(file_path):
            QMessageBox.critical(self, "Error", f"File not found:\n{file_path}")
            return

        if not file_path.lower().endswith(('.md', '.markdown')):
            QMessageBox.warning(self, "Warning", "This file is not a Markdown file.")
            return

        # Set the folder containing the file as root
        folder = os.path.dirname(file_path)
        self.current_folder = folder
        self.file_model.setRootPath(folder)
        self.tree_view.setRootIndex(self.file_model.index(folder))

        # Select the file in tree view
        file_index = self.file_model.index(file_path)
        self.tree_view.setCurrentIndex(file_index)
        self.tree_view.scrollTo(file_index)

        # Load and display the file
        self.current_file = file_path
        self._load_markdown_file(file_path)
        self.setWindowTitle(f"Markdown Viewer - {os.path.basename(file_path)}")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Check for file path argument
    file_path = None
    if len(sys.argv) > 1:
        file_path = sys.argv[1]

    viewer = MarkdownViewer(file_path=file_path)
    viewer.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
