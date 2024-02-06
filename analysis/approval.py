# import cv2

# # 映像1（デスクトップカメラ）の初期化
# cap1 = cv2.VideoCapture(0)  # カメラデバイスを開く

# # 映像2（保存されたビデオ）の初期化
# cap2 = cv2.VideoCapture("C:\\Users\\ryuno\\OneDrive\\画像\\カメラ ロール\\WIN_20240206_19_28_11_Pro.mp4")  # ビデオファイルを開く

# while True:
#     # 映像1のフレームを読み込む
#     ret1, frame1 = cap1.read()
#     if ret1:
#         cv2.imshow('Camera', frame1)

#     # 映像2のフレームを読み込む
#     ret2, frame2 = cap2.read()
#     if ret2:
#         cv2.imshow('Saved Video', frame2)
#     else:
#         # 映像2が終わったら、最初から再開
#         cap2.set(cv2.CAP_PROP_POS_FRAMES, 0)

#     # キー入力を待つ
#     if cv2.waitKey(25) & 0xFF == ord('q'):
#         break

# # リソースの解放
# cap1.release()
# cap2.release()
# cv2.destroyAllWindows()

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

# 音声ファイルの読み込み
# y, sr = librosa.load("C:\\Users\\ryuno\\OneDrive\\音楽

