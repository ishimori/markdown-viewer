# コンポーネント仕様

## モジュールレベル定数

### QT_STYLES

Qt ウィジェット用のスタイルシート定数。SSOT（Single Source of Truth）原則に従い、スタイルを一元管理。

| キー | 用途 |
|------|------|
| `filter_combo` | ファイルフィルタードロップダウン |
| `parent_btn` | 親ディレクトリ移動ボタン |
| `stats_panel` | 統計情報パネル |
| `stats_header` | 統計ヘッダーラベル |
| `stats_name` | 統計項目名ラベル |
| `stats_value` | 統計値ラベル |
| `tab_widget` | タブウィジェット |
| `history_container` | 履歴バーのコンテナ |
| `history_bar` | 履歴リンクボタン（通常状態） |
| `history_separator` | 履歴リンク間の区切り文字 |
| `history_current` | 履歴リンクボタン（現在のファイル） |

## クラス一覧

| クラス | 継承元 | 役割 |
|--------|--------|------|
| `FileType` | Enum | ファイルタイプ列挙型 |
| `SearchResult` | dataclass | 検索結果エントリ |
| `SearchEngine` | - | 全文検索エンジン |
| `BookmarkEntry` | dataclass | ブックマークエントリ |
| `BookmarkManager` | - | ブックマーク管理 |
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
| CDXML | ChemDraw CDXMLファイル（化学構造） |
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
    '.cdxml': FileType.CDXML,
}
```

---

## SearchResult

### 概要

検索結果の単一エントリを表すデータクラス。

### フィールド

| フィールド | 型 | 説明 |
|----------|-----|------|
| `file_path` | str | ファイルの絶対パス |
| `file_name` | str | ファイル名（basename） |
| `line_number` | int | マッチした行番号（1-indexed） |
| `line_content` | str | マッチした行の内容 |
| `context_before` | str | 前の行の内容（コンテキスト） |
| `context_after` | str | 次の行の内容（コンテキスト） |
| `match_count` | int | その行内のマッチ数 |

### 使用例

```python
result = SearchResult(
    file_path="C:/path/to/file.md",
    file_name="file.md",
    line_number=42,
    line_content="This is a matching line",
    context_before="Previous line",
    context_after="Next line",
    match_count=2
)
```

---

## SearchEngine

### 概要

フォルダ内の全ファイルを対象に全文検索を実行するエンジンクラス。

### 主要メソッド

#### search()

```python
def search(
    folder_path: str,
    tree_model: QFileSystemModel,
    query: str,
    case_sensitive: bool = False,
    use_regex: bool = False,
    search_filenames: bool = False,
    operator: str = 'AND'
) -> List[SearchResult]
```

フォルダ内の全ファイルを再帰的に検索。

**パラメータ:**
- `folder_path`: 検索対象のルートフォルダ
- `tree_model`: ファイルシステムモデル
- `query`: 検索クエリ
- `case_sensitive`: 大文字小文字を区別するか
- `use_regex`: 正規表現を使用するか
- `search_filenames`: ファイル名のみを検索するか
- `operator`: マルチキーワード検索時の演算子（"AND" or "OR"）

**戻り値:**
- `List[SearchResult]`: 検索結果のリスト

#### _collect_files_recursively()

```python
def _collect_files_recursively(
    tree_model: QFileSystemModel,
    folder_path: str
) -> List[str]
```

TreeModel から再帰的にすべてのファイルパスを収集。

#### _search_file()

```python
def _search_file(
    file_path: str,
    query: str,
    case_sensitive: bool
) -> List[SearchResult]
```

単純な文字列検索（部分一致）。

#### _search_file_regex()

```python
def _search_file_regex(
    file_path: str,
    pattern: str,
    case_sensitive: bool
) -> List[SearchResult]
```

正規表現パターンマッチング検索。

#### _search_multi_keyword()

```python
def _search_multi_keyword(
    file_path: str,
    keywords: List[str],
    operator: str,
    case_sensitive: bool
) -> List[SearchResult]
```

複数キーワードでの検索（AND/OR演算）。

#### search_single_file()

```python
def search_single_file(
    file_path: str,
    query: str,
    case_sensitive: bool = False,
    use_regex: bool = False,
    operator: str = 'AND'
) -> List[SearchResult]
```

単一ファイル内を検索。スコープが「このファイル」の場合に使用。

**パラメータ:**
- `file_path`: 検索対象のファイルパス
- `query`: 検索クエリ
- `case_sensitive`: 大文字小文字を区別するか
- `use_regex`: 正規表現を使用するか
- `operator`: マルチキーワード検索時の演算子（"AND" or "OR"）

**戻り値:**
- `List[SearchResult]`: 検索結果のリスト

#### _match_filename()

```python
def _match_filename(
    filename: str,
    query: str,
    case_sensitive: bool
) -> bool
```

ファイル名が検索クエリにマッチするかチェック。

### エラー処理

- `UnicodeDecodeError`: ファイルをスキップ
- `PermissionError`: ファイルをスキップ
- `FileNotFoundError`: ファイルをスキップ
- `OSError`: ファイルをスキップ
- 正規表現エラー: 空の結果を返す

---

## BookmarkEntry

### 概要

ブックマークの単一エントリを表すデータクラス。

### フィールド

| フィールド | 型 | 説明 |
|----------|-----|------|
| `file_path` | str | ファイルの絶対パス |
| `file_name` | str | ファイル名（basename） |
| `folder_path` | str | 親ディレクトリパス |
| `added_timestamp` | float | 追加日時（UNIX時刻） |
| `last_accessed` | float | 最終アクセス日時（UNIX時刻） |
| `note` | str | メモ（デフォルト: ""） |

### 使用例

```python
bookmark = BookmarkEntry(
    file_path="C:/path/to/file.md",
    file_name="file.md",
    folder_path="C:/path/to",
    added_timestamp=time.time(),
    last_accessed=time.time(),
    note="Important document"
)
```

---

## BookmarkManager

### 概要

ブックマークの管理を行うクラス。JSON形式で永続化。

### 初期化

```python
def __init__(self)
```

- ブックマークファイルパス: `~/.markdown-viewer/bookmarks.json`
- 初期化時に既存ブックマークを読み込み

### 主要メソッド

#### add_bookmark()

```python
def add_bookmark(file_path: str, note: str = "") -> bool
```

ブックマークを追加。既に存在する場合は `False` を返す。

#### remove_bookmark()

```python
def remove_bookmark(file_path: str) -> bool
```

ブックマークを削除。削除成功時は `True` を返す。

#### is_bookmarked()

```python
def is_bookmarked(file_path: str) -> bool
```

ファイルがブックマークされているかチェック。

#### get_all_bookmarks()

```python
def get_all_bookmarks() -> List[BookmarkEntry]
```

全ブックマークを最終アクセス日時の降順で取得。

#### update_access_time()

```python
def update_access_time(file_path: str) -> bool
```

ブックマークの最終アクセス時刻を更新。

### 内部メソッド

#### _load_bookmarks()

```python
def _load_bookmarks() -> List[BookmarkEntry]
```

JSON ファイルからブックマークを読み込み。

#### _save_bookmarks()

```python
def _save_bookmarks() -> bool
```

ブックマークを JSON ファイルに保存。

### JSON形式

```json
{
  "version": "1.0",
  "bookmarks": [
    {
      "file_path": "C:/path/to/file.md",
      "file_name": "file.md",
      "folder_path": "C:/path/to",
      "added_timestamp": 1234567890.0,
      "last_accessed": 1234567890.0,
      "note": ""
    }
  ]
}
```

### エラー処理

- JSON読み込み失敗: 空のリストを返す
- JSON保存失敗: `False` を返す
- ディレクトリ作成失敗: 例外を返す

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
    FileType.CDXML: ('#E91E63', 'CDX'),
}
```

### メソッド

#### `data(self, index, role)`

`DecorationRole` の場合、ファイルタイプに応じたバッジアイコンを返す。ディレクトリの場合は `QStyle.SP_DirIcon` で標準フォルダアイコンを明示的に返す。

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
- タブ情報（フォルダパス、選択ファイル、フィルターインデックス）
- アクティブタブインデックス
- 最近開いたファイル一覧（最大10件）
- 検索履歴（最大5件）

#### `load_session(self) -> dict | None`

| 戻り値 | 説明 |
|--------|------|
| dict | セッションデータ |
| None | ファイルが存在しないまたは読み込み失敗 |

#### `add_recent_file(self, file_path: str) -> None`

最近開いたファイルに追加。既存の同じパスを削除してから先頭に追加（重複排除＋順序更新）。最大10件まで保持。

| パラメータ | 型 | 説明 |
|-----------|---|------|
| file_path | str | ファイルの絶対パス |

#### `get_recent_files(self) -> List[dict]`

最近開いたファイル一覧を取得。

| 戻り値 | 説明 |
|--------|------|
| List[dict] | ファイル情報のリスト（最大10件） |

**リスト要素の形式:**
```python
{
    "file_path": "C:/path/to/file.md",
    "file_name": "file.md",
    "folder_path": "C:/path/to",
    "last_accessed": 1234567890.0
}
```

#### `add_search_history(self, query: str, options: dict, scope: str = 'all') -> None`

検索履歴に追加。最大5件まで保持（古いものから削除）。

| パラメータ | 型 | 説明 |
|-----------|---|------|
| query | str | 検索クエリ |
| options | dict | 検索オプション（case_sensitive, regex, search_filenames, operator） |
| scope | str | 検索スコープ（"all": 全ファイル, "current": このファイル）。デフォルト: "all" |

#### `get_search_history(self) -> List[dict]`

検索履歴を取得。

| 戻り値 | 説明 |
|--------|------|
| List[dict] | 検索履歴のリスト（最大5件） |

**リスト要素の形式:**
```python
{
    "query": "keyword",
    "case_sensitive": False,
    "regex": False,
    "search_filenames": False,
    "operator": "AND",
    "timestamp": 1234567890.0
}
```

### セッションファイル形式

```json
{
  "version": "2.0",
  "window": {
    "x": 100,
    "y": 100,
    "width": 1400,
    "height": 900
  },
  "tabs": [
    {
      "folder_path": "C:/path/to/folder",
      "current_file": "C:/path/to/file.md",
      "filter_index": 0
    }
  ],
  "active_tab": 0,
  "recent_files": [
    {
      "file_path": "C:/path/to/file.md",
      "file_name": "file.md",
      "folder_path": "C:/path/to",
      "last_accessed": 1234567890.0
    }
  ],
  "search_history": [
    {
      "query": "keyword",
      "case_sensitive": false,
      "regex": false,
      "search_filenames": false,
      "operator": "AND",
      "timestamp": 1234567890.0
    }
  ]
}
```

---

## FolderTab

### 概要

1つのタブを構成するウィジェット。ファイルツリー、統計パネル、Webビューを含む。

### 属性

| 属性名 | 型 | 説明 |
|--------|---|------|
| current_folder | str | 現在のフォルダパス |
| current_file | str | 選択中のファイルパス |
| file_model | FileTypeIconModel | ファイルシステムモデル（バッジ付き） |
| tree_view | QTreeView | ファイル一覧ツリービュー |
| web_view | QWebEngineView | コンテンツレンダリング領域 |
| web_page | MarkdownWebPage | リンクインターセプト用ページ |
| stats_labels | dict | 統計情報ラベル群 |
| filter_combo | QComboBox | ファイルフィルタードロップダウン |
| parent_btn | QPushButton | 親ディレクトリ移動ボタン（⬆） |
| navigation_history | list | ナビゲーション履歴スタック（tuple形式） |
| tab_recent_files | list[dict] | タブ固有の最近開いたファイルリスト（最大8件、履歴バー用） |
| search_input | QLineEdit | 検索入力ボックス |
| search_button | QPushButton | 検索実行ボタン |
| case_sensitive_check | QCheckBox | 大文字小文字区別チェックボックス |
| regex_check | QCheckBox | 正規表現検索チェックボックス |
| filename_check | QCheckBox | ファイル名検索チェックボックス |
| recent_btn | QPushButton | 最近開いたファイルボタン |
| bookmark_btn | QPushButton | ブックマーク一覧ボタン |
| current_search_query | str | 現在の検索クエリ |
| current_search_results | List[SearchResult] | 現在の検索結果 |
| scope_all_btn | QPushButton | "全ファイル" スコープ切り替えボタン |
| scope_current_btn | QPushButton | "このファイル" スコープ切り替えボタン |
| _highlight_line | int | ハイライト対象の行番号 |
| _highlight_keyword | str | ハイライト対象のキーワード |

### メソッド

#### `__init__(self, parent=None)`

| パラメータ | 型 | 説明 |
|-----------|---|------|
| parent | QWidget | 親ウィジェット |

#### `_setup_ui(self) -> None`

UIコンポーネントを初期化・配置。

**レイアウト構成:**
```
QSplitter (horizontal)
├── left_panel (QWidget, 幅250px)
│   ├── tree_view (QTreeView + FileTypeIconModel)
│   └── stats_panel (QWidget)
│       └── Lines / Chars / Words / Read / Size
└── web_view (QWebEngineView + MarkdownWebPage)
```

#### `add_recent_file(self, file_path: str) -> None`

タブ固有の最近開いたファイルリストにファイルを追加（最大8件、重複時は先頭に移動）。

| パラメータ | 型 | 説明 |
|-----------|---|------|
| file_path | str | 追加するファイルの絶対パス |

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
| app_title | str | アプリケーションタイトル（バージョン＋モード情報付き） |
| tab_widget | QTabWidget | タブコンテナ |
| css_content | str | 読み込んだスタイルシート |
| session_manager | SessionManager | セッション管理インスタンス |
| history_container | QWidget | 履歴バーのコンテナ（ツールバー下部） |
| history_bar | QWidget | 履歴リンクボタンのコンテナ |
| history_bar_layout | QHBoxLayout | 履歴リンクボタンのレイアウト |

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

ウィンドウタイトルとツールバーのパスラベルを現在のタブ状態に基づいて更新（SSOT原則）。

**タイトル形式:**
- ファイル選択時: `{app_title} - {ファイル名}`
- フォルダ選択時: `{app_title} - {フォルダパス}`
- 未選択時: `{app_title}`

`app_title` はバージョン情報を含む（例: `Markdown Viewer v1.0` または `Markdown Viewer v1.0 [Python]`）。

**パスラベル:**
- ファイル選択時: フルパスを表示
- フォルダ選択時: フォルダパスを表示
- 未選択時: 空文字

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
| Refresh | `_refresh_current_tab()` |
| Toggle Outline | `_toggle_overview()` |
| パスラベル | 現在のファイルのフルパスを右寄せで表示 |

#### `_setup_shortcuts(self) -> None`

キーボードショートカットを設定。

| キー | メソッド |
|------|---------|
| Ctrl+W | `_close_current_tab()` |
| Ctrl+O | `_open_folder()` |
| Ctrl+Tab | `_next_tab()` |
| Ctrl+Shift+Tab | `_prev_tab()` |
| Ctrl+Shift+O | `_toggle_overview()` |
| F5 | `_refresh_current_tab()` |
| Ctrl+= / Ctrl+Shift+= | `_zoom_in()` |
| Ctrl+- | `_zoom_out()` |
| Ctrl+0 | `_zoom_reset()` |

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

フォルダ選択ダイアログを表示。現在のタブにフォルダが未設定の場合は再利用し、それ以外は新しいタブを作成して設定。

#### `_refresh_current_tab(self) -> None`

現在表示中のファイルを再読み込み。スクロール位置を保持する。

**処理フロー:**
1. JavaScript で `window.pageYOffset` を取得
2. コールバックで `_do_reload()` を呼び出し

#### `_do_reload(self, tab: FolderTab, scroll_y) -> None`

ファイルの再読み込みとスクロール位置の復元を実行。

| パラメータ | 型 | 説明 |
|-----------|---|------|
| tab | FolderTab | 対象タブ |
| scroll_y | float/None | 復元するスクロール位置 |

**処理フロー:**
1. ファイルを再読み込み（`_load_file()`）
2. ナビゲーション履歴をクリア
3. `loadFinished` シグナルに一時接続
4. ページ読み込み完了後、100ms遅延で `window.scrollTo()` を実行
5. シグナルを `disconnect`

#### `_zoom_in(self) -> None`

現在のタブのWebViewのズームレベルを0.1増加（最大3.0）。

#### `_zoom_out(self) -> None`

現在のタブのWebViewのズームレベルを0.1減少（最小0.3）。

#### `_zoom_reset(self) -> None`

現在のタブのWebViewのズームレベルを1.0にリセット。

#### `_toggle_overview(self) -> None`

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

#### `_on_link_clicked(self, tab: FolderTab, url: str, open_in_new_tab: bool) -> None`

リンククリックを処理。

| パラメータ | 型 | 説明 |
|-----------|---|------|
| tab | FolderTab | 対象タブ |
| url | str | クリックされたURL |
| open_in_new_tab | bool | 新しいタブで開くか |

**処理フロー:**
1. URLスキームを判定（app://, http://, #, ファイルパス）
2. 種別に応じた処理を実行
3. 履歴スタックに現在ファイルを追加

#### `_update_history_bar(self) -> None`

ツールバーの履歴リンクバーを更新。`SessionManager.get_recent_files()` から最大5件取得し、QPushButton として表示。現在のファイルはハイライト表示。

#### `_on_history_link_clicked(self, file_path: str) -> None`

履歴リンクのクリックハンドラ。現在のタブ内でファイルを開く。

| パラメータ | 型 | 説明 |
|-----------|---|------|
| file_path | str | 開くファイルの絶対パス |

**処理フロー:**
1. ファイル存在チェック（不在時は警告＋履歴バー再描画）
2. 現在タブのフォルダコンテキストを必要に応じて変更
3. ナビゲーション履歴に現在ファイルを追加
4. ファイルを読み込み・レンダリング
5. TreeView の選択を更新
6. recent files に追加＋履歴バー再描画

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

#### `_on_file_clicked(self, tab: FolderTab, index: QModelIndex) -> None`

ファイルツリーのアイテムがクリックされた時の処理。

| パラメータ | 型 | 説明 |
|-----------|---|------|
| tab | FolderTab | 対象タブ |
| index | QModelIndex | クリックされたアイテムのインデックス |

#### `_load_file(self, tab: FolderTab, file_path: str) -> None`

ファイルタイプに応じて適切なレンダラーにディスパッチする。

| パラメータ | 型 | 説明 |
|-----------|---|------|
| tab | FolderTab | 対象タブ |
| file_path | str | ファイルパス |

**処理フロー:**
1. `detect_file_type()` でファイルタイプを判定
2. Markdown → `_render_markdown()`
3. XML/Python → `_render_code()`
4. CSV → `_render_csv()`
5. CDXML → `_render_cdxml()`

#### `_render_markdown(self, tab: FolderTab, markdown_content: str) -> None`

Markdownコンテンツをレンダリングして表示する。

| パラメータ | 型 | 説明 |
|-----------|---|------|
| tab | FolderTab | 対象タブ |
| markdown_content | str | Markdownテキスト |

**処理フロー:**
1. Markdownソースを行ごとに解析し、lineInfo（行番号・タイプ情報）JSON配列を生成
2. HTMLテンプレートにコンテンツ・lineInfo・rawLines・ファイルパスを埋め込み
3. ローカルのmarked.js/mermaid.jsを読み込み
4. Markdownをパース
5. `buildGutter()` で行番号ガターを生成
6. Mermaid図表を初期化
7. 目次（アウトライン）を生成
8. WebViewにHTMLをセット

**テンプレート変数:**
| 変数 | 説明 |
|------|------|
| `$MARKDOWN_CONTENT$` | Markdownテキスト（エスケープ済み） |
| `$LINE_INFO$` | 行番号・タイプ情報のJSON配列 |
| `$RAW_LINES$` | ソースを行分割したJSON配列 |
| `$FILE_PATH$` | 現在のファイルのフルパス |

#### `_render_code(self, tab: FolderTab, content: str, language: str, title: str) -> None`

XML/Pythonファイルをシンタックスハイライト付きで表示する。

| パラメータ | 型 | 説明 |
|-----------|---|------|
| tab | FolderTab | 対象タブ |
| content | str | ファイル内容 |
| language | str | 言語（xml, python, plaintext） |
| title | str | ファイル名 |

#### `_render_csv(self, tab: FolderTab, content: str) -> None`

CSVファイルをHTMLテーブルとして表示する。

| パラメータ | 型 | 説明 |
|-----------|---|------|
| tab | FolderTab | 対象タブ |
| content | str | CSVファイル内容 |

#### `_escape_for_js(self, content: str) -> str`

JavaScriptテンプレートリテラル用にバックスラッシュ、バッククォート、ドル記号をエスケープする。

#### `_escape_html(self, text: str) -> str`

HTMLエンティティ（&, <, >, ", '）をエスケープする。

#### `_set_html_with_base(self, tab: FolderTab, html: str) -> None`

QUrlベースURLを設定してHTMLをWebViewにセットする。相対リンク解決用。

#### `_add_welcome_tab(self) -> None`

ウェルカムタブを追加。キーボードショートカット一覧を表示。

#### `_on_scope_toggled(self, tab: FolderTab, current_file_checked: bool) -> None`

スコープ切り替え変更時のハンドラ。プレースホルダーテキストとファイル名検索チェックボックスの状態を更新する。

| パラメータ | 型 | 説明 |
|-----------|---|------|
| tab | FolderTab | 対象タブ |
| current_file_checked | bool | "このファイル" スコープが選択されているか |

**処理内容:**
1. 検索入力ボックスのプレースホルダーテキストをスコープに応じて更新
2. ファイル名検索チェックボックスの有効/無効状態を制御

#### `_update_scope_toggle_state(self, tab: FolderTab) -> None`

スコープ切り替えボタンの有効/無効状態を `tab.current_file` に基づいて更新する。

| パラメータ | 型 | 説明 |
|-----------|---|------|
| tab | FolderTab | 対象タブ |

**処理内容:**
1. `tab.current_file` が設定されている場合、スコープ切り替えボタンを有効化
2. `tab.current_file` が未設定の場合、スコープ切り替えボタンを無効化し「全ファイル」をデフォルトに設定

#### `_show_tree_context_menu(self, tab: FolderTab, pos: QPoint) -> None`

ファイルツリー上での右クリックメニューを表示。

| メニュー項目 | 表示条件 | 動作 |
|------------|---------|------|
| Open in New Tab | フォルダの場合 | フォルダを新タブで開く |
| Copy Path | 常に表示 | パスをクリップボードにコピー |

#### `_navigate_to_parent(self, tab: FolderTab) -> None`

現在のフォルダの親ディレクトリに移動。ドライブルートでは無効。

| パラメータ | 型 | 説明 |
|-----------|---|------|
| tab | FolderTab | 対象タブ |

---

#### `_render_cdxml(self, tab: FolderTab, content: str) -> None`

CDXML化学構造ファイルをSVG画像としてレンダリング。

| パラメータ | 型 | 説明 |
|-----------|---|------|
| tab | FolderTab | 対象タブ |
| content | str | CDXMLファイルの内容 |

**処理フロー:**
1. `cdxml_to_svg()` でSVGを生成
2. HTMLテンプレート（ヘッダーバッジ＋SVGコンテナ）に埋め込み
3. WebViewに表示

---

## モジュールレベル関数

### `get_version_info() -> tuple[str, bool]`

バージョン番号と実行モード（凍結exe or Python）を返す。

| 戻り値 | 説明 |
|--------|------|
| tuple[str, bool] | (バージョン文字列, PyInstaller実行かどうか) |

**処理フロー:**
1. `sys.frozen` 属性で PyInstaller 実行かを判定
2. `get_resource_path('version.txt')` からバージョン番号を読み込み
3. ファイルが見つからない場合は `'0.0'` をデフォルト値とする

### `cdxml_to_svg(cdxml_content: str) -> tuple[str, int]`

CDXML（ChemDraw XML）を解析し、化学構造のSVG画像を生成する。外部依存なし（`xml.etree.ElementTree`のみ使用）。

| パラメータ | 型 | 説明 |
|-----------|---|------|
| cdxml_content | str | CDXMLファイルの文字列 |

| 戻り値 | 説明 |
|--------|------|
| tuple[str, int] | (SVG文字列, 構造体数) |

**対応要素:**
| CDXML要素 | SVG描画 |
|-----------|---------|
| `<n>` (原子) | テキストラベル（非C原子のみ） |
| `<b>` (結合) | 線（Order=1:単線, 2:二重線, 3:三重線） |
| `<t>` (テキスト) | 構造名ラベル |

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
