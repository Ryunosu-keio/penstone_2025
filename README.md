# penstone
## 使い方
1. client側（電子ミラー出力側）のPCでmain.pyを実行
2. エクセルファイルと画像が出てくるのを待つ
3. git に merge する
4. server側（フロントディスプレイ側）のPCで最新を git merge する
5. server側で show_images_front.py を実行し、使用するファイル名、白黒どちらかを選択する
6. client側で show_images_back.py を実行し、使用するファイル名を入力する
7. 実験開始
## ファイル説明
- back_rate.py・・・ミラー側の画像の順番や変換パラメータを決め、実験リストとして出力している
- change_rawImage.py・・・不明
- create_edited_photo.py・・・画像をパラメータに応じて変換する
- create_experiment_list・・・ランダムで実験リストを作成する（現在は使っておらず、backrateで対応している）
- create_photos_fromlist.py・・・実験リストから画像を変換し、出力している
- front_rate・・・フロントディスプレイ側の実験リスト（エクセルファイル）を出力している
- log.txt・・・ログを出力している
- main.py・・・back_rateとcreate_photos_fromlistを実行し、実験リストと実験時に使用する画像を作成している。一度の実験で利用する画像の数などを変えられる
- requirements.txt・・・いつもの pip install -r requirements.txtで環境作る
- show_images_back.py・・・クライアント側（ミラー側）で実行するファイル
- show_images_front.py・・・サーバ側（フロントディスプレイ側）で実行するファイル
## ディレクトリ説明
### analysis
各種分析ファイル
- log_cleaner・・・ログを綺麗にする
### histgram
輝度のヒストグラムが入っているレガシーデータ
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
