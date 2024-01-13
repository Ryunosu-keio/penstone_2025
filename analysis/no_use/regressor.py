from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 1. データセットを生成（独立変数は3つ）


df = pd.read_excel("../data/final_recent_dark/final_recent_dark_add_entropy.xlsx")
X = df[['gamma', 'contrast', 'brightness', 'sharpness', 'equalization']]
y = df['entropy_gray']


# トレーニングセットとテストセットに分割
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# 3. 重回帰モデルをトレーニング
model = LinearRegression()
model.fit(X_train, y_train)

# 4. モデルをテスト
y_pred = model.predict(X_test)

# 精度評価
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

mse, r2

print("Mean Squared Error (MSE):", mse)
print("R-squared (R2 ):", r2)