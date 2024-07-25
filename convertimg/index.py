import os
from PIL import Image

source_folder = 'D:\WorkingTuan\pythontool\convertimg\input'
destination_folder = 'D:\WorkingTuan\pythontool\convertimg\output'

for filename in os.listdir(source_folder):
    if filename.endswith('.jfif'):
        im = Image.open(os.path.join(source_folder, filename))
        rgb_im = im.convert('RGB')
        rgb_im.save(os.path.join(destination_folder,
                    filename.replace('.jfif', '.png')))
