import cv2
import numpy as np
import matplotlib.pyplot as plt
from Photo_Parameters_2 import slide_brightness, adjust_contrast_adachi, adjust_gamma
from PIL import Image
import Photo_Parameters_2 as pp


def apply_brightness(image, brightness):
    return slide_brightness(image, brightness)

def apply_contrast(image, contrast):
    return adjust_contrast_adachi(image, contrast)

def apply_gamma(image, gamma):
    return adjust_gamma(image, gamma)

def transformBy3params(image, selected_parameters):
    # 画像変換の実行
    transformed_image = image.copy()
    for param in selected_parameters:
        if param == "brightness":
            transformed_image = pp.slide_brightness(transformed_image, selected_parameters["brightness"])
        elif param == "contrast":
            transformed_image = pp.adjust_contrast_adachi(transformed_image, selected_parameters["contrast"])
        elif param == "gamma":
            transformed_image = pp.adjust_gamma(transformed_image, selected_parameters["gamma"])
        elif param == "sharpness":
            transformed_image = pp.adjust_sharpness(transformed_image, selected_parameters["sharpness"])
        elif param == "blur":
            transformed_image = pp.adjust_blur(transformed_image, selected_parameters["blur"])
        elif param == "equalization":
            if selected_parameters[param] == 0:
                transformed_image = transformed_image
            else:
                transformed_image = pp.stretch_rgb_clahe(transformed_image, tile = selected_parameters["equalization"])
    return transformed_image


def transform(image, selected_parameters, parameter1_values, parameter2_values):
    # 変換した画像を格納するリスト
    transformed_images = []

    # 画像変換の実行
    for parameter1_value in parameter1_values:
        for parameter2_value in parameter2_values:
            transformed_image = image.copy()

            if selected_parameters[0] == "brightness":
                transformed_image = pp.slide_brightness(transformed_image, parameter1_value)
            elif selected_parameters[0] == "contrast":
                transformed_image = pp.adjust_contrast_adachi(transformed_image, parameter1_value)
            elif selected_parameters[0] == "gamma":
                transformed_image = pp.adjust_gamma(transformed_image, parameter1_value)
            elif selected_parameters[0] == "sharpness":
                transformed_image = pp.adjust_sharpness(transformed_image, parameter1_value)
            elif selected_parameters[0] == "blur":
                transformed_image = pp.adjust_blur(transformed_image, parameter1_value)
            elif selected_parameters[0] == "equalization":
                if parameter1_value == 0:
                    transformed_image = transformed_image
                else:
                    transformed_image = pp.stretch_rgb_clahe(transformed_image, parameter1_value)


            if selected_parameters[1] == "brightness":
                transformed_image = pp.slide_brightness(transformed_image, parameter2_value)
            elif selected_parameters[1] == "contrast":
                transformed_image = pp.adjust_contrast_adachi(transformed_image, parameter2_value)
            elif selected_parameters[1] == "gamma":
                transformed_image = pp.adjust_gamma(transformed_image, parameter2_value)
            elif selected_parameters[1] == "sharpness":
                transformed_image = pp.adjust_sharpness(transformed_image, parameter2_value)
            elif selected_parameters[1] == "blur":
                transformed_image = pp.adjust_blur(transformed_image, parameter2_value)
            elif selected_parameters[1] == "equalization":
                if parameter2_value == 0:
                    transformed_image = transformed_image
                else:
                    transformed_image = pp.stretch_rgb_clahe(image = transformed_image, tile = parameter2_value)

            transformed_images.append(transformed_image)
    
    return transformed_images

def display_images_matrix(images, parameter1_values, parameter2_values):
    num_rows = len(parameter1_values)
    num_cols = len(parameter2_values)

    fig, axs = plt.subplots(num_rows, num_cols, figsize=(12, 12))

    for i in range(num_rows):
        for j in range(num_cols):
            index = i * num_cols + j
            axs[i, j].imshow(cv2.cvtColor(np.array(images[index]), cv2.COLOR_BGR2RGB))
            axs[i, j].axis('off')
    plt.tight_layout()

    # savefig with higher dpi
    # fig.savefig("result.jpg", dpi=3000)

    return fig

# def concat_images(images, parameter1_values, parameter2_values):
    # num_rows = len(parameter1_values)
    # num_cols = len(parameter2_values)
    # width, height = images[0].size
    # width += 50
    # height += 50

    # # 新しい画像のサイズを定義
    # total_width = width * num_cols
    # total_height = height * num_rows

    # new_img = Image.new('RGB', (total_width, total_height))
    # print("######################")
    # print("images", images)

    # for i in range(num_cols):
    #     for j in range(num_rows):
    #         index = i * num_cols + j
    #         new_img.paste(images[index], (j*width, i*height))

    # new_img.save('concat_image.jpg')
    # print("new_img", new_img)
    # return new_img


def concat_images(images, parameter1_values, parameter2_values, param1, param2):

    num_rows = len(parameter1_values)
    num_cols = len(parameter2_values)
    width, height = images[0].size
    width += 50
    height += 50

    # 新しい画像のサイズを定義
    total_width = width * num_cols
    total_height = height * num_rows

    new_img = Image.new('RGB', (total_width, total_height))
    # print("######################")
    # print("images", images)

    for i in range(num_cols):
        for j in range(num_rows):
            index = i * num_cols + j
            if num_cols < 4:
                org = (50, 1000)
                text = param1 + str(parameter1_values[i]) + " " + param2 + str(parameter2_values[j])
                images[index] = np.array(images[index])
                cv2.putText(images[index], text, org, fontFace = cv2.FONT_HERSHEY_COMPLEX, fontScale = 1.2, color = (255,255,255), thickness = 4)
                # cv2 save image
                cv2.imwrite('test_image.jpg', images[index])
                images[index] = Image.fromarray(images[index])
                # images[index].save('test_image.jpg')
            new_img.paste(images[index], (j*width, i*height))


    new_img.save('concat_image.jpg')
    # print("new_img", new_img)
    return new_img


       
def main():
    selected_parameters = ["brightness", "contrast"]
    parameter_options = {
        "brightness": [0.5,1,1.5],
        "contrast": [0.5,1,1.5],
        "gamma": [0.5,1,1.5]
    }
    # 画像アップロード by cv2

    image = Image.open("2.jpg")
    # show image not using streamlit
    parameter1_values = parameter_options[selected_parameters[0]]
    parameter2_values = parameter_options[selected_parameters[1]]

    if image is not None:
        
        transformed_images = transform(image, selected_parameters, parameter1_values, parameter2_values)
        # print(transformed_images)
        # show transformed_images as matrix


        display_images_matrix(transformed_images, parameter1_values, parameter2_values)

# main()
