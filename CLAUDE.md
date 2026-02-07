# CLAUDE.md

このファイルは Claude Code（AI アシスタント）がプロジェクトを理解するためのガイドです。

## プロジェクト概要

**Markdown Viewer** - Windows 用の Markdown ビューアアプリケーション。Mermaid 図表対応、タブ UI、セッション管理機能を持つ。

## 技術スタック

- **言語**: Python 3.10+
- **GUI**: PyQt6, PyQt6-WebEngine
- **レンダリング**: marked.js (Markdown), mermaid.js (図表)

## ファイル構成

```
markdown-viewer/
├── src/
│   ├── main.py          # メインアプリ (QT_STYLES, MarkdownWebPage, SessionManager, FolderTab, MarkdownViewer)
│   ├── style.css        # UIスタイル定義
│   └── templates/
│       └── markdown.html # Markdownレンダリング用HTMLテンプレート
├── doc/
│   ├── spec/            # 詳細仕様書 ← 変更時は必ず参照
│   └── sample.md        # テスト用サンプル
├── requirements.txt     # PyQt6, PyQt6-WebEngine
└── run.bat              # 起動スクリプト
```

## 仕様書（重要）

変更を行う前に、以下の仕様書を必ず参照してください：

| 変更内容 | 参照する仕様書 |
|---------|---------------|
| 新機能追加 | [doc/spec/features.md](doc/spec/features.md), [doc/spec/architecture.md](doc/spec/architecture.md) |
| UI変更 | [doc/spec/ui-style.md](doc/spec/ui-style.md) |
| クラス・メソッド変更 | [doc/spec/components.md](doc/spec/components.md) |
| 全体把握 | [doc/spec/index.md](doc/spec/index.md) |
| 開発環境 | [doc/spec/development.md](doc/spec/development.md) |

## 主要クラス・定数

| クラス/定数 | 場所 | 役割 |
|-------------|------|------|
| `QT_STYLES` | main.py:33 | Qt ウィジェットスタイル定数 |
| `MarkdownWebPage` | main.py:93 | リンククリック処理 |
| `SessionManager` | main.py:121 | セッション保存・復元 |
| `FolderTab` | main.py:175 | タブUI・ファイル表示 |
| `MarkdownViewer` | main.py:335 | メインウィンドウ |

## よく使うコマンド

```bash
# 起動
python src/main.py

# 特定ファイルを開く
python src/main.py "path/to/file.md"

# 依存インストール
pip install -r requirements.txt
```

## 変更時の注意事項

1. **CSS 変数を使用** - 色は `style.css` の CSS 変数を使う
2. **セッション保存** - 新しい状態を追加する場合は `SessionManager` を更新
3. **仕様書の更新** - 機能変更時は該当する `doc/spec/*.md` も更新する
4. **UTF-8** - ファイル読み書きは UTF-8 を使用

## デバッグ

- サンプルファイル: `doc/sample.md`
- セッションファイル: `~/.markdown-viewer/session.json`

## 既知の制限事項・過去の教訓

### file:// スクリプト読み込み制限

Qt WebEngine (Chromium) は `setHtml(html, base_url)` で `base_url` と異なるディレクトリツリーの `file://` スクリプトをブロックする。外部ディレクトリのファイルを開くと `marked.js` が読み込めず、markdown がレンダリングされない問題があった。

**対策:** `marked.min.js` (40KB) と `highlight.min.js` (123KB) はインライン埋め込み。`mermaid.min.js` (3.3MB) は `setHtml()` の 2MB 制限により外部参照のまま（Mermaid 図表のみ影響）。

**調査のポイント:** 特定ディレクトリのファイルだけ表示が壊れる場合、ブラウザレベルのセキュリティ制限を疑う。静的解析（エスケープ処理・テンプレート生成・JS実行）では特定困難。
