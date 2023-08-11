import cv2
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from library.Photo_Parameters_2 import slide_brightness, adjust_contrast_adachi, adjust_gamma

def apply_brightness(image, brightness):
    return slide_brightness(image, brightness)

def apply_contrast(image, contrast):
    return adjust_contrast_adachi(image, contrast)

def apply_gamma(image, gamma):
    return adjust_gamma(image, gamma)

def transform(image, selected_parameters, parameter1_values, parameter2_values):
    # 変換した画像を格納するリスト
    transformed_images = []

    # 画像変換の実行
    for parameter1_value in parameter1_values:
        for parameter2_value in parameter2_values:
            transformed_image = image.copy()

            if selected_parameters[0] == "輝度":
                transformed_image = apply_brightness(transformed_image, parameter1_value)
            elif selected_parameters[0] == "コントラスト":
                transformed_image = apply_contrast(transformed_image, parameter1_value)
            elif selected_parameters[0] == "ガンマ":
                transformed_image = apply_gamma(transformed_image, parameter1_value)

            if selected_parameters[1] == "輝度":
                transformed_image = apply_brightness(transformed_image, parameter2_value)
            elif selected_parameters[1] == "コントラスト":
                transformed_image = apply_contrast(transformed_image, parameter2_value)
            elif selected_parameters[1] == "ガンマ":
                transformed_image = apply_gamma(transformed_image, parameter2_value)

            transformed_images.append(transformed_image)
    
    return transformed_images

def display_images_matrix(images, parameter1_values, parameter2_values):
    num_rows = len(parameter1_values)
    num_cols = len(parameter2_values)

    fig, axs = plt.subplots(num_rows, num_cols, figsize=(12, 12))

    for i in range(num_rows):
        for j in range(num_cols):
            index = i * num_cols + j
            axs[i, j].imshow(cv2.cvtColor(images[index], cv2.COLOR_BGR2RGB))
            axs[i, j].axis('off')

    plt.tight_layout()
    st.pyplot(fig)

def main():

    # パラメータ値の選択
    # 輝度、コントラスト、ガンマの値を入力
    brightness = st.text_input("輝度の値を入力してください（カンマ区切り）", "0,0,0")
    contrast = st.text_input("コントラストの値を入力してください（カンマ区切り）", "1.0,1.0,1.0")
    gamma = st.text_input("ガンマの値を入力してください（カンマ区切り）", "1.0,1.0,1.0")

    # 入力された値をリストに変換
    brightness_values = list(map(float, brightness.split(',')))
    contrast_values = list(map(float, contrast.split(',')))
    gamma_values = list(map(float, gamma.split(',')))

    # 輝度、コントラスト、ガンマの値を辞書に保存
    parameter_options = {
        "輝度": brightness_values,
        "コントラスト": contrast_values,
        "ガンマ": gamma_values
    }

    # 画像アップロード
    uploaded_file = st.file_uploader("画像をアップロードしてください", type=['jpg', 'jpeg', 'png'])
    
    #　パラメータ選択
    selected_parameters = st.multiselect("変換するパラメータを選択してください（2つ）", list(parameter_options.keys()), default=[], key="parameters")

    if len(selected_parameters) != 2:
        st.warning("2つのパラメータを選択してください。")
    else:
        parameter1_values = parameter_options[selected_parameters[0]]
        parameter2_values = parameter_options[selected_parameters[1]]

        if uploaded_file is not None:
            # 画像読み込み
            image = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR)
            transformed_images = transform(image, selected_parameters, parameter1_values, parameter2_values)
            display_images_matrix(transformed_images, parameter1_values, parameter2_values)
        
main()
