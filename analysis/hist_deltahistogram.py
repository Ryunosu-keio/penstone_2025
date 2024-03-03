# from PIL import Image
# import numpy as np
# import matplotlib.pyplot as plt
# import glob

# # 画像を読み込む
# def return_array(img_path):
#     image = Image.open(img_path)
#     img_array = np.array(image)
#     # 画像をグレースケールに変換し、numpy配列に変換
#     gray_image = image.convert("L")
#     gray_array = np.array(gray_image)
#     return img_array, gray_array

# def sharpness_factor(img_array,color):
#     # 各ピクセルについて、周囲8画素との輝度差の絶対値の和を計算
#     diff_sum_array = np.zeros_like(img_array, dtype=np.float32)

#     # 画像の境界を除くために1から開始し、-1で終了する
#     for y in range(1, img_array.shape[0] - 1):
#         for x in range(1, img_array.shape[1] - 1):
#             center_pixel = img_array[y, x]
#             # 周囲8画素との差を計算
#             neighbor_diffs = [
#                 np.abs(center_pixel - img_array[y-1, x-1]),
#                 np.abs(center_pixel - img_array[y-1, x]),
#                 np.abs(center_pixel - img_array[y-1, x+1]),
#                 np.abs(center_pixel - img_array[y, x-1]),
#                 np.abs(center_pixel - img_array[y, x+1]),
#                 np.abs(center_pixel - img_array[y+1, x-1]),
#                 np.abs(center_pixel - img_array[y+1, x]),
#                 np.abs(center_pixel - img_array[y+1, x+1]),
#             ]
#             # 差の絶対値の和を計算
#             diff_sum_array[y, x] = np.sum(neighbor_diffs)

#     # 平均を計算
#     average_diff = np.mean(diff_sum_array[1:-1, 1:-1])

#     # 累積ヒストグラム用のデータを生成
#     diff_hist, bin_edges = np.histogram(diff_sum_array[1:-1, 1:-1], bins=256, range=(0, 255))
#     cumulative_diff_hist = np.cumsum(diff_hist)

#     # 累積ヒストグラムをプロット
#     plt.figure(figsize=(10, 5))
#     plt.bar(bin_edges[:-1], cumulative_diff_hist, width=1, color=color, alpha=0.5)
#     plt.title('Cumulative Histogram of Average Absolute Differences in Brightness(blurred)')
#     plt.xlabel('Average Absolute Difference')
#     plt.ylabel('Cumulative Frequency')
#     plt.xlim(0, 255)
#     plt.ylim(0,800000)
#     plt.grid(True)
#     plt.show()

#     # 平均輝度差の値を表示
#     print(f"Average of absolute differences: {average_diff}")
#     return cumulative_diff_hist, bin_edges


# # img_path = glob.glob('../experiment_images//109_1/*_T_*jpg')[0]
# # img_array = return_array(img_path)
# # hist_gray,bin_gray = sharpness_factor(img_array,color="black")

# # 画像にガウシアンフィルタをかけてぼかす
# # from scipy.ndimage import gaussian_filter
# # blurred_img_array = gaussian_filter(img_array, sigma=1)
# # hist_blurred,bin_blurred = sharpness_factor(blurred_img_array,color="red")

# def kasaneru(hist_gray,hist_blurred):
#     plt.figure(figsize=(10, 5))
#     plt.bar(bin_gray[:-1], hist_gray, width=1, color='black', alpha=0.5, label='Original')
#     plt.bar(bin_blurred[:-1], hist_blurred, width=1, color='red', alpha=0.5, label='Blurred')
#     plt.title('Cumulative Histogram of Average Absolute Differences in Brightness')
#     plt.xlabel('Average Absolute Difference')
#     plt.ylabel('Cumulative Frequency')
#     plt.xlim(0, 255)
#     plt.legend()
#     plt.grid(True)
#     plt.show()




# #ソーベルフィルタをかけてエッジを抽出
# from scipy.ndimage import sobel
# # 画像を読み込む
# img_path = glob.glob('../experiment_images//109_1/*_T_*jpg')[0]
# img_path2 = glob.glob('../experiment_images//109_1/*_T_*jpg')[1]
# img_array, gray_array = return_array(img_path)
# img_array2, gray_array2 = return_array(img_path2)
# sobel_img_array = sobel(gray_array)
# sobel_img_array2 = sobel(gray_array2)
# #画像を表示
# plt.figure(figsize=(5, 5))
# plt.subplot(2, 2, 3)
# plt.imshow(sobel_img_array, cmap='gray')
# plt.axis('off')
# plt.title('Sobel Filtered Image')
# plt.subplot(2, 2, 4)
# plt.imshow(sobel_img_array2, cmap='gray')
# plt.axis('off')
# plt.title('Sobel Filtered Image')
# #元画像を表示
# plt.subplot(2, 2, 1)
# plt.imshow(img_array, cmap='gray')
# plt.axis('off')
# plt.title('Original Image')
# plt.subplot(2, 2, 2)
# plt.imshow(img_array2, cmap='gray')
# plt.axis('off')
# plt.title('Original Image')


# plt.show()


import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# 立方体のサイズ定義
x_start, x_end = 0, 10
y_start, y_end = 0, 10
z_start, z_end = 0, 10


def draw_hatch_lines_on_plane(ax, plane, start_point, end_point, fixed_value, delta, angle):
    """
    指定された平面に斜線を描画する関数。
    ax: 描画対象のAxes3Dオブジェクト。
    plane: 'xy', 'yz', 'xz' のいずれかを指定。
    start_point, end_point: 斜線を描画する範囲を定義する始点と終点の座標。
    fixed_value: 固定される軸の値。
    delta: 斜線間の間隔。
    angle: 斜線の方向。
    """
    if plane == 'xy':
        z = fixed_value
        for x in np.arange(start_point[0], end_point[0], delta):
            for y in np.arange(start_point[1], end_point[1], delta):
                ax.plot([x, x + angle[0]], [y, y + angle[1]], [z, z], color="black")
    elif plane == 'yz':
        x = fixed_value
        for y in np.arange(start_point[0], end_point[0], delta):
            for z in np.arange(start_point[1], end_point[1], delta):
                ax.plot([x, x], [y, y + angle[0]], [z, z + angle[1]], color="black")
    elif plane == 'xz':
        y = fixed_value
        for x in np.arange(start_point[0], end_point[0], delta):
            for z in np.arange(start_point[1], end_point[1], delta):
                ax.plot([x, x + angle[0]], [y, y], [z, z + angle[1]], color="black")

# 例: 底面、上面、側面に斜線を描画
delta = 1
draw_hatch_lines_on_plane(ax, 'xy', [x_start, y_start], [x_end, y_end], z_start, delta, [1, 1])
draw_hatch_lines_on_plane(ax, 'xy', [x_start, y_start], [x_end, y_end], z_end, delta, [1, -1])
draw_hatch_lines_on_plane(ax, 'yz', [y_start, z_start], [y_end, z_end], x_start, delta, [1, 1])
draw_hatch_lines_on_plane(ax, 'yz', [y_start, z_start], [y_end, z_end], x_end, delta, [1, -1])
draw_hatch_lines_on_plane(ax, 'xz', [x_start, z_start], [x_end, z_end], y_start, delta, [1, 1])
draw_hatch_lines_on_plane(ax, 'xz', [x_start, z_start], [x_end, z_end], y_end, delta, [1, -1])

ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_zlabel('Z Axis')
ax.set_xlim([x_start, x_end])
ax.set_ylim([y_start, y_end])
ax.set_zlim([z_start, z_end])
plt.show()
