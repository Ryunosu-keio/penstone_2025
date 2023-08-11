import library.Photo_Parameters_2 as pp
from PIL import Image
from library.cor2 import transform, display_images_matrix, concat_images, transformBy3params
import glob
import numpy as np
import cv2
import matplotlib.pyplot as plt

# files = glob.glob("testpic/*.jpg")
# files = glob.glob("testpic/O_light_dark_2.jpg")
file = "testpic/O_light_dark_2.jpg"
# adjust_params = {
#     "brightness": [0, 30, 60], # パラメーターの値を入れる
#     "contrast": [0.8, 1, 1.2],
#     "gamma": [0.5, 1, 1.1],
#     "sharpness":[0, 0.5, 1.0],
#     # "blur":[1, 3, 5],
#     "equalization":[0, 8, 32]
# }

param1 = "brightness"
param2 = "contrast"
param3 = "gamma"
param1_value = 30
param2_value = 1
param3_value = 1

selected_parameters = {
    param1 : param1_value, 
    param2 : param2_value, 
    param3 : param3_value
    }

def create_edited_photo(file, selected_parameters):
    image = Image.open(file)
    transformed_image = transformBy3params(image, selected_parameters)
    img_array = cv2.cvtColor(np.array(transformed_image), cv2.COLOR_RGB2BGR)
    # cv2.imwrite("edited_" + filename + ".jpg", img_array)
    return img_array



