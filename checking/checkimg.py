from PIL import Image
import numpy as np

# Open the new image file
new_img_path = r'D:\tools\dv\checking\logo-2024-en-2.png'
new_img = Image.open(new_img_path)

# Convert image to grayscale for easier processing
new_img_gray = new_img.convert('L')
new_img_array = np.array(new_img_gray)

# Get non-white pixels (assuming white background)
new_non_white_pixels = np.argwhere(new_img_array < 255)

# Get bounding box of non-white pixels
new_top, new_left = np.min(new_non_white_pixels, axis=0)
new_bottom, new_right = np.max(new_non_white_pixels, axis=0)

# Calculate margins
new_margin_top = new_top
new_margin_bottom = new_img.height - new_bottom
new_margin_left = new_left
new_margin_right = new_img.width - new_right

print(new_margin_top, new_margin_bottom, new_margin_left, new_margin_right)
