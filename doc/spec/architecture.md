# アーキテクチャ

## システム構成図

```
┌─────────────────────────────────────────────────────────────────┐
│                    MarkdownViewer (QMainWindow)                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Toolbar                                                   │  │
│  │  [Open] [New Tab] [Refresh] [Outline]    /path/to/file     │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                  QTabWidget                                │  │
│  │  ┌────────────────────────────────────────────────────┐   │  │
│  │  │               FolderTab                             │   │  │
│  │  │  ┌─────────┐  ┌─────────────────────────────────┐  │   │  │
│  │  │  │FileTree │  │        QWebEngineView           │  │   │  │
│  │  │  │  .md    │  │  ┌──────┬──────────┬─────────┐  │  │   │  │
│  │  │  │  .xml   │  │  │Gutter│ Content  │ Outline │  │  │   │  │
│  │  │  │  .py    │  │  │(Lines)│ (HTML)   │ (ToC)   │  │  │   │  │
│  │  │  ├─────────┤  │  │      │          │         │  │  │   │  │
│  │  │  │  Stats  │  │  │      │          │         │  │  │   │  │
│  │  │  │Lines:   │  │  │      │          │         │  │  │   │  │
│  │  │  │Chars:   │  │  │      │          │         │  │  │   │  │
│  │  │  └─────────┘  │  └──────┴──────────┴─────────┘  │  │   │  │
│  │  └────────────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐    ┌─────────────────────────────────────┐
│ SessionManager  │    │     Local Libraries (src/assets/)   │
│ ┌─────────────┐ │    │  ┌─────────┐ ┌───────────┐         │
│ │session.json │ │    │  │marked.js│ │mermaid.js │         │
│ └─────────────┘ │    │  └─────────┘ └───────────┘         │
│                 │    │  ┌──────────────┐                   │
│                 │    │  │highlight.js  │                   │
│                 │    │  └──────────────┘                   │
└─────────────────┘    └─────────────────────────────────────┘
```

## ファイル構造

```
markdown-viewer/
├── src/
│   ├── main.py              # メインアプリケーション
│   │   ├── FileType         # ファイルタイプ列挙型
│   │   ├── FileTypeIconModel# ファイルタイプバッジアイコン
│   │   ├── QT_STYLES        # Qt ウィジェットスタイル定数
│   │   ├── MarkdownWebPage  # リンククリック処理
│   │   ├── SessionManager   # セッション管理
│   │   ├── FolderTab        # タブUI
│   │   └── MarkdownViewer   # メインウィンドウ
│   ├── version.txt          # バージョン番号ファイル
│   ├── style.css            # UIスタイル定義
│   │   ├── CSS Variables    # カラーパレット
│   │   ├── Typography       # フォント・見出し
│   │   ├── Code Blocks      # コード表示
│   │   ├── Mermaid          # 図表スタイル
│   │   └── Layout           # レイアウト
│   ├── assets/
│   │   ├── css/
│   │   │   └── highlight-github.css  # シンタックスハイライトCSS
│   │   └── js/
│   │       ├── marked.min.js         # Markdownパーサー
│   │       ├── mermaid.min.js        # 図表ライブラリ
│   │       └── highlight.min.js      # シンタックスハイライト
│   └── templates/
│       └── markdown.html    # Markdownレンダリング用HTMLテンプレート
├── scripts/                  # ビルド・ユーティリティスクリプト
│   ├── build.bat            # ビルドスクリプト
│   ├── increment_version.py # バージョン自動インクリメント
│   └── markdown_viewer.spec # PyInstallerスペックファイル
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
| `$LINE_INFO$` | 行番号・タイプ情報のJSON配列 |
| `$RAW_LINES$` | Markdownソースの行分割JSON配列 |
| `$FILE_PATH$` | 現在のファイルのフルパス |

### HTML構造

テンプレートの主要構成：

- head: CSS埋め込み、marked.js/mermaid.js読み込み
- body: ガター（行番号）、Backボタン、コンテンツ領域、コピートースト、サイドバー（TOC）
- script: Markdownパース、ガター生成、Mermaid初期化、TOC生成

詳細は `src/templates/markdown.html` を参照。

### エスケープ処理

Markdownコンテンツは JavaScript テンプレートリテラル内に埋め込まれるため、バックスラッシュ、バッククォート、ドル記号をエスケープする。

### JavaScript機能

| 関数 | 説明 |
|------|------|
| `buildGutter()` | lineInfoとDOM要素を照合し、行番号ガターを生成 |
| `copyToClipboard(text)` | `document.execCommand('copy')` によるクリップボードコピー |
| `copyLineRange(startLine, endLine)` | 指定行範囲のソースをファイルパス付きでコピー |
| `showToast(message)` | コピー成功時のトースト通知表示 |
| `buildTOC()` | 見出しから目次を生成。ID がない場合は自動生成。行番号を表示 |
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
MarkdownViewer._on_file_clicked(tab, item)
  │
  ├─► ファイルパス取得
  │
  ├─► open(path, encoding='utf-8').read()
  │
  ├─► tab.update_stats(content)        # 統計情報更新
  │
  └─► _load_file(tab, file_path)       # ファイルタイプに応じてディスパッチ
        │
        ├─► detect_file_type() でファイルタイプを判定
        │
        ├─► Markdown → _render_markdown(tab, content)
        │     │
        │     ├─► lineInfo生成（Markdown行解析）
        │     │     ├─► 見出し、段落、リスト、テーブル等を検出
        │     │     └─► JSON配列として出力
        │     │
        │     ├─► HTMLテンプレート生成
        │     │     ├─► $MARKDOWN_CONTENT$, $LINE_INFO$ 等を置換
        │     │     ├─► marked.js / mermaid.js 読み込み
        │     │     └─► style.css 適用
        │     │
        │     ├─► JavaScript実行
        │     │     ├─► marked.parse(content)
        │     │     ├─► buildGutter()     # 行番号ガター生成
        │     │     ├─► mermaid.init()
        │     │     └─► buildTOC()        # 目次生成
        │     │
        │     └─► web_view.setHtml(html)
        │
        ├─► XML/Python → _render_code(tab, content, language, title)
        ├─► CSV → _render_csv(tab, content)
        └─► CDXML → _render_cdxml(tab, content)
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
MarkdownViewer._on_link_clicked(tab, url, open_in_new_tab)
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
  └─► open_in_new_tab=True の場合、新規タブ作成
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
│  │ - app_title: str                         │      │
│  │ - tab_widget: QTabWidget                 │      │
│  │ - css_content: str                       │      │
│  │ - session_manager: SessionManager        │      │
│  │ - path_label: QLabel                     │      │
│  ├──────────────────────────────────────────┤      │
│  │ + _setup_ui()                            │      │
│  │ + _setup_toolbar()                       │      │
│  │ + _setup_shortcuts()                     │      │
│  │ + _add_new_tab()                         │      │
│  │ + _restore_session()                     │      │
│  │ + open_file()                            │      │
│  │ + _on_file_clicked()                     │      │
│  │ + _load_file()                           │      │
│  │ + _render_markdown()                     │      │
│  │ + _refresh_current_tab()                 │      │
│  │ + _zoom_in() / _zoom_out() / _zoom_reset│      │
│  └──────────────────────────────────────────┘      │
│           │                                        │
│           │ contains                               │
│           ▼                                        │
│  ┌──────────────────────────────────────────┐     │
│  │              FolderTab                    │     │
│  │               (QWidget)                   │     │
│  ├──────────────────────────────────────────┤     │
│  │ - folder_path: str                        │     │
│  │ - tree_view: QTreeView                    │     │
│  │ - web_view: QWebEngineView                │     │
│  │ - stats_labels: dict                      │     │
│  │ - navigation_history: list                │     │
│  ├──────────────────────────────────────────┤     │
│  │ + _setup_ui()                             │     │
│  │ + set_folder()                            │     │
│  │ + update_stats()                          │     │
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
    "width": 1400,
    "height": 900
  },
  "tabs": [
    {
      "folder_path": "C:/path/to/folder",
      "selected_file": "document.md",
      "filter_index": 0
    }
  ],
  "active_tab_index": 0
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

## 外部依存（ローカルバンドル）

| ライブラリ | 配置場所 | 用途 |
|-----------|---------|------|
| marked.js | src/assets/js/marked.min.js | Markdown→HTML変換 |
| mermaid.js | src/assets/js/mermaid.min.js | 図表レンダリング |
| highlight.js | src/assets/js/highlight.min.js | シンタックスハイライト |

※ すべてローカルにバンドルされており、オフラインで動作可能（CDN接続不要）
