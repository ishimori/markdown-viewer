"""
Markdown Viewer with Mermaid support
Windows Desktop Application using PyQt6
"""

import sys
import os
import json
import csv
import xml.etree.ElementTree as ET
from io import StringIO
from pathlib import Path
from enum import Enum


def get_resource_path(relative_path: str) -> Path:
    """Get absolute path to resource, works for dev and PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent
    return base_path / relative_path


def get_version_info() -> tuple[str, bool]:
    """Get version number and whether running as frozen exe.

    Returns:
        tuple: (version_string, is_frozen)
    """
    # Check if running as frozen exe (PyInstaller)
    is_frozen = getattr(sys, 'frozen', False)

    # Read version from file
    version_file = get_resource_path('version.txt')
    try:
        with open(version_file, 'r', encoding='utf-8') as f:
            version = f.read().strip()
    except FileNotFoundError:
        version = '0.0'

    return version, is_frozen


class FileType(Enum):
    """Supported file types for viewing"""
    MARKDOWN = "markdown"
    XML = "xml"
    PYTHON = "python"
    CSV = "csv"
    CDXML = "cdxml"
    UNKNOWN = "unknown"


FILE_TYPE_MAP = {
    '.md': FileType.MARKDOWN,
    '.markdown': FileType.MARKDOWN,
    '.xml': FileType.XML,
    '.xsl': FileType.XML,
    '.xslt': FileType.XML,
    '.xsd': FileType.XML,
    '.svg': FileType.XML,
    '.py': FileType.PYTHON,
    '.pyw': FileType.PYTHON,
    '.csv': FileType.CSV,
    '.cdxml': FileType.CDXML,
}


def detect_file_type(file_path: str) -> FileType:
    """Detect file type from extension"""
    ext = os.path.splitext(file_path)[1].lower()
    return FILE_TYPE_MAP.get(ext, FileType.UNKNOWN)


# --- CDXML to SVG Converter ---

ELEMENT_SYMBOLS = {
    1: 'H', 5: 'B', 6: 'C', 7: 'N', 8: 'O', 9: 'F',
    14: 'Si', 15: 'P', 16: 'S', 17: 'Cl', 35: 'Br', 53: 'I',
}

ELEMENT_COLORS = {
    'O': '#e60000', 'N': '#0000e6', 'S': '#b8a000', 'P': '#ff8c00',
    'F': '#1a8c1a', 'Cl': '#1a8c1a', 'Br': '#8b0000', 'I': '#6600aa',
}


def cdxml_to_svg(cdxml_content: str) -> tuple[str, int]:
    """Convert CDXML content to SVG string.

    Returns:
        tuple: (svg_string, structure_count)
    """
    try:
        root = ET.fromstring(cdxml_content)
    except ET.ParseError:
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="50">'
            '<text x="10" y="30" fill="#c62828" font-family="Arial">Error: Invalid CDXML</text></svg>',
            0
        )

    atoms = {}   # id -> {x, y, element, label}
    bonds = []   # [{begin, end, order}]
    text_labels = []  # [{x, y, text}]
    structure_count = 0

    # Parse all fragments (chemical structures)
    for fragment in root.iter('fragment'):
        structure_count += 1
        for n in fragment.findall('n'):
            atom_id = n.get('id')
            pos_parts = n.get('p', '0 0').split()
            x, y = float(pos_parts[0]), float(pos_parts[1])
            element_num = int(n.get('Element', '6'))

            # Get label from <t><s> child elements
            label = ''
            t_elem = n.find('t')
            if t_elem is not None:
                label = ''.join(s.text or '' for s in t_elem.findall('s'))

            # Auto-generate label for non-carbon atoms without explicit label
            if not label and element_num != 6:
                symbol = ELEMENT_SYMBOLS.get(element_num, '?')
                num_h_attr = n.get('NumHydrogens')
                if num_h_attr is not None:
                    h = int(num_h_attr)
                    label = symbol + ('H' + (str(h) if h > 1 else '') if h > 0 else '')
                else:
                    label = symbol

            atoms[atom_id] = {'x': x, 'y': y, 'element': element_num, 'label': label}

        for b in fragment.findall('b'):
            bonds.append({
                'begin': b.get('B'),
                'end': b.get('E'),
                'order': int(b.get('Order', '1')),
            })

    # Collect structure name labels (direct children of <group> or <page>)
    for parent_tag in ('group', 'page'):
        for parent in root.iter(parent_tag):
            for t in parent.findall('t'):
                pos_parts = t.get('p', '0 0').split()
                x, y = float(pos_parts[0]), float(pos_parts[1])
                text = ''.join(s.text or '' for s in t.findall('s'))
                if text:
                    text_labels.append({'x': x, 'y': y, 'text': text})

    if not atoms:
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="50">'
            '<text x="10" y="30" font-family="Arial" fill="#555">No structures found</text></svg>',
            0
        )

    # Calculate bounding box with padding
    padding = 25
    all_x = [a['x'] for a in atoms.values()]
    all_y = [a['y'] for a in atoms.values()]
    if text_labels:
        all_x.extend(l['x'] for l in text_labels)
        all_y.extend(l['y'] for l in text_labels)

    min_x = min(all_x) - padding
    min_y = min(all_y) - padding
    max_x = max(all_x) + padding
    max_y = max(all_y) + padding + 10

    vb_w = max_x - min_x
    vb_h = max_y - min_y
    scale = 4.0
    svg_w = vb_w * scale
    svg_h = vb_h * scale

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{svg_w:.0f}" height="{svg_h:.0f}" '
        f'viewBox="{min_x:.2f} {min_y:.2f} {vb_w:.2f} {vb_h:.2f}">',
        '<style>',
        'text.atom { font-family: Arial, Helvetica, sans-serif; font-size: 11px; font-weight: bold; }',
        'text.name { font-family: Arial, Helvetica, sans-serif; font-size: 11px; fill: #333; }',
        'line.bond { stroke: #333; stroke-width: 1.2; stroke-linecap: round; }',
        '</style>',
    ]

    # 1) Draw bonds
    for bond in bonds:
        a1 = atoms.get(bond['begin'])
        a2 = atoms.get(bond['end'])
        if not a1 or not a2:
            continue

        x1, y1 = a1['x'], a1['y']
        x2, y2 = a2['x'], a2['y']
        dx, dy = x2 - x1, y2 - y1
        dist = (dx * dx + dy * dy) ** 0.5
        if dist == 0:
            continue
        ux, uy = dx / dist, dy / dist

        # Shorten towards labeled atoms so lines don't overlap text
        shrink1 = len(a1['label']) * 3.5 if a1['label'] else 0
        shrink2 = len(a2['label']) * 3.5 if a2['label'] else 0
        bx1, by1 = x1 + ux * shrink1, y1 + uy * shrink1
        bx2, by2 = x2 - ux * shrink2, y2 - uy * shrink2

        if bond['order'] == 2:
            nx, ny = -uy * 1.5, ux * 1.5
            svg.append(f'<line class="bond" x1="{bx1+nx:.2f}" y1="{by1+ny:.2f}" x2="{bx2+nx:.2f}" y2="{by2+ny:.2f}"/>')
            svg.append(f'<line class="bond" x1="{bx1-nx:.2f}" y1="{by1-ny:.2f}" x2="{bx2-nx:.2f}" y2="{by2-ny:.2f}"/>')
        elif bond['order'] == 3:
            nx, ny = -uy * 2.0, ux * 2.0
            svg.append(f'<line class="bond" x1="{bx1:.2f}" y1="{by1:.2f}" x2="{bx2:.2f}" y2="{by2:.2f}"/>')
            svg.append(f'<line class="bond" x1="{bx1+nx:.2f}" y1="{by1+ny:.2f}" x2="{bx2+nx:.2f}" y2="{by2+ny:.2f}"/>')
            svg.append(f'<line class="bond" x1="{bx1-nx:.2f}" y1="{by1-ny:.2f}" x2="{bx2-nx:.2f}" y2="{by2-ny:.2f}"/>')
        else:
            svg.append(f'<line class="bond" x1="{bx1:.2f}" y1="{by1:.2f}" x2="{bx2:.2f}" y2="{by2:.2f}"/>')

    # 2) White background rects behind atom labels (mask bond lines)
    for atom in atoms.values():
        if atom['label']:
            w = len(atom['label']) * 7 + 4
            h = 14
            svg.append(
                f'<rect x="{atom["x"] - w/2:.1f}" y="{atom["y"] - h/2:.1f}" '
                f'width="{w}" height="{h}" fill="white"/>'
            )

    # 3) Atom labels
    for atom in atoms.values():
        if atom['label']:
            symbol = ELEMENT_SYMBOLS.get(atom['element'], 'C')
            color = ELEMENT_COLORS.get(symbol, '#333')
            svg.append(
                f'<text class="atom" x="{atom["x"]:.1f}" y="{atom["y"]:.1f}" '
                f'text-anchor="middle" dominant-baseline="central" fill="{color}">'
                f'{atom["label"]}</text>'
            )

    # 4) Structure name labels
    for label in text_labels:
        svg.append(
            f'<text class="name" x="{label["x"]:.1f}" y="{label["y"]:.1f}" '
            f'text-anchor="start" dominant-baseline="hanging">'
            f'{label["text"]}</text>'
        )

    svg.append('</svg>')
    return '\n'.join(svg), structure_count


from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QTreeView,
    QVBoxLayout, QHBoxLayout, QWidget, QToolBar, QFileDialog, QMessageBox,
    QTabWidget, QTabBar, QLabel, QFrame, QMenu, QComboBox, QSizePolicy
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PyQt6.QtCore import Qt, QModelIndex, QTimer, QUrl, pyqtSignal, QRect, QFileSystemWatcher
from PyQt6.QtGui import (
    QAction, QFileSystemModel, QShortcut, QKeySequence, QCloseEvent,
    QDesktopServices, QPainter, QColor, QFont, QBrush, QPixmap, QIcon
)


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
            color: #5c6bc0;
        }
        QTabBar::tab:selected {
            background: #ffffff;
            border-bottom: 1px solid #ffffff;
            border-top: 3px solid #1976d2;
            font-weight: bold;
            color: #0d47a1;
        }
        QTabBar::tab:hover:!selected {
            background: #bbdefb;
        }
    """,
    'path_label': """
        QLabel {
            color: #90a4ae;
            font-family: 'Meiryo UI', 'Meiryo', sans-serif;
            font-size: 11px;
            padding: 0 8px;
        }
    """
}


class FileTypeIconModel(QFileSystemModel):
    """Custom QFileSystemModel with file type badge icons"""

    BADGE_CONFIG = {
        FileType.MARKDOWN: ('#4CAF50', 'MD'),    # Green
        FileType.XML: ('#FF9800', 'XML'),         # Orange
        FileType.PYTHON: ('#3776AB', 'PY'),       # Python blue
        FileType.CSV: ('#9C27B0', 'CSV'),         # Purple
        FileType.CDXML: ('#E91E63', 'CDX'),       # Pink (chemistry)
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._icon_cache = {}

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DecorationRole and index.column() == 0:
            file_path = self.filePath(index)
            if os.path.isfile(file_path):
                file_type = detect_file_type(file_path)
                if file_type in self.BADGE_CONFIG:
                    return self._get_badge_icon(file_type)
        return super().data(index, role)

    def _get_badge_icon(self, file_type: FileType) -> QIcon:
        """Get or create cached badge icon for file type"""
        if file_type in self._icon_cache:
            return self._icon_cache[file_type]

        bg_color, text = self.BADGE_CONFIG[file_type]

        # Create icon pixmap
        size = 16
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw rounded rectangle background
        painter.setBrush(QBrush(QColor(bg_color)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, size, size, 3, 3)

        # Draw text
        painter.setPen(QColor('#FFFFFF'))
        font = QFont()
        font.setPixelSize(8)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRect(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, text)

        painter.end()

        icon = QIcon(pixmap)
        self._icon_cache[file_type] = icon
        return icon


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
        ("All supported", ["*.md", "*.markdown", "*.xml", "*.xsl", "*.xslt", "*.xsd", "*.svg", "*.py", "*.pyw", "*.csv", "*.cdxml"]),
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

        # Tree view setup with custom icon model
        self.tree_view = QTreeView()
        self.file_model = FileTypeIconModel()
        self._apply_filter(0)  # Apply default filter (Markdown only)
        self.tree_view.setModel(self.file_model)

        # Hide unnecessary columns
        self.tree_view.setColumnHidden(1, True)
        self.tree_view.setColumnHidden(2, True)
        self.tree_view.setColumnHidden(3, True)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

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

        # Get version info
        version, is_frozen = get_version_info()
        mode_label = "" if is_frozen else " [Python]"
        self.app_title = f"Markdown Viewer v{version}{mode_label}"

        self.setWindowTitle(self.app_title)
        self.setGeometry(100, 100, 1400, 900)

        self.css_content = ""
        self.highlight_css = ""
        self.marked_js_path = ""
        self.mermaid_js_path = ""
        self.highlight_js_path = ""
        self.html_template = ""
        self.tab_widget = None
        self.session_manager = SessionManager()
        self._pending_load_finished_handler = None  # Track current loadFinished handler

        # File watcher for auto-reload
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.fileChanged.connect(self._on_file_changed)
        self._pending_reload_paths = set()
        self._reload_timer = QTimer()
        self._reload_timer.setSingleShot(True)
        self._reload_timer.setInterval(300)
        self._reload_timer.timeout.connect(self._process_pending_reloads)

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

        # Load highlight.js CSS
        highlight_css_path = get_resource_path("assets/css/highlight-github.css")
        if highlight_css_path.exists():
            self.highlight_css = highlight_css_path.read_text(encoding="utf-8")

        # Get JavaScript paths
        js_dir = get_resource_path("assets/js")
        self.marked_js_path = str(js_dir / "marked.min.js").replace('\\', '/')
        self.mermaid_js_path = str(js_dir / "mermaid.min.js").replace('\\', '/')
        self.highlight_js_path = str(js_dir / "highlight.min.js").replace('\\', '/')

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

        # Spacer to push path label to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        # Path label for current file
        self.path_label = QLabel("")
        self.path_label.setStyleSheet(QT_STYLES['path_label'])
        self.path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        toolbar.addWidget(self.path_label)


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

        # Zoom in (Ctrl+= or Ctrl+Shift+=)
        zoom_in_shortcut = QShortcut(QKeySequence("Ctrl+="), self)
        zoom_in_shortcut.activated.connect(self._zoom_in)
        zoom_in_shortcut2 = QShortcut(QKeySequence("Ctrl+Shift+="), self)
        zoom_in_shortcut2.activated.connect(self._zoom_in)

        # Zoom out (Ctrl+-)
        zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        zoom_out_shortcut.activated.connect(self._zoom_out)

        # Zoom reset (Ctrl+0)
        zoom_reset_shortcut = QShortcut(QKeySequence("Ctrl+0"), self)
        zoom_reset_shortcut.activated.connect(self._zoom_reset)

    def _zoom_in(self):
        """Increase zoom level of current tab's web view"""
        tab = self._get_current_tab()
        if tab and tab.web_view:
            current_zoom = tab.web_view.zoomFactor()
            tab.web_view.setZoomFactor(min(current_zoom + 0.1, 3.0))

    def _zoom_out(self):
        """Decrease zoom level of current tab's web view"""
        tab = self._get_current_tab()
        if tab and tab.web_view:
            current_zoom = tab.web_view.zoomFactor()
            tab.web_view.setZoomFactor(max(current_zoom - 0.1, 0.3))

    def _zoom_reset(self):
        """Reset zoom level to default"""
        tab = self._get_current_tab()
        if tab and tab.web_view:
            tab.web_view.setZoomFactor(1.0)

    def _add_welcome_tab(self):
        """Add initial welcome tab"""
        tab = self._add_new_tab()
        self._render_markdown(tab, "# Welcome to Markdown Viewer\n\nOpen a folder to get started.\n\n## Keyboard Shortcuts\n\n| Shortcut | Action |\n|----------|--------|\n| Ctrl+T | New Tab |\n| Ctrl+W | Close Tab |\n| Ctrl+O | Open Folder |\n| Ctrl+Tab | Next Tab |\n| Ctrl+Shift+Tab | Previous Tab |\n| Ctrl+Shift+O | Toggle Outline |\n| Ctrl+Shift+I | Toggle Stats |\n| Ctrl++ | Zoom In |\n| Ctrl+- | Zoom Out |\n| Ctrl+0 | Zoom Reset |\n| F5 | Refresh |")

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
        tab.tree_view.customContextMenuRequested.connect(
            lambda pos, t=tab: self._show_tree_context_menu(t, pos)
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
        self._update_file_watch()

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
                self.setWindowTitle(f"{self.app_title} - {os.path.basename(tab.current_file)}")
                dir_part = os.path.dirname(tab.current_file) + os.sep
                file_part = os.path.basename(tab.current_file)
                self.path_label.setText(f"{dir_part}<b>{file_part}</b>")
            elif tab.current_folder:
                self.setWindowTitle(f"{self.app_title} - {tab.current_folder}")
                self.path_label.setText(tab.current_folder)
            else:
                self.setWindowTitle(self.app_title)
                self.path_label.setText("")
        else:
            self.setWindowTitle(self.app_title)
            self.path_label.setText("")

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

        # Check if file should be opened based on type and filter
        file_type = detect_file_type(file_path)
        filter_index = tab.get_filter_index()

        # Allow: supported types, or "All files" filter (index 2)
        if file_type != FileType.UNKNOWN or filter_index == 2:
            # Clear navigation history when selecting from sidebar
            tab.navigation_history.clear()
            tab.current_file = file_path
            self._load_file(tab, file_path)
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
        # Build line info for gutter (detect all significant lines)
        # Each entry must correspond 1:1 with a rendered DOM element.
        # Consecutive text lines are merged into one <p> by marked.js,
        # so we must emit only one 'p' entry per paragraph block.
        import json
        lines = markdown_content.split('\n')
        line_info = []
        in_code_block = False
        in_table = False
        in_paragraph = False

        def _is_hr(s):
            """Check if line is a horizontal rule (3+ of same char: -, *, _)"""
            no_space = s.replace(' ', '')
            return (len(no_space) >= 3
                    and no_space[0] in '-*_'
                    and all(c == no_space[0] for c in no_space))

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Track code blocks
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                in_paragraph = False
                line_info.append({'line': i, 'type': 'code_fence'})
                continue

            if in_code_block:
                # Each line in code block
                line_info.append({'line': i, 'type': 'code_line'})
                continue

            # Empty line resets paragraph/table state
            if not stripped:
                in_paragraph = False
                in_table = False
                continue

            # Horizontal rule (check before list items to handle '* * *')
            if _is_hr(stripped) and not in_table:
                line_info.append({'line': i, 'type': 'hr'})
                in_paragraph = False
                in_table = False
            # Headings
            elif stripped.startswith('#'):
                level = len(stripped) - len(stripped.lstrip('#'))
                if 1 <= level <= 6:
                    line_info.append({'line': i, 'type': f'h{level}'})
                    in_paragraph = False
                    in_table = False
            # Unordered list item
            elif stripped.startswith(('- ', '* ', '+ ')) or stripped in ('- ', '* ', '+ ', '-', '*', '+'):
                line_info.append({'line': i, 'type': 'li'})
                in_paragraph = False
                in_table = False
            # Ordered list item
            elif stripped and stripped[0].isdigit() and '. ' in stripped[:4]:
                line_info.append({'line': i, 'type': 'li'})
                in_paragraph = False
                in_table = False
            # Blockquote line
            elif stripped.startswith('>'):
                line_info.append({'line': i, 'type': 'quote'})
                in_paragraph = False
                in_table = False
            # Table row
            elif stripped.startswith('|') and stripped.endswith('|'):
                # Table separator row - skip (don't create entry)
                sep_test = stripped.replace(' ', '').replace('-', '').replace('|', '').replace(':', '')
                if sep_test == '':
                    in_table = True
                else:
                    line_info.append({'line': i, 'type': 'tr'})
                    in_table = True
                in_paragraph = False
            # Paragraph: only emit one entry per paragraph block
            else:
                if not in_paragraph:
                    line_info.append({'line': i, 'type': 'p'})
                    in_paragraph = True
                in_table = False

        line_info_json = json.dumps(line_info)

        # Escape special characters for JavaScript template literal
        escaped_content = markdown_content.replace('\\', '\\\\')
        escaped_content = escaped_content.replace('`', '\\`')
        escaped_content = escaped_content.replace('$', '\\$')

        # Raw source lines for clipboard copy (JSON-encoded)
        raw_lines_json = json.dumps(markdown_content.split('\n'), ensure_ascii=False)

        # File path for clipboard copy
        file_path = (tab.current_file or '').replace('\\', '\\\\')

        # Back button visibility
        back_button_style = "display: flex;" if tab.navigation_history else "display: none;"

        # Build HTML from template
        html = self.html_template
        html = html.replace('$CSS_CONTENT$', self.css_content)
        html = html.replace('$MARKED_JS_PATH$', self.marked_js_path)
        html = html.replace('$MERMAID_JS_PATH$', self.mermaid_js_path)
        html = html.replace('$MARKDOWN_CONTENT$', escaped_content)
        html = html.replace('$LINE_INFO$', line_info_json)
        html = html.replace('$RAW_LINES$', raw_lines_json)
        html = html.replace('$FILE_PATH$', file_path)
        html = html.replace('$BACK_BUTTON_STYLE$', back_button_style)

        # Set base URL for relative links to work correctly
        if tab.current_file:
            base_url = QUrl.fromLocalFile(os.path.dirname(tab.current_file) + '/')
        elif tab.current_folder:
            base_url = QUrl.fromLocalFile(tab.current_folder + '/')
        else:
            base_url = QUrl()
        tab.web_view.setHtml(html, base_url)

    def _load_file(self, tab: FolderTab, file_path: str):
        """Load and render file based on type"""
        self._update_file_watch()
        file_type = detect_file_type(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if file_type == FileType.MARKDOWN:
                self._render_markdown(tab, content)
            elif file_type == FileType.XML:
                self._render_code(tab, content, 'xml', 'XML Document')
            elif file_type == FileType.PYTHON:
                self._render_code(tab, content, 'python', 'Python Script')
            elif file_type == FileType.CSV:
                self._render_csv(tab, content)
            elif file_type == FileType.CDXML:
                self._render_cdxml(tab, content)
            else:
                # Plain text fallback
                self._render_code(tab, content, 'plaintext', 'Text File')

            tab.update_stats(content)
        except UnicodeDecodeError:
            QMessageBox.warning(
                self, "Cannot Open File",
                f"This file cannot be displayed as text:\n{os.path.basename(file_path)}\n\n"
                "The file may be a binary file."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file:\n{e}")

    def _escape_for_js(self, content: str) -> str:
        """Escape content for JavaScript template literal"""
        escaped = content.replace('\\', '\\\\')
        escaped = escaped.replace('`', '\\`')
        escaped = escaped.replace('$', '\\$')
        return escaped

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))

    def _set_html_with_base(self, tab: FolderTab, html: str):
        """Set HTML with proper base URL"""
        if tab.current_file:
            base_url = QUrl.fromLocalFile(os.path.dirname(tab.current_file) + '/')
        elif tab.current_folder:
            base_url = QUrl.fromLocalFile(tab.current_folder + '/')
        else:
            base_url = QUrl()
        tab.web_view.setHtml(html, base_url)

    def _render_code(self, tab: FolderTab, content: str, language: str, title: str):
        """Render code with syntax highlighting"""
        escaped = self._escape_for_js(content)
        html = f'''<!DOCTYPE html>
<html><head>
    <meta charset="UTF-8">
    <style>{self.css_content}</style>
    <style>{self.highlight_css}</style>
    <script src="file:///{self.highlight_js_path}"></script>
    <style>
        body {{ margin: 0; padding: 20px; background: var(--bg-color, #f8faff); }}
        .file-header {{
            background: var(--h2-bg, linear-gradient(135deg, #1976d2 0%, #1565c0 100%));
            color: white; padding: 12px 20px;
            border-radius: 6px 6px 0 0; font-weight: 600;
            display: flex; align-items: center; gap: 8px;
        }}
        .file-badge {{
            background: rgba(255,255,255,0.2); padding: 2px 8px;
            border-radius: 4px; font-size: 11px; text-transform: uppercase;
        }}
        pre {{
            margin: 0; border-top-left-radius: 0; border-top-right-radius: 0;
            border-bottom-left-radius: 6px; border-bottom-right-radius: 6px;
            overflow: auto;
        }}
        .hljs {{
            background: var(--code-bg, #e3f2fd); padding: 16px;
            font-family: 'Consolas', 'Monaco', monospace; font-size: 13px;
            line-height: 1.5;
        }}
    </style>
</head><body>
    <div class="file-header">
        <span class="file-badge">{language.upper()}</span>
        <span>{title}</span>
    </div>
    <pre><code class="language-{language}" id="code-content"></code></pre>
    <script>
        document.getElementById('code-content').textContent = `{escaped}`;
        hljs.highlightAll();
    </script>
</body></html>'''
        self._set_html_with_base(tab, html)

    def _render_csv(self, tab: FolderTab, content: str):
        """Render CSV as HTML table"""
        rows = list(csv.reader(StringIO(content)))

        if not rows:
            html = f'''<!DOCTYPE html>
<html><head>
    <meta charset="UTF-8">
    <style>{self.css_content}</style>
    <style>
        body {{ margin: 0; padding: 40px; background: var(--bg-color, #f8faff); text-align: center; }}
    </style>
</head><body>
    <h3 style="color: var(--blockquote-color, #546e7a);">Empty CSV File</h3>
    <p style="color: var(--blockquote-color, #546e7a);">This CSV file contains no data.</p>
</body></html>'''
        else:
            # Build header row
            header = ''.join(f'<th>{self._escape_html(c)}</th>' for c in rows[0])
            # Build data rows
            body = ''.join(
                '<tr>' + ''.join(f'<td>{self._escape_html(c)}</td>' for c in row) + '</tr>'
                for row in rows[1:]
            )
            row_count = len(rows)
            col_count = len(rows[0]) if rows else 0

            html = f'''<!DOCTYPE html>
<html><head>
    <meta charset="UTF-8">
    <style>{self.css_content}</style>
    <style>
        body {{ margin: 0; padding: 20px; background: var(--bg-color, #f8faff); }}
        .csv-header {{
            background: var(--h2-bg, linear-gradient(135deg, #1976d2 0%, #1565c0 100%));
            color: white; padding: 12px 20px;
            border-radius: 6px; font-weight: 600; margin-bottom: 16px;
            display: flex; align-items: center; gap: 8px;
        }}
        .file-badge {{
            background: rgba(255,255,255,0.2); padding: 2px 8px;
            border-radius: 4px; font-size: 11px;
        }}
        .csv-stats {{
            font-size: 12px; font-weight: normal; opacity: 0.9; margin-left: auto;
        }}
        table {{
            width: 100%; border-collapse: collapse; font-size: 13px;
            background: white; border-radius: 6px; overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        th {{
            background: var(--table-header-bg, #e3f2fd);
            color: var(--heading-color, #0d47a1);
            padding: 10px 12px; text-align: left; font-weight: 600;
            border-bottom: 2px solid var(--table-border, #90caf9);
        }}
        td {{
            padding: 8px 12px;
            border-bottom: 1px solid var(--table-border, #e0e0e0);
            max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
        }}
        tr:hover td {{ background: var(--table-row-hover, #f5f5f5); }}
    </style>
</head><body>
    <div class="csv-header">
        <span class="file-badge">CSV</span>
        <span>CSV Data</span>
        <span class="csv-stats">{row_count} rows, {col_count} columns</span>
    </div>
    <table>
        <thead><tr>{header}</tr></thead>
        <tbody>{body}</tbody>
    </table>
</body></html>'''

        self._set_html_with_base(tab, html)

    def _render_cdxml(self, tab: FolderTab, content: str):
        """Render CDXML chemical structure as SVG"""
        svg_content, structure_count = cdxml_to_svg(content)
        struct_text = f"{structure_count} structure{'s' if structure_count != 1 else ''}"

        html = f'''<!DOCTYPE html>
<html><head>
    <meta charset="UTF-8">
    <style>{self.css_content}</style>
    <style>
        body {{ margin: 0; padding: 20px; background: var(--bg-color, #f8faff); }}
        .cdxml-header {{
            background: linear-gradient(135deg, #E91E63 0%, #C2185B 100%);
            color: white; padding: 12px 20px;
            border-radius: 6px; font-weight: 600; margin-bottom: 16px;
            display: flex; align-items: center; gap: 8px;
        }}
        .file-badge {{
            background: rgba(255,255,255,0.2); padding: 2px 8px;
            border-radius: 4px; font-size: 11px;
        }}
        .cdxml-stats {{
            font-size: 12px; font-weight: normal; opacity: 0.9; margin-left: auto;
        }}
        .structure-container {{
            background: white;
            border-radius: 6px;
            padding: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            text-align: center;
            overflow: auto;
        }}
        .structure-container svg {{
            max-width: 100%;
            height: auto;
        }}
    </style>
</head><body>
    <div class="cdxml-header">
        <span class="file-badge">CDXML</span>
        <span>Chemical Structure</span>
        <span class="cdxml-stats">{struct_text}</span>
    </div>
    <div class="structure-container">
        {svg_content}
    </div>
</body></html>'''
        self._set_html_with_base(tab, html)

    def _refresh_current_tab(self):
        """Refresh current file in current tab, preserving scroll position"""
        tab = self._get_current_tab()
        if tab and tab.current_file and os.path.exists(tab.current_file):
            tab.navigation_history.clear()
            self._reload_with_scroll(tab)

    def _reload_with_scroll(self, tab: FolderTab):
        """Reload tab's current file preserving scroll position"""
        tab.web_view.page().runJavaScript(
            "window.pageYOffset",
            lambda scroll_y, t=tab: self._do_reload(t, scroll_y)
        )

    def _do_reload(self, tab: FolderTab, scroll_y):
        """Perform reload and restore scroll position"""
        # Disconnect previous handler to prevent stacking
        if self._pending_load_finished_handler:
            try:
                tab.web_view.loadFinished.disconnect(self._pending_load_finished_handler)
            except TypeError:
                pass
            self._pending_load_finished_handler = None

        self._load_file(tab, tab.current_file)

        # Restore scroll position after page finishes loading
        if scroll_y is not None and scroll_y > 0:
            def on_load_finished(ok):
                self._pending_load_finished_handler = None
                try:
                    tab.web_view.loadFinished.disconnect(on_load_finished)
                except TypeError:
                    pass
                if ok:
                    # Delay for DOM rendering to complete before scrolling
                    QTimer.singleShot(100, lambda: tab.web_view.page().runJavaScript(
                        f"window.scrollTo(0, {int(scroll_y)})"
                    ))
            self._pending_load_finished_handler = on_load_finished
            tab.web_view.loadFinished.connect(on_load_finished)

    # --- File Watcher (auto-reload) ---

    def _update_file_watch(self):
        """Sync file watcher with currently open files across all tabs"""
        watched = set(self.file_watcher.files())
        needed = set()
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if tab.current_file:
                needed.add(tab.current_file)
        to_remove = watched - needed
        if to_remove:
            self.file_watcher.removePaths(list(to_remove))
        to_add = needed - watched
        if to_add:
            self.file_watcher.addPaths(list(to_add))

    def _on_file_changed(self, path: str):
        """Handle file change notification (debounced)"""
        self._pending_reload_paths.add(path)
        self._reload_timer.start()
        # Re-add path to watcher (some OS remove it after change)
        if os.path.exists(path) and path not in self.file_watcher.files():
            self.file_watcher.addPath(path)

    def _process_pending_reloads(self):
        """Process pending file reloads after debounce"""
        paths = self._pending_reload_paths.copy()
        self._pending_reload_paths.clear()
        for path in paths:
            for i in range(self.tab_widget.count()):
                tab = self.tab_widget.widget(i)
                if tab.current_file == path and os.path.exists(path):
                    self._reload_with_scroll(tab)

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

            # Check filter setting for unsupported files
            file_type = detect_file_type(target_path)
            filter_allows_all = tab.get_filter_index() == 2  # "All files"
            if file_type == FileType.UNKNOWN and not filter_allows_all:
                QMessageBox.warning(
                    self, "Warning",
                    f"Cannot open unsupported file:\n{os.path.basename(target_path)}\n\n"
                    "Switch to 'All files' filter to open this file."
                )
                return

            if open_in_new_tab:
                # Open in new tab
                folder = os.path.dirname(target_path)
                new_tab = self._add_new_tab(folder)
                new_tab.current_file = target_path
                self._load_file(new_tab, target_path)
                self._update_window_title()
            else:
                # Open in same tab - add current file to history for back navigation
                if tab.current_file:
                    tab.navigation_history.append(tab.current_file)
                tab.current_file = target_path
                self._load_file(tab, target_path)
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
            self._load_file(tab, previous_file)
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

    def _show_tree_context_menu(self, tab: FolderTab, pos):
        """Show context menu for right-click on file tree"""
        index = tab.tree_view.indexAt(pos)
        if not index.isValid():
            return

        file_path = tab.file_model.filePath(index)
        if not file_path:
            return

        menu = QMenu(self)
        copy_path_action = menu.addAction("Copy Path")

        action = menu.exec(tab.tree_view.mapToGlobal(pos))
        if action == copy_path_action:
            QApplication.clipboard().setText(file_path)

    def open_file(self, file_path: str):
        """Open a specific file"""
        file_path = os.path.abspath(file_path)

        if not os.path.exists(file_path):
            QMessageBox.critical(self, "Error", f"File not found:\n{file_path}")
            return

        # Create new tab with the folder
        folder = os.path.dirname(file_path)
        tab = self._add_new_tab(folder)

        # For unsupported files, switch filter to "All files"
        file_type = detect_file_type(file_path)
        if file_type == FileType.UNKNOWN:
            tab.set_filter_index(2)  # "All files"
        elif file_type != FileType.MARKDOWN:
            tab.set_filter_index(1)  # "All supported"

        # Select the file in tree view (with delay for QFileSystemModel)
        def select_file():
            file_index = tab.file_model.index(file_path)
            if file_index.isValid():
                tab.tree_view.setCurrentIndex(file_index)
                tab.tree_view.scrollTo(file_index)
        QTimer.singleShot(100, select_file)

        # Load and display the file
        tab.current_file = file_path
        self._load_file(tab, file_path)
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
                    self._load_file(tab, file_path)

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
