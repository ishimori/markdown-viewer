# コンポーネント仕様

## クラス一覧

| クラス | 継承元 | ファイル位置 | 役割 |
|--------|--------|-------------|------|
| `SessionManager` | - | main.py:23-71 | セッション状態の永続化 |
| `FolderTab` | QWidget | main.py:74-295 | タブ単位のUI・ロジック |
| `MarkdownViewer` | QMainWindow | main.py:298-673 | アプリケーション全体の制御 |

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
| current_file | str | 選択中のファイルパス |
| file_tree | QTreeWidget | ファイル一覧ツリー |
| web_view | QWebEngineView | Markdownレンダリング領域 |
| stats_labels | dict | 統計情報ラベル群 |
| outline_visible | bool | アウトライン表示状態 |
| css | str | スタイルシート文字列 |

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
```html
<!DOCTYPE html>
<html>
<head>
    <style>{css}</style>
    <script src="marked.js"></script>
    <script src="mermaid.js"></script>
</head>
<body>
    <div class="container">
        <div id="content">{rendered_markdown}</div>
        <div id="outline">{table_of_contents}</div>
    </div>
    <script>
        // Markdown parse & Mermaid init
    </script>
</body>
</html>
```

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

#### `_load_css(self) -> str`

`src/style.css` を読み込んで返す。

| 戻り値 | 説明 |
|--------|------|
| str | CSSテキスト |

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
