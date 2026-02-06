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
│   ├── version.txt        # バージョン番号
│   ├── style.css          # UIスタイルシート
│   ├── assets/            # 静的アセット
│   │   ├── css/
│   │   │   └── highlight-github.css  # シンタックスハイライトCSS
│   │   └── js/
│   │       ├── marked.min.js         # Markdownパーサー
│   │       ├── mermaid.min.js        # 図表ライブラリ
│   │       └── highlight.min.js      # シンタックスハイライト
│   └── templates/
│       └── markdown.html  # HTMLテンプレート
├── scripts/                # ビルド・ユーティリティ
│   ├── build.bat          # ビルドスクリプト
│   ├── increment_version.py # バージョン自動インクリメント
│   └── markdown_viewer.spec # PyInstallerスペックファイル
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
  - プライベート: アンダースコアプレフィックス (`_load_resources`)

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
| マルチフォーマット | XML/Python/CSV/CDXMLファイルが正しく表示される |
| Mermaid | 図表が正しくレンダリングされる |
| タブ操作 | 作成/閉じる/切り替えが動作する |
| セッション | 終了→起動で状態が復元される |
| ショートカット | 全てのキーバインドが動作する |
| 行番号ガター | 行番号が正しく表示され、クリックでコピーされる |
| ズーム | Ctrl++/-/0 でコンテンツの拡大・縮小・リセットが動作する |
| スクロール保持 | F5 でリフレッシュ後、スクロール位置が復元される |
| バージョン表示 | タイトルバーにバージョン番号が表示される |

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

- `src/assets/js/mermaid.min.js` が存在するか確認
- ファイルが破損していないか確認

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

## バージョン管理

### バージョンファイル

| 項目 | 値 |
|------|-----|
| ファイル | `src/version.txt` |
| 形式 | 浮動小数点数（例: `1.0`） |
| デフォルト値 | ファイル未存在時は `0.0` |

### バージョン自動インクリメント

ビルド時に `scripts/increment_version.py` が自動実行され、バージョン番号を0.1ずつ増加させる。

| 項目 | 説明 |
|------|------|
| スクリプト | `scripts/increment_version.py` |
| 増分 | +0.1 |
| 呼び出し元 | `scripts/build.bat` |
| エラー時 | バージョン形式が不正な場合、1.0にリセット |

### タイトルバー表示

| 実行環境 | 表示例 |
|---------|--------|
| PyInstaller実行ファイル | `Markdown Viewer v1.0` |
| Python直接実行 | `Markdown Viewer v1.0 [Python]` |

### 実装

`get_version_info()` 関数が `src/version.txt` を読み込み、`sys.frozen` 属性で実行モードを判定する。

## ビルド・配布

### ビルド手順

`scripts/build.bat` を使用してビルドする。バージョン番号の自動インクリメントとPyInstallerによるexe生成を行う。

```batch
:: scripts/build.bat
@echo off
cd /d "%~dp0\.."

REM バージョン番号をインクリメント
.venv\Scripts\python.exe scripts\increment_version.py

REM PyInstallerをインストール（未インストールの場合）
.venv\Scripts\python.exe -m pip install pyinstaller

REM exe をビルド
.venv\Scripts\python.exe -m PyInstaller scripts\markdown_viewer.spec --noconfirm
```

### PyInstaller スペックファイル

`scripts/markdown_viewer.spec` にビルド設定を定義。リソースファイル（CSS, JS, HTML, version.txt）を含む。

### リソースパス解決

PyInstaller でビルドされた実行ファイルでは、リソースファイルのパスが異なる。`get_resource_path()` 関数で対応。

```python
def get_resource_path(relative_path: str) -> Path:
    """PyInstaller対応のリソースパス解決"""
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent
    return base_path / relative_path
```

| 環境 | パス |
|------|------|
| 開発時 | `src/style.css` |
| PyInstaller | `{_MEIPASS}/src/style.css` |

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
