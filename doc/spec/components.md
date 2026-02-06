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
| `path_label` | ツールバーのファイルパス表示ラベル |

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
- タブ情報（フォルダパス、選択ファイル、フィルターインデックス）
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
| current_folder | str | 現在のフォルダパス |
| current_file | str | 選択中のファイルパス |
| file_model | FileTypeIconModel | ファイルシステムモデル（バッジ付き） |
| tree_view | QTreeView | ファイル一覧ツリービュー |
| web_view | QWebEngineView | コンテンツレンダリング領域 |
| web_page | MarkdownWebPage | リンクインターセプト用ページ |
| stats_labels | dict | 統計情報ラベル群 |
| filter_combo | QComboBox | ファイルフィルタードロップダウン |
| navigation_history | list | ナビゲーション履歴スタック |

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
| path_label | QLabel | ツールバー上のファイルパス表示ラベル |

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
| Open Folder | `_open_folder_in_current_tab()` |
| New Tab | `_add_new_tab()` |
| Refresh | `_refresh_current_tab()` |
| Toggle Outline | `_toggle_overview()` |
| パスラベル | 現在のファイルのフルパスを右寄せで表示 |

#### `_setup_shortcuts(self) -> None`

キーボードショートカットを設定。

| キー | メソッド |
|------|---------|
| Ctrl+T | `_add_new_tab()` |
| Ctrl+W | `_close_current_tab()` |
| Ctrl+O | `_open_folder_in_current_tab()` |
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

#### `_open_folder_in_current_tab(self) -> None`

フォルダ選択ダイアログを表示し、選択されたフォルダを現在のタブに設定。

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

#### `_show_tree_context_menu(self, tab: FolderTab, pos: QPoint) -> None`

ファイルツリー上での右クリックメニューを表示。

| メニュー項目 | 動作 |
|------------|------|
| Copy Path | ファイルパスをクリップボードにコピー |

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
