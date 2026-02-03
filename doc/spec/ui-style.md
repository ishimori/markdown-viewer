# UI・スタイル仕様

## 全体レイアウト

```
┌─────────────────────────────────────────────────────────────────┐
│ [Open] [New Tab] [Reload] [Outline]              Toolbar        │
├─────────────────────────────────────────────────────────────────┤
│ Tab1 │ Tab2 │ Tab3 │                             Tab Bar        │
├─────────────────────────────────────────────────────────────────┤
│         │                                      │                │
│ File    │                                      │  Outline       │
│ Tree    │           Content Area               │  (ToC)         │
│         │                                      │                │
│─────────│                                      │                │
│ Stats   │                                      │                │
│ Panel   │                                      │                │
│         │                                      │                │
└─────────┴──────────────────────────────────────┴────────────────┘
     250px              可変幅                        250px
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
.container {
    display: flex;
    max-width: 100%;
}

#content {
    flex: 1;
    padding: 30px 50px;
    max-width: calc(100% - 250px);
    overflow-y: auto;
}
```

### アウトライン（目次）

```css
#outline {
    width: 250px;
    min-width: 250px;
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
file_tree.setStyleSheet("""
    QTreeWidget {
        background: #f8faff;
        border: none;
        font-size: 13px;
    }
    QTreeWidget::item {
        padding: 8px;
        border-radius: 4px;
    }
    QTreeWidget::item:selected {
        background: #e3f2fd;
        color: #1976d2;
    }
    QTreeWidget::item:hover {
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
        border: none;
    }
    QTabBar::tab {
        background: #f0f4f8;
        padding: 10px 20px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }
    QTabBar::tab:selected {
        background: #ffffff;
        color: #1976d2;
        font-weight: bold;
    }
""")
```

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
