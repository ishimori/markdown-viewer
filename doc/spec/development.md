# 開発ガイド

## 環境構築

### 必要条件

- Python 3.10 以上
- pip（パッケージマネージャー）
- Git（バージョン管理）

### セットアップ手順

```bash
# 1. リポジトリをクローン
git clone <repository-url>
cd markdown-viewer

# 2. 仮想環境を作成・有効化
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# 3. 依存パッケージをインストール
pip install -r requirements.txt
```

### 依存パッケージ

```
# requirements.txt
PyQt6>=6.4.0
PyQt6-WebEngine>=6.4.0
```

## 起動方法

### 開発時

```bash
# 仮想環境を有効化後
python src/main.py

# 特定のファイルを開く
python src/main.py "path/to/file.md"
```

### バッチファイル

```batch
:: run.bat
@echo off
cd /d %~dp0
call .venv\Scripts\activate
python src/main.py %*
```

### Windows VBSスクリプト

```vbscript
' MarkdownViewer.vbs
' コンソールウィンドウを表示せずに起動
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "run.bat", 0, False
```

## ディレクトリ構成

```
markdown-viewer/
├── src/                    # ソースコード
│   ├── main.py            # メインアプリケーション
│   └── style.css          # UIスタイルシート
├── doc/                    # ドキュメント
│   ├── spec/              # 仕様書
│   └── sample.md          # サンプルファイル
├── .venv/                  # Python仮想環境（gitignore）
├── .vscode/                # VS Code設定
├── requirements.txt        # 依存パッケージ
├── pyproject.toml         # プロジェクト設定
├── run.bat                # 起動スクリプト
├── MarkdownViewer.vbs     # Windows起動用
└── .gitignore             # Git除外設定
```

## コーディング規約

### Python

- **スタイル**: PEP 8 準拠
- **インデント**: スペース4つ
- **最大行長**: 100文字
- **文字列**: ダブルクォート優先
- **命名規則**:
  - クラス: PascalCase (`MarkdownViewer`)
  - メソッド/変数: snake_case (`_setup_ui`, `folder_path`)
  - 定数: UPPER_SNAKE_CASE (`SESSION_DIR`)
  - プライベート: アンダースコアプレフィックス (`_load_css`)

### CSS

- **インデント**: スペース4つ
- **命名**: kebab-case (`--bg-color`, `.mermaid`)
- **変数**: CSS Custom Properties使用
- **単位**: px（絶対値）、em（相対値）

### コメント規約

```python
class MarkdownViewer(QMainWindow):
    """
    Markdownビューアのメインウィンドウ。

    タブ管理、ツールバー、キーボードショートカットを提供する。
    """

    def _setup_ui(self):
        """タブウィジェットとシグナルを初期化する。"""
        pass
```

## テスト

### 手動テスト項目

| テスト項目 | 確認内容 |
|-----------|---------|
| 起動 | アプリケーションが正常に起動する |
| ファイル読み込み | .mdファイルが正しく表示される |
| Mermaid | 図表が正しくレンダリングされる |
| タブ操作 | 作成/閉じる/切り替えが動作する |
| セッション | 終了→起動で状態が復元される |
| ショートカット | 全てのキーバインドが動作する |

### サンプルファイル

`doc/sample.md` を使用してテスト。以下を含む：

- 各レベルの見出し
- テーブル
- コードブロック
- 各種Mermaid図表

## トラブルシューティング

### よくある問題

#### PyQt6のインストールエラー

```bash
# pip を最新版にアップグレード
pip install --upgrade pip

# 再インストール
pip install PyQt6 PyQt6-WebEngine
```

#### Mermaidが表示されない

- インターネット接続を確認（CDNからロード）
- ブラウザキャッシュをクリア

#### セッションが復元されない

- `~/.markdown-viewer/session.json` の存在を確認
- JSONフォーマットエラーがないか確認

## デバッグ

### ログ出力

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Loading file: {file_path}")
```

### WebEngine DevTools

```python
# デバッグ用: DevToolsを有効化
from PyQt6.QtWebEngineWidgets import QWebEngineView
web_view.page().setDevToolsPage(QWebEnginePage())
```

## ビルド・配布

### PyInstaller（オプション）

```bash
pip install pyinstaller

pyinstaller --onefile --windowed \
    --name "MarkdownViewer" \
    --add-data "src/style.css;src" \
    src/main.py
```

## 変更履歴管理

### コミットメッセージ規約

```
<type>: <description>

[optional body]
```

**type:**
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント
- `style`: フォーマット変更
- `refactor`: リファクタリング
- `test`: テスト
- `chore`: その他

**例:**
```
feat: アウトラインのスクロール同期機能を追加

スクロール位置に応じて現在の見出しを
ハイライト表示するようにした。
```

## 拡張ガイドライン

### 新機能追加時

1. `doc/spec/features.md` に機能仕様を追加
2. 該当クラスに実装
3. `doc/spec/components.md` にメソッド仕様を追加
4. キーボードショートカットがあれば `_setup_shortcuts()` に追加

### UI変更時

1. `src/style.css` のCSS変数を確認・追加
2. `doc/spec/ui-style.md` にスタイル定義を追加
3. PyQt側のスタイルシートも必要に応じて更新

### 設定追加時

1. `SessionManager` に保存/復元ロジック追加
2. `doc/spec/architecture.md` の設定ファイル仕様を更新
