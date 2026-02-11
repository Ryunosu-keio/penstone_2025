# penstone_2025 プロジェクト README

## 概要

瞳孔反応・輻輳調節（ディオプター）測定実験のためのプロジェクト。
画像刺激を提示して眼球運動を計測し、データを解析する。

---

## 実験用スクリプト（ルートディレクトリ）

### `exp_create_images_izm.py`
**刺激画像生成スクリプト**

- 元画像ディレクトリをスキャンして自動取得（枚数任意）
- 被験者ごとに独立して画像・パラメータをランダム生成（48試行/セット）
- 画像処理（輝度・コントラスト・ガンマ・シャープネス・CLAHE）を適用
- Excel + 加工済み画像を出力

#### 実験前に設定する変数

| 変数 | 行 | 説明 |
|------|-----|------|
| `SEED` | L34 | 乱数シード（None=ランダム / 整数=固定） |
| `N_SETS` | L35 | 1被験者あたりのセット数 |
| `N_SUBJECTS` | L36 | 1条件あたりの被験者数 |
| `SUBJECT_PREFIX` | L37 | 被験者IDの接頭辞（例: "S"） |
| `TARGET_SIZE` | L39 | 出力画像サイズ (幅, 高さ) px |
| `N_TRIALS` / `N_DIGIT` / `N_FILLER` | L44-46 | 1セットの試行数（数字/フィラー配分） |
| `DEFAULT_DRIVE` | L56 | 画像出力先のドライブ文字 |
| `DEFAULT_SOURCE_BRIGHT` / `DARK` | L57-58 | 元画像ディレクトリパス |
| `ADJUST_PARAMS` | L64-69 | 画像加工パラメータのレンジ辞書（brightness, contrast, gamma, sharpness, equalization） |
| `LETTERS` | L282 | フィラー試行の front に使うアルファベット一覧 |
| `DIGITS` | L283 | 数字試行の front/back に使う数字一覧 |

---

### `exp_show_images_izm.py`
**実験提示スクリプト**

- マルチディスプレイ構成（DISPLAY1: 前景文字, DISPLAY2: 背景画像）
- Excelからシーケンスを読み込み、試行を順次提示
- キー入力（t: match / f: mismatch）で反応を取得、反応時間を計測
- 結果をCSVで `log/` に保存

#### 実験前に設定する変数

| 変数 | 行 | 説明 |
|------|-----|------|
| `TRIAL_SEC` | L39 | 1試行の提示秒数（例: 2.5） |
| `USE_FILLER_FIXED_IMAGE` | L51 | フィラー試行で固定画像を使うか（True=固定画像 / False=通常画像） |
| `TARGET_KEY_MAP` | L253 | 正解キーの対応（Match→"t", Mismatch→"f"） |
| `keyboard.on_press_key(...)` | L401-402 | 受け付けるキーの登録（TARGET_KEY_MAPと一致させる） |
| `get_display_rect(1)` / `(2)` | L428-429 | 使用するディスプレイ番号（環境に合わせて変更） |

---

## 分析パイプライン概要 (`analysis/main_process/`)

解析は大きく分けて「前処理・同期」「メトリクス算出・統合」「統計・可視化」の3フェーズで行われます。

```text
[1_divide_emrLog.py] (EMRデータの分割)
       │
       ▼
[2_log_integrate_preprocess_graph_series.py] (ログ同期・前処理)
       │
       ▼
[3_log_add_metrics_graph_window.py] (指標算出・データ統合) ★重要
       │
       ├─[5_integrated_analysis.py] (統計解析・グラフ作成)
       │
       ├─[6_prepare_grid_data.py] (3D/グリッド用データ整形)
       │      └─▶ [graph_grid/ フォルダ] (専門的な3D可視化)
       │
       └─ (4_graph_series_window_combined.py) ※確認用プロット結合
```

---

## 各スクリプトの詳細

### Phase 1: 前処理・同期

#### `1_divide_emrLog.py`
EMRログを被験者・セグメント（各ブロック）ごとに分割します。
- **入力**: `data/emr/` (生データ)
- **出力**: `data/devided_emr/`

#### `2_log_integrate_preprocess_graph_series.py`
EMRデータの前処理（Hampelフィルタ、平滑化等）を行い、実験ログとフレーム単位で同期します。
- **入力**: 実験ログCSV + `1_` の分割済みEMR CSV
- **同期**: `merge_asof` によるフレーム同期
- **出力**: `data/log_with_emr/`

---

### Phase 2: メトリクス算出・自動統合

#### `3_log_add_metrics_graph_window.py` (重要ステップ)
タスクウィンドウ（静止/縮瞳/ピーク）を自動決定し、各種指標（縮瞳率、ディオプター変化量等）を算出します。
全被験者の処理が終わると、**自動的に全データを1つのExcelファイルに統合**します。

- **指標内容**: `miosis_rate`, `diopter_delta`, `pupil_*` 等多数
- **可視化**: 4段連結プロット + 4×16グリッドプロット（マーカー付き）
- **出力**: `data/log_with_emr_metrics/` および `.../merged/integrated_*_metrics_n{N}.xlsx`

#### `4_graph_series_window_combined.py` (ユーティリティ)
`2_` の全体プロットと `3_` の詳細グリッドプロットを1枚の画像に統合します（目視確認用）。

---

### Phase 3: 統計解析・詳細可視化

#### `5_integrated_analysis.py`
統合されたExcelデータに対して統計解析と論文・報告用のグラフ作成を行います。
- **処理**: z-score標準化、外れ値除去、RM-ANOVA等
- **入力**: `3_` が出力した `merged/` 内のExcel

#### `6_prepare_grid_data.py`
統合データを `graph_grid` スクリプトが読み込める形式（5パラメータ展開済み）に変換します。
- **出力**: `data/merged_for_grid/{パラメータフォルダ}/{Bright|Dark}/`

#### `graph_grid/` 内のスクリプト
特定のグリッド位置での平均プロットや、3D空間内での反応分布を可視化します。
- **主要スクリプト**: `graph.py` (平均波形), `graph_3d_grid_average_count.py` (3Dグリッド)

---

## 出力ディレクトリ構造 (`data/`)

```
data/
├── emr/                  # EMRログ(生データ)
├── devided_emr/          # 分割済みEMR
├── log_with_emr/         # ログ+EMR同期済み (series プロット)
├── log_with_emr_metrics/ # 指標計算済み (window プロット)
│   ├── {params}/         # パラメータセット（lag, frames 等）
│   │   ├── Bright/       # 被験者ごとのCSV
│   │   ├── Dark/
│   │   └── merged/       # 統合済みExcel (5_ や 6_ の入力)
├── task_windows_combined/# 2_ と 3_ の統合プロット
├── merged_for_grid/      # 3D/グリッド可視化用変換済みデータ
└── statistics/           # 統計解析結果 (5_ の出力)
```




---

## 出力ディレクトリ構造 (`data/`)

```
data/
├── emr/                  # EMRログ(生データ)
├── devided_emr/          # 分割済みEMR
├── log_with_emr/         # ログ+EMR同期済み
├── log_with_emr_metrics/ # 指標計算済み
│   ├── {params}/
│   │   ├── Bright/
│   │   ├── Dark/
│   │   └── merged/       # 統合Excel
├── task_windows/         # タスクウィンドウグラフ(window)
│   └── {params}_markers/ # マーカー付きグラフ
├── graphs/               # ページプロット(series)
├── merged_for_grid/       # graph_grid用変換済みデータ

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

## EMR デバイス依存の列名（変数化）

EMR CSV に含まれる日本語列名は **各スクリプトの先頭で定数として定義** しており、
EMR-10 以外の機種に切り替える場合はこの定数だけ変更すればOKです。

| 変数名 | デフォルト値 | 使用ファイル |
|--------|-------------|-------------|
| `EMR_COL_CUE` | `"CUEスイッチ"` | `1_divide_emrLog.py` |
| `EMR_COL_FRAME` | `"番号"` | `2_...graph_series.py`, `3_...graph_window.py`, `graph_grid/graph.py` |
| `EMR_COL_LEFT_PUPIL` | `"左眼.瞳孔径[mm]"` | `2_...graph_series.py`, `3_...graph_window.py` |
| `EMR_COL_RIGHT_PUPIL` | `"右眼.瞳孔径[mm]"` | `2_...graph_series.py`, `3_...graph_window.py` |
| `EMR_COL_BOTH_Z` | `"両眼.注視Z座標[mm]"` | `2_...graph_series.py`, `3_...graph_window.py`, `graph_grid/graph.py` |
| `EMR_REQUIRED_COLS` | 上記4列のリスト | `2_...graph_series.py`, `3_...graph_window.py` |

> **Note**: `4_`, `5_`, `6_` および `graph_grid/` の3Dプロット系スクリプトは
> 前処理済みの `emr_*` 列（英字名）のみを参照するため、EMR列名変数は不要です。

---

## 主要な指標

| 指標 | 説明 |
|------|------|
| `miosis_rate` | 縮瞳率 (baseline - min) / baseline |
| `diopter_delta` | ディオプター変化量 (peak - baseline) |
| `distance_mm` | 輻輳距離 (1000 / diopter) |
| `RT` | 反応時間（キー入力まで） |
| `miosis_RT` | 縮瞳反応時間（刺激から縮瞳開始まで） |
