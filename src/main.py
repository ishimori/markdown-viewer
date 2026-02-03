"""
Markdown Viewer with Mermaid support
Windows Desktop Application using PyQt6
"""

import sys
import os
import json
from pathlib import Path


def get_resource_path(relative_path: str) -> Path:
    """Get absolute path to resource, works for dev and PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent
    return base_path / relative_path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QTreeView,
    QVBoxLayout, QHBoxLayout, QWidget, QToolBar, QFileDialog, QMessageBox,
    QTabWidget, QTabBar, QLabel, QFrame, QMenu, QComboBox
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PyQt6.QtCore import Qt, QModelIndex, QTimer, QUrl, pyqtSignal
from PyQt6.QtGui import QAction, QFileSystemModel, QShortcut, QKeySequence, QCloseEvent, QDesktopServices


# Qt Widget Styles (centralized for maintainability)
QT_STYLES = {
    'filter_combo': """
        QComboBox {
            padding: 4px 8px;
            border: 1px solid #90caf9;
            border-radius: 4px;
            background: #ffffff;
            color: #1e3a5f;
            font-size: 11px;
        }
        QComboBox:hover {
            border-color: #1976d2;
        }
        QComboBox::drop-down {
            border: none;
            padding-right: 8px;
        }
    """,
    'stats_panel': """
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
    """,
    'stats_header': "font-weight: bold; font-size: 12px; color: #0d47a1;",
    'stats_name': "color: #5c6bc0;",
    'stats_value': "font-weight: bold; color: #0d47a1;",
    'tab_widget': """
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
    """
}


class MarkdownWebPage(QWebEnginePage):
    """Custom WebEnginePage to handle link clicks"""
    link_clicked = pyqtSignal(str, bool)  # (url, open_in_new_tab)

    def acceptNavigationRequest(self, url: QUrl, nav_type, is_main_frame: bool) -> bool:
        try:
            # Only intercept link clicks
            if nav_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
                url_str = url.toString()

                # Allow anchor navigation within the same page
                if url_str.startswith('#') or (url.hasFragment() and url.path() == ''):
                    return True

                # Check if Shift is pressed for new tab
                modifiers = QApplication.keyboardModifiers()
                new_tab = bool(modifiers & Qt.KeyboardModifier.ShiftModifier)

                # Defer signal emission to avoid crash during navigation request
                QTimer.singleShot(0, lambda u=url_str, n=new_tab: self.link_clicked.emit(u, n))
                return False  # Prevent default navigation

            return True
        except Exception as e:
            print(f"Error in navigation request: {e}")
            return False


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
                        "selected_file": tab.current_file,
                        "filter_index": tab.get_filter_index()
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

    # Filter options: (display_name, filter_patterns or None for all)
    FILTER_OPTIONS = [
        ("Markdown only", ["*.md", "*.markdown"]),
        ("All files", None),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_folder = None
        self.current_file = None
        self.file_model = None
        self.tree_view = None
        self.web_view = None
        self.web_page = None
        self.stats_panel = None
        self.stats_labels = {}
        self.filter_combo = None
        self.navigation_history = []  # Stack for back navigation
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

        # Filter dropdown
        self.filter_combo = QComboBox()
        for display_name, _ in self.FILTER_OPTIONS:
            self.filter_combo.addItem(display_name)
        self.filter_combo.setStyleSheet(QT_STYLES['filter_combo'])
        self.filter_combo.currentIndexChanged.connect(self._on_filter_changed)
        left_layout.addWidget(self.filter_combo)

        # Tree view setup
        self.tree_view = QTreeView()
        self.file_model = QFileSystemModel()
        self._apply_filter(0)  # Apply default filter (Markdown only)
        self.tree_view.setModel(self.file_model)

        # Hide unnecessary columns
        self.tree_view.setColumnHidden(1, True)
        self.tree_view.setColumnHidden(2, True)
        self.tree_view.setColumnHidden(3, True)
        self.tree_view.setHeaderHidden(True)

        # Stats panel below tree view
        self.stats_panel = QFrame()
        self.stats_panel.setStyleSheet(QT_STYLES['stats_panel'])
        stats_layout = QVBoxLayout(self.stats_panel)
        stats_layout.setContentsMargins(8, 8, 8, 8)
        stats_layout.setSpacing(4)

        # Stats header
        header = QLabel("Stats")
        header.setStyleSheet(QT_STYLES['stats_header'])
        stats_layout.addWidget(header)

        # Stats rows
        for key, label in [("lines", "Lines"), ("chars", "Chars"), ("words", "Words"), ("time", "Read"), ("size", "Size")]:
            row = QHBoxLayout()
            row.setSpacing(4)
            name_label = QLabel(f"{label}:")
            name_label.setStyleSheet(QT_STYLES['stats_name'])
            value_label = QLabel("-")
            value_label.setStyleSheet(QT_STYLES['stats_value'])
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

        # Allow local content to access remote URLs (for CDN scripts)
        self.web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )

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

    def _apply_filter(self, index: int):
        """Apply file filter based on index"""
        _, filters = self.FILTER_OPTIONS[index]
        if filters is None:
            # Show all files
            self.file_model.setNameFilters([])
            self.file_model.setNameFilterDisables(True)
        else:
            self.file_model.setNameFilters(filters)
            self.file_model.setNameFilterDisables(False)

    def _on_filter_changed(self, index: int):
        """Handle filter dropdown change"""
        self._apply_filter(index)

    def get_filter_index(self) -> int:
        """Get current filter index"""
        return self.filter_combo.currentIndex()

    def set_filter_index(self, index: int):
        """Set filter index"""
        if 0 <= index < len(self.FILTER_OPTIONS):
            self.filter_combo.setCurrentIndex(index)


class MarkdownViewer(QMainWindow):
    def __init__(self, file_path: str = None):
        super().__init__()
        self.setWindowTitle("Markdown Viewer")
        self.setGeometry(100, 100, 1400, 900)

        self.css_content = ""
        self.marked_js_path = ""
        self.mermaid_js_path = ""
        self.html_template = ""
        self.tab_widget = None
        self.session_manager = SessionManager()

        self._load_resources()
        self._setup_ui()
        self._setup_toolbar()
        self._setup_shortcuts()

        # Open file if provided via command line, otherwise restore session
        if file_path:
            self.open_file(file_path)
        else:
            self._restore_session()

    def _load_resources(self):
        """Load CSS, JavaScript paths, and HTML template"""
        # Load CSS
        css_path = get_resource_path("style.css")
        if css_path.exists():
            self.css_content = css_path.read_text(encoding="utf-8")

        # Get JavaScript paths
        js_dir = get_resource_path("assets/js")
        self.marked_js_path = str(js_dir / "marked.min.js").replace('\\', '/')
        self.mermaid_js_path = str(js_dir / "mermaid.min.js").replace('\\', '/')

        # Load HTML template
        template_path = get_resource_path("templates/markdown.html")
        if template_path.exists():
            self.html_template = template_path.read_text(encoding="utf-8")

    def _setup_ui(self):
        """Setup main UI with tab widget"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self._close_tab)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        # Style the tab bar
        self.tab_widget.setStyleSheet(QT_STYLES['tab_widget'])

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
                self._update_window_title()

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
            self._update_window_title()

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

    def _update_window_title(self):
        """Update window title based on current tab state (SSOT)"""
        tab = self._get_current_tab()
        if tab:
            if tab.current_file:
                self.setWindowTitle(f"Markdown Viewer - {os.path.basename(tab.current_file)}")
            elif tab.current_folder:
                self.setWindowTitle(f"Markdown Viewer - {tab.current_folder}")
            else:
                self.setWindowTitle("Markdown Viewer")
        else:
            self.setWindowTitle("Markdown Viewer")

    def _update_tab_title(self, tab: FolderTab):
        """Update tab title"""
        index = self.tab_widget.indexOf(tab)
        if index >= 0:
            self.tab_widget.setTabText(index, tab.get_tab_name())

    def _on_tab_changed(self, index: int):
        """Handle tab change"""
        self._update_window_title()

    def _on_file_clicked(self, tab: FolderTab, index: QModelIndex):
        """Handle file click in tree view"""
        file_path = tab.file_model.filePath(index)

        if not os.path.isfile(file_path):
            return

        # Check if file should be opened based on current filter
        is_markdown = file_path.lower().endswith(('.md', '.markdown'))
        filter_allows_all = tab.get_filter_index() == 1  # "All files"

        if is_markdown or filter_allows_all:
            # Clear navigation history when selecting from sidebar
            tab.navigation_history.clear()
            tab.current_file = file_path
            self._load_markdown_file(tab, file_path)
            self._update_window_title()

    def _load_markdown_file(self, tab: FolderTab, file_path: str):
        """Load and render markdown file (or text file as markdown)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self._render_markdown(tab, content)
            tab.update_stats(content)
        except UnicodeDecodeError:
            QMessageBox.warning(
                self, "Cannot Open File",
                f"This file cannot be displayed as text:\n{os.path.basename(file_path)}\n\n"
                "The file may be a binary file (image, PDF, etc.)."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file:\n{e}")

    def _render_markdown(self, tab: FolderTab, markdown_content: str):
        """Render markdown content in web view"""
        # Escape special characters for JavaScript template literal
        escaped_content = markdown_content.replace('\\', '\\\\')
        escaped_content = escaped_content.replace('`', '\\`')
        escaped_content = escaped_content.replace('$', '\\$')

        # Back button visibility
        back_button_style = "display: flex;" if tab.navigation_history else "display: none;"

        # Build HTML from template
        html = self.html_template
        html = html.replace('$CSS_CONTENT$', self.css_content)
        html = html.replace('$MARKED_JS_PATH$', self.marked_js_path)
        html = html.replace('$MERMAID_JS_PATH$', self.mermaid_js_path)
        html = html.replace('$MARKDOWN_CONTENT$', escaped_content)
        html = html.replace('$BACK_BUTTON_STYLE$', back_button_style)

        # Set base URL for relative links to work correctly
        if tab.current_file:
            base_url = QUrl.fromLocalFile(os.path.dirname(tab.current_file) + '/')
        elif tab.current_folder:
            base_url = QUrl.fromLocalFile(tab.current_folder + '/')
        else:
            base_url = QUrl()
        tab.web_view.setHtml(html, base_url)

    def _refresh_current_tab(self):
        """Refresh current file in current tab"""
        tab = self._get_current_tab()
        if tab and tab.current_file and os.path.exists(tab.current_file):
            # Clear navigation history on refresh
            tab.navigation_history.clear()
            self._load_markdown_file(tab, tab.current_file)

    def _toggle_overview(self):
        """Toggle overview box visibility"""
        tab = self._get_current_tab()
        if tab and tab.web_view:
            tab.web_view.page().runJavaScript("try { toggleOverview(); } catch(e) { console.error('Toggle error:', e); }")

    def _on_link_clicked(self, tab: FolderTab, url: str, open_in_new_tab: bool):
        """Handle link click in markdown content"""
        try:
            # Handle back button click
            if url == 'app://back':
                self._navigate_back(tab)
                return

            # Handle external URLs - open in system browser
            if url.startswith('http://') or url.startswith('https://'):
                QDesktopServices.openUrl(QUrl(url))
                return

            # Handle anchor links within same file
            if url.startswith('#'):
                anchor_id = url[1:].replace("'", "\\'").replace("\\", "\\\\")
                tab.web_view.page().runJavaScript(
                    f"try {{ document.getElementById('{anchor_id}')?.scrollIntoView({{behavior: 'smooth'}}); }} catch(e) {{ console.error('Scroll error:', e); }}"
                )
                return

            # Convert file:// URL to local path
            qurl = QUrl(url)
            if qurl.isLocalFile():
                target_path = qurl.toLocalFile()
            else:
                # Handle relative paths
                if tab.current_file:
                    base_dir = os.path.dirname(tab.current_file)
                elif tab.current_folder:
                    base_dir = tab.current_folder
                else:
                    return
                target_path = os.path.normpath(os.path.join(base_dir, url))

            # Check if file exists, try .md extension if not
            if not os.path.exists(target_path):
                if os.path.exists(target_path + '.md'):
                    target_path = target_path + '.md'
                elif os.path.exists(target_path + '.markdown'):
                    target_path = target_path + '.markdown'
                else:
                    QMessageBox.warning(self, "Warning", f"File not found:\n{target_path}")
                    return

            # Check filter setting for non-markdown files
            is_markdown = target_path.lower().endswith(('.md', '.markdown'))
            filter_allows_all = tab.get_filter_index() == 1  # "All files"
            if not is_markdown and not filter_allows_all:
                QMessageBox.warning(
                    self, "Warning",
                    f"Cannot open non-Markdown file:\n{os.path.basename(target_path)}\n\n"
                    "Switch to 'All files' filter to open this file."
                )
                return

            if open_in_new_tab:
                # Open in new tab
                folder = os.path.dirname(target_path)
                new_tab = self._add_new_tab(folder)
                new_tab.current_file = target_path
                self._load_markdown_file(new_tab, target_path)
                self._update_window_title()
            else:
                # Open in same tab - add current file to history for back navigation
                if tab.current_file:
                    tab.navigation_history.append(tab.current_file)
                tab.current_file = target_path
                self._load_markdown_file(tab, target_path)
                self._update_window_title()

                # Update tree view selection if in same folder
                file_index = tab.file_model.index(target_path)
                if file_index.isValid():
                    tab.tree_view.setCurrentIndex(file_index)
                    tab.tree_view.scrollTo(file_index)
        except Exception as e:
            print(f"Error handling link click: {e}")
            QMessageBox.warning(self, "Error", f"Failed to open link:\n{url}\n\nError: {e}")

    def _navigate_back(self, tab: FolderTab):
        """Navigate back to previous file in history"""
        if not tab.navigation_history:
            return

        # Pop the previous file from history
        previous_file = tab.navigation_history.pop()

        # Load the previous file (without adding to history)
        if os.path.exists(previous_file):
            tab.current_file = previous_file
            self._load_markdown_file(tab, previous_file)
            self._update_window_title()

            # Update tree view selection if in same folder
            file_index = tab.file_model.index(previous_file)
            if file_index.isValid():
                tab.tree_view.setCurrentIndex(file_index)
                tab.tree_view.scrollTo(file_index)

    def _show_link_context_menu(self, tab: FolderTab, pos):
        """Show context menu for right-click on links"""
        try:
            # Get the link URL at the click position using JavaScript
            tab.web_view.page().runJavaScript(
                """
                (function() {
                    try {
                        var elem = document.elementFromPoint(%d, %d);
                        while (elem && elem.tagName !== 'A') {
                            elem = elem.parentElement;
                        }
                        return elem ? elem.href : null;
                    } catch(e) {
                        console.error('Context menu JS error:', e);
                        return null;
                    }
                })()
                """ % (pos.x(), pos.y()),
                lambda url: self._handle_context_menu(tab, pos, url)
            )
        except Exception as e:
            print(f"Error showing context menu: {e}")

    def _handle_context_menu(self, tab: FolderTab, pos, url: str):
        """Handle context menu after getting link URL"""
        try:
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
        except Exception as e:
            print(f"Error handling context menu: {e}")

    def open_file(self, file_path: str):
        """Open a specific file (markdown or text)"""
        file_path = os.path.abspath(file_path)

        if not os.path.exists(file_path):
            QMessageBox.critical(self, "Error", f"File not found:\n{file_path}")
            return

        # Create new tab with the folder
        folder = os.path.dirname(file_path)
        tab = self._add_new_tab(folder)

        # For non-markdown files, switch filter to "All files"
        if not file_path.lower().endswith(('.md', '.markdown')):
            tab.set_filter_index(1)  # "All files"

        # Select the file in tree view (with delay for QFileSystemModel)
        def select_file():
            file_index = tab.file_model.index(file_path)
            if file_index.isValid():
                tab.tree_view.setCurrentIndex(file_index)
                tab.tree_view.scrollTo(file_index)
        QTimer.singleShot(100, select_file)

        # Load and display the file
        tab.current_file = file_path
        self._load_markdown_file(tab, file_path)
        self._update_window_title()

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
                filter_index = tab_data.get('filter_index', 0)

                # Skip if folder doesn't exist
                if folder and not os.path.exists(folder):
                    continue

                if folder:
                    tab = self._add_new_tab(folder)
                    tab.set_filter_index(filter_index)
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
