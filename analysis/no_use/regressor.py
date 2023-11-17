from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import numpy as np

# 1. データセットを生成（独立変数は3つ）
X, y = make_regression(n_samples=200, n_features=3, noise=0.1, random_state=42)

# 2. データをトレーニングセットとテストセットに分割
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
