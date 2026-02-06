# Markdown Viewer 仕様書

> このドキュメントは生成AIが効率的にプロジェクトを理解・修正できるよう設計されています。

## ドキュメント構成

| ドキュメント | 内容 | 対象読者 |
|-------------|------|---------|
| [overview.md](overview.md) | プロジェクト概要・目的・技術スタック | 初回理解時 |
| [architecture.md](architecture.md) | システム構成・データフロー・ファイル構造 | 設計変更時 |
| [components.md](components.md) | 主要クラス・メソッドの詳細仕様 | 実装修正時 |
| [features.md](features.md) | 機能一覧・動作仕様 | 機能追加・修正時 |
| [ui-style.md](ui-style.md) | UI設計・スタイル定義・カラーパレット | UI変更時 |
| [development.md](development.md) | 開発環境構築・コーディング規約 | 開発開始時 |

## クイックリファレンス

### プロジェクト概要

- **名称**: Markdown Viewer
- **種別**: Windows デスクトップアプリケーション
- **言語**: Python 3.10+
- **GUI**: PyQt6 + WebEngine
- **主要機能**: Markdown表示、Mermaid対応、タブUI、セッション管理、マルチファイル形式対応、行番号ガター、ズーム

### ファイル構成（主要）

```
markdown-viewer/
├── src/
│   ├── main.py          # アプリケーション本体
│   ├── version.txt      # バージョン番号
│   ├── style.css        # UIスタイル定義
│   ├── assets/          # 静的アセット（JS/CSS）
│   │   ├── css/
│   │   │   └── highlight-github.css
│   │   └── js/
│   │       ├── marked.min.js
│   │       ├── mermaid.min.js
│   │       └── highlight.min.js
│   └── templates/
│       └── markdown.html # HTMLテンプレート
├── scripts/              # ビルド・ユーティリティ
│   ├── build.bat
│   ├── increment_version.py
│   └── markdown_viewer.spec
├── doc/
│   ├── spec/            # 本仕様書
│   └── sample.md        # サンプルMarkdown
├── requirements.txt     # 依存パッケージ
├── pyproject.toml       # プロジェクト設定
├── run.bat              # 起動スクリプト
└── MarkdownViewer.vbs   # Windows起動用VBS
```

### 主要クラス・定数

| 名前 | ファイル | 役割 |
|------|---------|------|
| `get_version_info` | main.py:26 | バージョン情報取得 |
| `FileType` | main.py:46 | ファイルタイプ列挙型 |
| `QT_STYLES` | main.py:272 | Qt ウィジェットスタイル定数 |
| `FileTypeIconModel` | main.py:344 | ファイルタイプバッジアイコン |
| `MarkdownWebPage` | main.py:403 | リンククリック処理 |
| `SessionManager` | main.py:431 | セッション状態の保存・復元 |
| `FolderTab` | main.py:485 | タブ単位のUI管理 |
| `MarkdownViewer` | main.py:647 | メインウィンドウ・アプリ制御 |

### 依存ライブラリ

| ライブラリ | バージョン/配置 | 用途 |
|-----------|---------------|------|
| PyQt6 | >=6.4.0 | GUIフレームワーク |
| PyQt6-WebEngine | >=6.4.0 | HTML/Webレンダリング |
| marked.js | src/assets/js/ | Markdownパース |
| mermaid.js | src/assets/js/ | 図表レンダリング |
| highlight.js | src/assets/js/ | シンタックスハイライト |

## 変更時の参照ガイド

### 新機能を追加したい場合

1. [features.md](features.md) で既存機能を確認
2. [architecture.md](architecture.md) でデータフローを理解
3. [components.md](components.md) で該当クラスの仕様を確認

### UIを変更したい場合

1. [ui-style.md](ui-style.md) でスタイル定義を確認
2. `src/style.css` のCSS変数を参照
3. [components.md](components.md) の `_render_markdown()` を確認

### バグを修正したい場合

1. [components.md](components.md) で該当クラス・メソッドを特定
2. [features.md](features.md) で期待される動作を確認
3. [architecture.md](architecture.md) でデータフローを追跡

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2026-02-03 | 初版作成 |
| 2026-02-04 | マルチファイル形式対応、ファイルタイプバッジ、CDXML対応を追加 |
| 2026-02-05 | 行番号ガター(F16拡張)、ズーム(F17)、スクロール保持(F18)、バージョン管理を追加 |
