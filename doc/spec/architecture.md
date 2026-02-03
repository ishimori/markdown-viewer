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
│   │   ├── QT_STYLES        # Qt ウィジェットスタイル定数
│   │   ├── MarkdownWebPage  # リンククリック処理
│   │   ├── SessionManager   # セッション管理
│   │   ├── FolderTab        # タブUI
│   │   └── MarkdownViewer   # メインウィンドウ
│   ├── style.css            # UIスタイル定義
│   │   ├── CSS Variables    # カラーパレット
│   │   ├── Typography       # フォント・見出し
│   │   ├── Code Blocks      # コード表示
│   │   ├── Mermaid          # 図表スタイル
│   │   └── Layout           # レイアウト
│   └── templates/
│       └── markdown.html    # Markdownレンダリング用HTMLテンプレート
├── doc/
│   ├── spec/                # 仕様書（本ドキュメント）
│   └── sample.md            # サンプルファイル
├── requirements.txt         # 依存パッケージ
├── pyproject.toml           # プロジェクト設定
├── run.bat                  # 起動バッチ
└── MarkdownViewer.vbs       # Windows起動スクリプト
```

## HTMLテンプレート

### markdown.html

Markdownレンダリング用のHTMLテンプレート。以下のプレースホルダーを Python 側で置換。

| プレースホルダー | 内容 |
|-----------------|------|
| `$CSS_CONTENT$` | style.css の内容 |
| `$MARKED_JS_PATH$` | marked.min.js のファイルパス |
| `$MERMAID_JS_PATH$` | mermaid.min.js のファイルパス |
| `$MARKDOWN_CONTENT$` | Markdown テキスト（エスケープ済み） |
| `$BACK_BUTTON_STYLE$` | Backボタンの表示スタイル |

### HTML構造

テンプレートの主要構成：

- head: CSS埋め込み、marked.js/mermaid.js読み込み
- body: Backボタン、コンテンツ領域、サイドバー（TOC）
- script: Markdownパース、Mermaid初期化、TOC生成

詳細は `src/templates/markdown.html` を参照。

### エスケープ処理

Markdownコンテンツは JavaScript テンプレートリテラル内に埋め込まれるため、バックスラッシュ、バッククォート、ドル記号をエスケープする。

### JavaScript機能

| 関数 | 説明 |
|------|------|
| `buildTOC()` | 見出しから目次を生成。ID がない場合は自動生成 |
| `updateActiveHeading()` | スクロール位置に応じて現在の見出しをハイライト |
| `toggleOverview()` | アウトラインの表示/非表示を切り替え |

---

## データフロー

### 1. アプリケーション起動

```
main()
  │
  ├─► QApplication 初期化
  │
  ├─► MarkdownViewer.__init__()
  │     ├─► _load_resources()     # CSS, JS, HTMLテンプレート読み込み
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
        │     ├─► アウトライン表示状態
        │     └─► フィルターインデックス
        │
        └─► JSON形式で保存
              └─► ~/.markdown-viewer/session.json
```

### 4. リンククリック処理

```
ユーザー操作: リンクをクリック
  │
  ▼
MarkdownWebPage.acceptNavigationRequest()
  │
  ├─► Shiftキー押下状態を確認
  │
  ├─► link_clicked シグナル発行
  │
  └─► False を返却（デフォルト動作抑制）
        │
        ▼
MarkdownViewer._handle_link_click(url, new_tab)
  │
  ├─► URLスキーム判定
  │     │
  │     ├─► app://back → _navigate_back()
  │     │
  │     ├─► http(s):// → QDesktopServices.openUrl()
  │     │
  │     ├─► #anchor → JavaScript scrollIntoView()
  │     │
  │     └─► ローカルファイル → ファイル読み込み
  │           │
  │           ├─► 相対パス解決
  │           ├─► .md 拡張子自動補完
  │           └─► 履歴スタックに追加
  │
  └─► new_tab=True の場合、新規タブ作成
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
      "outline_visible": true,
      "filter_index": 0
    }
  ],
  "active_tab": 0
}
```

#### セッション復元時の注意点

- **ウィンドウ位置の画面範囲チェック**: 復元時にウィンドウが画面外に出ないよう、利用可能な画面範囲内に収める
- **遅延ロード**: `QFileSystemModel` の非同期特性に対応するため、ファイル選択を 200ms 遅延させる（`QTimer.singleShot`）

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
