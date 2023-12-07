from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

def color_hist(filename):
    img = np.asarray(Image.open(filename).convert("RGB")).reshape(-1,3)
    plt.hist(img, color=["red", "green", "blue"], bins=128)
    plt.show()
    plt.xlim(0, 255)
    # plt.savefig('histogram/original_hist.png')


color_hist("photos/3.jpg")

