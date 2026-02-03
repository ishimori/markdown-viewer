# Markdown Viewer サンプル

これはMarkdown Viewerのサンプルファイルです。

## 基本的なMarkdown記法

### テキスト装飾

- **太字テキスト**
- *イタリック*
- ~~打ち消し線~~
- `インラインコード`

### リンクと画像

[GitHubへのリンク](https://github.com)

### 引用

> これは引用文です。
> 複数行にわたることもできます。

### コードブロック

```python
def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
```

### テーブル

| 名前 | 年齢 | 職業 |
|------|------|------|
| 田中 | 25 | エンジニア |
| 佐藤 | 30 | デザイナー |
| 鈴木 | 28 | マネージャー |

---

## Mermaid ダイアグラム

### フローチャート

```mermaid
flowchart TD
    A[開始] --> B{条件分岐}
    B -->|Yes| C[処理1]
    B -->|No| D[処理2]
    C --> E[終了]
    D --> E
```

### シーケンス図

```mermaid
sequenceDiagram
    participant U as ユーザー
    participant S as サーバー
    participant D as データベース

    U->>S: リクエスト送信
    S->>D: データ取得
    D-->>S: データ返却
    S-->>U: レスポンス返却
```

### クラス図

```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    class Dog {
        +String breed
        +bark()
    }
    class Cat {
        +String color
        +meow()
    }
    Animal <|-- Dog
    Animal <|-- Cat
```

### 円グラフ

```mermaid
pie title プログラミング言語の人気
    "Python" : 30
    "JavaScript" : 25
    "Java" : 20
    "C++" : 15
    "その他" : 10
```

---

## タスクリスト

- [x] Markdown対応
- [x] Mermaid対応
- [x] CSS装飾
- [x] TreeView表示
- [ ] ダークモード対応（将来の機能）

## 終わりに

このサンプルファイルでMarkdown ViewerのさまざまなMermaid図表が正しく表示されることを確認できます。
