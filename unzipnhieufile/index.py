import os
import zipfile
import re

# Đường dẫn tới folder chứa các file zip
input_folder = '/home/ellyluxury/htdocs/ellyluxury.com/wp-content'
output_folder = '/home/ellyluxury/htdocs/ellyluxury.com/wp-content'

# Tạo output_folder nếu chưa tồn tại
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Pattern để khớp với tên file
pattern = re.compile(r'backup_\d{4}-\d{2}-\d{2}-\d{4}_Where_Elegance_Meets_Affection__\w{12}-uploads\d{0,2}\.zip')

# Duyệt qua các file trong folder
for filename in os.listdir(input_folder):
    if pattern.match(filename):
        file_path = os.path.join(input_folder, filename)
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(output_folder)
        print(f'Extracted: {filename}')

print('All files have been extracted.')
