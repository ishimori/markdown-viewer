# UI・スタイル仕様

## 全体レイアウト

```
┌──────────────────────────────────────────────────────────────────────┐
│ [Open] [New Tab] [Refresh] [Outline]       /path/to/file   Toolbar  │
├──────────────────────────────────────────────────────────────────────┤
│ Tab1 │ Tab2 │ Tab3 │                                  Tab Bar       │
├──────────────────────────────────────────────────────────────────────┤
│         │       │                                │                  │
│ File    │ Gutter│                                │  Outline         │
│ Tree    │ (Lines)│       Content Area            │  (ToC)           │
│         │       │                                │                  │
│─────────│       │                                │                  │
│ Stats   │       │                                │                  │
│ Panel   │       │                                │                  │
│         │       │                                │                  │
└─────────┴───────┴────────────────────────────────┴──────────────────┘
   250px    38px            可変幅                       220px
```

## カラーパレット

### CSS変数定義

```css
:root {
    /* 背景色 */
    --bg-color: #f8faff;
    --sidebar-bg: #f0f4f8;
    --code-bg: #f5f7fa;
    --table-header-bg: #e8f0fe;
    --table-row-alt: #f5f8ff;

    /* テキスト色 */
    --text-color: #1e3a5f;
    --heading-color: #0d47a1;
    --link-color: #1976d2;
    --code-color: #0d47a1;

    /* ボーダー・装飾 */
    --border-color: #d0e0f0;
    --heading-bar: #1976d2;
    --blockquote-border: #64b5f6;

    /* Mermaid */
    --mermaid-bg: #ffffff;
    --mermaid-border: #1976d2;
}
```

### 色の用途

| 変数名 | 色 | 用途 |
|--------|-----|------|
| --bg-color | #f8faff | ページ全体の背景 |
| --text-color | #1e3a5f | 本文テキスト |
| --heading-color | #0d47a1 | 見出し（H1-H6） |
| --link-color | #1976d2 | リンク |
| --border-color | #d0e0f0 | テーブル・ボックス境界線 |
| --heading-bar | #1976d2 | 見出しの左バー |

## タイポグラフィ

### フォント設定

```css
body {
    font-family: 'Segoe UI', 'Meiryo', sans-serif;
    font-size: 16px;
    line-height: 1.8;
    color: var(--text-color);
}

code, pre {
    font-family: 'Consolas', 'Source Code Pro', monospace;
}
```

### 見出しスタイル

| レベル | サイズ | 装飾 |
|--------|--------|------|
| H1 | 2.2em | 左バー + 背景 + 下線 |
| H2 | 1.8em | 左バー + 背景 |
| H3 | 1.5em | 左バー + 背景 |
| H4 | 1.3em | 左バー |
| H5 | 1.1em | 太字 |
| H6 | 1.0em | 太字 + グレー |

### 見出しCSS例

```css
h1 {
    font-size: 2.2em;
    color: var(--heading-color);
    border-bottom: 3px solid var(--heading-bar);
    padding: 15px 20px;
    padding-left: 20px;
    margin: 40px 0 25px 0;
    background: linear-gradient(to right, #e3f2fd, transparent);
    border-left: 5px solid var(--heading-bar);
}
```

## コンポーネントスタイル

### テーブル

```css
table {
    width: 100%;
    border-collapse: collapse;
    margin: 25px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border-radius: 8px;
    overflow: hidden;
}

th {
    background: var(--table-header-bg);
    color: var(--heading-color);
    font-weight: 600;
    padding: 14px 18px;
    text-align: left;
    border-bottom: 2px solid var(--border-color);
}

td {
    padding: 12px 18px;
    border-bottom: 1px solid var(--border-color);
}

tr:nth-child(even) {
    background: var(--table-row-alt);
}
```

### コードブロック

```css
pre {
    background: var(--code-bg);
    border: 1px solid var(--border-color);
    border-left: 4px solid var(--heading-bar);
    border-radius: 6px;
    padding: 18px;
    overflow-x: auto;
    margin: 20px 0;
}

code {
    font-family: 'Consolas', 'Source Code Pro', monospace;
    font-size: 0.95em;
}

/* インラインコード */
p code, li code {
    background: #e8f0fe;
    padding: 3px 8px;
    border-radius: 4px;
    color: var(--code-color);
}
```

### 引用ブロック

```css
blockquote {
    border-left: 4px solid var(--blockquote-border);
    background: #e3f2fd;
    margin: 20px 0;
    padding: 15px 25px;
    border-radius: 0 8px 8px 0;
    color: #1565c0;
}
```

### Mermaid図表

```css
.mermaid {
    background: var(--mermaid-bg);
    border: 2px solid var(--mermaid-border);
    border-radius: 12px;
    padding: 30px;
    margin: 30px 0;
    text-align: center;
    box-shadow: 0 4px 12px rgba(25, 118, 210, 0.15);
}
```

## レイアウト構造

### コンテンツ領域

```css
body {
    padding: 30px 280px 30px 50px;  /* right: サイドバー分の余白 */
}
```

### アウトライン（目次）

```css
#outline {
    width: 220px;
    min-width: 220px;
    background: var(--sidebar-bg);
    border-left: 1px solid var(--border-color);
    padding: 20px;
    position: fixed;
    right: 0;
    top: 0;
    bottom: 0;
    overflow-y: auto;
    transition: width 0.3s ease, min-width 0.3s ease;
}

#outline.hidden {
    width: 0;
    min-width: 0;
    padding: 0;
    overflow: hidden;
}

#outline h3 {
    color: var(--heading-color);
    font-size: 1.1em;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--heading-bar);
}

#outline ul {
    list-style: none;
    padding: 0;
}

#outline li {
    margin: 8px 0;
}

#outline a {
    color: var(--text-color);
    text-decoration: none;
    font-size: 0.9em;
    display: block;
    padding: 5px 10px;
    border-radius: 4px;
}

#outline a:hover,
#outline a.active {
    background: #e3f2fd;
    color: var(--link-color);
}

/* インデント */
#outline li.h2 { padding-left: 15px; }
#outline li.h3 { padding-left: 30px; }
#outline li.h4 { padding-left: 45px; }
```

## PyQt側スタイル

### ファイルツリー

```python
tree_view.setStyleSheet("""
    QTreeView {
        background: #f8faff;
        border: none;
        font-size: 13px;
    }
    QTreeView::item {
        padding: 8px;
        border-radius: 4px;
    }
    QTreeView::item:selected {
        background: #e3f2fd;
        color: #1976d2;
    }
    QTreeView::item:hover {
        background: #f0f4f8;
    }
""")
```

### 統計パネル

```python
stats_panel.setStyleSheet("""
    QWidget {
        background: #f0f4f8;
        border-top: 1px solid #d0e0f0;
    }
    QLabel {
        font-size: 12px;
        color: #1e3a5f;
        padding: 5px;
    }
""")
```

### タブウィジェット

```python
tabs.setStyleSheet("""
    QTabWidget::pane {
        border: 1px solid #90caf9;
        border-top: none;
    }
    QTabBar::tab {
        background: #f0f4f8;
        padding: 10px 20px;
        margin-right: 2px;
        border: 1px solid #90caf9;
        border-bottom: none;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        color: #5c6bc0;
    }
    QTabBar::tab:selected {
        background: #ffffff;
        color: #0d47a1;
        font-weight: bold;
        border-top: 3px solid #1976d2;
        border-bottom: 1px solid #ffffff;
    }
    QTabBar::tab:hover:!selected {
        background: #bbdefb;
    }
""")
```

#### アクティブタブのスタイル

| 項目 | 値 |
|------|-----|
| 上部ボーダー | 3px solid #1976d2 |
| 背景色 | #ffffff |
| テキスト色 | #0d47a1 |
| フォントウェイト | bold |
| 下部ボーダー | 1px solid #ffffff（ペインとの継ぎ目を隠す） |

非選択タブのホバー時: 背景 #bbdefb

## レスポンシブ対応

### 最小ウィンドウサイズ

```python
self.setMinimumSize(800, 600)
```

### スプリッター比率

```python
splitter.setSizes([250, 950])  # 左パネル: 250px, コンテンツ: 残り
```

## スクロールバー

```css
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: #f0f4f8;
}

::-webkit-scrollbar-thumb {
    background: #b0c4de;
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: #90a4c0;
}
```

## ガター（行番号）

HTMLテンプレート内のインラインCSSで定義。Markdownコンテンツの左側に固定表示される行番号領域。

### スタイル定義

| 要素 | スタイル |
|------|---------|
| `#gutter` | position: fixed; left: 0; top: 0; bottom: 0; width: 38px; background: #f0f4f8; border-right: 1px solid #90caf9; z-index: 10 |
| `#gutter-content` | position: relative |
| `.gutter-line` | position: absolute; width: 100%; text-align: right; padding-right: 6px; cursor: pointer; box-sizing: border-box |
| `.gutter-line:hover` | background: #e3f2fd; color: #1976d2 |
| `.gutter-line.selected` | background: #bbdefb; color: #1565c0 |
| `.gutter-line.heading` | font-weight: bold; color: #1976d2 |

### フォント

```css
font-family: 'SFMono-Regular', 'Consolas', 'Liberation Mono', monospace;
font-size: 11px;
color: #90a4ae;
```

### body調整

ガター表示時はbodyに左マージンを追加：

```css
body {
    margin-left: 42px;
    padding-left: 25px;
}
```

## コピートースト通知

ガタークリックによるコピー成功時に表示されるフィードバック通知。

| 項目 | 値 |
|------|-----|
| 位置 | 画面下部中央 (fixed, bottom: 20px, left: 50%, transform: translateX(-50%)) |
| 背景色 | rgba(13, 71, 161, 0.9) |
| テキスト色 | white |
| 角丸 | 6px |
| フォントサイズ | 12px |
| パディング | 8px 20px |
| アニメーション | opacity 0.3s, transform 0.3s |
| 表示時間 | 1.5秒 |

## 目次内行番号

アウトラインサイドバーの各見出し項目に表示されるソース行番号。

| 項目 | 値 |
|------|-----|
| フォントサイズ | 9px |
| テキスト色 | #9e9e9e |
| フォント | SFMono-Regular, Consolas, monospace |
| 表示形式 | "L42" のように行番号の前に "L" を付与 |
