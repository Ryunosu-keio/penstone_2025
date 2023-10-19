
import glob
import numpy as np
import pandas as pd

csv = []
for i in range(18):
    try:
        path = "../data/integrate_emr_button_std/"+ str(i) + "_integrated_emr_button.csv"
        df = pd.read_csv(path)
        mean = df["timeFromDisplay"].mean()
        std_value = df["timeFromDisplay"].std()
        print(i,"平均",mean,"標準偏差",std_value)
        csv.append([i,mean,std_value])
    except:
        pass
df = pd.DataFrame(csv)
df
         
path = "../data/all_integrated_emr_button_removeNan.csv"
df = pd.read_csv(path)
print(df["timeFromDisplay"].std())


width = 1
df_1 = df[(df["diopter"] >= 1) & (df["diopter"] < 2)]["timeFromDisplay"]
df_2 = df[(df["diopter"] >= 2) & (df["diopter"] < 3)]["timeFromDisplay"]
df_3 = df[(df["diopter"] >= 3) & (df["diopter"] < 4)]["timeFromDisplay"]
df_4 = df[(df["diopter"] >= 4)]["timeFromDisplay"]
df_1 = df_1.reset_index(drop=True).to_frame("df_1")
df_2= df_2.reset_index(drop=True).to_frame("df_2")
df_3 = df_3.reset_index(drop=True).to_frame("df_3")
df_4 = df_4.reset_index(drop=True).to_frame("df_4")

# # %%

# %%
# 初期設定
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


path = "../data/all_integrated_emr_button_removeNan.csv"
df = pd.read_csv(path)

start = 1.5
end = 4
width = 1
dfs = {}
# 範囲の分割
ranges = [(round(i, 2), round(i + width, 2)) for i in np.arange(start, end + width, width)]
print("diopterの区切り", ranges)
dfs = {}
counter = 1

# 各範囲に対するデータフレームの作成
for lower_bound, upper_bound in ranges:
    
    # 最後の範囲の場合、上限を無限大に設定
    if upper_bound > end:
        upper_bound = np.inf
    
    # 条件に基づいてデータをフィルタリング
    column_name = "timeFromDisplay"
    current_df = df[(df["diopter"] >= lower_bound) & (df["diopter"] < upper_bound)][column_name]
    
    # インデックスをリセットしてデータフレームに追加
    dfs[f"df_{counter}"] = current_df.reset_index(drop=True).to_frame(f"df_{counter}")
    counter += 1

# dfs 内の全てのデータフレームを横方向に連結
result_df = pd.concat(dfs.values(), axis=1)
print(result_df.count())
result_df.hist(figsize=(10,7),bins=20)
plt.tight_layout()
plt.show()
result_df

result_df.to_csv("../data/approval/t_approval_1.5_4_0.5.csv")
# %%


# t検定
import matplotlib.pyplot as plt
from scipy import stats
import pandas as pd
import glob
import numpy as np

path = "../data/approval/mean_t_approval.csv"
df = pd.read_csv(path)

A = df["df_2"].values
A = [x for x in A if not np.isnan(x)]
B = df["df_3"].values
B = [x for x in B if not np.isnan(x)]

#まずは不偏分散を作ります。
A_var = np.var(A, ddof=1)
B_var = np.var(B, ddof=1)  

#自由度の算出
A_df = len(A) - 1
B_df = len(B) - 1

#F比
f = A_var / B_var


#片側検定のp値をそれぞれ調べる
one_sided_pval1 = stats.f.cdf(f, A_df, B_df)
one_sided_pval2 = stats.f.sf(f, A_df, B_df) 

#両側検定のp値は、片側検定のp値の小さい方を採用して2をかける
two_sided_pval = min(one_sided_pval1, one_sided_pval2) * 2

#出力用のフォーマット
print("F検定")
print('F:       ', round(f, 3))
print('p-value: ', round(two_sided_pval, 4))

t_stat,p_value = stats.ttest_ind(A, B, equal_var=True)
print("t検定")
print("t:",t_stat,"p:",p_value)

import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

# サンプルデータ生成

# 平均値計算
means = [np.mean(A), np.mean(B)]

# 95%信頼区間の計算
def compute_ci(data):
    ci = stats.t.interval(0.95, len(data)-1, loc=np.mean(data), scale=stats.sem(data))
    return (ci[1] - np.mean(data))

ci_values = [compute_ci(A), compute_ci(B)]

# 棒グラフの描画
labels = ['A', 'B']
x = np.arange(len(labels))
width = 0.35


fig, ax = plt.subplots()
rects1 = ax.bar(x, means, width, yerr=ci_values, capsize=5, label='Means', color=['blue', 'red'])

ax.set_ylabel('Values')
ax.set_title('Means with 95% confidence interval')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

fig.tight_layout()
plt.show()


#######################
plt.hist(A, bins=30, alpha=0.5, label='A')
plt.hist(B, bins=30, alpha=0.5, label='B')
plt.title(f't-statistic: {t_stat:.2f}\np-value: {p_value:.4f}')
plt.legend()
plt.show()


# %%
