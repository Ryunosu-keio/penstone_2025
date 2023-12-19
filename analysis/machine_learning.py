#%%
import pandas as pd
from sklearn.model_selection import train_test_split
import lightgbm as lgb
from sklearn.metrics import mean_squared_error
import joblib

# データの読み込み
# data = pd.read_excel("../data/final_part2/darkfinal_modified.xlsx")
data = pd.read_excel("../data/final_part2/add_contrast_max.xlsx")

# 特徴量とターゲットの分離
X = data[['gamma', 'contrast', 'sharpness', 'brightness', 'equalization','mode_brightness','max_brightness']]
y = data['diopter']

# データの分割
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# LightGBMモデルの構築
model = lgb.LGBMRegressor()
model.fit(X_train, y_train)

# モデルの評価
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f'Mean Squared Error: {mse}')

# モデルの保存
joblib.dump(model, 'diopter_prediction_model.pkl')
# LightGBMモデルの保存
model.booster_.save_model('diopter_prediction_model.txt')


# このスニペットでは、実際のファイルパスやデータセットの詳細に応じて調整が必要です。
# また、特にモデルのパラメータに関しては、データに合わせたチューニングが推奨されます。
#%%

import matplotlib.pyplot as plt
import lightgbm as lgb

# 既存のモデルを使用する場合
model = lgb.Booster(model_file='diopter_prediction_model.txt')

# フィーチャー重要度の取得
feature_importances = model.feature_importance()

# フィーチャー名
feature_names = model.feature_name()

# 重要度の高い順に並び替え
sorted_idx = feature_importances.argsort()

# プロット
plt.figure(figsize=(10, 6))
plt.barh(range(len(sorted_idx)), feature_importances[sorted_idx], align='center')
plt.yticks(range(len(sorted_idx)), [feature_names[i] for i in sorted_idx])
plt.xlabel('Feature Importance')
plt.title('Feature Importance in LightGBM Model')
plt.show()



# %%
