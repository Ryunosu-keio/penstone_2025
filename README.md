# penstone

## 使い方

1. client側（電子ミラー出力側）のPCでmain.pyを実行
2. エクセルファイルと画像が出てくるのを待つ
3. git に merge する
4. server側（フロントディスプレイ側）のPCで最新を git merge する
5. server側で show_images_front.py を実行し、使用するファイル名、白黒どちらかを選択する
6. client側で show_images_back.py を実行し、使用するファイル名を入力する
7. 実験開始

## 分析手順

### emrの処理

1. data/emrにemr-10のログを入れる
2. **devide_emrLog.py**を実行し、data/emrに出力されたcsvファイルをdata/devided_emrに保存する
3. **graph_10ko.py**を実行し、出力されたグラフからキャリブレーションごとの最大値最小値をメモする.
必要があれば**graph.py**で細かく確認し、出力されたグラフからタスクごとの最大値最小値をメモする.
4. **emr_extract_max2.py**を実行し、data/devided_emrに出力されたcsvファイルをdata/emr_extractedに保存する

### パラメータ情報の処理

1. **log_cleaner_answer.py**の中にあるuse_foldersを書き使ったものに書き換える
2. **log_cleaner_answer.py**を実行しimageCreationExcel/back/に生成されたexcelファイルを4以外を抽出しパラメータごとに分けて、log/answers/○○_cleaned/○○_cleaned.csvとして保存する

### パラメータと焦点深度の統合

1. log/answers/○○_cleaned/○○_cleaned.csvとdata/emr_extracted/それぞれにファイルが入っていることを確認する
2. **integrate_emr_answer.py**を実行し、data/integratedに出力される
3. 2 を全ての被験者に対して行う。
4. 全てのログに対して、フレーム数のずれがないか確認する。ある場合は手動で修正する。ミラーを見ている時のデータ点が4点以下だと取得されない
5. **integrate_adjust.py**を実行し、被験者ごとの同じ画像に対する差異を調整する。data/integrated_adjust_allに出力される。（4で取得されなかったデータは削除しないとNanになる？）
6. 被験者全てのデータを統合する。**integrate_participants.py**を実行し、data/final_part1に出力される。

## ファイル説明

- back_rate.py・・・ミラー側の画像の順番や変換パラメータを決め、実験リストとして出力している
- change_rawImage.py・・・ミラー側の画像の縦横比を電子ミラーの形に合わせる。暗所ライトの画像の場合更に左右反転
- create_edited_photo.py・・・画像をパラメータに応じて変換する
- create_photos_fromlist.py・・・実験リストから画像を変換し、出力している
- front_rate・・・フロントディスプレイ側の実験リスト（エクセルファイル）を出力している
- log.txt・・・ボタン押下のログを出力している
- main.py・・・back_rateとcreate_photos_fromlistを実行し、実験リストと実験時に使用する画像を作成している。一度の実験で利用する画像の数などを変えられる
- requirements.txt・・・いつもの pip install -r requirements.txtで環境作る
- show_images_back.py・・・クライアント側（ミラー側）で実行するファイル
- show_images_front.py・・・サーバ側（フロントディスプレイ側）で実行するファイル

## ディレクトリ説明

### analysis

各種分析ファイル
emr-10のログのクリーニング

- devide_emrLog.py・・・emr-10から取り出したcsvファイルを20タスクに切り分ける
- emr_extract_max2・・・ミラーを見た時のz座標を一つに決める。（input(下限)～input(上限)の値のうち上位90％の平均値を代表値とする。）
ディオプターのグラフ化
- graph.py・・・各被験者のタスクごとのディオプター変化
- graph_10ko.py・・・各被験者のキャリブレーションごとのディオプター変化
- graph_ed_grid.py・・・変数の変域で、5変数のうち変えている3変数を選んで順番に図示
ボタンログのクリーニング
- log_cleaner・・・ログを綺麗にする

### imageCreationExcel

実験用のexcelファイル

- back・・・ミラー側に出力する画像データ
- front・・・50インチ大型ディスプレイに表示するデータ

### library

画像変換等に使われているデータを格納

- Photo_Parameters_2・・・全パラメータの変換関数
- cor&cor2・・・画像をまとめて相関係数行列のように表示するプログラム
- histogram・・・ヒストグラム作成関数
- tools・・・不明

### testpic

もう使用しない画像データ

### testpic_yobi

使用している画像の加工前データ

### testpic_yobi_transformed

使用している画像の加工後データ

### testprograms

テストで使ったプログラム
