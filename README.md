# Markdown Viewer

Windows 用の軽量 Markdown ビューア。フォルダを開いてファイルツリーから選ぶだけで、Markdown を即座にプレビューできます。Mermaid 図表もそのまま表示。

<!-- TODO: 実際のスクリーンショットに差し替える -->
![Screenshot](doc/screenshot.png)

---

## 特徴

- **フォルダベースのファイルブラウジング** - フォルダを開くとファイルツリーが表示され、クリックで即プレビュー
- **全文検索** - フォルダ内のファイルを横断検索。AND/OR・正規表現・ファイル名検索に対応
- **Mermaid 図表** - フローチャート、シーケンス図、ER図、ガントチャートなど 7 種類をレンダリング
- **タブ UI** - 複数ファイルをタブで切り替え。ドラッグで並べ替え可能
- **セッション自動保存** - 次回起動時に前回の状態（タブ、ファイル、ウィンドウ位置）を自動復元
- **ブックマーク & 最近のファイル** - よく使うファイルを登録。最近開いた 10 件も自動追跡
- **アウトライン** - 見出し構造からの目次表示＆ジャンプ
- **行番号ガター** - 行番号クリックでソースコピー。Shift+クリックで範囲選択
- **ファイルインスペクター** - 文字数・行数・見出し数などの統計情報を表示
- **マルチフォーマット対応** - XML、Python、CSV はシンタックスハイライト/テーブル表示。CDXML は化学構造式を SVG 描画
- **外部変更の自動検知** - 別エディタで編集したファイルを自動リロード

---

## インストール & 起動

**必要環境**: Windows 10/11, Python 3.10+

```bash
git clone <repository-url>
cd markdown-viewer
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

```bash
# 起動
run.bat
# または
python src/main.py

# ファイルを直接開く
python src/main.py "path/to/file.md"
```

---

## キーボードショートカット

| キー | 機能 |
|------|------|
| `Ctrl+O` | フォルダを開く |
| `Ctrl+W` | タブを閉じる |
| `Ctrl+Tab` / `Ctrl+Shift+Tab` | タブ切り替え |
| `Ctrl+F` | 検索にフォーカス |
| `Ctrl+B` | ブックマーク |
| `Ctrl+H` | 最近開いたファイル |
| `Ctrl+Shift+L` | サイドバー表示切替 |
| `Ctrl+Shift+O` | アウトライン表示切替 |
| `Ctrl+Shift+I` | インスペクター表示切替 |
| `Ctrl++` / `Ctrl+-` / `Ctrl+0` | ズーム |
| `F5` | 再読み込み |
| `F1` | ヘルプ |
| `ESC` | 戻る |

全ショートカットの詳細は `F1` のヘルプを参照してください。

---

## 技術スタック

| | |
|---|---|
| GUI | PyQt6 + WebEngine |
| Markdown | marked.js (GFM) |
| 図表 | mermaid.js |
| ハイライト | highlight.js |

---

## ドキュメント

- アプリ内ヘルプ: `F1` キーまたはツールバーの `?` ボタン
- 詳細仕様: [doc/spec/](doc/spec/index.md)

## ライセンス

MIT License
