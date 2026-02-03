# Markdown Viewer

Mermaid ダイアグラム対応の Windows 用 Markdown ビューアアプリケーション。

## 特徴

- **Markdown レンダリング** - GitHub Flavored Markdown 対応
- **Mermaid 図表** - フローチャート、シーケンス図、クラス図などを表示
- **タブ UI** - 複数ファイルを同時に開ける
- **目次（アウトライン）** - 見出しから自動生成、クリックでジャンプ
- **セッション管理** - ウィンドウ状態・開いたファイルを自動保存・復元
- **統計情報** - 行数、文字数、読了時間を表示

## スクリーンショット

```
┌─────────────────────────────────────────────────────────────┐
│ [Open] [New Tab] [Reload] [Outline]                         │
├─────────────────────────────────────────────────────────────┤
│ Doc1.md │ Doc2.md │                                         │
├─────────┬───────────────────────────────────────┬───────────┤
│ Files   │                                       │ Outline   │
│ ─────── │  # Document Title                     │ ───────── │
│ doc1.md │                                       │ > Title   │
│ doc2.md │  Content here...                      │   Section │
│         │                                       │   ...     │
│─────────│  ```mermaid                          │           │
│ Stats   │  graph TD                             │           │
│ Lines:  │    A --> B                            │           │
│ Words:  │  ```                                  │           │
└─────────┴───────────────────────────────────────┴───────────┘
```

## 必要要件

- Windows 10/11
- Python 3.10 以上

## インストール

```bash
# リポジトリをクローン
git clone <repository-url>
cd markdown-viewer

# 仮想環境を作成・有効化
python -m venv .venv
.venv\Scripts\activate

# 依存パッケージをインストール
pip install -r requirements.txt
```

## 使い方

### 起動

```bash
# バッチファイルで起動
run.bat

# または直接実行
python src/main.py

# 特定のファイルを開く
python src/main.py "path/to/file.md"
```

### キーボードショートカット

| キー | 機能 |
|------|------|
| Ctrl+T | 新しいタブ |
| Ctrl+W | タブを閉じる |
| Ctrl+O | フォルダを開く |
| Ctrl+Tab | 次のタブ |
| Ctrl+Shift+Tab | 前のタブ |
| Ctrl+Shift+O | アウトライン表示切替 |
| F5 | 再読み込み |

## 対応 Mermaid 図表

| 図表 | 記法 |
|------|------|
| フローチャート | `graph TD` / `graph LR` |
| シーケンス図 | `sequenceDiagram` |
| クラス図 | `classDiagram` |
| 状態図 | `stateDiagram-v2` |
| ER図 | `erDiagram` |
| 円グラフ | `pie` |
| ガントチャート | `gantt` |

## ドキュメント

詳細な仕様は [doc/spec/](doc/spec/index.md) を参照してください。

| ドキュメント | 内容 |
|-------------|------|
| [仕様書インデックス](doc/spec/index.md) | 仕様書の目次・概要 |
| [プロジェクト概要](doc/spec/overview.md) | 目的・技術スタック |
| [アーキテクチャ](doc/spec/architecture.md) | システム構成・データフロー |
| [コンポーネント](doc/spec/components.md) | クラス・メソッド仕様 |
| [機能仕様](doc/spec/features.md) | 機能一覧・動作詳細 |
| [UIスタイル](doc/spec/ui-style.md) | デザイン・カラー定義 |
| [開発ガイド](doc/spec/development.md) | 環境構築・規約 |

## 技術スタック

- **GUI**: PyQt6 + WebEngine
- **Markdown**: marked.js
- **図表**: mermaid.js

## ライセンス

---

## 作者

