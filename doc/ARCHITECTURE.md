## UIコンポーネント構成

```mermaid
classDiagram
    class App {
        +DATA_DIR: Path
        +INTERMEDIATE_DIR: Path
        +catalogue: Dict
        +name2smi: Dict
        +descriptor_store: DescriptorStore
        +id_registry: IdRegistry
        +def_store: PolymerDefinitionStore
        +rows: List~ResistRowWidget~
        +display()
        +save()
        +load_latest()
    }

    class PolymericDefBuilder {
        +catalogue: DataFrame
        +name2smi: Series
        +id_registry: IdRegistry
        +def_store: PolymerDefinitionStore
        +rows: List~PolymericDefRowWidget~
        +add_row()
        +on_register()
    }

    class PolymericDefRowWidget {
        +slots: List~Tuple~
        +mw_input: FloatText
        +pd_input: FloatText
        +on_click_register()
    }

    class ResistRowWidget {
        +categories: List
        +controls_by_category: Dict
        +descriptor_store: DescriptorStore
        +get_state() Dict
        +set_state(state)
        +refresh_properties()
    }

    class DescriptorStore {
        +name2smi: Dict
        +cache: Dict
        +get_by_smiles(smiles) Dict
    }

    class IdRegistry {
        +path: Path
        +assign(cat, key) str
        +load() Dict
        +save(reg)
    }

    class PolymerDefinitionStore {
        +path: Path
        +append(category, pid, signature, mw, mw_mn)
        +load_latest_map() Dict
    }

    App *-- PolymericDefBuilder : tab_polymer, tab_fpolymer
    App *-- ResistRowWidget : rows
    App --> DescriptorStore
    App --> IdRegistry
    App --> PolymerDefinitionStore

    PolymericDefBuilder *-- PolymericDefRowWidget : rows
    PolymericDefBuilder --> IdRegistry
    PolymericDefBuilder --> PolymerDefinitionStore

    ResistRowWidget --> DescriptorStore
    ResistRowWidget --> IdRegistry
    ResistRowWidget --> PolymerDefinitionStore
```

---

## ワークフローシーケンス

### アプリケーション起動

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant NB as Notebook
    participant App as App
    participant CDXML as cdxml_extract
    participant Util as util
    participant DS as DescriptorStore
    participant IR as IdRegistry

    User->>NB: launch_app("./")
    NB->>App: __init__(data_dir)
    App->>CDXML: cdxml_to_table(*.cdxml)
    CDXML-->>App: DataFrame {Name, SMILES}
    App->>Util: build_catalogue()
    Util-->>App: catalogue, name2smi
    App->>DS: DescriptorStore(name2smi)
    App->>IR: IdRegistry(path)
    IR->>IR: load()
    App->>App: ensure_styles()
    App-->>User: UIを表示
```

### レジスト配合設計

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant RW as ResistRowWidget
    participant DS as DescriptorStore
    participant Props as properties.py
    participant IR as IdRegistry

    User->>RW: 成分・比率を選択
    RW->>DS: get_by_smiles(smiles)
    DS-->>RW: {mw, k, op, logp, ...}
    RW->>Props: compute_properties(state)
    Props-->>RW: {k, op, mop, logp, p_p, tsc}
    RW->>RW: UI更新（計算結果表示）

    User->>RW: Save ボタン
    RW->>IR: assign(category, smiles)
    IR-->>RW: ID (P-1, A-1, ...)
    RW->>RW: CSV/CDXML出力
```

---

## 物性計算フロー

```mermaid
flowchart TD
    subgraph 入力
        SMILES[SMILES文字列]
    end

    subgraph mol_calculator.py
        MOL[RDKit Mol生成]
        MW[mw: 分子量]
        K[k_value_euv: EUV吸収]
        OP[op_value: Ohnishi]
        MOP[mop_value: Modified Ohnishi]
        VDW[vdw: Van der Waals体積]
        LOGP[logp: 疎水性]
    end

    subgraph 出力
        RESULT[物性値Dict]
    end

    SMILES --> MOL
    MOL --> MW
    MOL --> K
    MOL --> OP
    MOL --> MOP
    MOL --> VDW
    MOL --> LOGP

    MW --> RESULT
    K --> RESULT
    OP --> RESULT
    MOP --> RESULT
    VDW --> RESULT
    LOGP --> RESULT
```

---

## ワークフロー詳細

### 1. 起動

```python
from app_core import launch_app
app = launch_app("./")
```

1. CDXMLファイル読み込み（cdxml_to_table）
2. カタログ構築（build_catalogue）
3. 物性値キャッシュ初期化（DescriptorStore）
4. ID レジストリ読み込み（IdRegistry.load）
5. UI表示

### 2. ポリマー定義

1. PolymericDefBuilderウィジェットでモノマー比率を入力
2. Signatureを生成（例: "M-1=70;M-2=30"）
3. IdRegistryでIDを発行/取得
4. PolymerDefinitionStoreに保存

### 3. レジスト配合設計

1. ResistRowWidgetで成分と比率を選択
2. compute_properties()でリアルタイム計算
3. 結果をテーブル表示

### 4. 保存

1. App.save()を呼び出し
2. Result_YYMMDD/ディレクトリ作成
3. CSV出力（UTF-8 BOM）
4. ID付きCDXML出力

---

## トラブルシューティング

### CDXML読み込みエラー

**症状**: cdxml_to_tableがエラーを返す

**原因と対策**:
- グループ内にテキスト（名前）がない → CDXMLに名前を追加
- 化学構造が辞書参照のみ → 実体原子として描画
- XMLパースエラー → CDXMLを再保存

### ID重複

**症状**: 同じSMILESに異なるIDが発行される

**原因**: SMILES正規化の不整合

**対策**:
- `util.canonicalize_smiles()`を必ず使用
- id_registry.jsonを確認・修正

### 物性計算がNaN

**症状**: compute_propertiesがNaNを返す

**原因と対策**:
- SMILESが無効 → RDKitでパース確認
- 3D構造生成失敗（VdW計算） → 2D物性のみ使用
- 成分の重量が0 → 入力値を確認

### UI更新されない

**症状**: 値を変更しても表示が更新されない

**原因**: traitletの同期問題

**対策**:
- `observe()`のコールバック確認
- `with self.hold_trait_notifications():`で一括更新
