# プロジェクト概要

## 基本情報

| 項目 | 内容 |
|------|------|
| プロジェクト名 | Markdown Viewer |
| 種別 | Windows デスクトップアプリケーション |
| 言語 | Python 3.10+ |
| ライセンス | - |
| リポジトリ | ローカル |

## 目的

技術ドキュメントや Mermaid 図表を含む Markdown ファイルを、美しく読みやすい形式で表示するビューアアプリケーション。

### 解決する課題

- Markdown ファイルの視覚的なプレビュー
- Mermaid ダイアグラムのリアルタイムレンダリング
- 複数ファイルの同時閲覧（タブUI）
- 作業状態の維持（セッション管理）

## 技術スタック

### ランタイム

```
Python 3.10+
├── PyQt6 >=6.4.0          # GUIフレームワーク
└── PyQt6-WebEngine >=6.4.0 # Chromiumベースのレンダリング
```

### フロントエンド（WebEngine内）

```
Local Libraries (src/assets/)
├── marked.js              # Markdownパーサー
├── mermaid.js             # 図表レンダリング
└── highlight.js           # シンタックスハイライト
```

### 開発環境

```
Tools
├── Python venv            # 仮想環境
├── hatchling              # ビルドシステム
└── VS Code                # 推奨IDE
```

## 主要機能一覧

| 機能 | 説明 | 関連クラス |
|------|------|-----------|
| Markdown表示 | .md/.markdownファイルのHTML変換・表示 | `MarkdownViewer` |
| Mermaid対応 | フローチャート・シーケンス図等のレンダリング | `_render_markdown()` |
| マルチファイル形式 | XML/Python/CSV/CDXML等の表示 | `_render_code()`, `_render_csv()`, `_render_cdxml()` |
| タブUI | 複数ファイルの同時閲覧 | `FolderTab` |
| ファイルツリー | フォルダ内ファイルの階層表示・タイプバッジ | `FolderTab`, `FileTypeIconModel` |
| 目次表示 | 見出しからの自動目次生成 | `_render_markdown()` |
| 行番号ガター | ソース行番号の表示・クリックでコピー | `_render_markdown()` |
| ズーム | コンテンツ表示倍率の変更 | `MarkdownViewer` |
| セッション管理 | ウィンドウ状態・開いたファイルの保存・復元 | `SessionManager` |
| 統計情報 | 行数・文字数・読了時間の表示 | `update_stats()` |

## 対応ファイル形式

### 入力

- `.md`, `.markdown` - Markdown ファイル
- `.xml`, `.xsl`, `.xslt`, `.xsd`, `.svg` - XMLファイル
- `.py`, `.pyw` - Pythonファイル
- `.csv` - CSVファイル
- `.cdxml` - ChemDraw化学構造ファイル

### Mermaid 対応図表

| 図表タイプ | 記法例 |
|-----------|--------|
| フローチャート | `graph TD` / `graph LR` |
| シーケンス図 | `sequenceDiagram` |
| クラス図 | `classDiagram` |
| 状態図 | `stateDiagram-v2` |
| ER図 | `erDiagram` |
| 円グラフ | `pie` |
| ガントチャート | `gantt` |

## 動作環境

### 必須要件

- Windows 10/11
- Python 3.10 以上
- 画面解像度: 1024x768 以上推奨

### オプション

- インターネット接続は不要（ライブラリはすべてローカルにバンドル済み）

## 制限事項

| 項目 | 内容 |
|------|------|
| ファイル監視 | 外部変更の自動検出なし（F5で手動更新） |
| 編集機能 | 読み取り専用（編集不可） |
| マルチインスタンス | セッションファイル競合の可能性あり |
| 文字コード | UTF-8 のみ対応 |
