import pandas as pd
import os


def integrate_emr_answer(name, answer):

    # iを0から19までfor文で回す
    for i in range(20):
        # i.csvのパスを指定10
        csv_path = f"../data/emr_extracted2/{name}/{i}.csv"
        # 0825_rb_fd_i.xlsxのパスを指定
        df_extracted = pd.read_csv(csv_path)

        # if int(name) > 5:
        #     xlsx_path = f"../log/answers/{answer}_cleaned/{answer}_{i}_cleaned.csv"
        # else:
        #     xlsx_path = f"../log/answers/{answer}_cleaned/{answer}_{i}_cleaned.csv"
        xlsx_path = f"../log/answers/{answer}_cleaned/{answer}_{i}_cleaned.csv"
        df_answer = pd.read_csv(xlsx_path)
        print(df_answer)
        print(df_answer.columns)
        e = 0
        for j in range(len(df_answer)):
            drop_bool = True
            for k in range(len(df_extracted)):
                print(df_extracted["フレーム数"][k], df_answer["frame"][j-e])

                if abs(int(df_extracted["フレーム数"][k]) - int(df_answer["frame"][j-e])) < 300:
                    drop_bool = False
                    print("break")
                    break
                else:
                    pass
            if drop_bool:
                df_answer = df_answer.drop(index=j-e)
                df_answer = df_answer.reset_index(drop=True)
                e += 1
        df_answer = df_answer.reset_index(drop=True)
        df_extracted["frame"] = df_answer["frame"]
        # rename column "フレーム数" to "diopter
        df_extracted = df_extracted.rename(columns={"両眼.注視Z座標[mm]": "diopter"})
        df_extracted = df_extracted.reindex(
            columns=["frame", "フレーム数", "diopter"])
        df_answer = df_answer.drop(columns=["frame"])
        concat_df = pd.concat([df_extracted, df_answer], axis=1)
        if not os.path.exists(f"../data/integrated2/{name}"):
            os.mkdir(f"../data/integrated2/{name}")
        concat_df.to_csv(f"../data/integrated2/{name}/{i}.csv", index=False)

# 0824_rb_fd
# 0824_rb_fd
# 0824_rb_fd
# 0824_rb_fd
# 0824_rb_fd
# 0824_rb_fd
# 0825_rb_fd
# 0825_rb_fd
# 0825_rb_fd
# 0825_rb_fd
# 0831_1
# ono
# yu
# kyoka
# kozaki
# yuta
# ken


emr_answer_dict = {
    "2": "0824_rb_fd",
    "3": "0824_rb_fd",
    "4": "0824_rb_fd",
    "5": "0824_rb_fd",
    "8": "0825_rb_fd",
    "10": "0825_rb_fd",
    "11": "0831_1",
    "12": "ono",
    "13": "yu",
    "14": "kyoka",
    "15": "kozaki",
    "16": "yuta",
    "17": "ken",
}

if __name__ == "__main__":
    if not os.path.exists("../data/integrated"):
        os.mkdir("../data/integrated")
    name = input("被験者番号を入力してください: ")
    answer = input("使用したexcelファイルを入力してください: ")
    integrate_emr_answer(name=name, answer=answer)
