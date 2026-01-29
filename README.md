# penstone_2025 プロジェクト README

## 概要

瞳孔反応・輻輳調節（ディオプター）測定実験のためのプロジェクト。
画像刺激を提示して眼球運動を計測し、データを解析する。

---

## 実験用スクリプト（ルートディレクトリ）

### `main_master_3display_DFG.py`
**マスターデータ作成スクリプト**

- 刺激画像（original/brightonly/model）からマスター画像セットを生成
- 48試行分のシーケンスを設計（数字課題16個 + フィラー32個）
- 被験者ごとにシャッフルしたExcelを出力
- 画像処理（輝度・コントラスト・彩度調整）を適用

### `show_images_3display_fillerpicstd.py`
**実験提示スクリプト**

- 3画面構成（DISPLAY1: 前景文字, DISPLAY3: 背景画像）
- Excelからシーケンスを読み込み、試行を順次提示
- キー入力（t/b）を取得し、反応時間を計測
- 結果をCSVで `log/` に保存

---

## 分析パイプライン (`analysis/main_process/`)

```
1_devide_emrLog.py
       ↓
2_emr_extract_max2_by_logframe.py
       ↓
3_emr_calculate_metrics_and_graph_by_logframe.py
       ↓
4_integrate_metrics.py
       ↓
integrated_analysis.py
```

### `1_devide_emrLog.py`
EMRログを被験者・セグメントごとに分割

### `2_emr_extract_max2_by_logframe.py`
- EMRデータとログCSVをフレームで同期（merge_asof）
- `emr_diopter_peak` を計算（上昇停止検出）
- ページ分割プロットを生成

**出力**: `data/log_with_emr/{Bright|Dark}/{Subject}/`

### `3_emr_calculate_metrics_and_graph_by_logframe.py`
- タスクウィンドウ（baseline/miosis/peak）を決定
- 縮瞳率・ディオプターデルタを計算
- 4×16グリッドプロットを生成（マーカー付き）

**出力**: `data/log_with_emr_metrics/{params}/{Bright|Dark}/{Subject}/`

**グラフ**: `data/task_windows/{params}_markers/{Bright|Dark}/{Subject}/`

### `4_integrate_metrics.py`
被験者・条件ごとのCSVを統合Excelにマージ

**出力**: `data/log_with_emr_metrics/{params}/merged/integrated_{Bright|Dark}_metrics_n{N}.xlsx`

### `integrated_analysis.py`
統合データに対して統計解析・可視化

- z-score標準化（被験者内）
- IQR外れ値検出
- RM-ANOVA / One-way ANOVA
- 被験者間比較グラフ

**出力**: `data/statistics/{params}/n{N}_{options}/`

---

## 出力ディレクトリ構造 (`data/`)

```
data/
├── devided_emr/          # 分割済みEMR
├── log_with_emr/         # ログ+EMR同期済み
├── log_with_emr_metrics/ # 指標計算済み
│   ├── {params}/
│   │   ├── Bright/
│   │   ├── Dark/
│   │   └── merged/       # 統合Excel
├── task_windows/         # タスクウィンドウグラフ
│   └── {params}_markers/ # マーカー付きグラフ
├── graphs/               # ページプロット
└── statistics/           # 統計解析結果
    └── {params}/n{N}_{options}/
```

---

## パラメータサフィックス例

```
lag0p5_mioF10_BLstim120_markers
```

| 要素 | 意味 |
|------|------|
| `lag0p5` | miosis_lag_sec = 0.5 |
| `mioF10` | miosis_frames = 10 |
| `BLstim120` | baseline_mode = stim, 120フレーム |
| `markers` | マーカー付きプロット |

---

## 主要な指標

| 指標 | 説明 |
|------|------|
| `miosis_rate` | 縮瞳率 (baseline - min) / baseline |
| `diopter_delta` | ディオプター変化量 (peak - baseline) |
| `distance_mm` | 輻輳距離 (1000 / diopter) |
| `RT` | 反応時間（キー入力まで） |
| `miosis_RT` | 縮瞳反応時間（刺激から縮瞳開始まで） |
