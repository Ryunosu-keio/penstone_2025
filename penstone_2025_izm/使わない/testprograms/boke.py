import cv2

def apply_blur(filename, blur_size):
    # Load the image
    img = cv2.imread(filename)
    
    # Apply Gaussian blur
    img = cv2.GaussianBlur(img, (blur_size, blur_size), 0)
    
    cv2.imwrite("photos/3_blur.jpg", img)

apply_blur("photos/3.jpg", 5)  # Apply blur with kernel size of 5
