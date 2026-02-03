# アーキテクチャ

## システム構成図

```
┌─────────────────────────────────────────────────────────────┐
│                    MarkdownViewer (QMainWindow)             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    Toolbar                            │  │
│  │  [Open] [New Tab] [Reload] [Toggle Outline]          │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  QTabWidget                           │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │               FolderTab                          │ │  │
│  │  │  ┌─────────┐  ┌──────────────────────────────┐  │ │  │
│  │  │  │FileTree │  │        QWebEngineView        │  │ │  │
│  │  │  │  .md    │  │  ┌────────────┬───────────┐  │  │ │  │
│  │  │  │  .md    │  │  │  Content   │  Outline  │  │  │ │  │
│  │  │  │  ...    │  │  │  (HTML)    │  (ToC)    │  │  │ │  │
│  │  │  ├─────────┤  │  │            │           │  │  │ │  │
│  │  │  │  Stats  │  │  │            │           │  │  │ │  │
│  │  │  │Lines:   │  │  │            │           │  │  │ │  │
│  │  │  │Chars:   │  │  │            │           │  │  │ │  │
│  │  │  └─────────┘  │  └────────────┴───────────┘  │  │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐    ┌─────────────────────────────┐
│ SessionManager  │    │     External Libraries      │
│ ┌─────────────┐ │    │  ┌─────────┐ ┌───────────┐ │
│ │session.json │ │    │  │marked.js│ │mermaid.js │ │
│ └─────────────┘ │    │  └─────────┘ └───────────┘ │
└─────────────────┘    └─────────────────────────────┘
```

## ファイル構造

```
markdown-viewer/
├── src/
│   ├── main.py              # メインアプリケーション
│   │   ├── SessionManager   # セッション管理 (L23-71)
│   │   ├── FolderTab        # タブUI (L74-295)
│   │   └── MarkdownViewer   # メインウィンドウ (L298-673)
│   └── style.css            # UIスタイル定義
│       ├── CSS Variables    # カラーパレット (L1-20)
│       ├── Typography       # フォント・見出し (L21-150)
│       ├── Code Blocks      # コード表示 (L151-200)
│       ├── Mermaid          # 図表スタイル (L201-250)
│       └── Layout           # レイアウト (L251-455)
├── doc/
│   ├── spec/                # 仕様書（本ドキュメント）
│   └── sample.md            # サンプルファイル
├── requirements.txt         # 依存パッケージ
├── pyproject.toml           # プロジェクト設定
├── run.bat                  # 起動バッチ
└── MarkdownViewer.vbs       # Windows起動スクリプト
```

## データフロー

### 1. アプリケーション起動

```
main()
  │
  ├─► QApplication 初期化
  │
  ├─► MarkdownViewer.__init__()
  │     ├─► _load_css()           # style.css 読み込み
  │     ├─► _setup_ui()           # タブウィジェット初期化
  │     ├─► _setup_toolbar()      # ツールバー設定
  │     ├─► _setup_shortcuts()    # キーボードショートカット
  │     └─► _restore_session()    # セッション復元
  │           └─► SessionManager.load_session()
  │
  └─► app.exec()                  # イベントループ開始
```

### 2. ファイル読み込み

```
ユーザー操作: ファイルツリーでファイルクリック
  │
  ▼
FolderTab._on_file_clicked(item)
  │
  ├─► ファイルパス取得
  │
  ├─► open(path, encoding='utf-8').read()
  │
  ├─► update_stats(content)       # 統計情報更新
  │
  └─► _render_markdown(content)   # HTML生成・表示
        │
        ├─► HTMLテンプレート生成
        │     ├─► marked.js 読み込み
        │     ├─► mermaid.js 読み込み
        │     └─► style.css 適用
        │
        ├─► JavaScript実行
        │     ├─► marked.parse(content)
        │     ├─► mermaid.init()
        │     └─► 目次生成
        │
        └─► web_view.setHtml(html)
```

### 3. セッション保存

```
アプリケーション終了 / ウィンドウ状態変更
  │
  ▼
MarkdownViewer.closeEvent()
  │
  └─► SessionManager.save_session(viewer)
        │
        ├─► ウィンドウ位置・サイズ取得
        │
        ├─► 開いているタブ情報取得
        │     ├─► フォルダパス
        │     ├─► 選択ファイル
        │     └─► アウトライン表示状態
        │
        └─► JSON形式で保存
              └─► ~/.markdown-viewer/session.json
```

## クラス関係図

```
┌─────────────────────────────────────────────────────┐
│                    main.py                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────┐                               │
│  │  SessionManager │ ◄─────────────────────────┐   │
│  ├─────────────────┤                           │   │
│  │ + save_session()│                           │   │
│  │ + load_session()│                           │   │
│  └─────────────────┘                           │   │
│           ▲                                    │   │
│           │ uses                               │   │
│           │                                    │   │
│  ┌────────┴────────────────────────────────┐  │   │
│  │           MarkdownViewer                 │  │   │
│  │              (QMainWindow)               │──┘   │
│  ├──────────────────────────────────────────┤      │
│  │ - tabs: QTabWidget                       │      │
│  │ - css: str                               │      │
│  │ - session_manager: SessionManager        │      │
│  ├──────────────────────────────────────────┤      │
│  │ + _setup_ui()                            │      │
│  │ + _setup_toolbar()                       │      │
│  │ + _setup_shortcuts()                     │      │
│  │ + _add_new_tab()                         │      │
│  │ + _restore_session()                     │      │
│  │ + open_file()                            │      │
│  └──────────────────────────────────────────┘      │
│           │                                        │
│           │ contains                               │
│           ▼                                        │
│  ┌──────────────────────────────────────────┐     │
│  │              FolderTab                    │     │
│  │               (QWidget)                   │     │
│  ├──────────────────────────────────────────┤     │
│  │ - folder_path: str                        │     │
│  │ - file_tree: QTreeWidget                  │     │
│  │ - web_view: QWebEngineView                │     │
│  │ - stats_labels: dict                      │     │
│  │ - outline_visible: bool                   │     │
│  ├──────────────────────────────────────────┤     │
│  │ + _setup_ui()                             │     │
│  │ + set_folder()                            │     │
│  │ + update_stats()                          │     │
│  │ + _render_markdown()                      │     │
│  │ + _on_file_clicked()                      │     │
│  │ + toggle_outline()                        │     │
│  └──────────────────────────────────────────┘     │
│                                                    │
└────────────────────────────────────────────────────┘
```

## 設定ファイル

### session.json

保存場所: `~/.markdown-viewer/session.json`

```json
{
  "window": {
    "x": 100,
    "y": 100,
    "width": 1200,
    "height": 800
  },
  "tabs": [
    {
      "folder_path": "C:/path/to/folder",
      "selected_file": "document.md",
      "outline_visible": true
    }
  ],
  "active_tab": 0
}
```

### pyproject.toml

```toml
[project]
name = "markdown-viewer"
requires-python = ">=3.10"
dependencies = [
    "PyQt6>=6.4.0",
    "PyQt6-WebEngine>=6.4.0"
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## 外部依存（CDN）

| ライブラリ | URL | 用途 |
|-----------|-----|------|
| marked.js | cdnjs.cloudflare.com | Markdown→HTML変換 |
| mermaid.js | cdn.jsdelivr.net | 図表レンダリング |

※ インターネット接続が必要（初回読み込み時、ブラウザキャッシュ使用）
