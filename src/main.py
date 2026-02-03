"""
Markdown Viewer with Mermaid support
Windows Desktop Application using PyQt6
"""

import sys
import os
import json
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QTreeView,
    QVBoxLayout, QHBoxLayout, QWidget, QToolBar, QFileDialog, QMessageBox,
    QTabWidget, QTabBar, QLabel, QFrame, QMenu
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import Qt, QModelIndex, QTimer, QUrl, pyqtSignal
from PyQt6.QtGui import QAction, QFileSystemModel, QShortcut, QKeySequence, QCloseEvent, QDesktopServices


class MarkdownWebPage(QWebEnginePage):
    """Custom WebEnginePage to handle link clicks"""
    link_clicked = pyqtSignal(str, bool)  # (url, open_in_new_tab)

    def acceptNavigationRequest(self, url: QUrl, nav_type, is_main_frame: bool) -> bool:
        # Only intercept link clicks
        if nav_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            url_str = url.toString()

            # Allow anchor navigation within the same page
            if url_str.startswith('#') or (url.hasFragment() and url.path() == ''):
                return True

            # Check if Shift is pressed for new tab
            modifiers = QApplication.keyboardModifiers()
            new_tab = bool(modifiers & Qt.KeyboardModifier.ShiftModifier)

            self.link_clicked.emit(url_str, new_tab)
            return False  # Prevent default navigation

        return True


class SessionManager:
    """Manages saving and restoring application session state"""

    def __init__(self):
        self.session_dir = Path.home() / ".markdown-viewer"
        self.session_file = self.session_dir / "session.json"

    def save_session(self, viewer: 'MarkdownViewer') -> bool:
        """Save current session state to JSON file"""
        try:
            self.session_dir.mkdir(parents=True, exist_ok=True)

            # Collect tab data
            tabs = []
            for i in range(viewer.tab_widget.count()):
                tab = viewer.tab_widget.widget(i)
                if tab.current_folder or tab.current_file:
                    tabs.append({
                        "folder_path": tab.current_folder,
                        "selected_file": tab.current_file
                    })

            session_data = {
                "version": "1.0",
                "window": {
                    "x": viewer.x(),
                    "y": viewer.y(),
                    "width": viewer.width(),
                    "height": viewer.height(),
                    "maximized": viewer.isMaximized()
                },
                "tabs": tabs,
                "active_tab_index": viewer.tab_widget.currentIndex()
            }

            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False

    def load_session(self) -> dict | None:
        """Load session state from JSON file"""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading session: {e}")
        return None


class FolderTab(QWidget):
    """A single folder tab containing tree view and web view"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_folder = None
        self.current_file = None
        self.file_model = None
        self.tree_view = None
        self.web_view = None
        self.stats_panel = None
        self.stats_labels = {}
        self._setup_ui()

    def _setup_ui(self):
        """Setup splitter layout for this tab"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Tree view + Stats
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Tree view setup
        self.tree_view = QTreeView()
        self.file_model = QFileSystemModel()
        self.file_model.setNameFilters(["*.md", "*.markdown"])
        self.file_model.setNameFilterDisables(False)
        self.tree_view.setModel(self.file_model)

        # Hide unnecessary columns
        self.tree_view.setColumnHidden(1, True)
        self.tree_view.setColumnHidden(2, True)
        self.tree_view.setColumnHidden(3, True)
        self.tree_view.setHeaderHidden(True)

        # Stats panel below tree view
        self.stats_panel = QFrame()
        self.stats_panel.setStyleSheet("""
            QFrame {
                background-color: #e3f2fd;
                border-top: 1px solid #90caf9;
                padding: 8px;
            }
            QLabel {
                color: #1e3a5f;
                font-size: 11px;
            }
            QLabel[class="value"] {
                font-weight: bold;
                color: #0d47a1;
            }
        """)
        stats_layout = QVBoxLayout(self.stats_panel)
        stats_layout.setContentsMargins(8, 8, 8, 8)
        stats_layout.setSpacing(4)

        # Stats header
        header = QLabel("Stats")
        header.setStyleSheet("font-weight: bold; font-size: 12px; color: #0d47a1;")
        stats_layout.addWidget(header)

        # Stats rows
        for key, label in [("lines", "Lines"), ("chars", "Chars"), ("words", "Words"), ("time", "Read"), ("size", "Size")]:
            row = QHBoxLayout()
            row.setSpacing(4)
            name_label = QLabel(f"{label}:")
            name_label.setStyleSheet("color: #5c6bc0;")
            value_label = QLabel("-")
            value_label.setStyleSheet("font-weight: bold; color: #0d47a1;")
            value_label.setProperty("class", "value")
            row.addWidget(name_label)
            row.addStretch()
            row.addWidget(value_label)
            stats_layout.addLayout(row)
            self.stats_labels[key] = value_label

        left_layout.addWidget(self.tree_view, 1)
        left_layout.addWidget(self.stats_panel)

        left_panel.setMinimumWidth(180)
        left_panel.setMaximumWidth(300)

        # Web view setup with custom page for link handling
        self.web_view = QWebEngineView()
        self.web_page = MarkdownWebPage(self.web_view)
        self.web_view.setPage(self.web_page)
        self.web_view.setMinimumWidth(600)

        # Enable context menu for right-click
        self.web_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        splitter.addWidget(left_panel)
        splitter.addWidget(self.web_view)
        splitter.setSizes([200, 1200])

        layout.addWidget(splitter)

    def update_stats(self, content: str):
        """Update stats panel with content statistics"""
        lines = len(content.split('\n'))
        chars = len(content)
        words = len(content.split())
        read_time = max(1, round(words / 200))
        size_kb = len(content.encode('utf-8')) / 1024

        self.stats_labels["lines"].setText(f"{lines:,}")
        self.stats_labels["chars"].setText(f"{chars:,}")
        self.stats_labels["words"].setText(f"{words:,}")
        self.stats_labels["time"].setText(f"~{read_time} min")
        self.stats_labels["size"].setText(f"{size_kb:.1f} KB")

    def set_folder(self, folder_path: str):
        """Set the root folder for this tab"""
        self.current_folder = folder_path
        self.file_model.setRootPath(folder_path)
        self.tree_view.setRootIndex(self.file_model.index(folder_path))

    def get_tab_name(self) -> str:
        """Return display name for tab"""
        if self.current_folder:
            return os.path.basename(self.current_folder)
        return "New Tab"


class MarkdownViewer(QMainWindow):
    def __init__(self, file_path: str = None):
        super().__init__()
        self.setWindowTitle("Markdown Viewer")
        self.setGeometry(100, 100, 1400, 900)

        self.css_content = ""
        self.tab_widget = None
        self.session_manager = SessionManager()

        self._load_css()
        self._setup_ui()
        self._setup_toolbar()
        self._setup_shortcuts()

        # Open file if provided via command line, otherwise restore session
        if file_path:
            self.open_file(file_path)
        else:
            self._restore_session()

    def _load_css(self):
        """Load CSS content from file"""
        css_path = Path(__file__).parent / "style.css"
        if css_path.exists():
            self.css_content = css_path.read_text(encoding="utf-8")

    def _setup_ui(self):
        """Setup main UI with tab widget"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self._close_tab)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        # Style the tab bar
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                padding: 8px 16px;
                margin-right: 2px;
                background: #e3f2fd;
                border: 1px solid #90caf9;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom: 1px solid #ffffff;
            }
            QTabBar::tab:hover:!selected {
                background: #bbdefb;
            }
        """)

        self.setCentralWidget(self.tab_widget)

    def _setup_toolbar(self):
        """Setup toolbar with actions"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # New tab action
        new_tab_action = QAction("➕ New Tab", self)
        new_tab_action.setShortcut("Ctrl+T")
        new_tab_action.triggered.connect(lambda: self._add_new_tab())
        toolbar.addAction(new_tab_action)

        # Open folder action
        open_folder_action = QAction("📂 Open Folder", self)
        open_folder_action.setShortcut("Ctrl+O")
        open_folder_action.triggered.connect(self._open_folder_in_current_tab)
        toolbar.addAction(open_folder_action)

        # Refresh action
        refresh_action = QAction("🔄 Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_current_tab)
        toolbar.addAction(refresh_action)

        toolbar.addSeparator()

        # Toggle overview action
        toggle_overview_action = QAction("📑 Outline", self)
        toggle_overview_action.setShortcut("Ctrl+Shift+O")
        toggle_overview_action.triggered.connect(self._toggle_overview)
        toolbar.addAction(toggle_overview_action)


    def _setup_shortcuts(self):
        """Setup additional keyboard shortcuts"""
        # Close tab
        close_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        close_shortcut.activated.connect(self._close_current_tab)

        # Next tab
        next_tab_shortcut = QShortcut(QKeySequence("Ctrl+Tab"), self)
        next_tab_shortcut.activated.connect(self._next_tab)

        # Previous tab
        prev_tab_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
        prev_tab_shortcut.activated.connect(self._prev_tab)

    def _add_welcome_tab(self):
        """Add initial welcome tab"""
        tab = self._add_new_tab()
        self._render_markdown(tab, "# Welcome to Markdown Viewer\n\nOpen a folder to get started.\n\n## Keyboard Shortcuts\n\n| Shortcut | Action |\n|----------|--------|\n| Ctrl+T | New Tab |\n| Ctrl+W | Close Tab |\n| Ctrl+O | Open Folder |\n| Ctrl+Tab | Next Tab |\n| Ctrl+Shift+Tab | Previous Tab |\n| Ctrl+Shift+O | Toggle Outline |\n| Ctrl+Shift+I | Toggle Stats |\n| F5 | Refresh |")

    def _add_new_tab(self, folder_path: str = None) -> FolderTab:
        """Create and add a new folder tab"""
        tab = FolderTab(self)
        tab.tree_view.clicked.connect(
            lambda idx, t=tab: self._on_file_clicked(t, idx)
        )

        # Connect link click signal
        tab.web_page.link_clicked.connect(
            lambda url, new_tab, t=tab: self._on_link_clicked(t, url, new_tab)
        )

        # Connect context menu for right-click
        tab.web_view.customContextMenuRequested.connect(
            lambda pos, t=tab: self._show_link_context_menu(t, pos)
        )

        if folder_path:
            tab.set_folder(folder_path)
            self.tab_widget.addTab(tab, tab.get_tab_name())
        else:
            self.tab_widget.addTab(tab, "New Tab")

        self.tab_widget.setCurrentWidget(tab)
        return tab

    def _open_folder_in_current_tab(self):
        """Open folder in current tab"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            tab = self._get_current_tab()
            if tab:
                tab.set_folder(folder)
                self._update_tab_title(tab)
                self.setWindowTitle(f"Markdown Viewer - {folder}")

    def _close_tab(self, index: int):
        """Close tab at given index"""
        if self.tab_widget.count() > 1:
            widget = self.tab_widget.widget(index)
            self.tab_widget.removeTab(index)
            widget.deleteLater()
        else:
            # Last tab - just reset it
            tab = self.tab_widget.widget(0)
            tab.current_folder = None
            tab.current_file = None
            self.tab_widget.setTabText(0, "New Tab")
            self._render_markdown(tab, "# Welcome to Markdown Viewer\n\nOpen a folder to get started.")
            self.setWindowTitle("Markdown Viewer")

    def _close_current_tab(self):
        """Close currently active tab"""
        current_index = self.tab_widget.currentIndex()
        self._close_tab(current_index)

    def _next_tab(self):
        """Switch to next tab"""
        current = self.tab_widget.currentIndex()
        next_index = (current + 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(next_index)

    def _prev_tab(self):
        """Switch to previous tab"""
        current = self.tab_widget.currentIndex()
        prev_index = (current - 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(prev_index)

    def _get_current_tab(self) -> FolderTab:
        """Get currently active tab"""
        return self.tab_widget.currentWidget()

    def _update_tab_title(self, tab: FolderTab):
        """Update tab title"""
        index = self.tab_widget.indexOf(tab)
        if index >= 0:
            self.tab_widget.setTabText(index, tab.get_tab_name())

    def _on_tab_changed(self, index: int):
        """Handle tab change"""
        tab = self.tab_widget.widget(index)
        if tab and tab.current_folder:
            self.setWindowTitle(f"Markdown Viewer - {tab.current_folder}")
        elif tab and tab.current_file:
            self.setWindowTitle(f"Markdown Viewer - {os.path.basename(tab.current_file)}")
        else:
            self.setWindowTitle("Markdown Viewer")

    def _on_file_clicked(self, tab: FolderTab, index: QModelIndex):
        """Handle file click in tree view"""
        file_path = tab.file_model.filePath(index)

        if os.path.isfile(file_path) and file_path.lower().endswith(('.md', '.markdown')):
            tab.current_file = file_path
            self._load_markdown_file(tab, file_path)
            self.setWindowTitle(f"Markdown Viewer - {os.path.basename(file_path)}")

    def _load_markdown_file(self, tab: FolderTab, file_path: str):
        """Load and render markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self._render_markdown(tab, content)
            tab.update_stats(content)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file:\n{e}")

    def _render_markdown(self, tab: FolderTab, markdown_content: str):
        """Render markdown content in web view"""
        # Escape special characters for JavaScript
        escaped_content = markdown_content.replace('\\', '\\\\')
        escaped_content = escaped_content.replace('`', '\\`')
        escaped_content = escaped_content.replace('$', '\\$')

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>{self.css_content}</style>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
</head>
<body>
    <div id="content"></div>

    <!-- Overview Sidebar (Right) -->
    <div id="sidebar-container" class="sidebar-container">
        <button class="sidebar-toggle" onclick="toggleOverview()">Outline</button>
        <div id="overview-box" class="overview-box">
            <h4>Outline</h4>
            <ul id="toc-list"></ul>
        </div>
    </div>


    <script>
        // Configure mermaid
        mermaid.initialize({{ startOnLoad: false, theme: 'default' }});

        // Custom renderer for mermaid code blocks (supports both old and new marked.js API)
        const renderer = {{
            code(codeOrObj, language) {{
                // Handle both old API (code, language) and new API ({{text, lang}})
                let code, lang;
                if (typeof codeOrObj === 'object' && codeOrObj !== null) {{
                    code = codeOrObj.text || codeOrObj.code || '';
                    lang = codeOrObj.lang || codeOrObj.language || '';
                }} else {{
                    code = codeOrObj || '';
                    lang = language || '';
                }}

                if (lang === 'mermaid') {{
                    return '<div class="mermaid">' + code + '</div>';
                }}
                // Default code block rendering
                const escaped = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                return '<pre><code class="language-' + lang + '">' + escaped + '</code></pre>';
            }}
        }};

        marked.use({{ renderer }});
        marked.setOptions({{
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

        // Build Table of Contents
        function buildTOC() {{
            const content = document.getElementById('content');
            const headings = content.querySelectorAll('h1, h2, h3, h4');
            const tocList = document.getElementById('toc-list');
            tocList.innerHTML = '';

            if (headings.length === 0) {{
                document.getElementById('sidebar-container').style.display = 'none';
                return;
            }}

            headings.forEach((heading, index) => {{
                if (!heading.id) {{
                    heading.id = 'heading-' + index;
                }}

                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = '#' + heading.id;
                a.textContent = heading.textContent;
                a.className = 'toc-' + heading.tagName.toLowerCase();
                a.onclick = function(e) {{
                    e.preventDefault();
                    heading.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                    document.querySelectorAll('.overview-box a').forEach(link => {{
                        link.classList.remove('active');
                    }});
                    this.classList.add('active');
                }};

                li.appendChild(a);
                tocList.appendChild(li);
            }});
        }}

        buildTOC();

        // Scroll spy - highlight current section
        function updateActiveHeading() {{
            const headings = document.querySelectorAll('#content h1, #content h2, #content h3, #content h4');
            const tocLinks = document.querySelectorAll('.overview-box a');

            let currentHeading = null;
            headings.forEach((heading, index) => {{
                const rect = heading.getBoundingClientRect();
                if (rect.top <= 100) {{
                    currentHeading = index;
                }}
            }});

            tocLinks.forEach((link, index) => {{
                link.classList.toggle('active', index === currentHeading);
            }});
        }}

        window.addEventListener('scroll', updateActiveHeading);

        // Toggle functions
        function toggleOverview() {{
            document.getElementById('sidebar-container').classList.toggle('closed');
        }}

    </script>
</body>
</html>"""

        tab.web_view.setHtml(html)

    def _refresh_current_tab(self):
        """Refresh current file in current tab"""
        tab = self._get_current_tab()
        if tab and tab.current_file and os.path.exists(tab.current_file):
            self._load_markdown_file(tab, tab.current_file)

    def _toggle_overview(self):
        """Toggle overview box visibility"""
        tab = self._get_current_tab()
        if tab and tab.web_view:
            tab.web_view.page().runJavaScript("toggleOverview();")

    def _on_link_clicked(self, tab: FolderTab, url: str, open_in_new_tab: bool):
        """Handle link click in markdown content"""
        # Handle external URLs - open in system browser
        if url.startswith('http://') or url.startswith('https://'):
            QDesktopServices.openUrl(QUrl(url))
            return

        # Handle local markdown links
        if tab.current_file:
            base_dir = os.path.dirname(tab.current_file)
        elif tab.current_folder:
            base_dir = tab.current_folder
        else:
            return

        # Remove file:// prefix if present
        if url.startswith('file:///'):
            url = url[8:]  # Remove 'file:///'
        elif url.startswith('file://'):
            url = url[7:]  # Remove 'file://'

        # Handle anchor links within same file
        if url.startswith('#'):
            tab.web_view.page().runJavaScript(
                f"document.getElementById('{url[1:]}')?.scrollIntoView({{behavior: 'smooth'}});"
            )
            return

        # Resolve relative path
        target_path = os.path.normpath(os.path.join(base_dir, url))

        # Check if it's a markdown file
        if not target_path.lower().endswith(('.md', '.markdown')):
            # Try adding .md extension
            if os.path.exists(target_path + '.md'):
                target_path = target_path + '.md'
            elif not os.path.exists(target_path):
                QMessageBox.warning(self, "Warning", f"File not found:\n{target_path}")
                return

        if not os.path.exists(target_path):
            QMessageBox.warning(self, "Warning", f"File not found:\n{target_path}")
            return

        if open_in_new_tab:
            # Open in new tab
            folder = os.path.dirname(target_path)
            new_tab = self._add_new_tab(folder)
            new_tab.current_file = target_path
            self._load_markdown_file(new_tab, target_path)
            self.setWindowTitle(f"Markdown Viewer - {os.path.basename(target_path)}")
        else:
            # Open in same tab
            tab.current_file = target_path
            self._load_markdown_file(tab, target_path)
            self.setWindowTitle(f"Markdown Viewer - {os.path.basename(target_path)}")

            # Update tree view selection if in same folder
            file_index = tab.file_model.index(target_path)
            if file_index.isValid():
                tab.tree_view.setCurrentIndex(file_index)
                tab.tree_view.scrollTo(file_index)

    def _show_link_context_menu(self, tab: FolderTab, pos):
        """Show context menu for right-click on links"""
        # Get the link URL at the click position using JavaScript
        tab.web_view.page().runJavaScript(
            """
            (function() {
                var elem = document.elementFromPoint(%d, %d);
                while (elem && elem.tagName !== 'A') {
                    elem = elem.parentElement;
                }
                return elem ? elem.href : null;
            })()
            """ % (pos.x(), pos.y()),
            lambda url: self._handle_context_menu(tab, pos, url)
        )

    def _handle_context_menu(self, tab: FolderTab, pos, url: str):
        """Handle context menu after getting link URL"""
        if not url:
            return

        menu = QMenu(self)
        open_action = menu.addAction("Open")
        open_new_tab_action = menu.addAction("Open in New Tab")

        action = menu.exec(tab.web_view.mapToGlobal(pos))
        if action == open_action:
            self._on_link_clicked(tab, url, False)
        elif action == open_new_tab_action:
            self._on_link_clicked(tab, url, True)

    def open_file(self, file_path: str):
        """Open a specific markdown file"""
        file_path = os.path.abspath(file_path)

        if not os.path.exists(file_path):
            QMessageBox.critical(self, "Error", f"File not found:\n{file_path}")
            return

        if not file_path.lower().endswith(('.md', '.markdown')):
            QMessageBox.warning(self, "Warning", "This file is not a Markdown file.")
            return

        # Create new tab with the folder
        folder = os.path.dirname(file_path)
        tab = self._add_new_tab(folder)

        # Select the file in tree view
        file_index = tab.file_model.index(file_path)
        tab.tree_view.setCurrentIndex(file_index)
        tab.tree_view.scrollTo(file_index)

        # Load and display the file
        tab.current_file = file_path
        self._load_markdown_file(tab, file_path)
        self.setWindowTitle(f"Markdown Viewer - {os.path.basename(file_path)}")

    def closeEvent(self, event: QCloseEvent):
        """Save session before closing"""
        self.session_manager.save_session(self)

        # Stop all WebViews before closing to prevent JS errors
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if tab and tab.web_view:
                tab.web_view.stop()
                tab.web_view.setHtml("")

        event.accept()

    def _restore_session(self):
        """Restore previous session on startup"""
        session_data = self.session_manager.load_session()

        if not session_data:
            self._add_welcome_tab()
            return

        try:
            # Restore window geometry
            window_state = session_data.get('window', {})
            x = window_state.get('x', 100)
            y = window_state.get('y', 100)
            width = window_state.get('width', 1400)
            height = window_state.get('height', 900)

            # Ensure window is within screen bounds
            screen = QApplication.primaryScreen().availableGeometry()
            x = max(0, min(x, screen.width() - width))
            y = max(0, min(y, screen.height() - height))
            width = min(width, screen.width())
            height = min(height, screen.height())

            self.setGeometry(x, y, width, height)

            if window_state.get('maximized', False):
                self.showMaximized()

            # Restore tabs
            tabs_data = session_data.get('tabs', [])
            restored_any = False
            pending_file_loads = []

            for tab_data in tabs_data:
                folder = tab_data.get('folder_path')
                selected_file = tab_data.get('selected_file')

                # Skip if folder doesn't exist
                if folder and not os.path.exists(folder):
                    continue

                if folder:
                    tab = self._add_new_tab(folder)
                    restored_any = True

                    # Queue file for delayed loading (QFileSystemModel needs time)
                    if selected_file and os.path.exists(selected_file):
                        pending_file_loads.append((tab, selected_file))

            # If no tabs were restored, show welcome tab
            if not restored_any:
                self._add_welcome_tab()
                return

            # Delay file selection and loading to allow QFileSystemModel to populate
            def load_pending_files():
                for tab, file_path in pending_file_loads:
                    tab.current_file = file_path
                    file_index = tab.file_model.index(file_path)
                    if file_index.isValid():
                        tab.tree_view.setCurrentIndex(file_index)
                        tab.tree_view.scrollTo(file_index)
                    self._load_markdown_file(tab, file_path)

            QTimer.singleShot(200, load_pending_files)

            # Restore active tab
            active_index = session_data.get('active_tab_index', 0)
            if 0 <= active_index < self.tab_widget.count():
                self.tab_widget.setCurrentIndex(active_index)

        except Exception as e:
            print(f"Error restoring session: {e}")
            self._add_welcome_tab()


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
