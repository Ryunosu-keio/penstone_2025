import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def main():
 # 画像パスを指定
 image_path = "../experiment_images/101_1/1_3_brightness23.072_gamma1.092_sharpness0.325.jpg"
 image = Image.open(image_path).convert('L') # 画像をグレースケールで読み込み
 image_array = np.asarray(image)
 f = np.fft.fft2(image_array)               # 2Dフーリエ変換

 # csvを読み込み、2Dフーリエ変換をする
#  df = pd.read_csv('pivdata.csv')            # csvを読み込み  
#  f = np.fft.fft2(df)                        # 2Dフーリエ変換
 f_shift = np.fft.fftshift(f)               # 直流成分を中心に移動させるためN/2シフトさせる
 mag = 20 * np.log(np.abs(f_shift))         # パワースペクトルの計算                

 #pd.DataFrame(f_shift).to_csv('out.csv')    # フーリエ変換の結果をcsvに保存

 # パワースペクトルの表示
 plt.figure() 
 plt.plot(mag)
 
 # 角度方向分布の表示 (Angular Distribution Function)
 adf = average_angle(mag, 10)              # average_angleに渡す
 plt.figure()   
 plt.plot(range(-180,180,10),adf)
 plt.show()
 
 # 動径方向分布の表示 (Radial Distribution Function)
 rdf = average_radius(mag, 1)             # average_radiusに渡す
 print(rdf)
 plt.figure()
 plt.plot(range(0, 32, 1),rdf)
 plt.show

 
 # 複素平面を構成する値の配列を生成(原点は中心)
def complex_plane(width):
    half_width = width // 2
    re = np.array(range(width)) - half_width
    im = - re
    re, im = np.meshgrid(re, im)
    return re + im * 1j

 # スペクトルを与えられた角度の範囲内だけ集計
def aggregate_in_angle(agg_fun, spectrum, min_angle, max_angle):
    width = spectrum.shape[0]
    min_radius, max_radius = 0, width // 2
    cp = complex_plane(width)
    cp_mag = np.abs(cp)
    in_radius = np.logical_and(min_radius < cp_mag, cp_mag < max_radius)
    cp_angle = np.angle(cp, deg=True)
    in_angle = np.logical_and(min_angle <= cp_angle, cp_angle < max_angle)
    return agg_fun(spectrum[np.logical_and(in_radius, in_angle)])
  

 # 指定角度ごとの平均を求める
def average_angle(spectrum, angle_gap):
    means = [aggregate_in_angle(np.mean, spectrum, angle, angle + angle_gap)
             for angle in range(-180, 180, angle_gap)]
    return means
    
 # スペクトルを与えられた半径の範囲内だけ集計
def aggregate_in_radius(agg_fun, spectrum, min_radius, max_radius):
    width = spectrum.shape[0]
    #min_radius, max_radius = 0, width // 2
    cp = complex_plane(width)
    cp_mag = np.abs(cp)
    #in_radius = np.logical_and(min_radius < cp_mag, cp_mag < max_radius)
    in_radius = np.logical_and(min_radius <= cp_mag, cp_mag < max_radius)
    #return agg_fun(spectrum[np.logical_and(in_radius)])
    return agg_fun(spectrum[in_radius])

 # 指定半径ごとの平均を求める
def average_radius(spectrum, radius_gap):
    #means = [aggregate_in_angle(np.mean, spectrum, radius, radius + radius_gap)
    means = [aggregate_in_radius(np.mean, spectrum, radius, radius + radius_gap)
             for radius in range(0, 32, radius_gap)]
    return means 

main()