import os
import pandas as pd

# ユーザーからのkの入力を受け取る
k = input("emr_extractedの下のディレクトリの数字を指定してください (2-10): ")
k = int(k)

# データフレームの初期化
df = pd.DataFrame(columns=["i", "emr", "answer","差分"])

# iを0から19までfor文で回す
for i in range(20):
    # i.csvのパスを指定
    csv_path = f"../data/emr_extracted/{k}/{i}.csv"
    # 0825_rb_fd_i.xlsxのパスを指定
    xlsx_path = f"../log/answers/0825_rb_fd/0825_rb_fd_{i}.xlsx"
    

    # ファイルが存在する場合、行数を取得
    if os.path.exists(csv_path):
        csv_df = pd.read_csv(csv_path)
        csv_rows = len(csv_df)
    else:
        csv_rows = 0
    
    if os.path.exists(xlsx_path):
        xlsx_df = pd.read_excel(xlsx_path, engine='openpyxl')
        xlsx_rows = len(xlsx_df)
    else:
        xlsx_rows = 0

    # データフレームに結果を追加
    df = df.append({"i": i, "emr": csv_rows, "answer": xlsx_rows,"差分": csv_rows - xlsx_rows}, ignore_index=True)


# 結果の表示
print(df)
