# コンポーネント仕様

## モジュールレベル定数

### QT_STYLES

Qt ウィジェット用のスタイルシート定数。SSOT（Single Source of Truth）原則に従い、スタイルを一元管理。

| キー | 用途 |
|------|------|
| `filter_combo` | ファイルフィルタードロップダウン |
| `stats_panel` | 統計情報パネル |
| `stats_header` | 統計ヘッダーラベル |
| `stats_name` | 統計項目名ラベル |
| `stats_value` | 統計値ラベル |
| `tab_widget` | タブウィジェット |

## クラス一覧

| クラス | 継承元 | 役割 |
|--------|--------|------|
| `FileType` | Enum | ファイルタイプ列挙型 |
| `FileTypeIconModel` | QFileSystemModel | ファイルタイプアイコン表示 |
| `MarkdownWebPage` | QWebEnginePage | リンククリック処理 |
| `SessionManager` | - | セッション状態の永続化 |
| `FolderTab` | QWidget | タブ単位のUI・ロジック |
| `MarkdownViewer` | QMainWindow | アプリケーション全体の制御 |

---

## FileType

### 概要

サポートするファイルタイプを定義する列挙型。

### 値

| 値 | 説明 |
|-----|------|
| MARKDOWN | Markdownファイル |
| XML | XMLファイル |
| PYTHON | Pythonファイル |
| CSV | CSVファイル |
| UNKNOWN | 未対応ファイル |

### 拡張子マッピング

```python
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
}
```

---

## FileTypeIconModel

### 概要

ファイルタイプに応じたバッジアイコンを表示するカスタムファイルシステムモデル。

### 定数

```python
BADGE_CONFIG = {
    FileType.MARKDOWN: ('#4CAF50', 'MD'),
    FileType.XML: ('#FF9800', 'XML'),
    FileType.PYTHON: ('#3776AB', 'PY'),
    FileType.CSV: ('#9C27B0', 'CSV'),
}
```

### メソッド

#### `data(self, index, role)`

`DecorationRole` の場合、ファイルタイプに応じたバッジアイコンを返す。

#### `_get_badge_icon(self, file_type) -> QIcon`

ファイルタイプ用のバッジアイコンを生成（キャッシュ付き）。

| 設定 | 値 |
|------|-----|
| アイコンサイズ | 16x16px |
| 角丸 | 3px |
| フォントサイズ | 8px |

---

## MarkdownWebPage

### 概要

リンククリックをインターセプトし、カスタム処理を行うためのQWebEnginePage拡張クラス。

### シグナル

| シグナル | 引数 | 説明 |
|---------|------|------|
| `link_clicked` | url: str, new_tab: bool | リンクがクリックされた時に発行 |

### メソッド

#### `acceptNavigationRequest(self, url, nav_type, is_main_frame) -> bool`

ナビゲーション要求をインターセプトし、リンククリックを処理。

| パラメータ | 型 | 説明 |
|-----------|---|------|
| url | QUrl | ナビゲーション先URL |
| nav_type | NavigationType | ナビゲーションの種類 |
| is_main_frame | bool | メインフレームかどうか |

**処理フロー:**
1. NavigationType.NavigationTypeLinkClicked を検出
2. Shift キー押下状態を確認
3. `link_clicked` シグナルを発行（URL と new_tab フラグ）
4. `False` を返してデフォルト動作を抑制

---

## SessionManager

### 概要

アプリケーションの状態（ウィンドウ位置、開いているタブ等）をJSONファイルに保存・復元する。

### 定数

```python
SESSION_DIR = Path.home() / ".markdown-viewer"
SESSION_FILE = SESSION_DIR / "session.json"
```

### メソッド

#### `__init__(self)`

セッション保存用ディレクトリを作成。

#### `save_session(self, viewer: MarkdownViewer) -> None`

| パラメータ | 型 | 説明 |
|-----------|---|------|
| viewer | MarkdownViewer | 保存対象のビューアインスタンス |

**保存内容:**
- ウィンドウ位置 (x, y)
- ウィンドウサイズ (width, height)
- タブ情報（フォルダパス、選択ファイル、アウトライン状態）
- アクティブタブインデックス

#### `load_session(self) -> dict | None`

| 戻り値 | 説明 |
|--------|------|
| dict | セッションデータ |
| None | ファイルが存在しないまたは読み込み失敗 |

---

## FolderTab

### 概要

1つのタブを構成するウィジェット。ファイルツリー、統計パネル、Webビューを含む。

### 属性

| 属性名 | 型 | 説明 |
|--------|---|------|
| folder_path | str | 表示中のフォルダパス |
| current_folder | str | 現在のフォルダパス（リンク解決用） |
| current_file | str | 選択中のファイルパス |
| file_tree | QTreeWidget | ファイル一覧ツリー |
| file_model | QFileSystemModel | ファイルシステムモデル |
| web_view | QWebEngineView | Markdownレンダリング領域 |
| stats_labels | dict | 統計情報ラベル群 |
| outline_visible | bool | アウトライン表示状態 |
| css | str | スタイルシート文字列 |
| navigation_history | list | ナビゲーション履歴スタック |
| filter_combo | QComboBox | ファイルフィルタードロップダウン |

### メソッド

#### `__init__(self, css: str, parent=None)`

| パラメータ | 型 | 説明 |
|-----------|---|------|
| css | str | HTMLに埋め込むCSS |
| parent | QWidget | 親ウィジェット |

#### `_setup_ui(self) -> None`

UIコンポーネントを初期化・配置。

**レイアウト構成:**
```
QSplitter (horizontal)
├── left_panel (QWidget, 幅250px)
│   ├── file_tree (QTreeWidget)
│   └── stats_panel (QWidget)
│       └── Lines / Chars / Words / Read / Size
└── web_view (QWebEngineView)
```

#### `set_folder(self, folder_path: str) -> None`

| パラメータ | 型 | 説明 |
|-----------|---|------|
| folder_path | str | 表示するフォルダのパス |

**処理内容:**
1. フォルダパスを保存
2. ファイルツリーをクリア
3. `.md` / `.markdown` ファイルを列挙
4. ツリーアイテムとして追加

#### `update_stats(self, content: str) -> None`

| パラメータ | 型 | 説明 |
|-----------|---|------|
| content | str | Markdownファイルの内容 |

**統計項目:**
| 項目 | 計算方法 |
|------|---------|
| Lines | `content.count('\n') + 1` |
| Chars | `len(content)` |
| Words | `len(content.split())` |
| Read | `words / 200` 分 |
| Size | ファイルサイズ (KB) |

#### `_render_markdown(self, content: str) -> None`

| パラメータ | 型 | 説明 |
|-----------|---|------|
| content | str | Markdownテキスト |

**処理フロー:**
1. HTMLテンプレート生成
2. CDNからmarked.js/mermaid.js読み込み
3. Markdownをパース
4. Mermaid図表を初期化
5. 目次（アウトライン）を生成
6. WebViewにHTMLをセット

**生成されるHTML構造:**

テンプレートファイル `src/templates/markdown.html` を使用。
詳細は [architecture.md](architecture.md) の「HTMLテンプレート」セクションを参照。

#### `_on_file_clicked(self, item: QTreeWidgetItem, column: int) -> None`

ファイルツリーのアイテムがクリックされた時の処理。

| パラメータ | 型 | 説明 |
|-----------|---|------|
| item | QTreeWidgetItem | クリックされたアイテム |
| column | int | クリックされた列 |

#### `toggle_outline(self) -> None`

アウトライン（目次）の表示/非表示を切り替え。JavaScript経由でDOM操作。

#### `get_tab_name(self) -> str`

タブに表示する名前を返す。フォルダ名またはデフォルト値。

#### `get_filter_index(self) -> int`

現在選択中のフィルターインデックスを返す。セッション保存用。

| 戻り値 | 説明 |
|--------|------|
| 0 | Markdown only |
| 1 | All supported |
| 2 | All files |

#### `set_filter_index(self, index: int) -> None`

フィルターインデックスを設定。セッション復元用。

| パラメータ | 型 | 説明 |
|-----------|---|------|
| index | int | フィルターインデックス |

---

## MarkdownViewer

### 概要

アプリケーションのメインウィンドウ。タブ管理、ツールバー、キーボードショートカットを提供。

### 属性

| 属性名 | 型 | 説明 |
|--------|---|------|
| tabs | QTabWidget | タブコンテナ |
| css | str | 読み込んだスタイルシート |
| session_manager | SessionManager | セッション管理インスタンス |

### メソッド

#### `__init__(self, file_path: str = None)`

| パラメータ | 型 | 説明 |
|-----------|---|------|
| file_path | str | 起動時に開くファイル（オプション） |

#### `_load_resources(self) -> None`

リソースファイルを読み込む。

**読み込むリソース:**
- `src/style.css` - CSSスタイルシート
- `src/assets/css/highlight-github.css` - シンタックスハイライトCSS
- `src/assets/js/marked.min.js` - Markdownパーサー
- `src/assets/js/mermaid.min.js` - 図表ライブラリ
- `src/assets/js/highlight.min.js` - シンタックスハイライト
- `src/templates/markdown.html` - HTMLテンプレート

#### `_update_window_title(self) -> None`

ウィンドウタイトルを現在のタブ状態に基づいて更新（SSOT原則）。

**タイトル形式:**
- ファイル選択時: `Markdown Viewer - {ファイル名}`
- フォルダ選択時: `Markdown Viewer - {フォルダパス}`
- 未選択時: `Markdown Viewer`

#### `_setup_ui(self) -> None`

- QTabWidgetを作成
- タブの閉じるボタンを有効化
- タブ移動を有効化
- シグナル接続

#### `_setup_toolbar(self) -> None`

ツールバーを構成。

| ボタン | アクション |
|--------|-----------|
| Open Folder | `_open_folder()` |
| New Tab | `_add_new_tab()` |
| Reload | `_reload_current()` |
| Toggle Outline | `_toggle_outline()` |

#### `_setup_shortcuts(self) -> None`

キーボードショートカットを設定。

| キー | メソッド |
|------|---------|
| Ctrl+T | `_add_new_tab()` |
| Ctrl+W | `_close_current_tab()` |
| Ctrl+O | `_open_folder()` |
| Ctrl+Tab | `_next_tab()` |
| Ctrl+Shift+Tab | `_prev_tab()` |
| Ctrl+Shift+O | `_toggle_outline()` |
| F5 | `_reload_current()` |

#### `_add_new_tab(self, folder_path: str = None) -> FolderTab`

| パラメータ | 型 | 説明 |
|-----------|---|------|
| folder_path | str | 初期表示フォルダ（オプション） |

| 戻り値 | 説明 |
|--------|------|
| FolderTab | 作成されたタブ |

#### `_close_current_tab(self) -> None`

現在のタブを閉じる。最後の1つは閉じない。

#### `_open_folder(self) -> None`

フォルダ選択ダイアログを表示し、選択されたフォルダをタブに設定。

#### `_reload_current(self) -> None`

現在表示中のファイルを再読み込み。

#### `_toggle_outline(self) -> None`

現在のタブのアウトライン表示を切り替え。

#### `_next_tab(self) / _prev_tab(self) -> None`

タブを循環的に切り替え。

#### `open_file(self, file_path: str) -> None`

| パラメータ | 型 | 説明 |
|-----------|---|------|
| file_path | str | 開くファイルのパス |

コマンドライン引数からファイルを直接開く。

#### `_restore_session(self) -> None`

セッションファイルからウィンドウ状態・タブを復元。

#### `closeEvent(self, event: QCloseEvent) -> None`

ウィンドウ閉じる前にセッションを保存。

#### `_handle_link_click(self, url: str, new_tab: bool) -> None`

リンククリックを処理。

| パラメータ | 型 | 説明 |
|-----------|---|------|
| url | str | クリックされたURL |
| new_tab | bool | 新しいタブで開くか |

**処理フロー:**
1. URLスキームを判定（app://, http://, #, ファイルパス）
2. 種別に応じた処理を実行
3. 履歴スタックに現在ファイルを追加

#### `_navigate_back(self) -> None`

現在のタブで履歴を1つ戻る。

**処理フロー:**
1. 現在タブの navigation_history から pop
2. 前のファイルを開く
3. 履歴が空の場合は何もしない

#### `_show_link_context_menu(self, pos: QPoint) -> None`

リンク上での右クリックメニューを表示。

| パラメータ | 型 | 説明 |
|-----------|---|------|
| pos | QPoint | クリック位置 |

**処理フロー:**
1. JavaScript で elementFromPoint() を実行
2. <a>タグの href を取得
3. QMenu を生成（Open / Open in New Tab）
4. 選択されたアクションを実行

#### `_add_welcome_tab(self) -> None`

ウェルカムタブを追加。キーボードショートカット一覧を表示。

---

## エントリーポイント

```python
def main():
    app = QApplication(sys.argv)

    # コマンドライン引数からファイルパス取得
    file_path = sys.argv[1] if len(sys.argv) > 1 else None

    viewer = MarkdownViewer(file_path)
    viewer.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```
