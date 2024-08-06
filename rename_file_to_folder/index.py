import os
import re

def rename_files_in_folder(folder_path):
    # Lặp qua tất cả các tệp và thư mục trong thư mục
    for item in os.listdir(folder_path):
        old_file_path = os.path.join(folder_path, item)
        
        # Nếu là thư mục, gọi đệ quy để xử lý các tệp bên trong
        if os.path.isdir(old_file_path):
            rename_files_in_folder(old_file_path)
        
        # Tạo tên mới với dấu gạch dưới thay cho khoảng trắng và ký tự đặc biệt
        new_filename = re.sub(r'[^\w\._]+', '_', item)
        new_file_path = os.path.join(folder_path, new_filename)
        
        # Đổi tên tệp hoặc thư mục
        os.rename(old_file_path, new_file_path)

# Đường dẫn đến thư mục cần đổi tên
folder_path = '/root/OneDrive/BACKUP2019/Share/ACCOUNTANT'
rename_files_in_folder(folder_path)

print("Đổi tên tệp và thư mục thành công!")
