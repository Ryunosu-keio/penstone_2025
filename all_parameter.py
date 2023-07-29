import Photo_Parameters_2 as pp
from PIL import Image
from cor2 import transform, display_images_matrix, concat_images
import glob
import numpy as np
import cv2
import matplotlib.pyplot as plt
from tqdm import tqdm

Image.MAX_IMAGE_PIXELS = None  # disable limit (not recommended)

# or set a higher limit
Image.MAX_IMAGE_PIXELS = 400000000  # set limit to 400 million pixels

# files = glob.glob("testpic/*.jpg")
# files = glob.glob("testpic/O_light_dark_2.jpg")
files = ["testpic/O_light_dark_2.jpg"]
adjust_params = {
    "brightness": [0, 30, 60], # パラメーターの値を入れる
    "contrast": [0.8, 1, 1.2],
    "gamma": [0.5, 1, 1.1],
    "sharpness":[0, 0.5, 1.0],
    # "blur":[1, 3, 5],
    "equalization":[0, 8, 32]
}
# selected_parameters = ["輝度", "コントラスト"]


def main():
    for file in files:
        filename = file.split("/")[-1]
        filename = filename.split(".")[0]
        image = Image.open(file)
        image_list = []
        for param1 in tqdm(adjust_params):
            # print("param1", param1)
            for param2 in tqdm(adjust_params):
                if param1 != param2:
                    # print(param1, param2)
                    selected_parameters = [param1, param2]
                    # toolに対してtool2を適用する
                    # for num in adjust_params[param1]:
                    #     print(num)
                    #     # tool2に対してnumを適用する
                    #     for num2 in adjust_params[param2]:
                    #         print(num2)
                    #         # tool2に対してnum2を適用する
                    #         #ここに処理を書く
                    #         parameter1_values = parameter_options[selected_parameters[0]]
                    #         parameter2_values = parameter_options[selected_parameters[1]]
                    transformed_images = transform(image, selected_parameters, adjust_params[param1], adjust_params[param2])
                    # print(transformed_images)
                    # show transformed_images as matrix
                    img = concat_images(transformed_images, adjust_params[param1], adjust_params[param2], param1, param2)
                    # fig = display_images_matrix(transformed_images, adjust_params[param1], adjust_params[param2])
                    
                else:
                    # print(param1, param2)
                    selected_parameters = [param1, param2]
                    transformed_images = transform(image, selected_parameters, adjust_params[param1], adjust_params[param2])
                    # print(transformed_images)
                    # show transformed_images as matrix
                    # img = display_images_matrix(transformed_images, adjust_params[param1], adjust_params[param2])
                    img = concat_images(transformed_images, adjust_params[param1], adjust_params[param2], param1, param2)
                    # 同じ場合、toolのみ適用する
                # print(fig)
                # print(type(fig))
                # fig.canvas.draw()
                # img = np.array(fig.canvas.renderer.buffer_rgba())
                # img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR) 
                # cv2.imwrite("result.jpg", img)
                image_list.append(img)
                # print(img)
        # print(image_list)
        # img = display_images_matrix(image_list, adjust_params, adjust_params)
        img = concat_images(image_list, adjust_params, adjust_params, param1, param2)
        # img = concat_images(image_list, len(adjust_params), len(adjust_params))
        img_array = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        # cv2.imwrite("result.jpg", img_array)
        # cv2.imwrite("output/"+ filename + "_edited.jpg", img_array)
        # one behind directory
        # cv2.imwrite("../output/"+ filename + "_edited.jpg", img_array)
        cv2.imwrite("edited_" + filename + ".jpg", img_array)
                        #ここに処理を書く
                
        # 画像アップロード by cv2

if __name__ == "__main__":
    main()

    # show image not using streamlit


