import cv2
import numpy as np
import matplotlib.pyplot as plt
from Photo_Parameters_2 import slide_brightness, adjust_contrast_adachi, adjust_gamma
from PIL import Image

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
    # image = np.array(image, dtype=np.uint8)
    for i in range(num_rows):
        for j in range(num_cols):
            index = i * num_cols + j
            axs[i, j].imshow(cv2.cvtColor(np.array(images[index]), cv2.COLOR_BGR2RGB))
            axs[i, j].axis('off')
    plt.tight_layout()
    plt.show()

def main():
    selected_parameters = ["輝度", "コントラスト"]
    parameter_options = {
        "輝度": [0.5,1,1.5],
        "コントラスト": [0.5,1,1.5],
        "ガンマ": [0.5,1,1.5]
    }
    # 画像アップロード by cv2

    image = Image.open("2.jpg")
    # show image not using streamlit
    parameter1_values = parameter_options[selected_parameters[0]]
    parameter2_values = parameter_options[selected_parameters[1]]

    if image is not None:
        
        transformed_images = transform(image, selected_parameters, parameter1_values, parameter2_values)
        print(transformed_images)
        # show transformed_images as matrix


        display_images_matrix(transformed_images, parameter1_values, parameter2_values)

main()
